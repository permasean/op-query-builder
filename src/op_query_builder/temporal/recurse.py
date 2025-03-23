from typing import Optional

class Recurse:
    def __init__(self, direction: str, set_name: Optional[str] = None) -> None:
        """Initialize a Recurse statement for deep recursion in Overpass QL (e.g., '>>' or '<<').

        Args:
            direction (str): The direction of recursion ('>>' for downward, '<<' for upward).
            set_name (Optional[str]): The name of the set to recurse from. Defaults to None.

        Raises:
            ValueError: If direction is invalid, or if set_name is empty or contains invalid characters.
            TypeError: If set_name is not a string.
        """
        self.direction = direction
        self.set_name = set_name
        self._validate()

    def _validate(self) -> None:
        """Validate the Recurse statement parameters.

        Raises:
            ValueError: If direction is invalid, or if set_name is empty or contains invalid characters.
            TypeError: If set_name is not a string.
        """
        valid_directions = ['>>', '<<']
        if self.direction not in valid_directions:
            raise ValueError(f"Direction must be one of {valid_directions}, got {self.direction}")
        if self.set_name is not None:
            if not isinstance(self.set_name, str):
                raise TypeError(f"set_name must be a string, got {type(self.set_name).__name__}")
            if not self.set_name.strip():
                raise ValueError("set_name cannot be empty or whitespace")
            if any(char in self.set_name for char in '[]{}();'):
                raise ValueError(f"set_name contains invalid characters for Overpass QL: {self.set_name}. Avoid using [], {{}}, (), or ;.")

    def __str__(self) -> str:
        """Generate the Overpass QL query string for this Recurse statement.

        Returns:
            str: The Overpass QL query string.
        """
        if self.set_name:
            return f".{self.set_name} {self.direction};"
        return f"{self.direction};"