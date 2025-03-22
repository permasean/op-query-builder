from op_query_builder.elements.node import Node
from op_query_builder.elements.relation import Relation
from op_query_builder.elements.way import Way
from op_query_builder.derived import Area
from typing import Tuple, Union, Optional

class Query:
    def __init__(self):
        self.output: str = 'json'  # json, csv, or xml
        self.output_detail: str = 'body'  # body, geom, or custom (e.g., center)
        self.timeout: Optional[int] = None  # Timeout in seconds
        self.global_bbox: Optional[Tuple[float, float, float, float]] = None  # (min_lat, min_lon, max_lat, max_lon)
        self.elements: list[Union[Node, Way, Relation, Area]] = []  # Order matters

    def set_output(self, output_type: str) -> 'Query':
        if output_type not in ['json', 'csv', 'xml']:
            raise ValueError(
                'Invalid output_type detected, must be "csv", "json", or "xml"'
            )
        self.output = output_type
        return self

    def set_output_detail(self, detail: str) -> 'Query':
        valid_details = ['body', 'geom', 'center', 'skel', 'ids']
        if detail not in valid_details:
            raise ValueError(
                f"Invalid output_detail, must be one of {valid_details}"
            )
        self.output_detail = detail
        return self

    def set_timeout(self, timeout: int) -> 'Query':
        if not isinstance(timeout, int):
            raise TypeError(
                f"Timeout must be an integer, got {type(timeout).__name__}"
            )
        if timeout <= 0:
            raise ValueError("Timeout must be a positive integer")
        self.timeout = timeout
        return self

    def set_global_bbox(self, bbox: Tuple[float, float, float, float]) -> 'Query':
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

    def add_area(self, area: Area) -> 'Query':
        self.elements.append(area)
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
        if self.timeout is not None:
            settings.append(f"[timeout:{self.timeout}]")
        if self.global_bbox:
            bbox_str = ",".join(map(str, self.global_bbox))
            settings.append(f"[bbox:{bbox_str}]")
        if self.output:
            settings.append(f"[out:{self.output}]")
        if settings:
            query_lines.append("".join(settings))

        # Add elements
        for element in self.elements:
            query_lines.append(str(element))

        # Add output detail
        if self.output_detail:
            query_lines.append(f"out {self.output_detail};")

        return "\n".join(query_lines)