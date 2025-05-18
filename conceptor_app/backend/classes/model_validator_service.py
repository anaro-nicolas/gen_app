import json
from jsonschema import validate, ValidationError

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


class ModelValidatorService:
    """
    Service class to handle JSON validation logic.
    """
    def __init__(self):
        pass

    @staticmethod
    def get_expected_json_schema(initial_workflow):
        """
        Returns the expected JSON schema based on the workflow name.
        """
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

    def validate_json(self, workflow_name, json_data):
        """
        Validates a JSON object against the schema for the given workflow.
        """
        schema = self.get_expected_json_schema(workflow_name)
        validator = JSONValidator(schema)
        return validator.validate(json_data)