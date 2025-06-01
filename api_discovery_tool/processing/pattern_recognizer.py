import re
from collections import Counter

class APIPatternRecognizer:
    """
    Recognizes common API conventions from OpenAPI specifications and HTTP interactions.
    """

    def __init__(self, openapi_spec: dict | None = None, http_interactions: list | None = None):
        self.openapi_spec = openapi_spec if openapi_spec else {}
        self.http_interactions = http_interactions if http_interactions else []

    def identify_all_patterns(self) -> dict:
        """Runs all identification methods and aggregates the results."""
        patterns = {
            "naming_conventions": self.identify_naming_conventions(),
            "versioning": self.identify_versioning(),
            "authentication": self.identify_authentication(),
            "pagination": self.identify_pagination(),
            "data_formats": self.identify_data_formats(),
            "http_methods": self.identify_http_methods(),
            "status_codes": self.identify_status_codes(),
        }
        return patterns

    def _get_from_spec(self, path_keys: list[str], default=None):
        """Helper to safely get nested values from OpenAPI spec."""
        current = self.openapi_spec
        for key in path_keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
                current = current[key]
            else:
                return default
        return current

    def identify_naming_conventions(self) -> dict:
        """
        Identifies naming conventions used in paths, parameters, and schemas.
        Detects camelCase, snake_case, PascalCase.
        """
        conventions = {
            "path_segments": Counter(),
            "query_parameters": Counter(),
            "header_parameters": Counter(),
            "path_parameters": Counter(),
            "request_body_keys": Counter(),
            "response_body_keys": Counter(),
            "component_schema_keys": Counter(),
        }
        
        name_pattern = r"^[a-z]+(?:[A-Z][a-z0-9]*)*$|^[a-z]+(?:_[a-z0-9]+)*$|^[A-Z][a-zA-Z0-9]*$" # camelCase, snake_case, PascalCase

        def get_case(name):
            if not name or not isinstance(name, str):
                return "unknown"
            if re.match(r"^[a-z]+([A-Z][a-z0-9]*)*$", name):
                return "camelCase"
            if re.match(r"^[a-z0-9]+(_[a-z0-9]+)*$", name):
                return "snake_case"
            if re.match(r"^[A-Z][a-zA-Z0-9]*$", name): # Simplified PascalCase for this context
                 return "PascalCase"
            if name.isupper() and "_" in name:
                return "UPPER_SNAKE_CASE"
            if name.islower() and "-" in name:
                return "kebab-case"
            return "mixed/other"

        # Analyze paths
        paths = self._get_from_spec(["paths"], {})
        for path_string in paths.keys():
            segments = [s for s in path_string.split('/') if s and not s.startswith('{') and not s.endswith('}')]
            for segment in segments:
                conventions["path_segments"][get_case(segment)] += 1

            for method_data in paths[path_string].values():
                if not isinstance(method_data, dict): continue
                # Parameters (query, header, path)
                parameters = method_data.get("parameters", [])
                for param in parameters:
                    if not isinstance(param, dict): continue
                    param_name = param.get("name")
                    param_in = param.get("in")
                    if param_name and param_in:
                        if param_in == "query":
                            conventions["query_parameters"][get_case(param_name)] += 1
                        elif param_in == "header":
                            conventions["header_parameters"][get_case(param_name)] += 1
                        elif param_in == "path":
                            conventions["path_parameters"][get_case(param_name)] += 1
                
                # Request body keys
                request_body = method_data.get("requestBody", {}).get("content", {})
                for media_type_obj in request_body.values():
                    schema_ref = media_type_obj.get("schema", {}).get("$ref")
                    if schema_ref:
                        schema_name = schema_ref.split('/')[-1]
                        schema = self._get_from_spec(["components", "schemas", schema_name], {})
                        if schema and isinstance(schema.get("properties"), dict):
                            for key in schema["properties"].keys():
                                conventions["request_body_keys"][get_case(key)] += 1
                    elif isinstance(media_type_obj.get("schema", {}).get("properties"), dict):
                         for key in media_type_obj["schema"]["properties"].keys():
                            conventions["request_body_keys"][get_case(key)] += 1


                # Response body keys
                responses = method_data.get("responses", {})
                for status_code, response_obj in responses.items():
                    if not isinstance(response_obj, dict): continue
                    content = response_obj.get("content", {})
                    for media_type_obj in content.values():
                        schema_ref = media_type_obj.get("schema", {}).get("$ref")
                        if schema_ref:
                            schema_name = schema_ref.split('/')[-1]
                            schema = self._get_from_spec(["components", "schemas", schema_name], {})
                            if schema and isinstance(schema.get("properties"), dict):
                                for key in schema["properties"].keys():
                                    conventions["response_body_keys"][get_case(key)] += 1
                        elif isinstance(media_type_obj.get("schema", {}).get("properties"), dict):
                            for key in media_type_obj["schema"]["properties"].keys():
                                conventions["response_body_keys"][get_case(key)] += 1
        
        # Component Schemas
        schemas = self._get_from_spec(["components", "schemas"], {})
        for schema_name, schema_def in schemas.items():
            conventions["component_schema_keys"][get_case(schema_name)] +=1 # Schema name itself
            if isinstance(schema_def.get("properties"), dict):
                for key in schema_def["properties"].keys():
                    conventions["component_schema_keys"][get_case(key)] += 1
        
        # Convert Counters to dicts for JSON serialization
        return {k: dict(v) for k, v in conventions.items() if v}


    def identify_versioning(self) -> dict:
        """
        Identifies API versioning strategies (path, header, query parameter).
        """
        versioning_info = {
            "path_versions": [],
            "header_versions": Counter(),
            "query_param_versions": Counter(),
            "identified_versions": set()
        }
        
        version_path_pattern = r"/v([0-9]+(?:[.][0-9]+)*)/|/api/v([0-9]+(?:[.][0-9]+)*)/"
        
        # From OpenAPI spec paths
        paths = self._get_from_spec(["paths"], {})
        for path_string in paths.keys():
            match = re.search(version_path_pattern, path_string)
            if match:
                version = match.group(1) or match.group(2)
                if version not in versioning_info["path_versions"]:
                    versioning_info["path_versions"].append(version)
                versioning_info["identified_versions"].add(version)

        # From HTTP interactions
        for interaction in self.http_interactions:
            if not isinstance(interaction, dict): continue
            request = interaction.get("request", {})
            
            # Path versioning from actual requests
            url = request.get("url", "")
            match = re.search(version_path_pattern, url)
            if match:
                version = match.group(1) or match.group(2)
                if version not in versioning_info["path_versions"]:
                     versioning_info["path_versions"].append(version) # Add if found in live traffic
                versioning_info["identified_versions"].add(version)

            # Header versioning
            headers = request.get("headers", {})
            if isinstance(headers, dict):
                for header_name, header_value in headers.items():
                    if header_name.lower() in ["x-api-version", "api-version"]:
                        versioning_info["header_versions"][str(header_value)] += 1
                        versioning_info["identified_versions"].add(str(header_value))
                    elif header_name.lower() == "accept":
                        # e.g., application/vnd.myapi.v1+json
                        m = re.search(r"v([0-9]+(?:[.][0-9]+)*)", str(header_value))
                        if m:
                            version = m.group(1)
                            versioning_info["header_versions"][f"accept_header_v{version}"] += 1
                            versioning_info["identified_versions"].add(version)
            
            # Query parameter versioning
            query_params = request.get("params", {}) # Assuming query params are parsed into 'params'
            if isinstance(query_params, dict):
                for param_name, param_value in query_params.items():
                    if param_name.lower() in ["version", "api_version", "apiversion"]:
                        versioning_info["query_param_versions"][str(param_value)] += 1
                        versioning_info["identified_versions"].add(str(param_value))
        
        versioning_info["identified_versions"] = sorted(list(versioning_info["identified_versions"]))
        versioning_info["header_versions"] = dict(versioning_info["header_versions"])
        versioning_info["query_param_versions"] = dict(versioning_info["query_param_versions"])
        
        return {k: v for k, v in versioning_info.items() if v}


    def identify_authentication(self) -> dict:
        """
        Identifies authentication/authorization schemes (API Key, Bearer Token, OAuth2).
        """
        auth_info = {
            "schemes_from_spec": [],
            "observed_auth_headers": Counter(),
            "observed_auth_query_params": Counter(),
        }

        # From OpenAPI spec securitySchemes
        security_schemes = self._get_from_spec(["components", "securitySchemes"], {})
        if security_schemes:
            for name, scheme_obj in security_schemes.items():
                if not isinstance(scheme_obj, dict): continue
                scheme_type = scheme_obj.get("type")
                scheme_details = {"name": name, "type": scheme_type}
                if scheme_type == "apiKey":
                    scheme_details["in"] = scheme_obj.get("in")
                    scheme_details["param_name"] = scheme_obj.get("name")
                elif scheme_type == "http":
                    scheme_details["scheme"] = scheme_obj.get("scheme") # e.g., bearer
                elif scheme_type == "oauth2":
                    scheme_details["flows"] = scheme_obj.get("flows", {})
                auth_info["schemes_from_spec"].append(scheme_details)
        
        # From HTTP interactions
        for interaction in self.http_interactions:
            if not isinstance(interaction, dict): continue
            request = interaction.get("request", {})
            
            # Auth headers
            headers = request.get("headers", {})
            if isinstance(headers, dict):
                for header_name, header_value in headers.items():
                    if header_name.lower() == "authorization":
                        auth_type = str(header_value).split(" ")[0] if " " in str(header_value) else "Unknown"
                        auth_info["observed_auth_headers"][f"Authorization: {auth_type}"] += 1
                    elif header_name.lower() in ["x-api-key", "apikey", "api-key", "x-auth-token"]:
                        auth_info["observed_auth_headers"][header_name.lower()] += 1
            
            # Auth query parameters
            query_params = request.get("params", {})
            if isinstance(query_params, dict):
                for param_name in query_params.keys():
                    if param_name.lower() in ["apikey", "api_key", "access_token", "auth_token"]:
                        auth_info["observed_auth_query_params"][param_name.lower()] += 1
        
        auth_info["observed_auth_headers"] = dict(auth_info["observed_auth_headers"])
        auth_info["observed_auth_query_params"] = dict(auth_info["observed_auth_query_params"])

        return {k: v for k, v in auth_info.items() if v}

    def identify_pagination(self) -> dict:
        """
        Identifies pagination patterns (limit/offset, page/per_page, cursor).
        """
        pagination_info = {
            "query_param_patterns": Counter(),
            "header_patterns": Counter()
        }
        
        common_page_params = ["page", "page_number", "pagenum"]
        common_size_params = ["size", "per_page", "pagesize", "limit", "count"]
        common_offset_params = ["offset", "skip"]
        common_cursor_params = ["cursor", "next_token", "continuation_token", "next_cursor", "page_token"]

        # From OpenAPI spec parameters
        paths = self._get_from_spec(["paths"], {})
        for path_data in paths.values():
            if not isinstance(path_data, dict): continue
            for method_data in path_data.values():
                if not isinstance(method_data, dict): continue
                parameters = method_data.get("parameters", [])
                for param in parameters:
                    if not isinstance(param, dict): continue
                    if param.get("in") == "query":
                        param_name = param.get("name", "").lower()
                        if param_name in common_page_params:
                            pagination_info["query_param_patterns"]["page_based (e.g., " + param_name + ")"] +=1
                        elif param_name in common_size_params:
                            pagination_info["query_param_patterns"]["size_based (e.g., " + param_name + ")"] +=1
                        elif param_name in common_offset_params:
                             pagination_info["query_param_patterns"]["offset_based (e.g., " + param_name + ")"] +=1
                        elif param_name in common_cursor_params:
                             pagination_info["query_param_patterns"]["cursor_based (e.g., " + param_name + ")"] +=1
        
        # From HTTP interactions
        for interaction in self.http_interactions:
            if not isinstance(interaction, dict): continue
            request = interaction.get("request", {})
            response_headers = interaction.get("response", {}).get("headers", {})

            # Query parameters from actual requests
            query_params = request.get("params", {})
            if isinstance(query_params, dict):
                for param_name in query_params.keys():
                    param_name_lower = param_name.lower()
                    if param_name_lower in common_page_params:
                        pagination_info["query_param_patterns"]["page_based (e.g., " + param_name_lower + ")"] +=1
                    elif param_name_lower in common_size_params:
                        pagination_info["query_param_patterns"]["size_based (e.g., " + param_name_lower + ")"] +=1
                    elif param_name_lower in common_offset_params:
                         pagination_info["query_param_patterns"]["offset_based (e.g., " + param_name_lower + ")"] +=1
                    elif param_name_lower in common_cursor_params:
                         pagination_info["query_param_patterns"]["cursor_based (e.g., " + param_name_lower + ")"] +=1
            
            # Link headers from responses
            if isinstance(response_headers, dict):
                link_header = response_headers.get("Link") or response_headers.get("link")
                if link_header:
                    if 'rel="next"' in str(link_header):
                        pagination_info["header_patterns"]["Link_header_next"] += 1
                    if 'rel="prev"' in str(link_header):
                        pagination_info["header_patterns"]["Link_header_prev"] += 1
                    if 'rel="first"' in str(link_header):
                        pagination_info["header_patterns"]["Link_header_first"] += 1
                    if 'rel="last"' in str(link_header):
                        pagination_info["header_patterns"]["Link_header_last"] += 1

        pagination_info["query_param_patterns"] = dict(pagination_info["query_param_patterns"])
        pagination_info["header_patterns"] = dict(pagination_info["header_patterns"])
        return {k: v for k, v in pagination_info.items() if v}

    def identify_data_formats(self) -> dict:
        """
        Identifies data formats used (JSON, XML, etc.) from 'produces', 'consumes',
        and Content-Type/Accept headers.
        """
        formats = {
            "spec_consumes": Counter(),
            "spec_produces": Counter(),
            "observed_request_content_types": Counter(),
            "observed_response_content_types": Counter(),
            "observed_accept_headers": Counter(),
        }

        # From OpenAPI spec (global consumes/produces if available)
        global_consumes = self._get_from_spec(["consumes"], [])
        for fmt in global_consumes: formats["spec_consumes"][fmt] += 1
        global_produces = self._get_from_spec(["produces"], [])
        for fmt in global_produces: formats["spec_produces"][fmt] += 1

        # From OpenAPI spec (path/operation level)
        paths = self._get_from_spec(["paths"], {})
        for path_data in paths.values():
            if not isinstance(path_data, dict): continue
            for method_data in path_data.values():
                if not isinstance(method_data, dict): continue
                
                op_consumes = method_data.get("consumes", [])
                for fmt in op_consumes: formats["spec_consumes"][fmt] += 1
                
                op_produces = method_data.get("produces", [])
                for fmt in op_produces: formats["spec_produces"][fmt] += 1

                # More specific: requestBody content types
                request_body_content = method_data.get("requestBody", {}).get("content", {})
                for fmt in request_body_content.keys(): formats["spec_consumes"][fmt] +=1

                # More specific: response content types
                responses_content = method_data.get("responses", {})
                for resp_obj in responses_content.values():
                    if not isinstance(resp_obj, dict): continue
                    for fmt in resp_obj.get("content", {}).keys():
                        formats["spec_produces"][fmt] += 1
        
        # From HTTP interactions
        for interaction in self.http_interactions:
            if not isinstance(interaction, dict): continue
            request_headers = interaction.get("request", {}).get("headers", {})
            response_headers = interaction.get("response", {}).get("headers", {})

            if isinstance(request_headers, dict):
                content_type = request_headers.get("Content-Type") or request_headers.get("content-type")
                if content_type:
                    formats["observed_request_content_types"][content_type.split(";")[0].strip()] += 1
                
                accept = request_headers.get("Accept") or request_headers.get("accept")
                if accept:
                    # Accept header can have multiple types with q-factors
                    for part in accept.split(","):
                        formats["observed_accept_headers"][part.split(";")[0].strip()] += 1
            
            if isinstance(response_headers, dict):
                content_type = response_headers.get("Content-Type") or response_headers.get("content-type")
                if content_type:
                    formats["observed_response_content_types"][content_type.split(";")[0].strip()] += 1
        
        return {k: dict(v) for k, v in formats.items() if v}

    def identify_http_methods(self) -> dict:
        """Identifies usage patterns of HTTP methods from spec and interactions."""
        methods_summary = {
            "spec_methods": Counter(),
            "observed_methods": Counter()
        }

        # From OpenAPI spec
        paths = self._get_from_spec(["paths"], {})
        for path_item in paths.values():
            if not isinstance(path_item, dict): continue
            for method_name in path_item.keys():
                if method_name.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD", "TRACE"]:
                    methods_summary["spec_methods"][method_name.upper()] += 1
        
        # From HTTP interactions
        for interaction in self.http_interactions:
            if not isinstance(interaction, dict): continue
            method = interaction.get("request", {}).get("method", "").upper()
            if method:
                methods_summary["observed_methods"][method] += 1
        
        return {k: dict(v) for k, v in methods_summary.items() if v}

    def identify_status_codes(self) -> dict:
        """Identifies usage patterns of HTTP status codes from spec and interactions."""
        status_codes_summary = {
            "spec_status_codes": Counter(),
            "observed_status_codes": Counter()
        }

        # From OpenAPI spec
        paths = self._get_from_spec(["paths"], {})
        for path_item in paths.values():
            if not isinstance(path_item, dict): continue
            for op_object in path_item.values():
                if not isinstance(op_object, dict): continue
                responses = op_object.get("responses", {})
                for status_code in responses.keys():
                    status_codes_summary["spec_status_codes"][str(status_code)] += 1

        # From HTTP interactions
        for interaction in self.http_interactions:
            if not isinstance(interaction, dict): continue
            status_code = interaction.get("response", {}).get("status_code")
            if status_code is not None: # Check for None explicitly
                 status_codes_summary["observed_status_codes"][str(status_code)] += 1
        
        return {k: dict(v) for k, v in status_codes_summary.items() if v}

