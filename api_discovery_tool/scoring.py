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

def calculate_confidence(result_data: dict) -> float:
    """
    Calculates a confidence score for a given discovery result.

    Args:
        result_data (dict): A dictionary containing processed result information.
            Expected keys in result_data['metadata']:
            - 'source_type': (str) Type of the source (e.g., 'official_doc').
            - 'fields_present': (int) Number of fields found.
            - 'total_expected_fields': (int) Total number of expected fields.
            - 'discovery_timestamp': (datetime.datetime, optional) When the info was found.
            - 'validated': (bool, optional) If the data passed automated checks.

    Returns:
        float: A confidence score between 0.0 and 1.0.
    """
    metadata = result_data.get('metadata', {})

    completeness = calculate_completeness_score(
        metadata.get('fields_present', 0),
        metadata.get('total_expected_fields', 0)
    )

    reliability = calculate_reliability_score(
        metadata.get('source_type', 'unknown')
    )

    recency = calculate_recency_score(
        metadata.get('discovery_timestamp')
    )

    validation = calculate_validation_score(
        metadata.get('validated')
    )

    # Weighted sum of scores
    confidence_score = (
        completeness * WEIGHTS['completeness'] +
        reliability * WEIGHTS['reliability'] +
        recency * WEIGHTS['recency'] +
        validation * WEIGHTS['validation']
    )
    
    return min(max(confidence_score, 0.0), 1.0)

if __name__ == '__main__':
    # Example Usage
    print("Running example confidence score calculations...")

    example_result_high_confidence = {
        'data': {}, # Add dummy data field
        'metadata': {
            'source_type': 'official_doc',
            'fields_present': 10,
            'total_expected_fields': 10,
            'discovery_timestamp': datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30),
            'validated': True
        }
    }
    score_high = calculate_confidence(example_result_high_confidence)
    print(f"High confidence example score: {score_high:.2f}")

    example_result_medium_confidence = {
        'data': {},
        'metadata': {
            'source_type': 'blog',
            'fields_present': 7,
            'total_expected_fields': 10,
            'discovery_timestamp': datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=365),
            'validated': False
        }
    }
    score_medium = calculate_confidence(example_result_medium_confidence)
    print(f"Medium confidence example score: {score_medium:.2f}")

    example_result_low_confidence = {
        'data': {},
        'metadata': {
            'source_type': 'unknown',
            'fields_present': 2,
            'total_expected_fields': 10,
            'discovery_timestamp': datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=365 * 3),
            'validated': None
        }
    }
    score_low = calculate_confidence(example_result_low_confidence)
    print(f"Low confidence example score: {score_low:.2f}")

    example_result_missing_data = {
        'data': {},
        'metadata': {
            'source_type': 'forum',
            'discovery_timestamp': None,
        }
    }
    score_missing = calculate_confidence(example_result_missing_data)
    print(f"Missing data example score: {score_missing:.2f}")

    example_result_future_date = {
        'data': {},
         'metadata': {
            'source_type': 'official_doc',
            'fields_present': 10,
            'total_expected_fields': 10,
            'discovery_timestamp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30),
            'validated': True
        }
    }
    score_future = calculate_confidence(example_result_future_date)
    print(f"Future date example score: {score_future:.2f}")

    example_zero_expected_fields = {
        'data': {},
        'metadata': {
            'source_type': 'official_doc',
            'fields_present': 5,
            'total_expected_fields': 0,
            'discovery_timestamp': datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30),
            'validated': True
        }
    }
    score_zero_expected = calculate_confidence(example_zero_expected_fields)
    print(f"Zero expected fields example score: {score_zero_expected:.2f}") 