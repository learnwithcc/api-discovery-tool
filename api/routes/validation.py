from flask import Blueprint, request, jsonify
import validators
from api.services.compliance import check_robots_txt_compliance

validation_bp = Blueprint('validation_bp', __name__)

@validation_bp.route('/validate-url', methods=['POST'])
def validate_url_endpoint():
    """
    Validates a URL provided in the request body.
    ---
    parameters:
      - name: url
        in: body
        required: true
        schema:
          type: object
          properties:
            url:
              type: string
              example: "http://example.com"
    responses:
      200:
        description: URL is valid
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "URL is valid"
                url:
                  type: string
                robots_check:
                  type: object
                  properties:
                    allowed:
                      type: boolean
                    message:
                      type: string
      400:
        description: Invalid or missing URL
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Invalid URL provided"
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