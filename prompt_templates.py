SYSTEM_BASE = """
You are an API design assistant that follows REST best practices.
- Use noun resources, plural names (e.g., /employees).
- Suggest CRUD endpoints and any useful query parameters.
- Provide JSON-serializable structures. Do not return extraneous chat.
- When returning suggestions, use the EXACT JSON schema described in the instructions.

Always output JSON only when asked for machine-readable output.
"""

DRAFT_PROMPT = """
User request:
{user_req}

Produce a JSON object with:
- resources: list of resource names (strings)
- endpoints: list of objects with keys: method, path, description, requestBody (if any), responses (sample)
- schemas: map of schemaName -> JSON schema (properties, required)
Example response:
{{
  "resources": ["employees"],
  "endpoints": [
    {{
      "method":"GET",
      "path":"/employees",
      "description":"list employees",
      "requestBody": null,
      "responses": {{
        "200": "array of Employee"
      }}
    }}
  ],
  "schemas": {{
    "Employee": {{
      "type":"object",
      "properties": {{
        "id":{{"type":"string"}},
        "name":{{"type":"string"}}
      }},
      "required":["id","name"]
    }}
  }}
}}
"""
