from typing import Optional, List, Tuple as TypingTuple, Union

class Element:
    def __init__(self):
        self.id: Optional[int] = None
        self.ids: List[int] = []
        self.tags: List[TypingTuple[str, str]] = []
        self.tag_conditions: List[str] = []
        self.if_conditions: List[str] = []
        self.pivot_set: Optional[str] = None
        self.filter_from_set: Optional[str] = None
        self._store_as_set_name: Optional[str] = None

    def with_id(self, id: int) -> 'Element':
        """Set a single ID for the element."""
        if not isinstance(id, int):
            raise TypeError("id must be of type int")
        if id < 0:
            raise ValueError("id must be a non-negative integer")
        if self.ids:
            raise ValueError("Cannot set id, field ids is already set. Choose one or the other")
        self.id = id
        return self

    def with_ids(self, ids: List[int]) -> 'Element':
        """Set multiple IDs for the element."""
        if not isinstance(ids, list):
            raise TypeError("ids must be of type list")
        if not ids:
            raise ValueError("ids list cannot be empty")
        for id in ids:
            if not isinstance(id, int):
                raise TypeError("All values in ids must be of type int")
            if id < 0:
                raise ValueError("All values in ids must be non-negative integers")
        if self.id is not None:
            raise ValueError("Cannot set ids, field id is already set. Choose one or the other")
        self.ids = ids
        return self

    def with_tags(self, tags: List[TypingTuple[str, str]]) -> 'Element':
        """Set tags for the element."""
        if not isinstance(tags, list):
            raise TypeError("tags must be of type list")
        for tag in tags:
            if not isinstance(tag, tuple):
                raise TypeError("Each tag in tags must be of type tuple")
            if len(tag) != 2:
                raise ValueError("Each tag in tags must be a tuple of length 2")
            for el in tag:
                if not isinstance(el, str):
                    raise TypeError("Tag key and value must be of type str")
        self.tags = tags
        return self

    def _update_or_append_tag(self, key: str, value: str) -> None:
        """Helper method to update an existing tag or append a new one, normalizing keys with '!' prefix."""
        # Normalize the key by stripping the '!' prefix for comparison
        normalized_key = key.lstrip("!")
        for i, (existing_key, _) in enumerate(self.tags):
            # Normalize the existing key as well
            normalized_existing_key = existing_key.lstrip("!")
            if normalized_existing_key == normalized_key:
                self.tags[i] = (key, value)
                return
        self.tags.append((key, value))

    def with_tag_exists(self, key: str) -> 'Element':
        """Filter elements where a tag key exists (e.g., '[key]')."""
        if not isinstance(key, str):
            raise TypeError("key must be of type str")
        if not key.strip():
            raise ValueError("key cannot be empty or whitespace")
        self._update_or_append_tag(key, "")  # Empty value indicates existence check
        return self

    def with_tag_not_exists(self, key: str) -> 'Element':
        """Filter elements where a tag key does not exist (e.g., '[!key]')."""
        if not isinstance(key, str):
            raise TypeError("key must be of type str")
        if not key.strip():
            raise ValueError("key cannot be empty or whitespace")
        self._update_or_append_tag(f"!{key}", "")  # !key with empty value
        return self

    def with_tag_not(self, key: str, value: str) -> 'Element':
        """Filter elements where a tag does not equal a value (e.g., '[key!=value]')."""
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("key and value must be of type str")
        if not key.strip() or not value.strip():
            raise ValueError("key and value cannot be empty or whitespace")
        self._update_or_append_tag(key, f"!={value}")
        return self

    def with_tag_regex(self, key: str, regex: str) -> 'Element':
        """Filter elements where a tag matches a regex (e.g., '[key~regex]')."""
        if not isinstance(key, str) or not isinstance(regex, str):
            raise TypeError("key and regex must be of type str")
        if not key.strip() or not regex.strip():
            raise ValueError("key and regex cannot be empty or whitespace")
        self._update_or_append_tag(key, f"~{regex}")
        return self

    def with_tag_condition(self, condition: str) -> 'Element':
        """Add a custom tag condition (e.g., '["highway"~"^(primary|secondary)$"]')."""
        if not isinstance(condition, str):
            raise TypeError("condition must be of type str")
        self.validate_tag_condition(condition)
        self.tag_conditions.append(condition)
        return self

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

    def from_set(self, set_name: str) -> 'Element':
        """Filter elements from a previously defined set (e.g., '.set_name element;')."""
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError("set_name contains invalid characters for Overpass QL")
        self.filter_from_set = set_name
        return self

    def store_as_set(self, set_name: str) -> 'Element':
        """Store the result of this query as a named set (e.g., '->.set_name')."""
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError("set_name contains invalid characters for Overpass QL")
        self._store_as_set_name = set_name
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