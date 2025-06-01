import logging
from typing import Any, Dict, List
from .confidence_scorer import ConfidenceScorer
from .result_cache import ResultCache
from .pattern_recognizer import APIPatternRecognizer
from ..processing.website_analyzer import WebsiteAnalyzer # Added import

logger = logging.getLogger(__name__)

class ResultProcessor:
    """
    Processes and analyzes results from various API discovery methods.
    This includes scoring, caching, and pattern recognition.
    """
    def __init__(self, cache_ttl_seconds: int = 3600):
        self.cache = ResultCache(max_age_seconds=cache_ttl_seconds)
        # Scorer might be initialized later if it needs specific data
        # self.scorer = ConfidenceScorer() 

    def process_results(
        self,
        discovery_method: str,
        data: Any,
        openapi_spec: Dict | None = None,
        http_interactions: List[Dict] | None = None
    ) -> Dict:
        """
        Main method to process discovery results.

        Args:
            discovery_method: Name of the discovery method (e.g., 'mitmproxy', 'openapi_spec').
            data: The raw data from the discovery method. This could be an OpenAPI spec,
                  a list of HTTP interactions, etc.
            openapi_spec: An OpenAPI specification dictionary, if available.
                         This is particularly useful for context even if data itself is the spec.
            http_interactions: A list of observed HTTP interactions, if available.

        Returns:
            A dictionary containing the processed and analyzed results.
        """
        cache_key = self.cache.generate_key(discovery_method, data)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result

        processed_output: Dict[str, Any] = {
            "discovery_method": discovery_method,
            "raw_data_summary": self._summarize_raw_data(data),
            "analysis_summary": {}
        }

        # Initialize scorer and recognizer with available context
        # The openapi_spec and http_interactions passed to process_results
        # are used as the primary context for pattern recognition.
        # If 'data' itself is an OpenAPI spec, it should also be passed as 'openapi_spec'.
        
        current_openapi_spec = openapi_spec
        if discovery_method == 'openapi_spec' and isinstance(data, dict):
            current_openapi_spec = data # data is the spec itself

        current_http_interactions = http_interactions
        if discovery_method == 'mitmproxy' and isinstance(data, list): # Assuming mitm data is a list of interactions
            current_http_interactions = data


        # Confidence Scoring
        # Scorer needs to be designed to work with various data types or structured input
        # Initialize scorer and recognizer
        # Scorer is initialized without spec/interactions here, as its `score` method takes patterns.
        # PatternRecognizer is initialized with spec/interactions if available for its main task.
        self.confidence_scorer = ConfidenceScorer(
            openapi_spec=current_openapi_spec, # Still useful if scorer's methods are adapted
            http_interactions=current_http_interactions
        )
        self.pattern_recognizer = APIPatternRecognizer(
            openapi_spec=current_openapi_spec,
            http_interactions=current_http_interactions
        )

        recognized_patterns: Dict[str, Any] = {}
        raw_data_to_store: Any = data # Default to original data for storing

        if discovery_method == 'openapi_spec':
            if current_openapi_spec:
                # The pattern_recognizer was already initialized with the spec
                recognized_patterns = self.pattern_recognizer.identify_all_patterns()
                # The score method in ConfidenceScorer now takes patterns and source type
                processed_output["analysis_summary"]["confidence_score"] = self.confidence_scorer.score(
                    recognized_patterns, data_source_type='openapi'
                )
            else:
                processed_output["analysis_summary"]["confidence_score"] = self.confidence_scorer.score(
                    {}, data_source_type='openapi' # Score with empty patterns if spec is missing
                )
            processed_output["analysis_summary"]["confidence_details"] = self.confidence_scorer.get_score_details() # Potentially adapt this too

        elif discovery_method == 'mitmproxy':
            if current_http_interactions:
                recognized_patterns = self.pattern_recognizer.identify_all_patterns()
                processed_output["analysis_summary"]["confidence_score"] = self.confidence_scorer.score(
                    recognized_patterns, data_source_type='http_interactions'
                )
            else:
                processed_output["analysis_summary"]["confidence_score"] = self.confidence_scorer.score(
                     {}, data_source_type='http_interactions'
                )
            processed_output["analysis_summary"]["confidence_details"] = self.confidence_scorer.get_score_details()

        elif discovery_method == "website_analysis":
            logger.info(f"Processing website analysis for data: {data}")
            url = data.get("url")
            if not url:
                logger.error("URL not provided for website analysis.")
                # Return error directly, do not cache this
                return {"error": "URL not provided for website analysis", "status_code": 400}

            website_analyzer = WebsiteAnalyzer(url)
            # Using crawl_depth=1 as per instruction, can be made configurable
            extracted_data = website_analyzer.analyze(crawl_depth=1)
            raw_data_to_store = extracted_data # Store the extracted URLs and text

            # Use the specialized recognizer method
            patterns_from_website = self.pattern_recognizer.recognize_from_website_data(
                urls=extracted_data.get("urls", []),
                text_content=extracted_data.get("text_content", [])
            )
            recognized_patterns = patterns_from_website # These are the main patterns for this method

            processed_output["analysis_summary"]["confidence_score"] = self.confidence_scorer.score(
                patterns_from_website, data_source_type='website'
            )
            # For website analysis, OpenAPI spec is None by default.
            # get_score_details might reflect this if not adapted.
            # We can pass a generic detail or specific one for website.
            processed_output["analysis_summary"]["confidence_details"] = {
                "source": "website_analysis",
                "url_analyzed": url,
                "urls_found": len(extracted_data.get("urls", [])),
                "text_snippets_found": len(extracted_data.get("text_content", []))
            }
            logger.info(f"Website analysis for {url} completed. Patterns: {patterns_from_website}")

        else: # Fallback for other or combined methods
            # Generic pattern recognition if spec or interactions are available
            if current_openapi_spec or current_http_interactions:
                 recognized_patterns = self.pattern_recognizer.identify_all_patterns()
            # Generic scoring, or decide based on available data
            # This part might need refinement based on how 'combined_source' etc. are defined
            processed_output["analysis_summary"]["confidence_score"] = self.confidence_scorer.score(
                recognized_patterns, data_source_type=discovery_method # Pass method name as type
            )
            processed_output["analysis_summary"]["confidence_details"] = self.confidence_scorer.get_score_details()

        processed_output["analysis_summary"]["api_conventions"] = recognized_patterns if recognized_patterns else "No patterns recognized or applicable."
        processed_output["raw_data_summary"] = self._summarize_raw_data(raw_data_to_store) # Use potentially transformed data

        self.cache.set(cache_key, processed_output)
        return processed_output

    def _summarize_raw_data(self, data: Any) -> str:
        """Provides a brief summary of the raw data type and size."""
        if isinstance(data, dict):
            return f"Dictionary with {len(data.keys())} top-level keys."
        elif isinstance(data, list):
            return f"List with {len(data)} items."
        elif isinstance(data, str):
            return f"String with length {len(data)}."
        else:
            return f"Data of type {type(data).__name__}."