if __name__ == '__main__':
    # Example Usage (requires mock data)
    mock_openapi_spec = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "v1.0"},
        "paths": {
            "/users": {
                "get": {
                    "summary": "List users",
                    "parameters": [
                        {"name": "page_number", "in": "query", "schema": {"type": "integer"}},
                        {"name": "pageSize", "in": "query", "schema": {"type": "integer"}}
                    ],
                    "responses": {
                        "200": {"description": "A list of users.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserList"}}}},
                        "401": {"description": "Unauthorized"}
                    }
                },
                "post": {
                    "summary": "Create user",
                     "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/NewUser"}
                            }
                        }
                    },
                    "responses": {"201": {"description": "User created"}}
                }
            },
            "/items/{itemId}":{
                "get":{
                    "parameters": [{"name": "itemId", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "An item"}}
                }
            }
        },
        "components": {
            "schemas": {
                "UserList": {"type": "object", "properties": {"users_data": {"type": "array", "items": {"type": "object"}}}},
                "NewUser": {"type": "object", "properties": {"userName": {"type": "string"}, "email_address": {"type": "string"}}}
            },
            "securitySchemes": {
                "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-KEY"}
            }
        },
        "security": [{"ApiKeyAuth": []}]
    }

    mock_http_interactions = [
        {
            "request": {
                "method": "GET",
                "url": "/users?page_number=1&pageSize=10",
                "headers": {"Accept": "application/json", "X-API-KEY": "testkey123"},
                "params": {"page_number": "1", "pageSize": "10"} # Example if params are pre-parsed
            },
            "response": {
                "status_code": 200,
                "headers": {"Content-Type": "application/json"},
                "body": {"users_data": [{"id": 1, "name": "Test User"}]}
            }
        },
        {
            "request": {
                "method": "POST",
                "url": "/users",
                "headers": {"Content-Type": "application/json", "X-API-KEY": "testkey123"},
                "body": {"userName": "newUser", "email_address": "new@example.com"}
            },
            "response": {
                "status_code": 201,
                "headers": {"Content-Type": "application/json"},
                "body": {"id": 2, "userName": "newUser"}
            }
        }
    ]

    recognizer = APIPatternRecognizer(openapi_spec=mock_openapi_spec, http_interactions=mock_http_interactions)
    all_patterns = recognizer.identify_all_patterns()
    import json
    print(json.dumps(all_patterns, indent=2))

    # Example for recognize_from_website_data
    print("\n--- Website Data Recognition Example ---")
    website_urls = [
        "https://example.com/api/v1/users",
        "https://example.com/service/data/v2/items",
        "https://example.com/core/auth/login",
        "https://example.com/api/products?id=123",
        "https://example.com/documentation/payment-api.html"
    ]
    website_text = [
        "Welcome to our API. Use your API key to authenticate.",
        "Explore our REST API for user management.",
        "GraphQL endpoint available at /graphql. See swagger docs.",
        "OpenAPI specification can be found here.",
        "This text does not have keywords."
    ]
    website_patterns = recognizer.recognize_from_website_data(website_urls, website_text)
    print(json.dumps(website_patterns, indent=2))