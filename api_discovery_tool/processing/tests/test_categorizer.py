import unittest
from api_discovery_tool.processing.categorizer import (
    categorize_api_type,
    API_TYPE_REST,
    API_TYPE_GRAPHQL,
    API_TYPE_SOAP,
    API_TYPE_WEBSOCKET,
    API_TYPE_UNKNOWN
)

class TestCategorizer(unittest.TestCase):

    def test_categorize_websocket(self):
        self.assertEqual(categorize_api_type({"url": "ws://example.com/socket"}), API_TYPE_WEBSOCKET)
        self.assertEqual(categorize_api_type({"url": "wss://example.com/secure/live"}), API_TYPE_WEBSOCKET)
        self.assertEqual(categorize_api_type({"url": "WS://UPPER.CASE/STREAM"}), API_TYPE_WEBSOCKET)

    def test_categorize_graphql(self):
        self.assertEqual(categorize_api_type({"url": "http://example.com/graphql", "method": "POST"}), API_TYPE_GRAPHQL)
        self.assertEqual(categorize_api_type({"url": "https://api.example.com/gql", "method": "POST", "request_body": "query { posts { title } }"}), API_TYPE_GRAPHQL)
        self.assertEqual(categorize_api_type({"url": "http://example/api", "method": "POST", "response_headers": {"Content-Type": "application/graphql+json"}}), API_TYPE_GRAPHQL)
        self.assertEqual(categorize_api_type({"url": "http://example/api", "method": "POST", "response_headers": {"content-type": "Application/GraphQL"}}), API_TYPE_GRAPHQL) # Case-insensitive header
        self.assertEqual(categorize_api_type({"url": "http://example/api", "method": "POST", "response_body": '{"data": {}, "errors": []}'}), API_TYPE_GRAPHQL)
        # Weak signal (body only) but POST helps
        self.assertEqual(categorize_api_type({"url": "http://example/api", "method": "POST", "response_body": '{"data": {}}'}), API_TYPE_GRAPHQL)
        # GET with GraphQL-like body should ideally be REST unless other strong GraphQL signals exist
        self.assertEqual(categorize_api_type({"url": "http://example/api", "method": "GET", "response_body": '{"data": {}}'}), API_TYPE_REST)

    def test_categorize_soap(self):
        self.assertEqual(categorize_api_type({"url": "http://example.com/service.asmx?WSDL"}), API_TYPE_SOAP)
        self.assertEqual(categorize_api_type({"url": "http://example.com/svc?wsdl"}), API_TYPE_SOAP)
        self.assertEqual(categorize_api_type({"url": "http://example/s", "response_headers": {"Content-Type": "application/soap+xml"}, "response_body": "<soap:Envelope></soap:Envelope>"}), API_TYPE_SOAP)
        self.assertEqual(categorize_api_type({"url": "http://example/s", "response_headers": {"Content-Type": "text/xml; charset=utf-8"}, "response_body": "<soapenv:Envelope></soapenv:Envelope>"}), API_TYPE_SOAP)
        # Body check without strong content type (weaker, but still SOAP)
        self.assertEqual(categorize_api_type({"url": "http://example/s", "response_body": "<s:Envelope xmlns:s='http://schemas.xmlsoap.org/soap/envelope/'></s:Envelope>"}), API_TYPE_SOAP)
        # XML but not SOAP
        self.assertEqual(categorize_api_type({"url": "http://example/xmlapi", "method": "POST", "response_headers": {"Content-Type": "text/xml"}, "response_body": "<root><item/></root>"}), API_TYPE_REST)

    def test_categorize_rest(self):
        self.assertEqual(categorize_api_type({"url": "http://example.com/api/users", "method": "GET", "response_headers": {"Content-Type": "application/json"}}), API_TYPE_REST)
        self.assertEqual(categorize_api_type({"url": "http://example.com/api/users", "method": "get", "response_headers": {"content-type": "application/json; charset=UTF-8"}}), API_TYPE_REST)
        self.assertEqual(categorize_api_type({"url": "http://example.com/api/posts", "method": "POST", "openapi_spec": {"openapi": "3.0.0"}}), API_TYPE_REST)
        self.assertEqual(categorize_api_type({"url": "http://example.com/api/items/1", "method": "PUT"}), API_TYPE_REST) # Generic, no headers/body
        self.assertEqual(categorize_api_type({"url": "http://example.com/api/products", "method": "DELETE", "response_headers": {"Content-Type": "application/xml"}}), API_TYPE_REST)
        self.assertEqual(categorize_api_type({"url": "http://example.com/resource-search", "method": "GET"}), API_TYPE_REST)
        self.assertEqual(categorize_api_type({"url": "http://example.com/resource.php", "method": "POST", "response_headers": {"Content-Type": "application/x-www-form-urlencoded"}}), API_TYPE_REST)

    def test_categorize_unknown(self):
        self.assertEqual(categorize_api_type({"url": "http://example.com/page.html", "method": "GET", "response_headers": {"Content-Type": "text/html"}}), API_TYPE_UNKNOWN)
        self.assertEqual(categorize_api_type({"url": "ftp://example.com/files/doc.txt"}), API_TYPE_UNKNOWN)
        self.assertEqual(categorize_api_type({"url": "http://example.com", "method": "GET"}), API_TYPE_REST) # A generic GET might be REST by default in _check_rest
        self.assertEqual(categorize_api_type({}), API_TYPE_UNKNOWN)
        self.assertEqual(categorize_api_type({"url": "just-a-string-not-url"}), API_TYPE_UNKNOWN) # Not starting with known schemes for ws, and _check_rest might be too greedy
        self.assertEqual(categorize_api_type({"url": "http://example.com/image.png", "response_headers": {"Content-Type": "image/png"}}), API_TYPE_UNKNOWN)

    def test_categorization_order_and_ambiguity(self):
        # Should be GraphQL due to specific body structure despite generic JSON content type and POST method
        graphql_ish_json = {"url": "http://example.com/api", "method": "POST", 
                              "response_headers": {"Content-Type": "application/json"}, 
                              "response_body": '{"data": {"user": {"id": "1"}}}'}
        self.assertEqual(categorize_api_type(graphql_ish_json), API_TYPE_GRAPHQL)

        # Should be SOAP due to WSDL, even if other things look RESTy
        soap_with_wsdl = {"url": "http://example.com/UserService?wsdl", "method": "GET", "response_headers": {"Content-Type": "application/json"}}
        self.assertEqual(categorize_api_type(soap_with_wsdl), API_TYPE_SOAP)

        # Should be WebSocket, highest priority
        ws_with_rest_hints = {"url": "ws://example.com/api", "method": "GET", "response_headers": {"Content-Type": "application/json"}}
        self.assertEqual(categorize_api_type(ws_with_rest_hints), API_TYPE_WEBSOCKET)

    def test_empty_and_malformed_input(self):
        self.assertEqual(categorize_api_type(None), API_TYPE_UNKNOWN)
        self.assertEqual(categorize_api_type([]), API_TYPE_UNKNOWN)
        self.assertEqual(categorize_api_type("string input"), API_TYPE_UNKNOWN)
        self.assertEqual(categorize_api_type({"key": "value"}), API_TYPE_UNKNOWN) # No URL
        self.assertEqual(categorize_api_type({"url": None, "method": "GET"}), API_TYPE_UNKNOWN)

if __name__ == '__main__':
    unittest.main() 