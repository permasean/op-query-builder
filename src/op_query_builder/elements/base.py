from typing import Optional, List, Tuple as TypingTuple

class Element:
    def __init__(self):
        self.tag_conditions: List[str] = []
        self.if_conditions: List[str] = []
        self.pivot_set: Optional[str] = None

    def with_if_condition(self, condition: str) -> 'Element':
        """Add an if condition to filter elements (e.g., 't[\"population\"] > 100000')."""
        if not isinstance(condition, str):
            raise TypeError("condition must be of type str")
        if not condition.strip():
            raise ValueError("condition cannot be empty or whitespace")
        self.if_conditions.append(condition)
        return self

    def with_pivot(self, set_name: str) -> 'Element':
        """Filter elements using a pivot set (e.g., 'pivot.set_name')."""
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError("set_name contains invalid characters")
        self.pivot_set = set_name
        return self

    def validate_tag_condition(self, condition: str) -> None:
        """Validate the syntax of a tag condition (e.g., '[key=value]')."""
        if not condition.strip():
            raise ValueError("condition cannot be empty or whitespace")
        if not condition.startswith('[') or not condition.endswith(']'):
            raise ValueError("condition must be formatted as a tag filter, e.g., '[key=value]'")
        # Remove the brackets and split on the operator
        inner = condition[1:-1].strip()
        if not inner:
            raise ValueError("Tag condition cannot be empty inside brackets")

        # Check for common operators: =, !=, ~, >, <, >=, <=
        operators = ['=', '!=', '~', '>', '<', '>=', '<=']
        operator_found = None
        for op in operators:
            if op in inner:
                operator_found = op
                break

        if operator_found is None:
            raise ValueError("Tag condition must contain a valid operator (e.g., '=', '!=', '~', '>', '<', '>=', '<=')")

        # Split on the operator to check key and value
        parts = inner.split(operator_found, 1)
        if len(parts) != 2:
            raise ValueError("Tag condition must have exactly one key and one value separated by an operator")

        key, value = parts
        key = key.strip()
        value = value.strip()

        if not key:
            raise ValueError("Tag key cannot be empty")
        if operator_found not in ['~', '>', '<', '>=', '<='] and not value:
            raise ValueError("Tag value cannot be empty for operators '=', '!='")

        # Check for quoted values when required
        if operator_found in ['=', '!=', '~']:
            if not (value.startswith('"') and value.endswith('"')):
                raise ValueError("Tag value must be quoted for operators '=', '!=', '~' (e.g., '[key=\"value\"]')")

    def _append_if_conditions(self, query: str) -> str:
        """Helper method to append if conditions to the query string."""
        for condition in self.if_conditions:
            query += f"[if:{condition}]"
        return query