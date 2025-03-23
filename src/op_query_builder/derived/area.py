from typing import Optional, List, Tuple as TypingTuple, Union as TypingUnion
from op_query_builder.elements.base import Element

class Area(Element):
    def __init__(self) -> None:
        super().__init__()

    def with_id(self, id: int) -> 'Area':
        """Set a single ID for the area.

        Args:
            id (int): The area ID, typically derived from OSM way/relation IDs by adding 2400000000.

        Returns:
            Area: Self, for method chaining.

        Raises:
            TypeError: If id is not an integer.
            ValueError: If id is negative, less than 2400000000, or a pivot set is already set.
        """
        if not isinstance(id, int):
            raise TypeError(f"id must be an integer, got {type(id).__name__}")
        if id < 0:
            raise ValueError(f"id must be a non-negative integer, got {id}")
        if id < 2400000000:
            raise ValueError(f"Area IDs in Overpass QL are typically derived from OSM way/relation IDs by adding 2400000000, e.g., 2400000001, got {id}")
        if self.pivot_set is not None:
            raise ValueError("Cannot set id because a pivot set is already set. Use either with_id() or with_pivot(), not both.")
        self.id = id
        return self

    def with_pivot(self, set_name: str) -> 'Area':
        """Filter areas using a pivot set (e.g., 'pivot.set_name').

        Args:
            set_name (str): The name of the set to use as a pivot.

        Returns:
            Area: Self, for method chaining.

        Raises:
            TypeError: If set_name is not a string.
            ValueError: If set_name is empty, contains invalid characters, or an id is already set.
        """
        if self.id is not None:
            raise ValueError("Cannot set pivot because an id is already set. Use either with_id() or with_pivot(), not both.")
        # Call the parent class's with_pivot for common validation
        super().with_pivot(set_name)
        return self

    def with_boundary(self, boundary: str) -> 'Area':
        """Filter areas by a specific boundary type (e.g., '[boundary=administrative]').

        Args:
            boundary (str): The boundary type to filter by (e.g., 'administrative', 'political').

        Returns:
            Area: Self, for method chaining.

        Raises:
            TypeError: If boundary is not a string.
            ValueError: If boundary is empty or whitespace.
        """
        if not isinstance(boundary, str):
            raise TypeError(f"boundary must be a string, got {type(boundary).__name__}")
        if not boundary.strip():
            raise ValueError("boundary cannot be empty or whitespace")
        self._update_or_append_tag("boundary", boundary)
        return self

    def with_name(self, name: str) -> 'Area':
        """Filter areas by a specific name (e.g., '[name=Berlin]').

        Args:
            name (str): The name of the area to filter by.

        Returns:
            Area: Self, for method chaining.

        Raises:
            TypeError: If name is not a string.
            ValueError: If name is empty or whitespace.
        """
        if not isinstance(name, str):
            raise TypeError(f"name must be a string, got {type(name).__name__}")
        if not name.strip():
            raise ValueError("name cannot be empty or whitespace")
        self._update_or_append_tag("name", name)
        return self

    def __str__(self) -> str:
        """Generate the Overpass QL query string for this Area object.

        Returns:
            str: The Overpass QL query string.
        """
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