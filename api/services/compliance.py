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