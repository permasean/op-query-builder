from typing import Tuple as TypingTuple, Union as TypingUnion, Optional, List
from op_query_builder.elements.node import Node
from op_query_builder.elements.way import Way
from op_query_builder.elements.relation import Relation
from op_query_builder.elements.changeset import Changeset
from op_query_builder.derived.area import Area
from op_query_builder.temporal.adiff import Adiff
from op_query_builder.temporal.timeline import Timeline
from op_query_builder.temporal.diff import Diff
from op_query_builder.temporal.recurse import Recurse

class Query:
    def __init__(self):
        self.output: str = 'json'  # json, csv, or xml
        self.output_detail: Optional[str] = 'body'  # body, skel, geom, tags, meta, center, or None
        self.timeout: Optional[int] = None  # Timeout in seconds
        self.date: Optional[str] = None  # Date for historical queries (e.g., "2023-01-01T00:00:00Z")
        self.global_bbox: Optional[TypingTuple[float, float, float, float]] = None  # (min_lat, min_lon, max_lat, max_lon)
        self.statements: List[TypingUnion[Node, Way, Relation, Changeset, Area, 'Union', 'Difference', Adiff, Timeline, Diff, Recurse]] = []  # Combined list for all statements
        self.is_in_statements: List[TypingTuple[float, float, Optional[str]]] = []  # (lat, lon, set_name)
        self.foreach_statements: List[TypingTuple[str, 'Query']] = []  # (set_name, subquery)
        self.convert_statements: List[TypingTuple[str, str, List[str]]] = []  # (element_type, set_name, tags)
        self.sort_order: Optional[str] = None  # qt, asc, or desc
        self.limit: Optional[int] = None  # Limit the number of results
        self.output_mode: Optional[str] = None  # count, ids, or None
        self.settings: dict[str, str] = {}  # For arbitrary settings

    def with_output(self, output: str) -> 'Query':
        if output not in ['json', 'csv', 'xml']:
            raise ValueError("Invalid output type, must be 'json', 'csv', or 'xml'")
        self.output = output
        return self

    def with_output_detail(self, detail: Optional[str]) -> 'Query':
        if detail is not None:
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
        if not isinstance(date, str):
            raise TypeError(f"Date must be a string, got {type(date).__name__}")
        if not date.strip():
            raise ValueError("Date cannot be empty or whitespace")
        if 'T' not in date or 'Z' not in date:
            raise ValueError("Date must be in ISO 8601 format (e.g., '2023-01-01T00:00:00Z')")
        self.date = date
        return self

    def with_global_bbox(self, bbox: TypingTuple[float, float, float, float]) -> 'Query':
        self._validate_bbox(bbox)
        self.global_bbox = bbox
        return self

    def with_sort_order(self, sort_order: str) -> 'Query':
        """Set the sort order for the output (e.g., 'qt', 'asc', 'desc')."""
        valid_sort_orders = ['qt', 'asc', 'desc']
        if sort_order not in valid_sort_orders:
            raise ValueError(f"Sort order must be one of {valid_sort_orders}, got {sort_order}")
        self.sort_order = sort_order
        return self

    def with_limit(self, limit: int) -> 'Query':
        """Set a limit on the number of results returned."""
        if not isinstance(limit, int):
            raise TypeError(f"Limit must be an integer, got {type(limit).__name__}")
        if limit <= 0:
            raise ValueError("Limit must be a positive integer")
        self.limit = limit
        return self

    def with_output_mode(self, mode: Optional[str]) -> 'Query':
        """Set the output mode (e.g., 'count', 'ids')."""
        if mode is not None:
            valid_modes = ['count', 'ids']
            if mode not in valid_modes:
                raise ValueError(f"Output mode must be one of {valid_modes}, got {mode}")
        self.output_mode = mode
        return self

    def with_setting(self, key: str, value: str) -> 'Query':
        """Add a global setting (e.g., 'maxsize:1000000')."""
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("key and value must be of type str")
        if not key.strip():
            raise ValueError("key cannot be empty or whitespace")
        # Basic validation for common settings
        if key == "maxsize":
            try:
                int(value)
            except ValueError:
                raise ValueError("maxsize must be an integer")
        elif key == "diff":
            if 'T' not in value or 'Z' not in value:
                raise ValueError("diff must be in ISO 8601 format (e.g., '2023-01-01T00:00:00Z')")
        self.settings[key] = value
        return self

    def add_node(self, node: Node) -> 'Query':
        self.statements.append(node)
        return self

    def add_way(self, way: Way) -> 'Query':
        self.statements.append(way)
        return self

    def add_relation(self, relation: Relation) -> 'Query':
        self.statements.append(relation)
        return self

    def add_changeset(self, changeset: Changeset) -> 'Query':
        self.statements.append(changeset)
        return self

    def add_area(self, area: Area) -> 'Query':
        self.statements.append(area)
        return self

    def add_union(self, *elements: TypingUnion[Node, Way, Relation, Changeset, Area]) -> 'Query':
        if not elements:
            raise ValueError("At least one element must be provided for a union")
        union = Union(elements)
        self.statements.append(union)
        return self

    def add_difference(self, base: TypingUnion[Node, Way, Relation, Changeset, Area], *subtract: TypingUnion[Node, Way, Relation, Changeset, Area]) -> 'Query':
        if not subtract:
            raise ValueError("At least one element must be provided to subtract in a difference")
        difference = Difference(base, subtract)
        self.statements.append(difference)
        return self

    def add_adiff(self, adiff: Adiff) -> 'Query':
        self.statements.append(adiff)
        return self

    def add_timeline(self, timeline: Timeline) -> 'Query':
        self.statements.append(timeline)
        return self

    def add_diff(self, diff: Diff) -> 'Query':
        self.statements.append(diff)
        return self

    def add_recurse(self, recurse: Recurse) -> 'Query':
        self.statements.append(recurse)
        return self

    def add_is_in(self, lat: float, lon: float, set_name: Optional[str] = None) -> 'Query':
        """Add an 'is_in' statement to find areas containing the given point (e.g., 'is_in(51.5,-0.1)->.areas;')."""
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            raise TypeError("lat and lon must be int or float")
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ValueError("lat must be -90 to 90, lon must be -180 to 180")
        if set_name is not None:
            if not isinstance(set_name, str):
                raise TypeError("set_name must be of type str")
            if not set_name.strip():
                raise ValueError("set_name cannot be empty or whitespace")
            if any(char in set_name for char in '[]{}();'):
                raise ValueError("set_name contains invalid characters for Overpass QL")
        self.is_in_statements.append((lat, lon, set_name))
        return self

    def add_foreach(self, set_name: str, subquery: 'Query') -> 'Query':
        """Add a 'foreach' statement to iterate over elements in a set (e.g., '.set_name foreach { ... };')."""
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError("set_name contains invalid characters for Overpass QL")
        if not isinstance(subquery, Query):
            raise TypeError("subquery must be of type Query")
        # Ensure the subquery doesn't include its own output statement
        subquery.with_output_detail(None)
        self.foreach_statements.append((set_name, subquery))
        return self

    def add_convert(self, element_type: str, set_name: str, tags: List[str]) -> 'Query':
        """Add a 'convert' statement to transform elements (e.g., 'convert node ::id=way.id;')."""
        valid_types = ['node', 'way', 'relation']
        if element_type not in valid_types:
            raise ValueError(f"element_type must be one of {valid_types}")
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError("set_name contains invalid characters for Overpass QL")
        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            raise TypeError("tags must be a list of strings")
        self.convert_statements.append((element_type, set_name, tags))
        return self

    def print(self) -> None:
        print(self.__str__())

    def _validate_bbox(self, bbox: TypingTuple[float, float, float, float]) -> None:
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

    def _get_subquery_elements(self, subquery: 'Query') -> List[str]:
        """Extract only the element statements from a subquery, excluding global settings and output."""
        subquery_lines = str(subquery).split('\n')
        element_lines = []
        for line in subquery_lines:
            # Skip global settings (e.g., "[out:json];") and output (e.g., "out body;")
            if line.startswith('[') or line.startswith('out '):
                continue
            if line.strip():  # Skip empty lines
                element_lines.append(line.rstrip(';'))
        return element_lines

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
        for key, value in self.settings.items():
            if key in ["date", "timeout", "bbox", "out"]:  # Avoid duplicates
                continue
            if key in ["date", "diff"]:
                settings.append(f'{key}:"{value}"')
            else:
                settings.append(f"{key}:{value}")
        if settings:
            query_lines.append(f"[{' '.join(settings)}];")

        # Add is_in statements
        for lat, lon, set_name in self.is_in_statements:
            line = f"is_in({lat},{lon})"
            if set_name:
                line += f"->.{set_name}"
            query_lines.append(f"{line};")

        # Add all statements (elements and temporal) in order of addition
        for statement in self.statements:
            statement_str = str(statement)
            if statement_str.endswith(';'):
                statement_str = statement_str[:-1]
            query_lines.append(f"{statement_str};")

        # Add foreach statements
        for set_name, subquery in self.foreach_statements:
            subquery_elements = self._get_subquery_elements(subquery)
            if not subquery_elements:
                continue  # Skip empty subqueries
            query_lines.append(f".{set_name} foreach {{")
            for line in subquery_elements:
                query_lines.append(f"  {line};")
            query_lines.append("};")

        # Add convert statements
        for element_type, set_name, tags in self.convert_statements:
            tags_str = ", ".join(tags)
            line = f"convert {element_type} {tags_str}"
            if set_name:
                line += f"->.{set_name}"
            query_lines.append(f"{line};")

        # Add output statement with modifiers
        if self.output_mode == 'count':
            query_lines.append("out count;")
        elif self.output_mode == 'ids':
            query_lines.append("out ids;")
        elif self.output_detail is not None:
            out_parts = [f"out {self.output_detail}"]
            if self.sort_order:
                out_parts.append(self.sort_order)
            if self.limit is not None:
                out_parts.append(str(self.limit))
            query_lines.append(f"{' '.join(out_parts)};")

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