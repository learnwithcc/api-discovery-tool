import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import requests # Import for requests.exceptions.RequestException

# Adjust import path based on your project structure
# If tests are run from the root directory:
from api_discovery_tool.processing.website_analyzer import WebsiteAnalyzer
# If tests are run from within the tests directory, you might need:
# from ..website_analyzer import WebsiteAnalyzer

class TestWebsiteAnalyzer(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://example.com"
        self.analyzer = WebsiteAnalyzer(self.base_url)

    def test_init(self):
        """Test WebsiteAnalyzer initialization."""
        self.assertEqual(self.analyzer.base_url, self.base_url)
        analyzer_with_slash = WebsiteAnalyzer("http://example.com/")
        self.assertEqual(analyzer_with_slash.base_url, "http://example.com")

    @patch('requests.get')
    def test_fetch_url_content_success(self, mock_get):
        """Test _fetch_url_content successfully fetches content."""
        mock_response = MagicMock()
        mock_response.text = "<html><body>Hello World</body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        content = self.analyzer._fetch_url_content(self.base_url + "/testpage")
        self.assertEqual(content, "<html><body>Hello World</body></html>")
        mock_get.assert_called_once_with(self.base_url + "/testpage", timeout=10)
        mock_response.raise_for_status.assert_called_once()

    @patch('requests.get')
    def test_fetch_url_content_failure(self, mock_get):
        """Test _fetch_url_content handles requests exception."""
        mock_get.side_effect = requests.exceptions.RequestException("Test error")

        content = self.analyzer._fetch_url_content(self.base_url + "/testpage")
        self.assertIsNone(content)
        mock_get.assert_called_once_with(self.base_url + "/testpage", timeout=10)

    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer._fetch_url_content')
    def test_fetch_and_parse_html_success(self, mock_fetch_content):
        """Test fetch_and_parse_html successfully parses HTML."""
        html_content = "<html><head><title>Test</title></head><body><h1>Hello</h1></body></html>"
        mock_fetch_content.return_value = html_content

        soup = self.analyzer.fetch_and_parse_html(self.base_url + "/page1")
        self.assertIsNotNone(soup)
        self.assertIsInstance(soup, BeautifulSoup)
        self.assertEqual(soup.find('h1').text, "Hello")
        mock_fetch_content.assert_called_once_with(self.base_url + "/page1")

    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer._fetch_url_content')
    def test_fetch_and_parse_html_fetch_failure(self, mock_fetch_content):
        """Test fetch_and_parse_html handles content fetch failure."""
        mock_fetch_content.return_value = None

        soup = self.analyzer.fetch_and_parse_html(self.base_url + "/page1")
        self.assertIsNone(soup)
        mock_fetch_content.assert_called_once_with(self.base_url + "/page1")

    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer._fetch_url_content')
    def test_fetch_and_parse_html_parse_failure(self, mock_fetch_content):
        """Test fetch_and_parse_html handles non-HTML content gracefully (e.g. JSON)."""
        # BeautifulSoup can sometimes parse non-HTML, but it might be malformed or empty.
        # The key is that it doesn't crash.
        json_content = '{"not": "html"}'
        mock_fetch_content.return_value = json_content

        soup = self.analyzer.fetch_and_parse_html(self.base_url + "/json_endpoint")
        self.assertIsNotNone(soup) # BeautifulSoup will still create a soup object
        self.assertIsInstance(soup, BeautifulSoup)
        # Check that it didn't find expected HTML tags like <html>
        self.assertIsNone(soup.find('html'))
        mock_fetch_content.assert_called_once_with(self.base_url + "/json_endpoint")


    def test_extract_links(self):
        """Test extract_links correctly finds and resolves URLs."""
        html_doc = """
        <html><body>
            <a href="page1.html">Page 1</a>
            <a href="/abs/page2">Page 2</a>
            <a href="http://otherdomain.com/page3">Page 3</a>
            <a href="https://example.com/page4#section">Page 4 with fragment</a>
            <a name="no-href">No Href</a>
            <a>Empty Href</a>
            <a href="">Empty Href String</a>
            <a href="mailto:test@example.com">Mailto</a>
        </body></html>
        """
        soup = BeautifulSoup(html_doc, 'html.parser')
        current_url = "http://example.com/path/current.html"

        links = self.analyzer.extract_links(soup, current_url)
        expected_links = {
            "http://example.com/path/page1.html",
            "http://example.com/abs/page2",
            "http://otherdomain.com/page3", # External links are included
            "https://example.com/page4#section", # Fragment preserved
            # mailto links are usually not desired for crawling, urljoin handles them okay
            "http://example.com/path/mailto:test@example.com"
        }
        # Depending on strictness, mailto might be filtered. Current implementation includes it.
        # If mailto links should be excluded, the extract_links method needs adjustment.
        # For now, testing current behavior.

        self.assertSetEqual(links, expected_links)

        # Test with a different base URL for current_url
        current_url_root = "http://example.com/"
        links_root = self.analyzer.extract_links(soup, current_url_root)
        expected_links_root = {
            "http://example.com/page1.html",
            "http://example.com/abs/page2",
            "http://otherdomain.com/page3",
            "https://example.com/page4#section",
            "http://example.com/mailto:test@example.com"
        }
        self.assertSetEqual(links_root, expected_links_root)

        empty_soup = BeautifulSoup("", 'html.parser')
        self.assertSetEqual(self.analyzer.extract_links(empty_soup, current_url), set())

    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer._fetch_url_content')
    def test_find_sitemap_urls_success(self, mock_fetch_content):
        """Test find_sitemap_urls with a valid sitemap."""
        sitemap_xml = """
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>http://example.com/page1</loc></url>
            <url><loc>https://example.com/page2.html</loc></url>
        </urlset>
        """
        mock_fetch_content.return_value = sitemap_xml
        urls = self.analyzer.find_sitemap_urls()
        self.assertSetEqual(urls, {"http://example.com/page1", "https://example.com/page2.html"})
        mock_fetch_content.assert_called_once_with(self.base_url + "/sitemap.xml")

    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer._fetch_url_content')
    def test_find_sitemap_urls_fetch_failure(self, mock_fetch_content):
        """Test find_sitemap_urls when fetching sitemap.xml fails."""
        mock_fetch_content.return_value = None
        urls = self.analyzer.find_sitemap_urls()
        self.assertSetEqual(urls, set())

    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer._fetch_url_content')
    def test_find_sitemap_urls_malformed_xml(self, mock_fetch_content):
        """Test find_sitemap_urls with malformed XML."""
        sitemap_xml = "<urlset><url><loc>http://example.com/page1</loc></ur" # Malformed
        mock_fetch_content.return_value = sitemap_xml
        urls = self.analyzer.find_sitemap_urls()
        self.assertSetEqual(urls, set()) # Expect empty set on parsing error

    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer._fetch_url_content')
    def test_find_sitemap_urls_no_urls(self, mock_fetch_content):
        """Test find_sitemap_urls with sitemap having no loc tags."""
        sitemap_xml = "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'></urlset>"
        mock_fetch_content.return_value = sitemap_xml
        urls = self.analyzer.find_sitemap_urls()
        self.assertSetEqual(urls, set())

    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer._fetch_url_content')
    def test_find_interesting_robots_paths_success(self, mock_fetch_content):
        """Test find_interesting_robots_paths with a valid robots.txt."""
        robots_txt_content = """
        User-agent: *
        Allow: /api/
        Disallow: /admin/
        Allow: /users/profile
        Disallow: /tmp # some comment
        Sitemap: http://example.com/sitemap.xml
        """
        mock_fetch_content.return_value = robots_txt_content
        paths = self.analyzer.find_interesting_robots_paths()
        expected_paths = {
            self.base_url + "/api/",
            self.base_url + "/admin/",
            self.base_url + "/users/profile",
            self.base_url + "/tmp"
        }
        self.assertSetEqual(paths, expected_paths)
        mock_fetch_content.assert_called_once_with(self.base_url + "/robots.txt")

    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer._fetch_url_content')
    def test_find_interesting_robots_paths_fetch_failure(self, mock_fetch_content):
        """Test find_interesting_robots_paths when fetching robots.txt fails."""
        mock_fetch_content.return_value = None
        paths = self.analyzer.find_interesting_robots_paths()
        self.assertSetEqual(paths, set())

    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer._fetch_url_content')
    def test_find_interesting_robots_paths_no_directives(self, mock_fetch_content):
        """Test find_interesting_robots_paths with no relevant directives."""
        robots_txt_content = "User-agent: *\nSitemap: http://example.com/sitemap.xml"
        mock_fetch_content.return_value = robots_txt_content
        paths = self.analyzer.find_interesting_robots_paths()
        self.assertSetEqual(paths, set())

    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer.find_interesting_robots_paths')
    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer.find_sitemap_urls')
    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer.fetch_and_parse_html')
    def test_analyze_crawl_depth_0(self, mock_fetch_parse, mock_sitemap, mock_robots):
        """Test analyze with crawl_depth = 0."""
        mock_base_soup = BeautifulSoup("<html><body>Base page text <a href='link1.html'>Link 1</a></body></html>", 'html.parser')
        mock_fetch_parse.return_value = mock_base_soup
        mock_sitemap.return_value = {"http://example.com/sitemap_url1"}
        mock_robots.return_value = {"http://example.com/robots_url1"}

        results = self.analyzer.analyze(crawl_depth=0)

        mock_fetch_parse.assert_called_once_with(self.base_url)
        mock_sitemap.assert_called_once()
        mock_robots.assert_called_once()

        self.assertIn(self.base_url, results["urls"])
        self.assertIn("http://example.com/sitemap_url1", results["urls"])
        self.assertIn("http://example.com/robots_url1", results["urls"])
        # link1.html should not be crawled or added to discovered_urls directly from crawling logic at depth 0
        # but extract_links might be called on base_url's soup. However, these links are not added to queue for depth 0.
        # The current implementation of analyze() adds current_url to discovered_urls IF soup is not None.
        # And links from extract_links are only added to queue if depth + 1 <= crawl_depth.
        # So, for depth 0, only base_url, sitemap, and robots URLs should be present.

        # Let's re-verify the logic in analyze for depth 0:
        # The queue starts with (base_url, 0). Loop runs.
        # fetch_and_parse_html(base_url) is called. If soup, base_url is added. text is extracted.
        # depth (0) < crawl_depth (0) is FALSE. So, extract_links is NOT called for queuing.
        # Loop finishes. Sitemap and robots URLs are added.

        self.assertNotIn("http://example.com/link1.html", results["urls"]) # This was a bug in my reasoning, fixed
        self.assertListEqual(results["text_content"], ["Base page text Link 1"])
        self.assertEqual(len(results["urls"]), 3) # base_url, sitemap_url1, robots_url1

    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer.find_interesting_robots_paths')
    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer.find_sitemap_urls')
    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer.fetch_and_parse_html')
    def test_analyze_crawl_depth_1(self, mock_fetch_parse, mock_sitemap, mock_robots):
        """Test analyze with crawl_depth = 1."""
        base_html_content = "<html><body>Base content <a href='page1.html'>Page 1</a> <a href='ext/page2.html'>Page 2</a></body></html>"
        page1_html_content = "<html><body>Page 1 content <a href='sub/page1_1.html'>Sub Page</a></body></html>"
        # page2.html (ext/page2.html) will not be fetched as it's on a different path unless base_url is example.com/
        # For this test, assume base_url is "http://example.com"

        mock_base_soup = BeautifulSoup(base_html_content, 'html.parser')
        mock_page1_soup = BeautifulSoup(page1_html_content, 'html.parser')

        # Configure mock_fetch_parse to return different soups based on URL
        def fetch_parse_side_effect(url):
            if url == self.base_url:
                return mock_base_soup
            elif url == self.base_url + "/page1.html": # urljoin(base_url, "page1.html")
                return mock_page1_soup
            elif url == self.base_url + "/ext/page2.html": # urljoin(base_url, "ext/page2.html")
                return None # Simulate this page not found or not parsable to stop crawl here
            return None

        mock_fetch_parse.side_effect = fetch_parse_side_effect
        mock_sitemap.return_value = {"http://example.com/sitemap_url"}
        mock_robots.return_value = {"http://example.com/robots_url"}

        results = self.analyzer.analyze(crawl_depth=1)

        self.assertEqual(mock_fetch_parse.call_count, 3) # base_url, page1.html, ext/page2.html
        mock_sitemap.assert_called_once()
        mock_robots.assert_called_once()

        expected_urls = {
            self.base_url,
            self.base_url + "/page1.html",
            # self.base_url + "/ext/page2.html" # Not added if fetch returns None
            "http://example.com/sitemap_url",
            "http://example.com/robots_url"
        }
        self.assertSetEqual(set(results["urls"]), expected_urls)

        # Text content from base_url and page1.html
        self.assertIn("Base content Page 1 Page 2", results["text_content"])
        self.assertIn("Page 1 content Sub Page", results["text_content"])
        self.assertEqual(len(results["text_content"]), 2)

        # page1_1.html should not be in results["urls"] as it's at depth 2
        self.assertNotIn(self.base_url + "/page1.html/sub/page1_1.html", results["urls"]) # urljoin behavior

    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer.find_interesting_robots_paths')
    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer.find_sitemap_urls')
    @patch('api_discovery_tool.processing.website_analyzer.WebsiteAnalyzer.fetch_and_parse_html')
    def test_analyze_initial_fetch_fails(self, mock_fetch_parse, mock_sitemap, mock_robots):
        """Test analyze when the initial fetch_and_parse_html returns None."""
        mock_fetch_parse.return_value = None # Initial fetch fails
        mock_sitemap.return_value = {"http://example.com/sitemap_url"}
        mock_robots.return_value = {"http://example.com/robots_url"}

        results = self.analyzer.analyze(crawl_depth=1)

        mock_fetch_parse.assert_called_once_with(self.base_url)
        mock_sitemap.assert_called_once()
        mock_robots.assert_called_once()

        # Only sitemap and robots URLs should be found. Base URL is not added if soup is None.
        expected_urls = {
            "http://example.com/sitemap_url",
            "http://example.com/robots_url"
        }
        self.assertSetEqual(set(results["urls"]), expected_urls)
        self.assertListEqual(results["text_content"], [])


if __name__ == '__main__':
    unittest.main()
