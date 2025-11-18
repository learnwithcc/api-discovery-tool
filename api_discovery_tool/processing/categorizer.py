"""
API Type Categorization Module

This module provides functionality to categorize discovered API endpoints into specific types
based on their characteristics, including URL patterns, content types, request/response data,
and protocol indicators.

Supported API Types:
    - REST: RESTful APIs using standard HTTP methods and content types (JSON, XML)
    - GraphQL: GraphQL APIs with characteristic query/mutation patterns
    - SOAP: SOAP APIs using XML envelopes and WSDL
    - WebSocket: Real-time communication APIs using ws:// or wss:// protocols
    - Unknown: Endpoints that don't match any known API pattern

Categorization Decision Tree:
    1. Check for WebSocket protocol (ws://, wss://)
    2. Check for GraphQL indicators (/graphql endpoint, query/mutation patterns)
    3. Check for SOAP indicators (WSDL, SOAP envelopes, soap+xml content-type)
    4. Check for REST indicators (JSON/XML content-types, standard HTTP methods, OpenAPI spec)
    5. Default to Unknown if no patterns match

Constants:
    API_TYPE_REST: Identifier for REST APIs
    API_TYPE_GRAPHQL: Identifier for GraphQL APIs
    API_TYPE_SOAP: Identifier for SOAP APIs
    API_TYPE_WEBSOCKET: Identifier for WebSocket APIs
    API_TYPE_UNKNOWN: Identifier for unrecognized API types
    NON_API_CONTENT_TYPES: Content types that indicate non-API resources
    DEFINITELY_REST_CONTENT_TYPES: Content types that strongly indicate REST APIs

Usage Example:
    >>> endpoint_data = {
    ...     "url": "https://api.example.com/users",
    ...     "method": "GET",
    ...     "response_headers": {"Content-Type": "application/json"}
    ... }
    >>> api_type = categorize_api_type(endpoint_data)
    >>> print(api_type)
    'REST'
"""

import re
from typing import Any, Dict

# Define constants for API types
API_TYPE_REST = "REST"
API_TYPE_GRAPHQL = "GraphQL"
API_TYPE_SOAP = "SOAP"
API_TYPE_WEBSOCKET = "WebSocket"
API_TYPE_UNKNOWN = "Unknown"

NON_API_CONTENT_TYPES = [
    "text/html",
    "image/jpeg",
    "image/png",
    "image/gif",
    "text/css",
    "application/javascript", # .js files
    "application/pdf",
    # Add more specific non-api types if needed
]

# Content types that are strong indicators of REST if no other category matches
DEFINITELY_REST_CONTENT_TYPES = [
    "application/json",
    "application/xml", # Note: SOAP check runs before REST, so this would be non-SOAP XML
    "text/xml",        # Note: SOAP check runs before REST
    "application/octet-stream",
    "text/plain", 
    "application/x-www-form-urlencoded",
]

def _get_content_type(endpoint_data: Dict[str, Any]) -> str:
    """
    Extract the content-type from endpoint response headers.

    Performs case-insensitive search for the Content-Type header and returns
    its value in lowercase for consistent matching.

    Args:
        endpoint_data: Dictionary containing endpoint information with response_headers

    Returns:
        The lowercase content-type value, or empty string if not found
    """
    headers = endpoint_data.get("response_headers", {})
    content_type_val = ""
    if isinstance(headers, dict):
        for k, v in headers.items():
            if k.lower() == "content-type" and isinstance(v, str):
                content_type_val = v.lower()
                break
    return content_type_val

def _check_websocket(endpoint_data: Dict[str, Any]) -> bool:
    """
    Check if the endpoint is a WebSocket connection.

    WebSocket APIs are identified by the ws:// or wss:// protocol prefixes.

    Args:
        endpoint_data: Dictionary containing endpoint information with a url field

    Returns:
        True if the URL uses WebSocket protocol, False otherwise
    """
    url = endpoint_data.get("url")
    if not isinstance(url, str) or not url:
        return False
    return url.lower().startswith("ws://") or url.lower().startswith("wss://")

def _check_graphql(endpoint_data: Dict[str, Any]) -> bool:
    """
    Check if the endpoint is a GraphQL API.

    GraphQL APIs are identified by:
    - URL ending with /graphql
    - Content-Type: application/graphql
    - Request body containing 'query' or 'mutation' keywords
    - Response body with GraphQL-specific structure (data/errors fields)

    Args:
        endpoint_data: Dictionary containing endpoint information

    Returns:
        True if the endpoint appears to be GraphQL, False otherwise
    """
    url_str = endpoint_data.get("url")
    url = url_str.lower() if isinstance(url_str, str) else ""

    method = endpoint_data.get("method", "").upper()
    content_type = _get_content_type(endpoint_data)

    request_body = endpoint_data.get("request_body", "")
    if not isinstance(request_body, str): request_body = str(request_body)

    response_body = endpoint_data.get("response_body", "")
    if not isinstance(response_body, str): response_body = str(response_body)

    if url.endswith("/graphql"): return True
    if "application/graphql" in content_type: return True
    if method == "POST" and ("query" in request_body or "mutation" in request_body): return True
    if method == "POST" and (('"data":' in response_body and '"errors":' in response_body) or \
       ('"data":' in response_body and not '"errors":' in response_body and response_body.strip().startswith("{"))):
        return True
    return False

