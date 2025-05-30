from flask import Blueprint, jsonify

health_bp = Blueprint('health_bp', __name__)

@health_bp.route('/health')
def health_check():
    """
    Health check endpoint.
    ---
    responses:
      200:
        description: API is healthy
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: "healthy"
    """
    return jsonify({"status": "healthy"}), 200 