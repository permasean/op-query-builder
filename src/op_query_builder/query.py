from elements import Node, Way, Relation
from derived import Area
from typing import Tuple

class Query:
    output = 'json'
    output_detail = 'body'
    timeout = ''
    global_bbox = ''
    elements = [] # note that the order of elements matter

    def __new__(cls) -> str:
        return cls.__build_query()
    
    # need a method to adjust output detail (body, geom, recursive)
    
    @classmethod
    def set_output(cls, output_type: str) -> None:
        if output_type not in ['json', 'csv', 'xml']:
            raise ValueError(
                'Invalid output_type detected, must be "csv", "json", or "xml"'
            )
        
        cls.output = output_type

    @classmethod
    def set_timeout(cls, timeout: int) -> None:
        if not isinstance(timeout, int):
            raise TypeError(
                f"Timeout must be an integer, got {type(timeout).__name__}"
            )

        if timeout <= 0:
            raise ValueError("Timeout must be a positive integer")
        
        cls.timeout = timeout

    @classmethod
    def set_global_bbox(cls, bbox: Tuple[float, float, float, float]):
        if cls.__validate_bbox(bbox):
            cls.global_bbox = bbox
        else:
            raise ValueError("Invalid bbox value")
    
    @classmethod
    def add_node(cls, node: Node) -> None:
        cls.elements.append(node)

    @classmethod
    def add_way(cls, way: Way) -> None:
        cls.elements.append(way)

    @classmethod
    def add_relation(cls, relation: Relation) -> None:
        cls.elements.append(relation)

    @classmethod
    def add_area(cls, area: Area) -> None:
        cls.elements.append(area)
    
    @classmethod
    def print(cls) -> None:
        print(cls.__build_query())

    @classmethod
    def __validate_bbox(cls, bbox: Tuple[float, float, float, float]) -> bool:
        if not isinstance(bbox, tuple):
            print(f"TypeError: Expected a tuple, got {type(bbox).__name__}")
            return False
        if len(bbox) != 4:
            print(f"ValueError: Bounding box must have exactly 4 values, got {len(bbox)}")
            return False
        for i, value in enumerate(bbox):
            if not isinstance(value, (float, int)):
                print(f"TypeError: Element {i} must be a float or int, got {type(value).__name__}")
                return False
            
        min_lat, min_lon, max_lat, max_lon = bbox
        if not (-90 <= min_lat <= max_lat <= 90):
            print("ValueError: Latitude must be between -90 and 90, with min <= max")
            return False
        if not (-180 <= min_lon <= max_lon <= 180):
            print("ValueError: Longitude must be between -180 and 180, with min <= max")
            return False
        
        return True
    
    @classmethod
    def __build_query(cls) -> str:
        return ''