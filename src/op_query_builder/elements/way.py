from typing import Tuple, Optional

class Way:
    def __init__(self) -> None:
        self.id = ''
        self.ids = []
        self.tags = []
        self.bbox = None
        self.area = None
        self.around = None
        self.relation = None
        self.node = None
        self.store_as_set = None

        # need set filtering and conditional logic

    def with_id(self, id: str) -> 'Way':
        if not self.ids:
            self.id = id
        else:
            raise ValueError('Cannot set id, field ids is already set. Choose one or the other')
        
        return self
    
    def with_ids(self, ids: list[str]) -> 'Way':
        if not self.id:
            self.ids = ids
        else:
            raise ValueError('Cannot set ids, field id is already set. Choose one or the other')

        return self
    
    def with_tags(self, tags) -> 'Way':
        return self
    
    def with_bbox(self, bbox) -> 'Way':
        return self
    
    def with_area(self, area) -> 'Way':
        return self
    
    def with_around(self, around) -> 'Way':
        return self
    
    def with_relation(self, relation) -> 'Way':
        return self
    
    def with_node(self, node: str) -> 'Way':
        return self
    
    def with_spatial_filter(self, spatial_filter) -> 'Way':
        return self
    
    def store_as_set(self, set_name: str) -> None:
        self.store_as_set = set_name
    
    def __str__(self) -> str:
        return ''