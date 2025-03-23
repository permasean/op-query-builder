from typing import Optional, List, Tuple as TypingTuple, Union as TypingUnion
from op_query_builder.elements.base import Element

class Area(Element):
    def __init__(self) -> None:
        super().__init__()

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