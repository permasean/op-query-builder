from typing import Tuple, Union as TypingUnion, Optional, List, Tuple as TypingTuple
from op_query_builder.elements.node import Node
from op_query_builder.elements.way import Way
from op_query_builder.elements.relation import Relation
from op_query_builder.elements.changeset import Changeset
from op_query_builder.derived.area import Area

class Query:
    def __init__(self):
        self.output: str = 'json'  # json, csv, or xml
        self.output_detail: str = 'body'  # body, skel, geom, tags, meta, center
        self.timeout: Optional[int] = None  # Timeout in seconds
        self.date: Optional[str] = None  # Date for historical queries (e.g., "2023-01-01T00:00:00Z")
        self.global_bbox: Optional[Tuple[float, float, float, float]] = None  # (min_lat, min_lon, max_lat, max_lon)
        self.elements: List[TypingUnion[Node, Way, Relation, Changeset, Area, 'Union', 'Difference']] = []  # Order matters

    def with_output(self, output: str) -> 'Query':
        if output not in ['json', 'csv', 'xml']:
            raise ValueError("Invalid output type, must be 'json', 'csv', or 'xml'")
        self.output = output
        return self

    def with_output_detail(self, detail: str) -> 'Query':
        valid_details = ['body', 'skel', 'geom', 'tags', 'meta', 'center']
        if detail not in valid_details:
            raise ValueError(f"Invalid output_detail, must be one of {valid_details}")
        self.output_detail = detail
        return self

    def with_timeout(self, timeout: int) -> 'Query':
        if not isinstance(timeout, int):
            raise TypeError(f"Timeout must be an integer, got {type(timeout).__name__}")
        if timeout <= 0:
            raise ValueError("Timeout must be a positive integer")
        self.timeout = timeout
        return self

    def with_date(self, date: str) -> 'Query':
        """Set a date for historical queries (e.g., '[date:\"2023-01-01T00:00:00Z\"]')."""
        if not isinstance(date, str):
            raise TypeError(f"Date must be a string, got {type(date).__name__}")
        if not date.strip():
            raise ValueError("Date cannot be empty or whitespace")
        if 'T' not in date or 'Z' not in date:
            raise ValueError("Date must be in ISO 8601 format (e.g., '2023-01-01T00:00:00Z')")
        self.date = date
        return self

    def with_global_bbox(self, bbox: Tuple[float, float, float, float]) -> 'Query':
        self._validate_bbox(bbox)
        self.global_bbox = bbox
        return self

    def add_node(self, node: Node) -> 'Query':
        self.elements.append(node)
        return self

    def add_way(self, way: Way) -> 'Query':
        self.elements.append(way)
        return self

    def add_relation(self, relation: Relation) -> 'Query':
        self.elements.append(relation)
        return self

    def add_changeset(self, changeset: Changeset) -> 'Query':
        self.elements.append(changeset)
        return self

    def add_area(self, area: Area) -> 'Query':
        self.elements.append(area)
        return self

    def add_union(self, *elements: TypingUnion[Node, Way, Relation, Changeset, Area]) -> 'Query':
        """Add a union of elements (e.g., '(way[highway=primary]; way[highway=secondary];);')."""
        if not elements:
            raise ValueError("At least one element must be provided for a union")
        union = Union(elements)
        self.elements.append(union)
        return self

    def add_difference(self, base: TypingUnion[Node, Way, Relation, Changeset, Area], *subtract: TypingUnion[Node, Way, Relation, Changeset, Area]) -> 'Query':
        """Add a difference of elements (e.g., '(way[highway=primary]; - way[highway=secondary];);')."""
        if not subtract:
            raise ValueError("At least one element must be provided to subtract in a difference")
        difference = Difference(base, subtract)
        self.elements.append(difference)
        return self

    def print(self) -> None:
        print(self.__str__())

    def _validate_bbox(self, bbox: Tuple[float, float, float, float]) -> None:
        if not isinstance(bbox, tuple):
            raise TypeError(f"Expected a tuple, got {type(bbox).__name__}")
        if len(bbox) != 4:
            raise ValueError(f"Bounding box must have exactly 4 values, got {len(bbox)}")
        for i, value in enumerate(bbox):
            if not isinstance(value, (float, int)):
                raise TypeError(f"Element {i} must be a float or int, got {type(value).__name__}")
        min_lat, min_lon, max_lat, max_lon = bbox
        if not (-90 <= min_lat <= max_lat <= 90):
            raise ValueError("Latitude must be between -90 and 90, with min <= max")
        if not (-180 <= min_lon <= max_lon <= 180):
            raise ValueError("Longitude must be between -180 and 180, with min <= max")

    def __str__(self) -> str:
        # Build the Overpass QL query string
        query_lines = []

        # Add global settings
        settings = []
        if self.output:
            settings.append(f"out:{self.output}")
        if self.timeout is not None:
            settings.append(f"timeout:{self.timeout}")
        if self.date is not None:
            settings.append(f'date:"{self.date}"')
        if self.global_bbox:
            bbox_str = ",".join(map(str, self.global_bbox))
            settings.append(f"bbox:{bbox_str}")
        if settings:
            query_lines.append(f"[{' '.join(settings)}];")

        # Add elements
        for element in self.elements:
            element_str = str(element)
            # Remove trailing semicolon from element if present, as we'll add it consistently
            if element_str.endswith(';'):
                element_str = element_str[:-1]
            query_lines.append(f"{element_str};")

        # Add output detail
        if self.output_detail:
            query_lines.append(f"out {self.output_detail};")

        return "\n".join(query_lines)

class Union:
    def __init__(self, elements: TypingTuple[TypingUnion[Node, Way, Relation, Changeset, Area], ...]):
        self.elements = elements

    def __str__(self) -> str:
        element_strs = [str(element).rstrip(';') for element in self.elements]
        return f"({' '.join(f'{s};' for s in element_strs)});"

class Difference:
    def __init__(self, base: TypingUnion[Node, Way, Relation, Changeset, Area], subtract: TypingTuple[TypingUnion[Node, Way, Relation, Changeset, Area], ...]):
        self.base = base
        self.subtract = subtract

    def __str__(self) -> str:
        base_str = str(self.base).rstrip(';')
        subtract_strs = [str(element).rstrip(';') for element in self.subtract]
        subtract_part = ' '.join(f'- {s};' for s in subtract_strs)
        return f"({base_str}; {subtract_part});"