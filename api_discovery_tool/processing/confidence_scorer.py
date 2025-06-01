import datetime

# Define constants for source reliability scores
SOURCE_RELIABILITY_SCORES = {
    'official_doc': 0.9,
    'known_api_db': 0.8,
    'partner_api': 0.75, # Assuming partner APIs are generally reliable
    'internal_source': 0.95, # Internal sources might be highly reliable
    'blog': 0.5,
    'forum': 0.3,
    'code_repository': 0.6, # e.g., GitHub search results
    'web_search': 0.4, # General web search results
    'unknown': 0.2,
}

# Define constants for weighting factors
WEIGHTS = {
    'completeness': 0.3,
    'reliability': 0.4,
    'recency': 0.15,
    'validation': 0.15,
}

# Define recency score parameters
MAX_RECENCY_SCORE = 1.0
RECENCY_DECAY_RATE_PER_YEAR = 0.1 # Score decays by 10% per year of age

def calculate_completeness_score(fields_present: int, total_expected_fields: int) -> float:
    """Calculates a score based on data completeness."""
    if total_expected_fields <= 0:
        return 0.0  # Avoid division by zero, or handle as low confidence
    completeness_ratio = fields_present / total_expected_fields
    return min(max(completeness_ratio, 0.0), 1.0) # Ensure score is between 0 and 1

def calculate_reliability_score(source_type: str) -> float:
    """Calculates a score based on source reliability."""
    return SOURCE_RELIABILITY_SCORES.get(source_type.lower(), SOURCE_RELIABILITY_SCORES['unknown'])

def calculate_recency_score(discovery_timestamp: datetime.datetime | None) -> float:
    """Calculates a score based on the recency of the information."""
    if discovery_timestamp is None:
        return 0.5 # Neutral score if timestamp is unknown

    # Ensure discovery_timestamp is offset-aware for comparison with offset-aware datetime.now()
    if discovery_timestamp.tzinfo is None or discovery_timestamp.tzinfo.utcoffset(discovery_timestamp) is None:
        # If naive, assume UTC. This might need adjustment based on how timestamps are stored.
        discovery_timestamp = discovery_timestamp.replace(tzinfo=datetime.timezone.utc)

    age_in_days = (datetime.datetime.now(datetime.timezone.utc) - discovery_timestamp).days
    if age_in_days < 0: # Timestamp is in the future, treat as very recent or an error
        return MAX_RECENCY_SCORE

    age_in_years = age_in_days / 365.25
    decay_factor = RECENCY_DECAY_RATE_PER_YEAR * age_in_years
    recency_score = MAX_RECENCY_SCORE - decay_factor
    return min(max(recency_score, 0.0), MAX_RECENCY_SCORE) # Ensure score is between 0 and MAX_RECENCY_SCORE

def calculate_validation_score(validated: bool | None) -> float:
    """Calculates a score based on whether the data was validated."""
    if validated is None:
        return 0.5 # Neutral score if validation status is unknown
    return 1.0 if validated else 0.0

