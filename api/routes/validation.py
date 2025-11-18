"""
URL Validation API Route

This module provides endpoints for validating URLs and checking their compliance
with robots.txt policies. It helps ensure that target URLs are well-formed and
that scraping/crawling operations respect website policies.

Validation Process:

1. URL Format Validation
   - Checks if URL is a valid string
   - Validates URL structure using the validators library
   - Ensures protocol, domain, and path are properly formatted

2. Robots.txt Compliance Check
   - Fetches and parses the target's robots.txt file
   - Checks if the URL is allowed for crawling
   - Returns detailed compliance information

Validation Rules:
   - URL must be present in request body
   - URL must be a non-empty string
   - URL must follow valid HTTP/HTTPS URL format
   - Protocol must be http:// or https://

Response Information:
   - Validation status (valid/invalid)
   - Original URL
   - Robots.txt compliance status
   - Descriptive messages for any failures

Security Considerations:
   - Input sanitization to prevent injection attacks
   - URL validation to prevent SSRF (Server-Side Request Forgery)
   - Rate limiting should be applied to prevent abuse
   - Consider implementing URL blacklisting for sensitive targets

Usage Example:
    # Valid URL request
    POST /api/validate-url
    Content-Type: application/json
    {
        "url": "https://api.example.com"
    }

    # Response
    {
        "message": "URL is valid",
        "url": "https://api.example.com",
        "robots_check": {
            "allowed": true,
            "message": "robots.txt allows crawling https://api.example.com"
        }
    }

Error Responses:
    400 Bad Request: Missing or invalid URL
    {
        "error": "Missing URL in request body"
    }
    or
    {
        "error": "Invalid URL provided",
        "url": "not-a-valid-url"
    }

Routes:
    POST /validate-url: Validate a URL and check robots.txt compliance
"""

from flask import Blueprint, request, jsonify
import validators
from api.services.compliance import check_robots_txt_compliance

validation_bp = Blueprint('validation_bp', __name__)

@validation_bp.route('/validate-url', methods=['POST'])
def validate_url_endpoint():
    """
    Validates a URL and checks its robots.txt compliance.

    This endpoint performs two validation steps:
    1. Verifies the URL is properly formatted
    2. Checks if the URL allows crawling per robots.txt

    Request Body:
        {
            "url": "https://api.example.com/endpoint"
        }

    Returns:
        200 OK: URL is valid
            {
                "message": "URL is valid",
                "url": "https://api.example.com/endpoint",
                "robots_check": {
                    "allowed": true,
                    "message": "robots.txt allows crawling..."
                }
            }

        400 Bad Request: Missing or invalid URL
            {
                "error": "Missing URL in request body"
            }
            or
            {
                "error": "Invalid URL provided",
                "url": "invalid-url"
            }

    Validation Logic:
        - Checks if 'url' field exists in request body
        - Validates URL is a string
        - Uses validators library to check URL format
        - Performs robots.txt compliance check via compliance service

    Status Codes:
        200: URL is valid and formatted correctly
        400: URL is missing, malformed, or invalid

    Security Notes:
        - Only accepts JSON content type
        - URL must be properly formatted HTTP/HTTPS
        - Consider implementing rate limiting to prevent abuse
    """
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "Missing URL in request body"}), 400

    url_to_validate = data['url']

    if not isinstance(url_to_validate, str) or not validators.url(url_to_validate):
        return jsonify({"error": "Invalid URL provided", "url": url_to_validate}), 400

    # Perform robots.txt check after URL validation
    is_allowed, robots_message = check_robots_txt_compliance(url_to_validate)

    return jsonify({
        "message": "URL is valid",
        "url": url_to_validate,
        "robots_check": {
            "allowed": is_allowed,
            "message": robots_message
        }
    }), 200


# It might be better to have a dedicated endpoint for robots.txt check
# or include it as part of a larger discovery process endpoint.
# For now, adding it to the validation endpoint as per subtask description. 