if __name__ == '__main__':
    # Example Usage
    logging.basicConfig(level=logging.INFO) # Setup basic logging for the example
    processor = ResultProcessor(cache_ttl_seconds=60)

    # --- Example 1: Processing an OpenAPI spec ---
    sample_openapi_spec = {
        "openapi": "3.0.0",
        "info": {"title": "Test API from Spec", "version": "v1.0"},
        "paths": {
            "/test": {
                "get": {
                    "summary": "Test endpoint",
                    "responses": {"200": {"description": "OK"}}
                }
            }
        },
        "components": {
            "securitySchemes": { "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-KEY"}}
        }
    }
    processed_spec_results = processor.process_results(
        discovery_method='openapi_spec',
        data=sample_openapi_spec,
        openapi_spec=sample_openapi_spec # Pass spec as context for recognizer
    )
    print("--- Processed OpenAPI Spec ---   ")
    import json
    print(json.dumps(processed_spec_results, indent=2))
    print("\n")

    # --- Example 2: Processing HTTP interactions ---
    sample_http_interactions = [
        {
            "request": {"method": "GET", "url": "/api/v1/items", "headers": {"X-API-Version": "1"}},
            "response": {"status_code": 200, "headers": {"Content-Type": "application/json"}}
        },
        {
            "request": {"method": "POST", "url": "/api/v1/items", "headers": {}},
            "response": {"status_code": 201}
        }
    ]
    processed_http_results = processor.process_results(
        discovery_method='mitmproxy',
        data=sample_http_interactions,
        http_interactions=sample_http_interactions # Pass interactions as context
    )
    print("--- Processed HTTP Interactions ---   ")
    print(json.dumps(processed_http_results, indent=2))
    print("\n")
    
    # --- Example 3: Processing with both OpenAPI and HTTP interactions for richer context ---
    # (e.g. an OpenAPI spec was found, AND live traffic was captured)
    processed_combined_results = processor.process_results(
        discovery_method='combined_source', # Hypothetical method
        data={"summary": "Data from combined source..."}, # The primary data might be something else
        openapi_spec=sample_openapi_spec,       # Provide the spec
        http_interactions=sample_http_interactions # Provide the traffic
    )
    print("--- Processed Combined Context (Spec + HTTP) ---   ")
    print(json.dumps(processed_combined_results, indent=2))
    print("\n")

    # --- Example 4: No spec or interactions for pattern recognizer ---
    processed_minimal_results = processor.process_results(
        discovery_method='some_other_data',
        data="Some opaque data string"
        # No openapi_spec or http_interactions provided
    )
    print("--- Processed Minimal Context (No Spec/HTTP for Patterns) ---   ")
    print(json.dumps(processed_minimal_results, indent=2))
    print("\n")

    # --- Example 5: Processing Website Analysis ---
    # Assuming WebsiteAnalyzer and its dependencies are available
    # and the test URL is accessible or mocked.
    # For a real run, ensure 'requests' can access the URL.
    # This example will likely make a real HTTP request if not mocked.
    website_data = {"url": "http://example.com"} # A site known to have some content
    # To test sitemap/robots, a more specific test URL or local http server setup is needed.
    # For local testing:
    # 1. Create dummy files: index.html, robots.txt, sitemap.xml in a folder.
    #    index.html: <html><body><a href="page1.html">Page 1</a> API docs <a href="/api/v1/info">Info</a></body></html>
    #    robots.txt: User-agent: *\nAllow: /api/\nDisallow: /private/
    #    sitemap.xml: <?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>http://localhost:8000/page1.html</loc></url></urlset>
    # 2. Run `python -m http.server 8000` in that folder.
    # 3. Change website_data to `{"url": "http://localhost:8000"}`

    print(f"--- Processing Website Analysis for URL: {website_data['url']} ---")
    # As this makes live requests, it's good practice to wrap in try/except for tests
    try:
        processed_website_results = processor.process_results(
            discovery_method='website_analysis',
            data=website_data
            # openapi_spec and http_interactions are not typically provided here
        )
        print(json.dumps(processed_website_results, indent=2))
    except Exception as e:
        print(f"Error during website analysis example: {e}")
        print("This might be due to network issues or the target website's structure.")
    print("\n")