class ConfidenceScorer:
    def __init__(self, openapi_spec=None, http_interactions=None):
        self.openapi_spec = openapi_spec if openapi_spec else {}
        self.http_interactions = http_interactions if http_interactions else []
        # TODO: Potentially pre-process or extract features from spec/interactions here
        # For now, calculate_overall_score will expect structured metadata.

    def score(self, patterns: dict, data_source_type: str) -> float:
        """
        Calculates a confidence score based on recognized patterns and data source type.

        Args:
            patterns: A dictionary of recognized API patterns.
            data_source_type: The type of data source (e.g., 'openapi', 'website', 'http_interactions').

        Returns:
            A confidence score between 0 and 100.
        """
        score = 0

        if data_source_type == 'openapi':
            # Basic scoring for OpenAPI specs
            score += 50  # Base score for being an OpenAPI spec
            if patterns.get("versioning_schemes"): # from pattern_recognizer's versioning
                score += 10
            if patterns.get("naming_conventions"):
                score += 5
            if patterns.get("authentication_schemes"):
                score += 10
            if patterns.get("data_formats") and any(fmt for fmt in patterns["data_formats"].values() if isinstance(fmt, dict) and fmt): # Check if any format is specified
                score += 5
            # This is a simplistic example. A more detailed OpenAPI scoring
            # would use the old calculate_overall_score logic or similar.
            # For now, let's use some elements from the old logic directly if openapi_spec is available
            if self.openapi_spec:
                if self.openapi_spec.get("info", {}).get("title"):
                    score += 5
                if self.openapi_spec.get("paths"):
                    score += 10 * min(len(self.openapi_spec.get("paths", {})), 3) # Add up to 30 points for paths
                if self.openapi_spec.get("components", {}).get("securitySchemes"):
                    score += 5
            return min(max(score, 0), 100)

        elif data_source_type == 'website':
            score += 30  # Base score for website data
            if patterns.get("versioning_schemes"):
                score += 20
            if patterns.get("common_paths"):
                score += 15 * len(patterns.get("common_paths", [])) # 15 per common path type
            if patterns.get("keyword_matches_in_urls"):
                score += 5 * len(patterns.get("keyword_matches_in_urls", [])) # 5 per URL with keyword
            # Add points for keyword_matches_in_text when implemented
            # if patterns.get("keyword_matches_in_text"):
            #     score += 2 * len(patterns.get("keyword_matches_in_text", []))
            return min(max(score, 0), 100)

        elif data_source_type == 'http_interactions':
            # Basic scoring for HTTP interactions
            score += 40 # Base score for having interactions
            if patterns.get("versioning", {}).get("identified_versions"):
                score += 15
            if patterns.get("authentication", {}).get("observed_auth_headers"):
                score += 15
            if patterns.get("http_methods",{}).get("observed_methods"):
                 score += 5 * len(patterns.get("http_methods",{}).get("observed_methods",[]))
            if self.http_interactions: # from the constructor
                score += 2 * len(self.http_interactions) # 2 points per interaction, cap later
            return min(max(score, 0), 100)

        # Default for unknown or other types
        return 10


    def calculate_individual_metric_score(self, metric_name: str, data_point: dict) -> float:
        """
        Calculates a score for an individual metric based on available data.
        This is a placeholder and would need to be expanded based on actual metrics.
        """
        if metric_name == "has_description":
            return 1.0 if data_point.get("description") else 0.0
        elif metric_name == "has_clear_versioning": # Example: has_clear_versioning
             # This would require versioning info from APIPatternRecognizer or similar
            return data_point.get("versioning_clarity_score", 0.5) # Default to neutral
        # Add more metric calculations here
        return 0.5 # Default for unhandled metrics


    def calculate_overall_score(self, discovery_results: list | None = None) -> float:
        """
        Calculates an overall confidence score based on various factors.
        This method is kept for potential internal use or for a different scoring model,
        but the primary scoring is now intended via the `score` method.
        """
        # This is a high-level placeholder. A real implementation would be more complex.
        # It might iterate through endpoints, parameters, etc., from spec/interactions,
        # calculate sub-scores, and then aggregate them.

        total_score = 0
        num_components = 0

        if self.openapi_spec.get("info", {}).get("title"):
            total_score += 0.8 # Base score for having a title
            num_components += 1
        if self.openapi_spec.get("paths"):
            total_score += 1.0 * len(self.openapi_spec["paths"]) # Score per path
            num_components += len(self.openapi_spec["paths"])
        
        if self.http_interactions:
            total_score += 0.5 * len(self.http_interactions) # Score per interaction
            num_components += len(self.http_interactions)

        if num_components == 0:
            return 0.2 # Low confidence if no data to score

        # Simple average for now, normalized (this isn't a true weighted score yet)
        # The original score was 0-1. The new `score` method is 0-100.
        # This method will remain 0-1 for now.
        overall_confidence = (total_score / (num_components * 1.0)) * 0.7
        
        if self.openapi_spec and self.http_interactions:
            overall_confidence += 0.1
            
        return min(max(overall_confidence, 0.0), 1.0)


    def get_score_details(self) -> dict:
        """
        Returns a dictionary with details about how the score was calculated.
        Placeholder for more detailed breakdown.
        """
        details = {
            "factors_considered": [],
            "warnings": []
        }
        if not self.openapi_spec:
            details["warnings"].append("OpenAPI specification not provided or empty.")
        else:
            details["factors_considered"].append("OpenAPI spec presence")
            if "paths" in self.openapi_spec and len(self.openapi_spec["paths"]) > 0 :
                 details["factors_considered"].append(f"{len(self.openapi_spec['paths'])} paths found in spec")
            else:
                 details["warnings"].append("No paths found in OpenAPI spec.")


        if not self.http_interactions:
            details["warnings"].append("HTTP interactions not provided or empty.")
        else:
            details["factors_considered"].append("HTTP interactions presence")
            details["factors_considered"].append(f"{len(self.http_interactions)} HTTP interactions found")

        # Add more detailed scoring logic and reporting here
        # For example, check for presence of security definitions, examples, etc.
        if self.openapi_spec.get("components", {}).get("securitySchemes"):
            details["factors_considered"].append("Security schemes defined in spec.")
        else:
            details["warnings"].append("No security schemes defined in OpenAPI spec.")
            
        return details