def _check_soap(endpoint_data: Dict[str, Any]) -> bool:
    """
    Check if the endpoint is a SOAP API.

    SOAP APIs are identified by:
    - URL containing ?WSDL query parameter
    - Content-Type: application/soap+xml
    - Content-Type: text/xml with SOAP envelope in response body
    - Response body containing SOAP envelope tags (soap:Envelope, soapenv:Envelope, etc.)

    Args:
        endpoint_data: Dictionary containing endpoint information

    Returns:
        True if the endpoint appears to be SOAP, False otherwise
    """
    url_str = endpoint_data.get("url")
    url = url_str.lower() if isinstance(url_str, str) else ""

    content_type = _get_content_type(endpoint_data)
    response_body_str = endpoint_data.get("response_body", "")
    response_body = response_body_str.lower() if isinstance(response_body_str, str) else ""

    if "?wsdl" in url: return True

    is_soap_content_type = "application/soap+xml" in content_type
    is_text_xml_content_type = "text/xml" in content_type
    has_soap_envelope = "<soap:envelope" in response_body or \
                        "<soapenv:envelope" in response_body or \
                        "<s:envelope" in response_body # Common namespaces, case S might be used by some

    if is_soap_content_type: return True # application/soap+xml is a strong signal
    if is_text_xml_content_type and has_soap_envelope: return True
    if not content_type and has_soap_envelope: return True # No CT, but body looks like SOAP
    return False

def _check_rest(endpoint_data: Dict[str, Any]) -> bool:
    """
    Check if the endpoint is a REST API.

    REST APIs are identified using a multi-rule decision process:

    Rule 1: OpenAPI specification present (strongest indicator)
    Rule 2: Exclude non-API content types (HTML, CSS, images, etc.)
    Rule 3: Include known REST content types (JSON, XML, octet-stream, etc.)
    Rule 4: Standard HTTP methods (GET, POST, PUT, DELETE, PATCH, etc.)
            without static file extensions

    Args:
        endpoint_data: Dictionary containing endpoint information

    Returns:
        True if the endpoint appears to be REST, False otherwise
    """
    method = endpoint_data.get("method", "").upper()
    content_type = _get_content_type(endpoint_data)
    url_str = endpoint_data.get("url")
    url = url_str if isinstance(url_str, str) else "" # Keep original case for path splitting if needed, normalize later

    openapi_spec = endpoint_data.get("openapi_spec")

    # Rule 1: If OpenAPI spec is present, it's REST (very strong signal)
    if openapi_spec and isinstance(openapi_spec, dict) and openapi_spec.get("openapi"):
        return True

    # Rule 2: Exclude if content type is definitively non-API (unless overridden by OpenAPI spec)
    for non_api_ct in NON_API_CONTENT_TYPES:
        if non_api_ct in content_type:
            return False

    # Rule 3: Definitely REST if content type is a known API type
    for rest_ct in DEFINITELY_REST_CONTENT_TYPES:
        if rest_ct in content_type:
            return True

    # Rule 4: Common methods without specific problematic content types, and URL doesn't look like a static file
    common_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
    if method in common_methods:
        if url: # Ensure URL exists
            path_lower = url.lower().split("?", 1)[0]
            # If no content type OR a generic one not yet caught (e.g. unspecified application/*)
            # And path doesn't end with common non-API file extensions
            if not content_type or content_type.startswith("application/"):
                 if not re.search(r'\.(html|htm|css|js|png|jpg|jpeg|gif|pdf|txt|ico|svg|woff|woff2|ttf|eot)$', path_lower):
                    return True
    return False

def categorize_api_type(endpoint_data: Dict[str, Any]) -> str:
    if not isinstance(endpoint_data, dict):
        return API_TYPE_UNKNOWN
    # URL must exist and be a non-empty string for any categorization beyond UNKNOWN
    url_val = endpoint_data.get("url")
    if not isinstance(url_val, str) or not url_val.strip():
        return API_TYPE_UNKNOWN

    if _check_websocket(endpoint_data): return API_TYPE_WEBSOCKET
    if _check_graphql(endpoint_data): return API_TYPE_GRAPHQL
    if _check_soap(endpoint_data): return API_TYPE_SOAP
    if _check_rest(endpoint_data): return API_TYPE_REST
        
    return API_TYPE_UNKNOWN

