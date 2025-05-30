import unittest
from api_discovery_tool.processing.deduplicator import normalize_url, get_endpoint_signature, deduplicate_endpoints

class TestDeduplicator(unittest.TestCase):

    def test_normalize_url(self):
        self.assertEqual(normalize_url("http://example.com/api"), "example.com/api")
        self.assertEqual(normalize_url("https://example.com/api/"), "example.com/api")
        self.assertEqual(normalize_url("HTTP://Example.com/API"), "example.com/api")
        self.assertEqual(normalize_url("http://www.example.com/api"), "example.com/api")
        self.assertEqual(normalize_url("https://WWW.EXAMPLE.COM/api/"), "example.com/api")
        self.assertEqual(normalize_url("example.com/api"), "example.com/api") # No protocol
        self.assertEqual(normalize_url(""), "") # Empty string
        self.assertEqual(normalize_url("http://example.com"), "example.com") # No path
        self.assertEqual(normalize_url("http://example.com/"), "example.com") # No path with slash
        self.assertEqual(normalize_url("ws://example.com/socket"), "example.com/socket") # WebSocket
        self.assertEqual(normalize_url("wss://example.com/socket/"), "example.com/socket") # Secure WebSocket

    def test_get_endpoint_signature(self):
        self.assertEqual(get_endpoint_signature({"url": "http://example.com/api", "method": "GET"}), ("example.com/api", "GET"))
        self.assertEqual(get_endpoint_signature({"url": "https://Example.com/API/", "method": "post"}), ("example.com/api", "POST"))
        self.assertEqual(get_endpoint_signature({"url": "ws://example.com/socket"}), "example.com/socket")
        self.assertEqual(get_endpoint_signature({"url": "http://example.com/no-method"}), "example.com/no-method") # No method
        self.assertIsNone(get_endpoint_signature({"url": ""})) # Empty URL should return None
        self.assertEqual(get_endpoint_signature({"url": "http://example.com", "method": 123}), "example.com") # Non-string method
        self.assertIsNone(get_endpoint_signature({})) # Empty dict should return None
        self.assertIsNone(get_endpoint_signature({"url": None})) # None URL should return None

    def test_deduplicate_endpoints_basic(self):
        endpoints = [
            {"url": "http://example.com/api/users", "method": "GET"},
            {"url": "https://example.com/api/users", "method": "GET"}, # Duplicate
            {"url": "http://example.com/api/users/", "method": "GET"}, # Duplicate
            {"url": "http://EXAMPLE.COM/api/USERS", "method": "GET"}, # Duplicate
        ]
        expected = [
            {"url": "http://example.com/api/users", "method": "GET"},
        ]
        self.assertEqual(deduplicate_endpoints(endpoints), expected)

    def test_deduplicate_endpoints_mixed_methods(self):
        endpoints = [
            {"url": "http://example.com/api/items", "method": "GET"},
            {"url": "http://example.com/api/items", "method": "POST"},
            {"url": "https://example.com/api/items", "method": "GET"}, # Duplicate GET
        ]
        expected = [
            {"url": "http://example.com/api/items", "method": "GET"},
            {"url": "http://example.com/api/items", "method": "POST"},
        ]
        # Order might not be preserved by set, so check contents
        result = deduplicate_endpoints(endpoints)
        self.assertEqual(len(result), len(expected))
        for item in expected:
            self.assertIn(item, result)

    def test_deduplicate_endpoints_non_http(self):
        endpoints = [
            {"url": "ws://example.com/chat"},
            {"url": "WS://EXAMPLE.COM/chat/"}, # Duplicate
            {"url": "wss://example.com/realtime"},
        ]
        expected = [
            {"url": "ws://example.com/chat"},
            {"url": "wss://example.com/realtime"},
        ]
        result = deduplicate_endpoints(endpoints)
        self.assertEqual(len(result), len(expected))
        for item in expected:
            self.assertIn(item, result)

    def test_deduplicate_endpoints_no_method_field(self):
        endpoints = [
            {"url": "http://example.com/resource"},
            {"url": "https://example.com/resource/"}, # Duplicate
            {"url": "http://example.com/another"},
        ]
        expected = [
            {"url": "http://example.com/resource"},
            {"url": "http://example.com/another"},
        ]
        result = deduplicate_endpoints(endpoints)
        self.assertEqual(len(result), len(expected))
        for item in expected:
            self.assertIn(item, result)

    def test_deduplicate_endpoints_empty_input(self):
        self.assertEqual(deduplicate_endpoints([]), [])

    def test_deduplicate_endpoints_no_duplicates(self):
        endpoints = [
            {"url": "http://one.com", "method": "GET"},
            {"url": "http://two.com", "method": "POST"},
        ]
        self.assertEqual(deduplicate_endpoints(endpoints), endpoints)

    def test_deduplicate_malformed_entries(self):
        endpoints = [
            {"url": "http://good.com/a", "method": "GET"},
            {},
            {"method": "POST"},
            {"url": None, "method": "GET"}, # URL is None
            {"url": "http://good.com/b"}
        ]
        expected = [
            {"url": "http://good.com/a", "method": "GET"},
            {"url": "http://good.com/b"}
        ]
        result = deduplicate_endpoints(endpoints)
        self.assertEqual(len(result), len(expected), f"Result: {result}, Expected: {expected}")
        for item in expected:
            self.assertIn(item, result)

if __name__ == '__main__':
    unittest.main() 