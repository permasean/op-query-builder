from typing import Optional, List, Tuple as TypingTuple

class Element:
    def __init__(self):
        self.tag_conditions: List[str] = []
        self.if_conditions: List[str] = []  # New list for if conditions
        self.pivot_set: Optional[str] = None  # For pivot.set_name

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

    def _append_if_conditions(self, query: str) -> str:
        """Helper method to append if conditions to the query string."""
        for condition in self.if_conditions:
            query += f"[if:{condition}]"
        return query