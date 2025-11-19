"""
Confidence Scoring Module

This module provides functionality to calculate confidence scores for discovered API information
based on multiple factors including data completeness, source reliability, recency, and validation
status. Higher scores indicate more trustworthy and complete API discovery results.

Scoring Algorithm:
    The overall confidence score is a weighted combination of four key factors:

    1. Completeness Score (Weight: 30%)
       - Measures how many expected fields are present in the discovery data
       - Formula: (fields_present / total_expected_fields)
       - Range: 0.0 to 1.0

    2. Reliability Score (Weight: 40%)
       - Based on the trustworthiness of the data source
       - Official documentation: 0.9
       - Known API databases: 0.8
       - Partner APIs: 0.75
       - Internal sources: 0.95
       - Code repositories: 0.6
       - Blogs: 0.5
       - Web search: 0.4
       - Forums: 0.3
       - Unknown: 0.2

    3. Recency Score (Weight: 15%)
       - Measures how recent the discovered information is
       - Decay rate: 10% per year of age
       - Formula: MAX_SCORE - (decay_rate * age_in_years)
       - Range: 0.0 to 1.0

    4. Validation Score (Weight: 15%)
       - Whether the discovered data has been validated
       - Validated: 1.0
       - Not validated: 0.0
       - Unknown: 0.5 (neutral)

    Final Score = (completeness * 0.3) + (reliability * 0.4) + (recency * 0.15) + (validation * 0.15)

Scoring Weights:
    COMPLETENESS: 30% - Ensures discovered data has all necessary fields
    RELIABILITY:  40% - Most important factor, prioritizes trustworthy sources
    RECENCY:      15% - Prefers newer information but not critical
    VALIDATION:   15% - Prefers validated data but accounts for unvalidated discoveries

Usage Example:
    >>> scorer = ConfidenceScorer(
    ...     openapi_spec={"openapi": "3.0.0", "paths": {"/users": {"get": {}}}},
    ...     http_interactions=[{"request": {}, "response": {}}]
    ... )
    >>> score = scorer.calculate_overall_score()
    >>> print(f"Confidence: {score:.2f}")
    Confidence: 0.75
    >>> details = scorer.get_score_details()

Constants:
    SOURCE_RELIABILITY_SCORES: Mapping of source types to reliability scores
    WEIGHTS: Weighting factors for each scoring dimension
    MAX_RECENCY_SCORE: Maximum score for recency (1.0)
    RECENCY_DECAY_RATE_PER_YEAR: Annual decay rate for recency score (0.1)

Classes:
    ConfidenceScorer: Main scoring class for API discovery results
"""

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

    def calculate_individual_metric_score(self, metric_name: str, data_point: dict) -> float:
        """
        Calculates a score for an individual metric based on available data.
        This is a placeholder and would need to be expanded based on actual metrics.
        """
        if metric_name == "has_description":
            return 1.0 if data_point.get("description") else 0.0
        elif metric_name == "has_明確な_versioning": # Example: has_clear_versioning
             # This would require versioning info from APIPatternRecognizer or similar
            return data_point.get("versioning_clarity_score", 0.5) # Default to neutral
        # Add more metric calculations here
        return 0.5 # Default for unhandled metrics


    def calculate_overall_score(self, discovery_results: list | None = None) -> float:
        """
        Calculates an overall confidence score based on various factors.
        This version is simplified and assumes a list of discovery_results,
        or uses internal openapi_spec/http_interactions if discovery_results is None.
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
        overall_confidence = (total_score / (num_components * 1.0)) * 0.7 # Max possible is 1, scale to 0.7 for now
        
        # Add a small bonus if both spec and interactions are present
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

    # Example 1: Based on an OpenAPI spec
    spec_good = {"openapi": "3.0.0", "info": {"title": "Good API"}, "paths": {"/test": {"get": {}}}, "components": {"securitySchemes": {"apikey": {"type": "apiKey"}}}}
    scorer1 = ConfidenceScorer(openapi_spec=spec_good)
    score1 = scorer1.calculate_overall_score()
    details1 = scorer1.get_score_details()
    print(f"Good Spec Score: {score1:.2f}")
    print(f"Details: {details1}")

    # Example 2: Based on HTTP interactions only
    interactions_some = [{"request": {}, "response": {}}, {"request": {}, "response": {}}]
    scorer2 = ConfidenceScorer(http_interactions=interactions_some)
    score2 = scorer2.calculate_overall_score()
    details2 = scorer2.get_score_details()
    print(f"Some Interactions Score: {score2:.2f}")
    print(f"Details: {details2}")

    # Example 3: Both spec and interactions
    scorer3 = ConfidenceScorer(openapi_spec=spec_good, http_interactions=interactions_some)
    score3 = scorer3.calculate_overall_score()
    details3 = scorer3.get_score_details()
    print(f"Spec + Interactions Score: {score3:.2f}")
    print(f"Details: {details3}")
    
    # Example 4: Empty/minimal data
    scorer4 = ConfidenceScorer()
    score4 = scorer4.calculate_overall_score()
    details4 = scorer4.get_score_details()
    print(f"Minimal Data Score: {score4:.2f}")
    print(f"Details: {details4}") 