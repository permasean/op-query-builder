from typing import Tuple

class Node:
    def __init__(self) -> None:
        self.id: str = ''
        self.ids: list[str] = []
        self.tags: list[Tuple[str, str]] = []
        self.bbox: Tuple[int | float, int | float, int | float, int | float] = None
        self.area_id = None
        self.area_name = None
        self.around = None
        self.relation = None
        self.way = None
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
        if not isinstance(tags, list):
            raise TypeError('Cannot set tags, tags must be of type list')
        
        for tag in tags:
            if not isinstance(tag, Tuple):
                raise TypeError('Cannot set tags, tag in tags must be of type Tuple')
            
            if len(tag) != 2:
                raise ValueError('Cannot set tags, tag in tags must be of length 2')
            
            for el in tag:
                if not isinstance(el, str):
                    raise TypeError('Cannot set tags, values in tuple must be of type str')
                
        self.tags = tags

        return self
    
    def with_bbox(self, bbox: Tuple[int | float, int | float, int | float, int | float]) -> 'Node':
        # (float, float, float ,float)
        if not isinstance(bbox, Tuple):
            raise TypeError('Cannot set bbox, bbox must be of type Tuple')
        
        if len(bbox) != 4:
            raise ValueError('Cannot set bbox, Tuple must be of length 4')
        
        for val in bbox:
            if not isinstance(val, int) and not isinstance(val, float):
                raise TypeError('Cannot set bbox, Tuple must only contain values of type int or float')
        
        self.bbox = bbox
        
        return self
    
    def with_area_by_id(self, area_id: int) -> 'Node':
        # (area:area_id)
        if not self.area_name:
            self.area_id = area_id
        else:
            raise ValueError('Cannot set area_id, area_name is already set. Choose one or the other')
        return self
    
    def with_area_by_name(self, area_name: str) -> 'Node':
        # (area.area_name)
        if not self.area_id:
            self.area_name = area_name
        else:
            raise ValueError('Cannot set area_name, area_id is already set. Choose one or the other')
        return self
    
    def with_around_point(self, radius, lat, long) -> 'Node':
        # (around:<radius>,<lat>,<lon>)

        return self
    
    def with_around_set(self, set_name, radius) -> 'Node':
        # (around.<setname>:<radius>)
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