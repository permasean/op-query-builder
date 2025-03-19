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
    
    def with_ids(self, ids: list[str]) -> 'Node':
        if not self.id:
            self.ids = ids
        else:
            raise ValueError('Cannot set ids, field id is already set. Choose one or the other')

        return self
    
    def with_tags(self, tags) -> 'Node':
        return self
    
    def with_bbox(self, bbox) -> 'Node':
        return self
    
    def with_area(self, area) -> 'Node':
        return self
    
    def with_around(self, around) -> 'Node':
        return self
    
    def with_relation(self, relation) -> 'Node':
        return self
    
    def with_way(self, way) -> 'Node':
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
    
    def with_node(self, node) -> 'Way':
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
    
    def __str__(self) -> str:
        return ''