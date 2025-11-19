"""
Robots.txt Compliance Service

This module provides functionality to check whether crawling or scraping a target URL
is allowed according to its robots.txt file. It helps ensure ethical and legal web
scraping practices by respecting website policies.

Legal and Ethical Context:
    - robots.txt is a standard used by websites to communicate with web crawlers
    - While not legally binding in all jurisdictions, respecting robots.txt is
      considered best practice and ethical behavior
    - Violating robots.txt may:
        * Be against Terms of Service
        * Result in IP blocking
        * Have legal consequences in some jurisdictions (e.g., CFAA in the US)
        * Damage your reputation and relationships with API providers

Compliance Checking Process:
    1. Construct robots.txt URL from target URL (always at /robots.txt)
    2. Fetch and parse the robots.txt file
    3. Check if the target URL is allowed for the specified user agent
    4. Return allowance status and descriptive message

Default Behavior:
    - Uses '*' (wildcard) user agent for checking (most restrictive)
    - If robots.txt cannot be fetched or parsed, assumes allowed (permissive fallback)
    - Logs warnings for any issues encountered during checking

User Agent Handling:
    - Currently uses '*' which applies to all user agents
    - Can be customized to use a specific user agent string
    - Different rules may apply to different user agents

Usage Example:
    >>> is_allowed, message = check_robots_txt_compliance("https://example.com/api")
    >>> if is_allowed:
    ...     print("Allowed to crawl:", message)
    ... else:
    ...     print("Not allowed:", message)

Best Practices:
    - Always check robots.txt before scraping or crawling
    - Respect rate limits and crawl delays specified in robots.txt
    - Use a descriptive user agent that identifies your bot
    - Provide contact information in your user agent string
    - Honor the website's wishes even if not legally required

Functions:
    check_robots_txt_compliance: Check if crawling a URL is allowed by robots.txt
"""

import urllib.robotparser
from urllib.parse import urljoin, urlparse
import logging

# Configure logging for the service
logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def check_robots_txt_compliance(target_url: str) -> tuple[bool, str]:
    """
    Checks if crawling the target_url is allowed by its robots.txt.

    Args:
        target_url (str): The URL to check.

    Returns:
        tuple[bool, str]: (is_allowed, message)
                          is_allowed is True if crawling is permitted or robots.txt is not found/parsable.
                          message provides details.
    """
    if not target_url or not urlparse(target_url).scheme or not urlparse(target_url).netloc:
        return False, "Invalid URL provided for robots.txt check."

    try:
        robots_url = urljoin(target_url, '/robots.txt')
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()

        # Check if scraping is allowed for a generic user agent
        # In a real application, you might use a specific user agent string
        can_fetch = rp.can_fetch('*', target_url)

        if not can_fetch:
            message = f"robots.txt disallows crawling {target_url}"
            logger.warning(message)
            return False, message
        
        message = f"robots.txt allows crawling {target_url}"
        logger.info(message)
        return True, message
        
    except Exception as e:
        message = f"Could not check robots.txt for {target_url}: {e}"
        logger.warning(message)
        # If robots.txt is inaccessible or unparsable, typically treat as allowed but log warning
        return True, message # Or False, depending on strictness policy 