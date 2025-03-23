from typing import Optional

class Recurse:
    def __init__(self, direction: str, set_name: Optional[str] = None) -> None:
        self.direction = direction
        self.set_name = set_name
        self._validate()

    def _validate(self) -> None:
        valid_directions = ['>>', '<<']
        if self.direction not in valid_directions:
            raise ValueError(f"Direction must be one of {valid_directions}, got {self.direction}")
        if self.set_name is not None:
            if not isinstance(self.set_name, str):
                raise TypeError("set_name must be of type str")
            if not self.set_name.strip():
                raise ValueError("set_name cannot be empty or whitespace")
            if any(char in self.set_name for char in '[]{}();'):
                raise ValueError("set_name contains invalid characters for Overpass QL")

    def __str__(self) -> str:
        if self.set_name:
            return f".{self.set_name} {self.direction};"
        return f"{self.direction};"