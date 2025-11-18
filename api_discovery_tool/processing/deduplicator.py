"""
API Endpoint Deduplication Module

This module provides functionality to identify and remove duplicate API endpoints from
discovery results. Endpoints are considered duplicates based on normalized URL matching
and HTTP method comparison.

Deduplication Algorithm:
    1. Normalize each endpoint's URL (case-insensitive, protocol-agnostic, no trailing slash)
    2. Create a unique signature combining normalized URL and HTTP method
    3. Track seen signatures in a set
    4. Keep only the first occurrence of each unique signature

URL Normalization Process:
    - Convert to lowercase for case-insensitive comparison
    - Remove protocol prefixes (http://, https://, ws://, wss://)
    - Remove 'www.' subdomain
    - Remove trailing slashes

Signature Generation:
    - For HTTP/HTTPS endpoints: (normalized_url, HTTP_METHOD) tuple
    - For WebSocket and other endpoints: normalized_url string
    - Invalid or empty URLs return None

Usage Example:
    >>> endpoints = [
    ...     {"url": "http://example.com/api/users", "method": "GET"},
    ...     {"url": "https://example.com/api/users", "method": "GET"},  # Duplicate
    ...     {"url": "http://example.com/api/users", "method": "POST"},  # Different method
    ... ]
    >>> unique_endpoints = deduplicate_endpoints(endpoints)
    >>> len(unique_endpoints)
    2

Functions:
    normalize_url: Normalizes a URL string for consistent comparison
    get_endpoint_signature: Generates a unique signature for an endpoint
    deduplicate_endpoints: Removes duplicate endpoints from a list
"""

import re
from typing import Any, Dict, List, Set, Tuple, Union

def normalize_url(url: str) -> str:
    """
    Normalizes a URL for consistent comparison across different representations.

    Normalization steps:
    1. Convert to lowercase for case-insensitive matching
    2. Remove protocol prefixes (http://, https://, ws://, wss://)
    3. Remove 'www.' subdomain prefix
    4. Remove trailing slashes

    Args:
        url: The URL string to normalize

    Returns:
        The normalized URL string, or empty string if input is invalid

    Examples:
        >>> normalize_url("HTTP://WWW.Example.com/API/")
        'example.com/api'
        >>> normalize_url("https://example.com/users")
        'example.com/users'
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
    Generates a unique signature for an endpoint to identify duplicates.

    The signature format depends on whether the endpoint has an HTTP method:
    - With method: (normalized_url, uppercase_method) tuple
    - Without method: normalized_url string
    - Invalid URL: None

    This allows the same URL with different HTTP methods (e.g., GET vs POST)
    to be treated as distinct endpoints.

    Args:
        endpoint: Dictionary containing at least a 'url' field, optionally a 'method' field

    Returns:
        A tuple of (normalized_url, method), a string (normalized_url), or None if invalid

    Examples:
        >>> get_endpoint_signature({"url": "http://example.com/api", "method": "GET"})
        ('example.com/api', 'GET')
        >>> get_endpoint_signature({"url": "ws://example.com/socket"})
        'example.com/socket'
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