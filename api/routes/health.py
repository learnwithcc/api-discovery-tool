"""
Health Check API Route

This module provides a health check endpoint for monitoring the API's availability
and basic functionality. Health checks are essential for production deployments,
load balancers, and monitoring systems.

Health Check Best Practices:

1. Minimal Dependencies
   - Health checks should be lightweight and fast
   - Avoid complex operations or external service calls in basic health checks
   - For comprehensive checks, use separate /readiness or /liveness endpoints

2. Consistent Response Format
   - Always return a consistent JSON structure
   - Include a clear status indicator
   - Consider adding version, uptime, or timestamp information

3. Appropriate HTTP Status Codes
   - 200 OK: Service is healthy and ready to handle requests
   - 503 Service Unavailable: Service is running but not ready
   - 500 Internal Server Error: Service has critical errors

4. Load Balancer Integration
   - Configure your load balancer to poll this endpoint
   - Set appropriate timeout and interval values
   - Use health checks to automatically remove unhealthy instances

5. Monitoring and Alerting
   - Monitor health check response times
   - Alert on consecutive failures
   - Track availability metrics over time

6. Kubernetes Readiness/Liveness
   - Readiness: Is the service ready to accept traffic?
   - Liveness: Is the service running and not deadlocked?
   - This endpoint can be used for both in simple cases

Enhanced Health Checks (Future Considerations):
   - Database connectivity check
   - External service dependency checks
   - Disk space and memory checks
   - Background job queue health
   - Cache system status

Usage Example:
    # From command line
    $ curl http://localhost:5001/api/health
    {"status": "healthy"}

    # In load balancer configuration (nginx)
    upstream api_backend {
        server api1:5001;
        server api2:5001;
        check interval=3000 rise=2 fall=3 timeout=1000 type=http;
        check_http_send "GET /api/health HTTP/1.0\\r\\n\\r\\n";
        check_http_expect_alive http_2xx http_3xx;
    }

Routes:
    GET /health: Basic health check endpoint
"""

from flask import Blueprint, jsonify

health_bp = Blueprint('health_bp', __name__)

@health_bp.route('/health')
def health_check():
    """
    Health check endpoint for monitoring API availability.

    This endpoint provides a simple way for monitoring tools, load balancers,
    and orchestration systems to verify that the API is running and responsive.

    Returns:
        JSON response with status "healthy" and HTTP 200 status code

    Response Format:
        {
            "status": "healthy"
        }

    Status Codes:
        200: Service is healthy and operational
    """
    return jsonify({"status": "healthy"}), 200 