if __name__ == '__main__':
    test_cases = [
        # WebSocket
        ({"url": "ws://example.com/socket"}, API_TYPE_WEBSOCKET),
        ({"url": "wss://example.com/secure"}, API_TYPE_WEBSOCKET),
        ({"url": None}, API_TYPE_UNKNOWN),
        ({"url": ""}, API_TYPE_UNKNOWN),
        
        # GraphQL
        ({"url": "http://example.com/graphql", "method": "POST"}, API_TYPE_GRAPHQL),
        ({"url": "http://example.com/api", "method": "POST", "request_body": "query { users { id } }"}, API_TYPE_GRAPHQL),
        ({"url": "http://example.com/api", "method": "POST", "response_headers": {"Content-Type": "application/graphql+json"}}, API_TYPE_GRAPHQL),
        ({"url": "http://example.com/api", "method": "POST", "response_body": '{"data": {}}'}, API_TYPE_GRAPHQL),
        ({"url": "http://example.com/api", "method": "GET", "response_body": '{"data": {}}', "response_headers": {"Content-Type": "application/json"}}, API_TYPE_REST), 

        # SOAP
        ({"url": "http://example.com/service.asmx?WSDL"}, API_TYPE_SOAP),
        ({"url": "http://example.com/service", "response_headers": {"Content-Type": "application/soap+xml"}, "response_body": "<soap:Envelope></soap:Envelope>"}, API_TYPE_SOAP),
        ({"url": "http://example.com/service", "response_headers": {"Content-Type": "text/xml; charset=utf-8"}, "response_body": "<soapenv:Envelope></soapenv:Envelope>"}, API_TYPE_SOAP),
        ({"url": "http://example.com/service", "response_body": "<s:Envelope xmlns:s='http://schemas.xmlsoap.org/soap/envelope/'></s:Envelope>"}, API_TYPE_SOAP),
        ({"url": "http://example.com/item", "response_headers": {"Content-Type": "text/xml"}, "response_body": "<S:Envelope></S:Envelope>" }, API_TYPE_SOAP), 

        # REST
        ({"url": "http://example.com/api/users", "method": "GET", "response_headers": {"Content-Type": "application/json"}}, API_TYPE_REST),
        ({"url": "http://example.com/api/posts", "method": "POST", "openapi_spec": {"openapi": "3.0.0"}}, API_TYPE_REST),
        ({"url": "http://example.com/api/items", "method": "PUT"}, API_TYPE_REST),
        ({"url": "http://example.com/api/data.xml", "method": "GET", "response_headers": {"Content-Type": "application/xml"}}, API_TYPE_REST),
        ({"url": "http://example.com/api/data.xml", "method": "GET", "response_headers": {"Content-Type": "text/xml"}}, API_TYPE_REST), # Test text/xml as REST
        ({"url": "http://example.com/api/download", "method": "GET", "response_headers": {"Content-Type": "application/octet-stream"}}, API_TYPE_REST),
        ({"url": "http://example.com/resource.txt", "method": "GET", "response_headers": {"Content-Type": "text/plain"}}, API_TYPE_REST),
        ({"url": "http://example.com", "method": "GET"}, API_TYPE_REST), # Generic GET to root
        ({"url": "http://example.com/api/v1/status", "method": "HEAD"}, API_TYPE_REST), # HEAD request

        # Unknown
        ({"url": "http://example.com/page.html", "method": "GET", "response_headers": {"Content-Type": "text/html"}}, API_TYPE_UNKNOWN),
        ({"url": "http://example.com/style.css", "method": "GET", "response_headers": {"Content-Type": "text/css"}}, API_TYPE_UNKNOWN),
        ({"url": "ftp://example.com/file"}, API_TYPE_UNKNOWN),
        ({}, API_TYPE_UNKNOWN),
        ({"url": "http://example.com/resource.pdf", "method": "GET", "response_headers": {"Content-Type": "application/pdf"}}, API_TYPE_UNKNOWN),
        ({"url": "http://example.com/resource"}, API_TYPE_REST), # No method, no ext, could be REST
        ({"url": "http://example.com/index" , "method": "GET"}, API_TYPE_REST), # No ext, could be API
        ({"url": "http://example.com/image.jpg", "method": "GET", "response_headers": {"Content-Type": "image/jpeg"}}, API_TYPE_UNKNOWN),
        
        # Ambiguous / Edge cases
        ({"url": "http://example.com/api", "method": "POST", "response_headers": {"Content-Type": "application/json"}, "response_body": '{"data": {"user": {"id": "1"}}}'}, API_TYPE_GRAPHQL),
        ({"url": "http://example.com/xmlapi", "method": "POST", "response_headers": {"Content-Type": "text/xml"}, "response_body": "<root><item/></root>"}, API_TYPE_REST),
        ({"url": "http://example.com/page.html", "method": "GET", "response_headers": {"Content-Type": "text/html"}, "openapi_spec": {"openapi": "3.0.0"}}, API_TYPE_REST),
    ]
    passed_count = 0
    failed_count = 0
    for i, (data, expected) in enumerate(test_cases):
        result = categorize_api_type(data)
        status = 'Pass' if result == expected else 'Fail'
        if result == expected: passed_count +=1
        else: failed_count += 1
        print(f"Test Case {i+1}: {status}")
        print(f"  Input: {data}")
        print(f"  Expected: {expected}, Got: {result}\n")
    print(f"Summary: Passed: {passed_count}, Failed: {failed_count}") 