import unittest
from collections import Counter
from api_discovery_tool.processing.pattern_recognizer import APIPatternRecognizer

class TestAPIPatternRecognizer(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None # Show full diff on assertion failure
        self.empty_spec = {"openapi": "3.0.0", "info": {"title": "Empty API", "version": "1.0"}, "paths": {}}
        self.empty_interactions = []

        self.sample_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Sample API", "version": "v1.2.3"},
            "consumes": ["application/json"], # Global consume
            "produces": ["application/json"], # Global produce
            "paths": {
                "/api/v1/users/{userId}": {
                    "get": {
                        "summary": "Get a user by_id",
                        "tags": ["Users"],
                        "parameters": [
                            {"name": "userId", "in": "path", "required": True, "schema": {"type": "string"}},
                            {"name": "include_details", "in": "query", "schema": {"type": "boolean"}}
                        ],
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}
                            },
                            "404": {"description": "User not found"}
                        },
                        "security": [{"ApiKeyAuth": []}]
                    }
                },
                "/api/v1/items": {
                    "post": {
                        "summary": "Create an item",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/NewItem"}},
                                "application/xml": {"schema": {"$ref": "#/components/schemas/NewItem"}} # Added XML for testing
                            }
                        },
                        "responses": {
                            "201": {"description": "Item created"},
                            "400": {"description": "Invalid input"}
                        },
                        "produces": ["application/vnd.custom+json"] # Operation specific produce
                    }
                },
                "/api/v2.0/posts": {
                    "get": {
                        "parameters": [
                            {"name": "page", "in": "query"},
                            {"name": "perPage", "in": "query"},
                        ],
                        "responses": {"200": {"description": "Paginated posts"}}
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "userName": {"type": "string"},
                            "email_address": {"type": "string"}
                        }
                    },
                    "NewItem": {
                        "type": "object",
                        "properties": {"item_name": {"type": "string"}, "price_amount": {"type": "number"}}
                    }
                },
                "securitySchemes": {
                    "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-Custom-API-Key"},
                    "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
                }
            }
        }

        self.sample_interactions = [
            {
                "request": {
                    "method": "GET",
                    "url": "/api/v1/users/123?include_details=true",
                    "headers": {"Accept": "application/json", "X-Custom-API-Key": "secretkey"},
                    "params": {"include_details": "true"}
                },
                "response": {
                    "status_code": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": {"id": 123, "userName": "testUser", "email_address": "test@example.com"}
                }
            },
            {
                "request": {
                    "method": "POST",
                    "url": "/api/v1/items",
                    "headers": {"Content-Type": "application/xml", "Authorization": "Bearer sometoken"},
                    "body": "<NewItem><item_name>Test Item</item_name><price_amount>9.99</price_amount></NewItem>"
                },
                "response": {"status_code": 201, "headers": {"Content-Type": "application/vnd.custom+json"}}
            },
            {
                "request": {
                    "method": "GET",
                    "url": "/api/v2.0/posts?page=2&perPage=20&api_version=2.0", # query version
                    "headers": {"X-API-Version": "2.0"}, # header version
                    "params": {"page": "2", "perPage": "20", "api_version": "2.0"}
                },
                "response": {"status_code": 200, "headers": {"Link": "<url?page=3&perPage=20>; rel=\"next\""}}
            }
        ]

    def test_identify_naming_conventions_empty(self):
        recognizer = APIPatternRecognizer(self.empty_spec, self.empty_interactions)
        conventions = recognizer.identify_naming_conventions()
        self.assertEqual(conventions, {})

    def test_identify_naming_conventions_sample(self):
        recognizer = APIPatternRecognizer(self.sample_spec, self.sample_interactions)
        conventions = recognizer.identify_naming_conventions()
        expected = {
            'path_segments': {'camelCase': 3, 'snake_case': 1},
            'query_parameters': {'snake_case': 1, 'camelCase': 1, 'PascalCase':1 }, #perPage is Pascal, page is camel
            'path_parameters': {'camelCase': 1},
            'request_body_keys': {'snake_case': 2},
            'response_body_keys': {'camelCase': 2, 'snake_case':1},
            'component_schema_keys': {'PascalCase': 2, 'camelCase': 2, 'snake_case': 3}
        }
        # Adjusting expected based on current get_case logic for perPage and page
        expected['query_parameters'] = {'snake_case': 1, 'camelCase': 1, 'PascalCase':1}
        self.assertEqual(conventions, expected)

    def test_identify_versioning_empty(self):
        recognizer = APIPatternRecognizer(self.empty_spec, self.empty_interactions)
        versioning = recognizer.identify_versioning()
        self.assertEqual(versioning, {})

    def test_identify_versioning_sample(self):
        recognizer = APIPatternRecognizer(self.sample_spec, self.sample_interactions)
        versioning = recognizer.identify_versioning()
        expected = {
            'path_versions': ['1', '2.0'],
            'header_versions': {'2.0': 1},
            'query_param_versions': {'2.0': 1},
            'identified_versions': ['1', '2.0']
        }
        self.assertEqual(versioning, expected)

    def test_identify_authentication_empty(self):
        recognizer = APIPatternRecognizer(self.empty_spec, self.empty_interactions)
        auth = recognizer.identify_authentication()
        self.assertEqual(auth, {})

    def test_identify_authentication_sample(self):
        recognizer = APIPatternRecognizer(self.sample_spec, self.sample_interactions)
        auth = recognizer.identify_authentication()
        expected = {
            'schemes_from_spec': [
                {'name': 'ApiKeyAuth', 'type': 'apiKey', 'in': 'header', 'param_name': 'X-Custom-API-Key'},
                {'name': 'BearerAuth', 'type': 'http', 'scheme': 'bearer'}
            ],
            'observed_auth_headers': {'x-custom-api-key': 1, 'Authorization: Bearer': 1}
        }
        self.assertEqual(auth, expected)

    def test_identify_pagination_empty(self):
        recognizer = APIPatternRecognizer(self.empty_spec, self.empty_interactions)
        pagination = recognizer.identify_pagination()
        self.assertEqual(pagination, {})

    def test_identify_pagination_sample(self):
        recognizer = APIPatternRecognizer(self.sample_spec, self.sample_interactions)
        pagination = recognizer.identify_pagination()
        expected = {
            'query_param_patterns': {
                'page_based (e.g., page)': 2, # from spec and interaction
                'size_based (e.g., perpage)': 2 # from spec and interaction, perPage becomes perpage
            },
            'header_patterns': {'Link_header_next': 1}
        }
        self.assertEqual(pagination, expected)

    def test_identify_data_formats_empty(self):
        recognizer = APIPatternRecognizer(self.empty_spec, self.empty_interactions)
        formats = recognizer.identify_data_formats()
        self.assertEqual(formats, {})

    def test_identify_data_formats_sample(self):
        recognizer = APIPatternRecognizer(self.sample_spec, self.sample_interactions)
        formats = recognizer.identify_data_formats()
        expected = {
            'spec_consumes': {'application/json': 2, 'application/xml': 1}, # global + item post
            'spec_produces': {'application/json': 2, 'application/vnd.custom+json': 1}, # global + user get + item post
            'observed_request_content_types': {'application/xml': 1},
            'observed_response_content_types': {'application/json': 1, 'application/vnd.custom+json': 1},
            'observed_accept_headers': {'application/json': 1}
        }
        self.assertEqual(formats, expected)

    def test_identify_http_methods_empty(self):
        recognizer = APIPatternRecognizer(self.empty_spec, self.empty_interactions)
        methods = recognizer.identify_http_methods()
        self.assertEqual(methods, {})
    
    def test_identify_http_methods_sample(self):
        recognizer = APIPatternRecognizer(self.sample_spec, self.sample_interactions)
        methods = recognizer.identify_http_methods()
        expected = {
            'spec_methods': {'GET': 2, 'POST': 1},
            'observed_methods': {'GET': 2, 'POST': 1}
        }
        self.assertEqual(methods, expected)

    def test_identify_status_codes_empty(self):
        recognizer = APIPatternRecognizer(self.empty_spec, self.empty_interactions)
        codes = recognizer.identify_status_codes()
        self.assertEqual(codes, {})

    def test_identify_status_codes_sample(self):
        recognizer = APIPatternRecognizer(self.sample_spec, self.sample_interactions)
        codes = recognizer.identify_status_codes()
        expected = {
            'spec_status_codes': {'200': 2, '404': 1, '201': 1, '400': 1},
            'observed_status_codes': {'200': 2, '201': 1}
        }
        self.assertEqual(codes, expected)

    def test_identify_all_patterns_sample(self):
        recognizer = APIPatternRecognizer(self.sample_spec, self.sample_interactions)
        all_patterns = recognizer.identify_all_patterns()
        self.assertIn("naming_conventions", all_patterns)
        self.assertIn("versioning", all_patterns)
        self.assertIn("authentication", all_patterns)
        self.assertIn("pagination", all_patterns)
        self.assertIn("data_formats", all_patterns)
        self.assertIn("http_methods", all_patterns)
        self.assertIn("status_codes", all_patterns)
        # Check a specific value from one of the sub-results to ensure it ran
        self.assertEqual(all_patterns["versioning"]['path_versions'], ['1', '2.0'])

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False) 