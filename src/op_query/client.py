from typing import Tuple
import overpy

class Node:
    def __init__(self) -> None:
        self.id = ''
        self.ids = []
        self.tags = []
        self.bbox = None
        self.area = None
        self.around = None
        self.relation = None
        self.way = None

        # need set filtering and conditional logic

    def with_id(self, id: str) -> 'Node':
        if not self.ids:
            self.id = id
        else:
            raise ValueError('Cannot set id, field ids is already set. Choose one or the other')
        
        return self
    
    def with_ids(self, ids: list[str]):
        if not self.id:
            self.ids = ids
        else:
            raise ValueError('Cannot set ids, field id is already set. Choose one or the other')

        return self
    
    def with_tags(self, tags):
        return self
    
    def with_bbox(self, bbox):
        return self
    
    def with_area(self, area):
        return self
    
    def with_around(self, around):
        return self
    
    def with_relation(self, relation):
        return self
    
    def with_way(self, way):
        return self
    
    def __str__(self) -> str:
        return ''
    
class Way:
    def __new__(cls) -> str:
        return ''
    
class Relation:
    def __new__(cls) -> str:
        return ''

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

class QueryClient:
    def __init__(self) -> None:
        self.api = overpy.Overpass()

    # method to get admin level
    # method to add area
    # method to add node/way/relation
    
    def validate_query(self, query) -> bool:
        try:
            self.api.query(query)
            print("Query is syntactically valid.")
            return True
        except overpy.exception.OverpassSyntaxError as e:
            print(f"Syntax error: {e}")
            return False
        except Exception as e:
            print(f"Other error: {e}")
            return False
    
    # method to execute query