from typing import Tuple

class Node:
    def __init__(self) -> None:
        self.id: str = ''
        self.ids: list[str] = []
        self.tags: list[Tuple[str, str]] = []
        self.bbox: Tuple[float, float, float, float] = None
        self.area = None
        self.around = None
        self.relation = None
        self.way = None
        self.spatial_filter = None
        self.store_as_set = None

        # need set filtering and conditional logic

    def with_id(self, id: str) -> 'Node':
        if not isinstance(id, str):
            raise TypeError('id must be of type str')

        if not self.ids:
            self.id = id
        else:
            raise ValueError('Cannot set id, field ids is already set. Choose one or the other')
        
        return self
    
    def with_ids(self, ids: list[str]) -> 'Node':
        if not isinstance(ids, list):
            raise TypeError('Cannot set ids, ids must be of type list')
        
        for id in ids:
            if not isinstance(id, str):
                raise TypeError('Cannot set ids, values in ids must be of type str')

        if not self.id:
            self.ids = ids
        else:
            raise ValueError('Cannot set ids, field id is already set. Choose one or the other')

        return self
    
    def with_tags(self, tags:list[Tuple[str, str]]) -> 'Node':
        return self
    
    def with_bbox(self, bbox: Tuple[float, float, float, float]) -> 'Node':
        if not isinstance(bbox, Tuple):
            raise TypeError('Cannot set bbox, bbox must be of type Tuple')
        
        if len(bbox) < 0:
            raise ValueError('Cannot set bbox, invalid length detected for the Tuple')
        
        if len(bbox) != 4:
            raise ValueError('Cannot set bbox, Tuple must be of length 4')
        
        self.bbox = bbox
        
        return self
    
    def with_area(self, area) -> 'Node':
        return self
    
    def with_around(self, around) -> 'Node':
        return self
    
    def with_relation(self, relation) -> 'Node':
        return self
    
    def with_way(self, way) -> 'Node':
        return self
    
    def with_spatial_filter(self, spatial_filter) -> 'Node':
        return self
    
    def store_as_set(self, set_name: str) -> 'Node':
        self.store_as_set = set_name
        return self
    
    def __str__(self) -> str:
        return ''
    
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
        self.spatial_filter = None
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
    
    def store_as_set(self, set_name: str) -> 'Way':
        self.store_as_set = set_name
        return self
    
    def __str__(self) -> str:
        return ''
    
class Relation:
    def __init__(self) -> None:
        self.id = ''
        self.ids = []
        self.tags = []
        self.bbox = None
        self.area = None
        self.around = None
        self.node_member = None
        self.way_member = None
        self.relation_member = None
        self.node_member_and_role = None
        self.way_member_and_role = None
        self.relation_member_and_role = None
        self.spatial_filter = None
        self.store_as_set = None

        # need set filtering and conditional logic

    def with_id(self, id: str) -> 'Relation':
        if not self.ids:
            self.id = id
        else:
            raise ValueError('Cannot set id, field ids is already set. Choose one or the other')
        
        return self
    
    def with_ids(self, ids: list[str]) -> 'Relation':
        if not self.id:
            self.ids = ids
        else:
            raise ValueError('Cannot set ids, field id is already set. Choose one or the other')

        return self
    
    def with_tags(self, tags) -> 'Relation':
        return self
    
    def with_bbox(self, bbox) -> 'Relation':
        return self
    
    def with_area(self, area) -> 'Relation':
        return self
    
    def with_around(self, around) -> 'Relation':
        return self
    
    def with_node_member(self, node_member) -> 'Relation':
        return self
    
    def with_way_member(self, way_member) -> 'Relation':
        return self
    
    def with_relation_member(self, relation_member) -> 'Relation':
        return self
    
    def with_node_member_and_role(self, node_member, role) -> 'Relation':
        return self
    
    def with_way_member_and_role(self, way_member, role) -> 'Relation':
        return self
    
    def with_relation_member_and_role(self, relation_member, role) -> 'Relation':
        return self
    
    def with_spatial_filter(self, spatial_filter) -> 'Relation':
        return self
    
    def store_as_set(self, set_name:str) -> 'Relation':
        self.store_as_set = set_name
        return self
    
    def __str__(self) -> str:
        return ''
    
class Changeset:
    def __init__(self) -> None:
        self.id = ''