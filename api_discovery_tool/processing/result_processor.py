"""
Result Processing Pipeline Module

This module orchestrates the complete API discovery result processing pipeline, integrating
caching, confidence scoring, and pattern recognition to provide comprehensive analysis of
discovered API endpoints.

Processing Pipeline:
    1. Cache Check
       - Check if results for the same parameters already exist in cache
       - If found and not stale, return cached results immediately
       - Cache uses SHA256 hashing of parameters for consistent key generation

    2. Data Preparation
       - Extract OpenAPI specifications from discovery data (if available)
       - Extract HTTP interactions from discovery data (if available)
       - Prepare data for scoring and pattern recognition

    3. Confidence Scoring
       - Initialize ConfidenceScorer with available data
       - Calculate overall confidence score based on multiple factors
       - Generate detailed scoring breakdown for transparency

    4. Pattern Recognition
       - Initialize APIPatternRecognizer with OpenAPI spec and HTTP interactions
       - Identify naming conventions (camelCase, snake_case, etc.)
       - Detect versioning strategies (path, header, query param)
       - Recognize authentication schemes (API key, Bearer, OAuth2)
       - Identify pagination patterns (page-based, offset, cursor)
       - Analyze data formats and content types
       - Detect HTTP method usage patterns
       - Identify status code patterns

    5. Result Assembly
       - Combine all analysis results into structured output
       - Include raw data summary
       - Include confidence score and details
       - Include recognized API conventions and patterns

    6. Cache Storage
       - Store processed results in cache with current timestamp
       - Cache expires based on configured TTL (default: 1 hour)
       - Subsequent identical requests will use cached results

Pipeline Architecture:
    ResultProcessor
    ├── ResultCache (Caching layer)
    ├── ConfidenceScorer (Quality assessment)
    └── APIPatternRecognizer (Convention detection)

Supported Discovery Methods:
    - 'openapi_spec': OpenAPI/Swagger specification discovered
    - 'mitmproxy': HTTP traffic captured via MITM proxy
    - 'combined_source': Multiple discovery methods used together
    - Custom methods can be added by users

Output Structure:
    {
        "discovery_method": str,
        "raw_data_summary": str,
        "analysis_summary": {
            "confidence_score": float,
            "confidence_details": dict,
            "api_conventions": dict
        }
    }

Usage Example:
    >>> processor = ResultProcessor(cache_ttl_seconds=3600)
    >>> result = processor.process_results(
    ...     discovery_method='openapi_spec',
    ...     data=openapi_spec_data,
    ...     openapi_spec=openapi_spec_data
    ... )
    >>> print(f"Confidence: {result['analysis_summary']['confidence_score']:.2f}")

Classes:
    ResultProcessor: Main orchestrator for the result processing pipeline
"""

from typing import Any, Dict, List
from .confidence_scorer import ConfidenceScorer
from .result_cache import ResultCache
from .pattern_recognizer import APIPatternRecognizer

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
        # For now, let's assume it can take the spec and interactions
        scorer = ConfidenceScorer(
            openapi_spec=current_openapi_spec,
            http_interactions=current_http_interactions
        )
        processed_output["analysis_summary"]["confidence_score"] = scorer.calculate_overall_score()
        processed_output["analysis_summary"]["confidence_details"] = scorer.get_score_details()


        # Pattern Recognition
        if current_openapi_spec or current_http_interactions: # Only run if there's data to analyze
            pattern_recognizer = APIPatternRecognizer(
                openapi_spec=current_openapi_spec,
                http_interactions=current_http_interactions
            )
            recognized_patterns = pattern_recognizer.identify_all_patterns()
            processed_output["analysis_summary"]["api_conventions"] = recognized_patterns
        else:
            processed_output["analysis_summary"]["api_conventions"] = "No OpenAPI spec or HTTP interactions provided for pattern recognition."


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