if __name__ == '__main__':
    # Example Usage (adapted from the original scoring.py)
    print("Running example confidence score calculations (using ConfidenceScorer class)...")

    # Instantiate scorer (can be done once)
    scorer = ConfidenceScorer()

    # Example 1: Website Data
    website_patterns_example = {
        "versioning_schemes": ["v1", "v2"],
        "common_paths": ["api", "service"],
        "keyword_matches_in_urls": [{"url": "example.com/api/users", "keyword": "users"}, {"url": "example.com/api/products", "keyword": "products"}],
        "keyword_matches_in_text": []
    }
    score_website = scorer.score(website_patterns_example, data_source_type='website')
    print(f"Website Data Score: {score_website}")

    # Example 2: OpenAPI Data (basic)
    # For a more accurate OpenAPI score, the scorer would need the spec via its constructor,
    # and the patterns would be generated by APIPatternRecognizer.
    openapi_patterns_example = {
        "versioning_schemes": ["v1"],
        "naming_conventions": {"path_segments": {"camelCase": 5}},
        "authentication_schemes": [{"name": "ApiKeyAuth", "type": "apiKey"}],
        "data_formats": {"spec_produces": {"application/json": 1}}
    }
    # Example with a spec passed to constructor for more detailed scoring
    spec_good = {"openapi": "3.0.0", "info": {"title": "Good API"}, "paths": {"/test/v1/go": {"get": {}}}, "components": {"securitySchemes": {"apikey": {"type": "apiKey"}}}}
    scorer_with_spec = ConfidenceScorer(openapi_spec=spec_good)
    score_openapi = scorer_with_spec.score(openapi_patterns_example, data_source_type='openapi')
    print(f"OpenAPI Data Score (with spec): {score_openapi}")

    # Example 3: HTTP Interactions Data (basic)
    http_patterns_example = {
        "versioning": {"identified_versions": ["v2"]},
        "authentication": {"observed_auth_headers": {"Authorization: Bearer": 5}},
        "http_methods": {"observed_methods": {"GET":10, "POST":5}}
    }
    # Example with interactions passed to constructor
    interactions_some = [{"request": {"method":"GET"}, "response": {}}, {"request": {"method":"POST"}, "response": {}}]
    scorer_with_interactions = ConfidenceScorer(http_interactions=interactions_some)
    score_http = scorer_with_interactions.score(http_patterns_example, data_source_type='http_interactions')
    print(f"HTTP Interactions Data Score (with interactions): {score_http}")

    # Example 4: Unknown type
    score_unknown = scorer.score({}, data_source_type='unknown_type')
    print(f"Unknown Data Type Score: {score_unknown}")

    # Test the old calculate_overall_score method (still exists)
    scorer_old_method = ConfidenceScorer(openapi_spec=spec_good, http_interactions=interactions_some)
    old_score = scorer_old_method.calculate_overall_score()
    details_old = scorer_old_method.get_score_details()
    print(f"Old calculate_overall_score (spec + interactions): {old_score:.2f}")
    # print(f"Old method details: {details_old}")