import re
from typing import Any, Dict, List, Set, Tuple, Union

def normalize_url(url: str) -> str:
    """
    Normalizes a URL by:
    1. Converting to lowercase.
    2. Removing http://, https://, ws://, or wss://.
    3. Removing www.
    4. Removing trailing slashes.
    """
    if not url or not isinstance(url, str):
        return ""
    normalized = url.lower()
    normalized = re.sub(r"^https?://|^wss?://", "", normalized)
    normalized = re.sub(r"^www\.", "", normalized)
    normalized = normalized.rstrip('/')
    return normalized

def get_endpoint_signature(endpoint: Dict[str, Any]) -> Union[Tuple[str, str], str, None]:
    """
    Generates a unique signature for an endpoint.
    For HTTP/S endpoints, it's (normalized_url, METHOD).
    For others (e.g., WebSocket), it's just normalized_url.
    Returns None if the URL is invalid or empty after normalization.
    """
    url = endpoint.get("url")
    method = endpoint.get("method")

    if not url or not isinstance(url, str):
        return None

    normalized = normalize_url(url)
    if not normalized:
        return None

    if method and isinstance(method, str):
        return (normalized, method.upper())
    return normalized

def deduplicate_endpoints(endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicates a list of discovered API endpoints.

    Endpoints are considered duplicates if they have:
    - The same normalized URL (case-insensitive, protocol-agnostic, no trailing slash)
    - AND the same HTTP method (if applicable).

    Args:
        endpoints: A list of endpoint dictionaries. Each dictionary is expected
                   to have at least a "url" key. An optional "method" key
                   can specify the HTTP method.

    Returns:
        A new list containing only unique endpoints.
    """
    if not endpoints:
        return []

    unique_endpoints: List[Dict[str, Any]] = []
    seen_signatures: Set[Union[Tuple[str, str], str]] = set()

    for endpoint in endpoints:
        if not isinstance(endpoint, dict):
            continue

        signature = get_endpoint_signature(endpoint)

        if signature is not None and signature not in seen_signatures:
            seen_signatures.add(signature)
            unique_endpoints.append(endpoint)

    return unique_endpoints

if __name__ == '__main__':
    # Example Usage
    sample_endpoints = [
        {"url": "http://example.com/api/v1/users", "method": "GET"},
        {"url": "https://example.com/api/v1/users", "method": "GET"}, # Duplicate
        {"url": "http://example.com/api/v1/users/", "method": "GET"}, # Duplicate
        {"url": "http://EXAMPLE.com/api/v1/USERS", "method": "GET"}, # Duplicate
        {"url": "http://www.example.com/api/v1/users", "method": "GET"}, # Duplicate
        {"url": "http://example.com/api/v1/users", "method": "POST"},
        {"url": "http://example.com/api/v1/products", "method": "GET"},
        {"url": "ws://example.com/socket"},
        {"url": "WS://Example.com/socket/"}, # Duplicate WebSocket
        {"url": "wss://secure.example.com/socket"}, # New wss
        {"url": "http://example.com/api/v2/users", "method": "GET"},
        {"url": "http://another.com/api/data", "method": "PUT"},
        {}, # Malformed
        {"method": "GET"}, # Malformed
        {"url": None, "method": "GET"}, # Malformed with None URL
        {"url": "http://example.com/no-method"}, # No method, treated as unique URL
        {"url": "http://example.com/no-method"}, # Duplicate of above
    ]

    unique = deduplicate_endpoints(sample_endpoints)
    print("Original count:", len(sample_endpoints))
    print("Unique count:", len(unique))
    for ep in unique:
        print(ep)

    # Test with empty list
    print("\nTest with empty list:")
    unique_empty = deduplicate_endpoints([])
    print("Original count: 0")
    print("Unique count:", len(unique_empty))

    # Test with no duplicates
    print("\nTest with no duplicates:")
    no_duplicates_list = [
        {"url": "http://site1.com/a", "method": "GET"},
        {"url": "http://site2.com/b", "method": "POST"},
    ]
    unique_no_dups = deduplicate_endpoints(no_duplicates_list)
    print("Original count:", len(no_duplicates_list))
    print("Unique count:", len(unique_no_dups))
    for ep in unique_no_dups:
        print(ep) 