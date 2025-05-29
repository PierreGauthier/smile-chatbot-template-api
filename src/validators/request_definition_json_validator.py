import jsonschema
from jsonschema.exceptions import ValidationError

class RequestDefinitionJsonValidator:
    @classmethod
    def is_valid(cls, json):
        print(json)
        schema = {
            "type": "object",
            "properties": {
                "subject": {"type": "string"},
                "ai_response": {"type": "string"}
            },
            "required": ["subject", "ai_response"],
            "additionalProperties": False
        }
        #validator = jsonschema.Draft202012Validator(schema=schema)
        #return validator.is_valid(instance=json)
        try:
            jsonschema.validate(instance=json, schema=schema, cls=jsonschema.Draft202012Validator)
            print("JSON validation successful.")
            return True
        except ValidationError as ve:
            print("Validation error:", ve.message)
            return False