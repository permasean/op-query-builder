from typing import Optional, List, Tuple as TypingTuple, Union as TypingUnion
from op_query_builder.elements.base import Element

class Area(Element):
    def __init__(self) -> None:
        super().__init__()
        self.id: Optional[int] = None
        self.tags: List[TypingTuple[str, str]] = []
        self._store_as_set_name: Optional[str] = None
        self.filter_from_set: Optional[str] = None

    def with_id(self, id: int) -> 'Area':
        if not isinstance(id, int):
            raise TypeError("id must be of type int")
        if id < 0:
            raise ValueError("id must be a non-negative integer")
        if id < 2400000000:
            raise ValueError("Area IDs in Overpass QL are typically derived from OSM way/relation IDs by adding 2400000000 (e.g., 2400000001)")
        if self.pivot_set is not None:
            raise ValueError("Cannot set id when a pivot set is already set")
        self.id = id
        return self

    def with_pivot(self, set_name: str) -> 'Area':
        """Filter areas using a pivot set (e.g., 'pivot.set_name')."""
        if self.id is not None:
            raise ValueError("Cannot set pivot when an id is already set")
        # Call the parent class's with_pivot for common validation
        super().with_pivot(set_name)
        return self

    def with_tags(self, tags: List[TypingTuple[str, str]]) -> 'Area':
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

    def with_boundary(self, boundary: str) -> 'Area':
        if not isinstance(boundary, str):
            raise TypeError("boundary must be of type str")
        if not boundary.strip():
            raise ValueError("boundary cannot be empty or whitespace")
        self._update_or_append_tag("boundary", boundary)
        return self

    def with_name(self, name: str) -> 'Area':
        if not isinstance(name, str):
            raise TypeError("name must be of type str")
        if not name.strip():
            raise ValueError("name cannot be empty or whitespace")
        self._update_or_append_tag("name", name)
        return self

    def from_set(self, set_name: str) -> 'Area':
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError("set_name contains invalid characters for Overpass QL")
        self.filter_from_set = set_name
        return self

    def with_tag_exists(self, key: str) -> 'Area':
        if not isinstance(key, str):
            raise TypeError("key must be of type str")
        if not key.strip():
            raise ValueError("key cannot be empty or whitespace")
        self._update_or_append_tag(key, "")
        return self

    def with_tag_not_exists(self, key: str) -> 'Area':
        if not isinstance(key, str):
            raise TypeError("key must be of type str")
        if not key.strip():
            raise ValueError("key cannot be empty or whitespace")
        self._update_or_append_tag(f"!{key}", "")
        return self

    def with_tag_not(self, key: str, value: str) -> 'Area':
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("key and value must be of type str")
        if not key.strip() or not value.strip():
            raise ValueError("key and value cannot be empty or whitespace")
        self._update_or_append_tag(key, f"!={value}")
        return self

    def with_tag_regex(self, key: str, regex: str) -> 'Area':
        if not isinstance(key, str) or not isinstance(regex, str):
            raise TypeError("key and regex must be of type str")
        if not key.strip() or not regex.strip():
            raise ValueError("key and regex cannot be empty or whitespace")
        self._update_or_append_tag(key, f"~{regex}")
        return self

    def with_tag_condition(self, condition: str) -> 'Area':
        if not isinstance(condition, str):
            raise TypeError("condition must be of type str")
        if not condition.strip():
            raise ValueError("condition cannot be empty or whitespace")
        if not condition.startswith('[') or not condition.endswith(']'):
            raise ValueError("condition must be formatted as a tag filter, e.g., '[key=value]'")
        self.tag_conditions.append(condition)
        return self

    def store_as_set(self, set_name: str) -> 'Area':
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError("set_name contains invalid characters for Overpass QL")
        self._store_as_set_name = set_name
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

    def __str__(self) -> str:
        query = ""
        if self.filter_from_set:
            query += f".{self.filter_from_set} "
        query += "area"
        if self.id is not None:
            query += f"({self.id})"
        if self.pivot_set:
            query += f"(pivot.{self.pivot_set})"
        for key, value in self.tags:
            if value == "":
                query += f"[{key}]"
            elif value.startswith("~"):
                query += f"[{key}{value}]"
            elif value.startswith("!="):
                query += f"[{key}{value}]"
            else:
                query += f"[{key}={value}]"
        for condition in self.tag_conditions:
            query += condition
        query = self._append_if_conditions(query)
        if self._store_as_set_name:
            query += f"->.{self._store_as_set_name}"
        query += ";"
        return query