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
        self.statements: List[TypingUnion[Node, Way, Relation, Changeset, Area, 'Union', 'Difference', Adiff, Timeline, Diff, Recurse, str]] = []  # Combined list for all statements
        self.is_in_statements: List[TypingTuple[float, float, Optional[str]]] = []  # (lat, lon, set_name)
        self.foreach_statements: List[TypingTuple[str, 'Query']] = []  # (set_name, subquery)
        self.convert_statements: List[TypingTuple[str, str, List[str]]] = []  # (element_type, set_name, tags)
        self.sort_order: Optional[str] = None  # qt, asc, or desc
        self.limit: Optional[int] = None  # Limit the number of results
        self.output_mode: Optional[str] = None  # count, ids, or None
        self.settings: dict[str, str] = {}  # For arbitrary settings

    def with_output(self, output: str) -> 'Query':
        """Set the output format for the query (e.g., 'json', 'csv', 'xml').

        Args:
            output (str): The desired output format.

        Returns:
            Query: Self, for method chaining.

        Raises:
            ValueError: If output is not one of 'json', 'csv', or 'xml'.
        """
        if output not in ['json', 'csv', 'xml']:
            raise ValueError(f"Invalid output type, must be one of 'json', 'csv', or 'xml', got {output}")
        self.output = output
        return self

    def with_output_detail(self, detail: Optional[str]) -> 'Query':
        """Set the level of detail for the output (e.g., 'body', 'skel', 'geom').

        Args:
            detail (Optional[str]): The output detail level. Can be None to disable.

        Returns:
            Query: Self, for method chaining.

        Raises:
            ValueError: If detail is not one of the valid options.
        """
        if detail is not None:
            valid_details = ['body', 'skel', 'geom', 'tags', 'meta', 'center']
            if detail not in valid_details:
                raise ValueError(f"Invalid output_detail, must be one of {valid_details}, got {detail}")
        self.output_detail = detail
        return self

    def with_timeout(self, timeout: int) -> 'Query':
        """Set the timeout for the query in seconds.

        Args:
            timeout (int): The timeout value in seconds.

        Returns:
            Query: Self, for method chaining.

        Raises:
            TypeError: If timeout is not an integer.
            ValueError: If timeout is not a positive integer.
        """
        if not isinstance(timeout, int):
            raise TypeError(f"Timeout must be an integer, got {type(timeout).__name__}")
        if timeout <= 0:
            raise ValueError(f"Timeout must be a positive integer, got {timeout}")
        self.timeout = timeout
        return self

    def with_date(self, date: str) -> 'Query':
        """Set a historical date for the query (e.g., '2023-01-01T00:00:00Z').

        Args:
            date (str): The date in ISO 8601 format.

        Returns:
            Query: Self, for method chaining.

        Raises:
            TypeError: If date is not a string.
            ValueError: If date is empty or not in ISO 8601 format.
        """
        if not isinstance(date, str):
            raise TypeError(f"Date must be a string, got {type(date).__name__}")
        if not date.strip():
            raise ValueError("Date cannot be empty or whitespace")
        if 'T' not in date or 'Z' not in date:
            raise ValueError(f"Date must be in ISO 8601 format, e.g., '2023-01-01T00:00:00Z', got {date}")
        self.date = date
        return self

    def with_global_bbox(self, bbox: TypingTuple[float, float, float, float]) -> 'Query':
        """Set a global bounding box for the query (e.g., (51.0, -0.2, 51.1, -0.1)).

        Args:
            bbox (Tuple[float, float, float, float]): A tuple of (south, west, north, east) coordinates.

        Returns:
            Query: Self, for method chaining.

        Raises:
            TypeError: If bbox is not a tuple or values are not numbers.
            ValueError: If bbox does not have exactly 4 values or coordinates are invalid.
        """
        self._validate_bbox(bbox)
        self.global_bbox = bbox
        return self

    def with_sort_order(self, sort_order: str) -> 'Query':
        """Set the sort order for the output (e.g., 'qt', 'asc', 'desc').

        Args:
            sort_order (str): The sort order to apply.

        Returns:
            Query: Self, for method chaining.

        Raises:
            ValueError: If sort_order is not one of 'qt', 'asc', or 'desc'.
        """
        valid_sort_orders = ['qt', 'asc', 'desc']
        if sort_order not in valid_sort_orders:
            raise ValueError(f"Sort order must be one of {valid_sort_orders}, got {sort_order}")
        self.sort_order = sort_order
        return self

    def with_limit(self, limit: int) -> 'Query':
        """Set a limit on the number of results returned.

        Args:
            limit (int): The maximum number of results to return.

        Returns:
            Query: Self, for method chaining.

        Raises:
            TypeError: If limit is not an integer.
            ValueError: If limit is not a positive integer.
        """
        if not isinstance(limit, int):
            raise TypeError(f"Limit must be an integer, got {type(limit).__name__}")
        if limit <= 0:
            raise ValueError(f"Limit must be a positive integer, got {limit}")
        self.limit = limit
        return self

    def with_output_mode(self, mode: Optional[str]) -> 'Query':
        """Set the output mode (e.g., 'count', 'ids').

        Args:
            mode (Optional[str]): The output mode. Can be None to disable.

        Returns:
            Query: Self, for method chaining.

        Raises:
            ValueError: If mode is not one of 'count' or 'ids'.
        """
        if mode is not None:
            valid_modes = ['count', 'ids']
            if mode not in valid_modes:
                raise ValueError(f"Output mode must be one of {valid_modes}, got {mode}")
        self.output_mode = mode
        return self

    def with_setting(self, key: str, value: str) -> 'Query':
        """Add a global setting (e.g., 'maxsize:1000000').

        Args:
            key (str): The setting key (e.g., 'maxsize', 'diff').
            value (str): The setting value.

        Returns:
            Query: Self, for method chaining.

        Raises:
            TypeError: If key or value is not a string.
            ValueError: If key is empty, or if the value is invalid for the given key.
        """
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError(f"key and value must be strings, got key={type(key).__name__}, value={type(value).__name__}")
        if not key.strip():
            raise ValueError("key cannot be empty or whitespace")
        # Basic validation for common settings
        if key == "maxsize":
            try:
                int(value)
            except ValueError:
                raise ValueError(f"maxsize must be an integer, got {value}")
        elif key == "diff":
            if 'T' not in value or 'Z' not in value:
                raise ValueError(f"diff must be in ISO 8601 format, e.g., '2023-01-01T00:00:00Z', got {value}")
        self.settings[key] = value
        return self

    def add_node(self, node: Node) -> 'Query':
        """Add a Node element to the query.

        Args:
            node (Node): The Node element to add.

        Returns:
            Query: Self, for method chaining.
        """
        self.statements.append(node)
        return self

    def add_way(self, way: Way) -> 'Query':
        """Add a Way element to the query.

        Args:
            way (Way): The Way element to add.

        Returns:
            Query: Self, for method chaining.
        """
        self.statements.append(way)
        return self

    def add_relation(self, relation: Relation) -> 'Query':
        """Add a Relation element to the query.

        Args:
            relation (Relation): The Relation element to add.

        Returns:
            Query: Self, for method chaining.
        """
        self.statements.append(relation)
        return self

    def add_changeset(self, changeset: Changeset) -> 'Query':
        """Add a Changeset element to the query.

        Args:
            changeset (Changeset): The Changeset element to add.

        Returns:
            Query: Self, for method chaining.
        """
        self.statements.append(changeset)
        return self

    def add_area(self, area: Area) -> 'Query':
        """Add an Area element to the query.

        Args:
            area (Area): The Area element to add.

        Returns:
            Query: Self, for method chaining.
        """
        self.statements.append(area)
        return self

    def add_union(self, *elements: TypingUnion[Node, Way, Relation, Changeset, Area]) -> 'Query':
        """Add a union of elements to the query (e.g., '(node[amenity=restaurant]; way[highway=primary];)').

        Args:
            *elements (Union[Node, Way, Relation, Changeset, Area]): The elements to union.

        Returns:
            Query: Self, for method chaining.

        Raises:
            ValueError: If no elements are provided.
        """
        if not elements:
            raise ValueError("At least one element must be provided for a union. Provide at least one Node, Way, Relation, Changeset, or Area.")
        union = Union(elements)
        self.statements.append(union)
        return self

    def add_difference(self, base: TypingUnion[Node, Way, Relation, Changeset, Area], *subtract: TypingUnion[Node, Way, Relation, Changeset, Area]) -> 'Query':
        """Add a difference operation to the query (e.g., '(node[amenity=restaurant]; - node[access=customers];)').

        Args:
            base (Union[Node, Way, Relation, Changeset, Area]): The base element.
            *subtract (Union[Node, Way, Relation, Changeset, Area]): The elements to subtract from the base.

        Returns:
            Query: Self, for method chaining.

        Raises:
            ValueError: If no elements are provided to subtract.
        """
        if not subtract:
            raise ValueError("At least one element must be provided to subtract in a difference. Provide at least one Node, Way, Relation, Changeset, or Area to subtract.")
        difference = Difference(base, subtract)
        self.statements.append(difference)
        return self

    def add_adiff(self, adiff: Adiff) -> 'Query':
        """Add an Adiff temporal statement to the query.

        Args:
            adiff (Adiff): The Adiff statement to add.

        Returns:
            Query: Self, for method chaining.
        """
        self.statements.append(adiff)
        return self

    def add_timeline(self, timeline: Timeline) -> 'Query':
        """Add a Timeline temporal statement to the query.

        Args:
            timeline (Timeline): The Timeline statement to add.

        Returns:
            Query: Self, for method chaining.
        """
        self.statements.append(timeline)
        return self

    def add_diff(self, diff: Diff) -> 'Query':
        """Add a Diff temporal statement to the query.

        Args:
            diff (Diff): The Diff statement to add.

        Returns:
            Query: Self, for method chaining.
        """
        self.statements.append(diff)
        return self

    def add_recurse(self, recurse: Recurse) -> 'Query':
        """Add a Recurse temporal statement to the query.

        Args:
            recurse (Recurse): The Recurse statement to add.

        Returns:
            Query: Self, for method chaining.
        """
        self.statements.append(recurse)
        return self

    def add_is_in(self, lat: float, lon: float, set_name: Optional[str] = None) -> 'Query':
        """Add an 'is_in' statement to find areas containing the given point (e.g., 'is_in(51.5,-0.1)->.areas;').

        Args:
            lat (float): The latitude of the point.
            lon (float): The longitude of the point.
            set_name (Optional[str]): The name of the set to store the result in. Defaults to None.

        Returns:
            Query: Self, for method chaining.

        Raises:
            TypeError: If lat or lon is not a number, or set_name is not a string.
            ValueError: If lat/lon are out of range or set_name contains invalid characters.
        """
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            raise TypeError(f"lat and lon must be numbers (int or float), got lat={type(lat).__name__}, lon={type(lon).__name__}")
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ValueError(f"lat must be between -90 and 90, lon between -180 and 180, got lat={lat}, lon={lon}")
        if set_name is not None:
            if not isinstance(set_name, str):
                raise TypeError(f"set_name must be a string, got {type(set_name).__name__}")
            if not set_name.strip():
                raise ValueError("set_name cannot be empty or whitespace")
            if any(char in set_name for char in '[]{}();'):
                raise ValueError(f"set_name contains invalid characters for Overpass QL: {set_name}. Avoid using [], {{}}, (), or ;.")
        self.is_in_statements.append((lat, lon, set_name))
        return self

    def add_foreach(self, set_name: str, subquery: 'Query') -> 'Query':
        """Add a 'foreach' statement to iterate over elements in a set (e.g., '.set_name foreach { ... };').

        Args:
            set_name (str): The name of the set to iterate over.
            subquery (Query): The subquery to execute for each element in the set.

        Returns:
            Query: Self, for method chaining.

        Raises:
            TypeError: If set_name is not a string or subquery is not a Query.
            ValueError: If set_name is empty or contains invalid characters.
        """
        if not isinstance(set_name, str):
            raise TypeError(f"set_name must be a string, got {type(set_name).__name__}")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError(f"set_name contains invalid characters for Overpass QL: {set_name}. Avoid using [], {{}}, (), or ;.")
        if not isinstance(subquery, Query):
            raise TypeError(f"subquery must be a Query object, got {type(subquery).__name__}")
        # Ensure the subquery doesn't include its own output statement
        subquery.with_output_detail(None)
        self.foreach_statements.append((set_name, subquery))
        return self

    def add_convert(self, element_type: str, set_name: str, tags: List[str]) -> 'Query':
        """Add a 'convert' statement to transform elements (e.g., 'convert node ::id=way.id;').

        Args:
            element_type (str): The type of element to convert to ('node', 'way', 'relation').
            set_name (str): The name of the set to store the converted elements in.
            tags (List[str]): The tags to apply during conversion.

        Returns:
            Query: Self, for method chaining.

        Raises:
            ValueError: If element_type is invalid or set_name contains invalid characters.
            TypeError: If element_type or set_name is not a string, or tags is not a list of strings.
        """
        valid_types = ['node', 'way', 'relation']
        if element_type not in valid_types:
            raise ValueError(f"element_type must be one of {valid_types}, got {element_type}")
        if not isinstance(set_name, str):
            raise TypeError(f"set_name must be a string, got {type(set_name).__name__}")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError(f"set_name contains invalid characters for Overpass QL: {set_name}. Avoid using [], {{}}, (), or ;.")
        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            raise TypeError("tags must be a list of strings")
        self.convert_statements.append((element_type, set_name, tags))
        return self

    def add_raw(self, raw_statement: str) -> 'Query':
        """Add a raw Overpass QL statement to the query.

        Args:
            raw_statement (str): The raw Overpass QL statement to add (e.g., 'node[amenity=park];').

        Returns:
            Query: Self, for method chaining.

        Raises:
            TypeError: If raw_statement is not a string.
            ValueError: If raw_statement is empty or does not end with a semicolon.
        """
        if not isinstance(raw_statement, str):
            raise TypeError(f"raw_statement must be a string, got {type(raw_statement).__name__}")
        if not raw_statement.strip():
            raise ValueError("raw_statement cannot be empty or whitespace")
        if not raw_statement.strip().endswith(';'):
            raise ValueError(f"raw_statement must end with a semicolon for valid Overpass QL syntax, got {raw_statement}")
        self.statements.append(raw_statement)
        return self

    def union_with(self, other: 'Query') -> 'Query':
        """Combine this query with another query using a union operation.

        Args:
            other (Query): The other query to union with.

        Returns:
            Query: Self, for method chaining.

        Raises:
            TypeError: If other is not a Query object.
        """
        if not isinstance(other, Query):
            raise TypeError(f"other must be a Query object, got {type(other).__name__}")
        # Extract statements from the other query and add them as a union
        if other.statements:
            self.statements.append(Union(tuple(other.statements)))
        return self

    def difference_with(self, other: 'Query') -> 'Query':
        """Combine this query with another query using a difference operation.

        Args:
            other (Query): The other query to subtract from this query.

        Returns:
            Query: Self, for method chaining.

        Raises:
            TypeError: If other is not a Query object.
            ValueError: If this query or the other query has no statements.
        """
        if not isinstance(other, Query):
            raise TypeError(f"other must be a Query object, got {type(other).__name__}")
        if not self.statements:
            raise ValueError("Cannot perform a difference operation because this query has no statements. Add at least one statement to this query first.")
        if not other.statements:
            raise ValueError("Cannot perform a difference operation because the other query has no statements. Add at least one statement to the other query first.")
        # Use the first statement of this query as the base and subtract the other query's statements
        base = self.statements[0]
        subtract = tuple(other.statements)
        difference = Difference(base, subtract)
        self.statements = self.statements[1:]  # Remove the base statement
        self.statements.insert(0, difference)  # Add the difference as the first statement
        return self

    def print(self) -> None:
        """Print the Overpass QL query string to the console."""
        print(self.__str__())

    def _validate_bbox(self, bbox: TypingTuple[float, float, float, float]) -> None:
        """Validate the bounding box coordinates.

        Args:
            bbox (Tuple[float, float, float, float]): The bounding box to validate.

        Raises:
            TypeError: If bbox is not a tuple or values are not numbers.
            ValueError: If bbox does not have exactly 4 values or coordinates are invalid.
        """
        if not isinstance(bbox, tuple):
            raise TypeError(f"Expected a tuple for bbox, got {type(bbox).__name__}")
        if len(bbox) != 4:
            raise ValueError(f"Bounding box must have exactly 4 values (south, west, north, east), got {len(bbox)} values: {bbox}")
        for i, value in enumerate(bbox):
            if not isinstance(value, (float, int)):
                raise TypeError(f"Element {i} of bbox must be a float or int, got {value} of type {type(value).__name__}")
        min_lat, min_lon, max_lat, max_lon = bbox
        if not (-90 <= min_lat <= max_lat <= 90):
            raise ValueError(f"Latitude must be between -90 and 90, with min_lat <= max_lat, got min_lat={min_lat}, max_lat={max_lat}")
        if not (-180 <= min_lon <= max_lon <= 180):
            raise ValueError(f"Longitude must be between -180 and 180, with min_lon <= max_lon, got min_lon={min_lon}, max_lon={max_lon}")

    def _validate_query(self) -> None:
        """Validate the query for common Overpass QL syntax errors.

        Raises:
            ValueError: If the query has invalid output mode combinations.
        """
        # Check for invalid output mode combinations
        if self.output_mode in ['count', 'ids']:
            if self.sort_order:
                raise ValueError(f"Cannot use sort_order with output_mode '{self.output_mode}'. Sort order (qt, asc, desc) is not supported with count or ids output modes.")
            if self.limit:
                raise ValueError(f"Cannot use limit with output_mode '{self.output_mode}'. Limit is not supported with count or ids output modes.")
            if self.output_detail and self.output_detail != 'body':
                raise ValueError(f"Cannot use output_detail '{self.output_detail}' with output_mode '{self.output_mode}'. Only 'body' is supported with count or ids output modes.")

    def _get_subquery_elements(self, subquery: 'Query') -> List[str]:
        """Extract only the element statements from a subquery, excluding global settings and output.

        Args:
            subquery (Query): The subquery to extract elements from.

        Returns:
            List[str]: A list of element statements.
        """
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
        """Generate the Overpass QL query string for this Query object.

        Returns:
            str: The Overpass QL query string.

        Raises:
            ValueError: If the query is invalid (e.g., no statements, invalid output mode combinations).
        """
        # Validate the query before generating the string
        self._validate_query()

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

        # Add all statements (elements, temporal, and raw) in order of addition
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

        # If no statements were added, return a minimal query with just the settings and output
        if not query_lines:
            query_lines.append("[out:json];")
            query_lines.append("out body;")

        return "\n".join(query_lines)

class Union:
    def __init__(self, elements: TypingTuple[TypingUnion[Node, Way, Relation, Changeset, Area], ...]):
        self.elements = elements

    def __str__(self) -> str:
        """Generate the Overpass QL query string for this Union object.

        Returns:
            str: The Overpass QL query string.
        """
        element_strs = [str(element).rstrip(';') for element in self.elements]
        return f"({' '.join(f'{s};' for s in element_strs)});"

class Difference:
    def __init__(self, base: TypingUnion[Node, Way, Relation, Changeset, Area], subtract: TypingTuple[TypingUnion[Node, Way, Relation, Changeset, Area], ...]):
        self.base = base
        self.subtract = subtract

    def __str__(self) -> str:
        """Generate the Overpass QL query string for this Difference object.

        Returns:
            str: The Overpass QL query string.
        """
        base_str = str(self.base).rstrip(';')
        subtract_strs = [str(element).rstrip(';') for element in self.subtract]
        subtract_part = ' '.join(f'- {s};' for s in subtract_strs)
        return f"({base_str}; {subtract_part});"