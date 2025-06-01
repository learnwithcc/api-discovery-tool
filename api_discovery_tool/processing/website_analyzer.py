import logging
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class WebsiteAnalyzer:
    """
    Analyzes a website to discover URLs and extract text content.
    """

    def __init__(self, base_url: str):
        """
        Initializes the WebsiteAnalyzer with a base URL.

        Args:
            base_url: The base URL of the website to analyze.
        """
        self.base_url = base_url.rstrip('/')

    def _fetch_url_content(self, url: str) -> str | None:
        """
        Fetches raw text content from a URL.

        Args:
            url: The URL to fetch content from.

        Returns:
            The text content of the URL, or None if an error occurs.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.text
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error fetching content from {url}: {e}")
            return None

    def fetch_and_parse_html(self, url: str) -> BeautifulSoup | None:
        """
        Fetches HTML content from a URL and parses it using BeautifulSoup.

        Args:
            url: The URL to fetch and parse.

        Returns:
            A BeautifulSoup object representing the parsed HTML, or None if an error occurs.
        """
        logger.info(f"Fetching HTML from: {url}")
        content = self._fetch_url_content(url)
        if content:
            try:
                soup = BeautifulSoup(content, 'html.parser')
                return soup
            except Exception as e: # Broad exception for parsing errors
                logger.warning(f"Error parsing HTML from {url}: {e}")
                return None
        return None

    def extract_links(self, soup: BeautifulSoup, current_url: str) -> set[str]:
        """
        Extracts all <a> tags with href attributes from a BeautifulSoup object
        and resolves them to absolute URLs.

        Args:
            soup: The BeautifulSoup object to extract links from.
            current_url: The URL from which the soup was generated, used for resolving relative links.

        Returns:
            A set of absolute URLs found in the soup.
        """
        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href:  # Ensure href is not empty
                absolute_link = urljoin(current_url, href)
                links.add(absolute_link)
        logger.info(f"Extracted {len(links)} links from {current_url}")
        return links

    def find_sitemap_urls(self) -> set[str]:
        """
        Attempts to fetch and parse sitemap.xml to find all URLs within <loc> tags.

        Returns:
            A set of URLs found in the sitemap, or an empty set if an error occurs.
        """
        sitemap_url = urljoin(self.base_url, '/sitemap.xml')
        logger.info(f"Attempting to fetch sitemap from: {sitemap_url}")
        content = self._fetch_url_content(sitemap_url)
        sitemap_urls = set()

        if content:
            try:
                soup = BeautifulSoup(content, 'xml')  # Use 'xml' parser for sitemaps
                for loc_tag in soup.find_all('loc'):
                    if loc_tag.text:
                        sitemap_urls.add(loc_tag.text.strip())
                logger.info(f"Found {len(sitemap_urls)} URLs in sitemap.xml")
            except Exception as e:
                logger.warning(f"Error parsing sitemap.xml from {sitemap_url}: {e}")
        return sitemap_urls

    def find_interesting_robots_paths(self) -> set[str]:
        """
        Attempts to fetch and parse robots.txt to find paths specified in
        'Allow:' or 'Disallow:' directives.

        Returns:
            A set of absolute URLs constructed from the paths found in robots.txt,
            or an empty set if an error occurs.
        """
        robots_url = urljoin(self.base_url, '/robots.txt')
        logger.info(f"Attempting to fetch robots.txt from: {robots_url}")
        content = self._fetch_url_content(robots_url)
        robots_paths = set()

        if content:
            try:
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith('Allow:') or line.startswith('Disallow:'):
                        parts = line.split(':', 1)
                        if len(parts) > 1:
                            path = parts[1].strip()
                            if path: # Ensure path is not empty
                                # Attempt to create a full URL.
                                # This might not always be a directly crawlable page,
                                # but it's an "interesting" path.
                                full_url = urljoin(self.base_url, path)
                                robots_paths.add(full_url)
                logger.info(f"Found {len(robots_paths)} interesting paths in robots.txt")
            except Exception as e: # Broad exception for parsing errors
                logger.warning(f"Error parsing robots.txt from {robots_url}: {e}")
        return robots_paths

    def analyze(self, crawl_depth: int = 1) -> dict[str, list[str]]:
        """
        Analyzes the website by crawling pages, extracting links and text.
        It also incorporates URLs from sitemap.xml and paths from robots.txt.

        Args:
            crawl_depth: The maximum depth to crawl links. 0 means only the base_url,
                         1 means base_url and its direct links, etc.

        Returns:
            A dictionary with two keys:
            "urls": A sorted list of unique discovered URLs.
            "text_content": A list of text snippets extracted from the crawled pages.
        """
        discovered_urls = set()
        text_snippets = []
        visited_urls = set()
        # queue stores (url, current_depth)
        queue: list[tuple[str, int]] = [(self.base_url, 0)]

        logger.info(f"Starting analysis of {self.base_url} with crawl_depth={crawl_depth}")

        while queue:
            current_url, depth = queue.pop(0)

            if current_url in visited_urls:
                continue
            visited_urls.add(current_url)

            logger.info(f"Crawling: {current_url} at depth {depth}")
            soup = self.fetch_and_parse_html(current_url)

            if soup:
                discovered_urls.add(current_url)
                text = soup.get_text(separator=' ', strip=True)
                if text:
                    text_snippets.append(text)

                if depth < crawl_depth:
                    links = self.extract_links(soup, current_url)
                    for link in links:
                        if link not in visited_urls:
                            # Ensure we only add links that are within the same domain or subdomains
                            # This is a basic check, more sophisticated checks might be needed
                            if self.base_url in link:
                                queue.append((link, depth + 1))
                            else:
                                logger.debug(f"Skipping external link: {link}")
            else:
                logger.warning(f"Could not fetch or parse {current_url}")


        sitemap_urls = self.find_sitemap_urls()
        discovered_urls.update(sitemap_urls)

        robots_urls = self.find_interesting_robots_paths()
        discovered_urls.update(robots_urls) # Add these as they might be discoverable

        logger.info(f"Analysis complete. Found {len(discovered_urls)} unique URLs and {len(text_snippets)} text snippets.")

        return {
            "urls": sorted(list(discovered_urls)),
            "text_content": text_snippets
        }

if __name__ == '__main__':
    # Basic configuration for logging (e.g., to console)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Example Usage (replace with a real, accessible URL for testing)
    # Note: Running this example directly might require internet access
    # and could take time depending on the website and crawl_depth.
    try:
        # A site known to have sitemap.xml and robots.txt for better testing
        # For a quick local test, you might need to set up a simple HTTP server
        # with dummy files.
        # Example: python -m http.server 8000
        # and then use base_url = "http://localhost:8000"
        # Ensure you have dummy sitemap.xml and robots.txt in that directory.

        # For this example, let's use a placeholder.
        # For real testing, use a controllable environment or a public site that allows crawling.
        test_url = "http://example.com" # Replace with a testable URL
        # test_url = "http://localhost:8000" # if running a local server for testing

        # Create dummy files for local testing if using localhost:8000
        # In the directory where you run `python -m http.server 8000`:
        # robots.txt:
        #   User-agent: *
        #   Allow: /allowed-path/
        #   Disallow: /disallowed-path/
        # sitemap.xml:
        #   <?xml version="1.0" encoding="UTF-8"?>
        #   <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        #     <url><loc>http://localhost:8000/sitemap-page1.html</loc></url>
        #     <url><loc>http://localhost:8000/sitemap-page2.html</loc></url>
        #   </urlset>
        # index.html (optional, for base URL crawl):
        #   <html><body><a href="page1.html">Page 1</a></body></html>
        # page1.html (optional):
        #   <html><body><a href="page2.html">Page 2</a></body></html>


        analyzer = WebsiteAnalyzer(base_url=test_url)

        # Test individual components (optional)
        logger.info("Testing find_sitemap_urls...")
        s_urls = analyzer.find_sitemap_urls()
        logger.info(f"Sitemap URLs found: {s_urls}")

        logger.info("Testing find_interesting_robots_paths...")
        r_paths = analyzer.find_interesting_robots_paths()
        logger.info(f"Robots paths found: {r_paths}")

        logger.info("Testing analyze (crawl_depth=0)...")
        analysis_result_depth0 = analyzer.analyze(crawl_depth=0)
        logger.info(f"Analysis (depth 0) URLs: {analysis_result_depth0['urls']}")
        # logger.info(f"Analysis (depth 0) Text: {analysis_result_depth0['text_content']}")


        logger.info("Testing analyze (crawl_depth=1)...")
        # analysis_result_depth1 = analyzer.analyze(crawl_depth=1)
        # logger.info(f"Analysis (depth 1) URLs: {analysis_result_depth1['urls']}")
        # logger.info(f"Analysis (depth 1) Text: {analysis_result_depth1['text_content']}")
        # Be cautious with crawl_depth > 0 on external sites to avoid excessive requests.

    except Exception as e:
        logger.error(f"An error occurred during example execution: {e}")
    finally:
        logger.info("Example usage finished.")
