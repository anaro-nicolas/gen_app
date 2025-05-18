import json
from jsonschema import validate, ValidationError
import argparse
import sys

class JSONValidator:
    """
    A class to validate if a JSON file follows the expected JSON schema using jsonschema.
    """
    
    def __init__(self, schema):
        self.schema = schema
    
    def validate(self, json_data):
        """
        Validates a JSON object against the expected schema.
        Returns a list of validation errors if any.
        """
        errors = []
        try:
            validate(instance=json_data, schema=self.schema)
        except ValidationError as e:
            errors.append(f"Validation Error: {e.message} at {list(e.absolute_path)}")
        
        return errors

# Expected JSON Schema Template
# The workflow name (e.g., "Qualify") will be provided at runtime.
def get_expected_json_schema(initial_workflow):
    return {
        "type": "object",
        "properties": {
            initial_workflow: {
                "type": "object",
                "properties": {
                    "tableMaster": {
                        "type": "object",
                        "properties": {
                            "table": {"type": "string"},
                            "where": {"type": "object"}
                        },
                        "required": ["table"]
                    },
                    "fields": {"type": "object"},
                    "tableSecondaire": {
                        "type": "object",
                        "properties": {
                            "table": {"type": "string"},
                            "relation": {"type": "string"},
                            "expander": {"type": "boolean"},
                            "count_field": {"type": "string"},
                            "fields": {"type": "object"}
                        },
                        "required": ["table", "relation"]
                    },
                    "next_step": {
                        "type": "object",
                        "properties": {
                            "step": {
                                "type": "object",
                                "properties": {
                                    "value": {"type": "integer"},
                                    "session_var": {"type": "string"}
                                },
                                "required": ["value"]
                            },
                            "entity_id": {"type": "object"},
                        }
                    },
                    "form-buttons": {
                        "type": "object",
                        "properties": {
                            "form_submit": {
                                "type": "object",
                                "properties": {"type": {"type": "string"}}
                            },
                            "label": {"type": "string"},
                        }
                    }
                },
                "required": ["tableMaster", "fields", "next_step", "form-buttons"]
            }
        },
        "required": [initial_workflow]
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate a JSON file against a predefined schema.")
    parser.add_argument(
        "-fp",
        required=True,
        help="Path to the JSON file to validate"
    )
    parser.add_argument(
        "-w",
        required=True,
        help="Workflow name to validate against"
    )

    # Check if required arguments are present, else exit with error
    if "-fp" not in sys.argv or "-w" not in sys.argv:
        print("❌ Error: Both --file-path and --workflow arguments are required.")
        sys.exit(1)
    args = parser.parse_args()
    initial_workflow = args.w

    EXPECTED_JSON_SCHEMA = get_expected_json_schema(initial_workflow)
    # Load JSON file
    with open(args.fp, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    
    validator = JSONValidator(EXPECTED_JSON_SCHEMA)
    errors = validator.validate(json_data)
    
    if errors:
        print("🚨 JSON structure does not match expected format. Issues found:")
        for error in errors:
            print(f"❌ {error}")
    else:
        print("✅ JSON structure is valid.")