from typing import Tuple, Optional
from .base import Element

class Node(Element):
    def __init__(self) -> None:
        super().__init__()
        self.id: Optional[int] = None
        self.ids: list[int] = []
        self.tags: list[Tuple[str, str]] = []
        self.bbox: Tuple[int | float, int | float, int | float, int | float] = None
        self.area_id: Optional[int] = None
        self.area_name: Optional[str] = None
        self.around_point: Tuple[int | float, int | float, int | float] = None
        self.around_set: Tuple[str, int | float] = None
        self.relation: Optional[int] = None
        self.relation_and_role: Tuple[int, str] = None
        self.relation_from_set: Optional[str] = None
        self.way: Optional[int] = None
        self.way_from_set: Optional[str] = None
        self.set_name: Optional[str] = None
        self.filter_from_set: Optional[str] = None

    # Helper method to check spatial filter exclusivity
    def _has_spatial_filter(self) -> bool:
        return any([self.bbox, self.area_id, self.area_name, self.around_point, self.around_set])

    # Helper method to check relation/way filter exclusivity
    def _has_relation_filter(self) -> bool:
        return any([self.relation, self.relation_and_role, self.relation_from_set])

    def _has_way_filter(self) -> bool:
        return any([self.way, self.way_from_set])

    def with_id(self, id: int) -> 'Node':
        if not isinstance(id, int):
            raise TypeError("id must be of type int")
        if id < 0:
            raise ValueError("id must be a non-negative integer")
        if not self.ids:
            self.id = id
        else:
            raise ValueError("Cannot set id, field ids is already set. Choose one or the other")
        return self
    
    def with_ids(self, ids: list[int]) -> 'Node':
        if not isinstance(ids, list):
            raise TypeError("ids must be of type list")
        if not ids:
            raise ValueError("ids list cannot be empty")
        for id in ids:
            if not isinstance(id, int):
                raise TypeError("Cannot set ids, all values in ids must be of type int")
            if id < 0:
                raise ValueError("Cannot set ids, all values in ids must be non-negative integers")
        if not self.id:
            self.ids = ids
        else:
            raise ValueError("Cannot set ids, field id is already set. Choose one or the other")
        return self
    
    def with_tags(self, tags: list[Tuple[str, str]]) -> 'Node':
        if not isinstance(tags, list):
            raise TypeError('tags must be of type list')
        
        for tag in tags:
            if not isinstance(tag, Tuple):
                raise TypeError('tag in tags must be of type Tuple')
            
            if len(tag) != 2:
                raise ValueError('tag in tags must be of length 2')
            
            for el in tag:
                if not isinstance(el, str):
                    raise TypeError('Cannot set tags, values in tuple must be of type str')
                
        self.tags = tags
        return self
    
    def with_bbox(self, bbox: Tuple[int | float, int | float, int | float, int | float]) -> 'Node':
        # (float, float, float ,float)
        if not isinstance(bbox, Tuple) or len(bbox) != 4:
            raise ValueError("bbox must be a Tuple of length 4")
        south, west, north, east = bbox
        if not all(isinstance(v, (int, float)) for v in bbox):
            raise TypeError("bbox values must be int or float")
        if not (-90 <= south <= north <= 90) or not (-180 <= west <= east <= 180):
            raise ValueError("Invalid bbox coordinates")
        if self._has_spatial_filter():
            raise ValueError("Only one spatial filter (bbox, area, around) can be set")
        self.bbox = bbox
        return self
    
    def with_area_by_id(self, area_id: int) -> 'Node':
        # (area:area_id)
        if not isinstance(area_id, int):
            raise TypeError("area_id must be of type int")
        if area_id < 0:
            raise ValueError("area_id must be a non-negative integer")
        if self._has_spatial_filter():
            raise ValueError("Only one spatial filter (bbox, area, around) can be set")
        self.area_id = area_id
        return self
    
    def with_area_by_name(self, area_name: str) -> 'Node':
        # (area.area_name)
        if not isinstance(area_name, str):
            raise TypeError("area_name must be of type str")
        if not area_name.strip():
            raise ValueError("area_name cannot be empty or whitespace")
        if any(char in area_name for char in '[]{}();'):
            raise ValueError("area_name contains invalid characters")
        if self._has_spatial_filter():
            raise ValueError("Only one spatial filter (bbox, area, around) can be set")
        self.area_name = area_name
        return self
    
    def with_around_point(self, radius: int|float, lat: int|float, lon: int|float) -> 'Node':
        # (around:<radius>,<lat>,<lon>)
        if not all(isinstance(v, (int, float)) for v in (radius, lat, lon)):
            raise TypeError("radius, lat, and lon must be int or float")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ValueError("lat must be -90 to 90, lon must be -180 to 180")
        if self._has_spatial_filter():
            raise ValueError("Only one spatial filter (bbox, area, around) can be set")
        self.around_point = (radius, lat, lon)
        return self
    
    def with_around_set(self, set_name: str, radius: int | float) -> 'Node':
        # (around.<set_name>:<radius>)
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if not isinstance(radius, (int, float)) or radius < 0:
            raise ValueError("radius must be a non-negative int or float")
        if self._has_spatial_filter():
            raise ValueError("Only one spatial filter (bbox, area, around) can be set")
        self.around_set = (set_name, radius)
        return self
    
    def with_relation(self, relation_id: int) -> 'Node':
        """Filter nodes that are members of a specific relation (e.g., 'node(r:<relation_id>)')."""
        if not isinstance(relation_id, int):
            raise TypeError("relation_id must be of type int")
        if relation_id < 0:
            raise ValueError("relation_id must be a non-negative integer")
        if self._has_relation_filter() or self._has_way_filter():
            raise ValueError("Cannot set relation filter when another relation or way filter is set")
        self.relation = relation_id
        return self
    
    def with_relation_and_role(self, relation_id: int, role: str) -> 'Node':
        """Filter nodes that are members of a relation with a specific role (e.g., 'node(r:<relation_id>,"role")')."""
        if not isinstance(relation_id, int):
            raise TypeError("relation_id must be of type int")
        if relation_id < 0:
            raise ValueError("relation_id must be a non-negative integer")
        if not isinstance(role, str) or not role.strip():
            raise ValueError("role must be a non-empty string")
        if self._has_relation_filter() or self._has_way_filter():
            raise ValueError("Cannot set relation filter when another relation or way filter is set")
        self.relation_and_role = (relation_id, role)
        return self
    
    def with_relation_from_set(self, set_name: str) -> 'Node':
        """Filter nodes that are members of relations in a set (e.g., 'node(r.<set_name>)')."""
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError("set_name contains invalid characters")
        if self._has_relation_filter() or self._has_way_filter():
            raise ValueError("Cannot set relation filter when another relation or way filter is set")
        self.relation_from_set = set_name
        return self
    
    def with_way(self, way_id: int) -> 'Node':
        """Filter nodes that are part of a specific way (e.g., 'node(w:<way_id>)')."""
        if not isinstance(way_id, int):
            raise TypeError("way_id must be of type int")
        if way_id < 0:
            raise ValueError("way_id must be a non-negative integer")
        if self._has_way_filter() or self._has_relation_filter():
            raise ValueError("Cannot set way filter when another way or relation filter is set")
        self.way = way_id
        return self
    
    def with_way_from_set(self, set_name: str) -> 'Node':
        """Filter nodes that are part of ways in a set (e.g., 'node(w.<set_name>)')."""
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError("set_name contains invalid characters")
        if self._has_way_filter() or self._has_relation_filter():
            raise ValueError("Cannot set way filter when another way or relation filter is set")
        self.way_from_set = set_name
        return self
    
    def from_set(self, set_name: str) -> 'Node':
        """Filter nodes from a previously defined set (e.g., '.set_name node;')."""
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError("set_name contains invalid characters for Overpass QL")
        self.filter_from_set = set_name
        return self

    def with_tag_exists(self, key: str) -> 'Node':
        """Filter nodes where a tag key exists (e.g., '[key]')."""
        if not isinstance(key, str):
            raise TypeError("key must be of type str")
        if not key.strip():
            raise ValueError("key cannot be empty or whitespace")
        self.tags.append((key, ""))  # Empty value indicates existence check
        return self

    def with_tag_not_exists(self, key: str) -> 'Node':
        """Filter nodes where a tag key does not exist (e.g., '[!key]')."""
        if not isinstance(key, str):
            raise TypeError("key must be of type str")
        if not key.strip():
            raise ValueError("key cannot be empty or whitespace")
        self.tags.append((f"!{key}", ""))  # !key with empty value
        return self

    def with_tag_not(self, key: str, value: str) -> 'Node':
        """Filter nodes where a tag does not equal a value (e.g., '[key!=value]')."""
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("key and value must be of type str")
        if not key.strip() or not value.strip():
            raise ValueError("key and value cannot be empty or whitespace")
        self.tags.append((key, f"!={value}"))
        return self

    def with_tag_regex(self, key: str, regex: str) -> 'Node':
        """Filter nodes where a tag matches a regex (e.g., '[key~regex]')."""
        if not isinstance(key, str) or not isinstance(regex, str):
            raise TypeError("key and regex must be of type str")
        if not key.strip() or not regex.strip():
            raise ValueError("key and regex cannot be empty or whitespace")
        self.tags.append((key, f"~{regex}"))
        return self

    def with_tag_condition(self, condition: str) -> 'Node':
        """Add a custom tag condition (e.g., '["highway"~"^(primary|secondary)$"]')."""
        if not isinstance(condition, str):
            raise TypeError("condition must be of type str")
        if not condition.strip():
            raise ValueError("condition cannot be empty or whitespace")
        # Basic validation: should look like a tag filter
        if not condition.startswith('[') or not condition.endswith(']'):
            raise ValueError("condition must be formatted as a tag filter, e.g., '[key=value]'")
        self.tag_conditions.append(condition)
        return self
    
    def with_user(self, username: str) -> 'Node':
        """Filter nodes edited by a specific user (e.g., '[user:username]')."""
        if not isinstance(username, str):
            raise TypeError("username must be of type str")
        if not username.strip():
            raise ValueError("username cannot be empty or whitespace")
        self.tags.append(("user", username))
        return self

    def with_uid(self, uid: int) -> 'Node':
        """Filter nodes edited by a specific user ID (e.g., '[uid:123]')."""
        if not isinstance(uid, int):
            raise TypeError("uid must be of type int")
        if uid < 0:
            raise ValueError("uid must be a non-negative integer")
        self.tags.append(("uid", str(uid)))
        return self

    def with_newer(self, timestamp: str) -> 'Node':
        """Filter nodes newer than a timestamp (e.g., '[newer:\"2023-01-01T00:00:00Z\"]')."""
        if not isinstance(timestamp, str):
            raise TypeError("timestamp must be of type str")
        if not timestamp.strip():
            raise ValueError("timestamp cannot be empty or whitespace")
        # Basic ISO 8601 check (could be stricter with regex)
        if 'T' not in timestamp or 'Z' not in timestamp:
            raise ValueError("timestamp must be in ISO 8601 format (e.g., '2023-01-01T00:00:00Z')")
        self.tags.append(("newer", f'"{timestamp}"'))
        return self

    def with_version(self, version: int) -> 'Node':
        """Filter nodes with a specific version (e.g., '[version=2]')."""
        if not isinstance(version, int):
            raise TypeError("version must be of type int")
        if version < 1:
            raise ValueError("version must be a positive integer")
        self.tags.append(("version", str(version)))
        return self
    
    def store_as_set(self, set_name: str) -> 'Node':
        """Store the result of this query as a named set (e.g., '->.set_name')."""
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError("set_name contains invalid characters for Overpass QL")
        self.set_name = set_name
        return self
    
    def __str__(self) -> str:
        """Generate the Overpass QL query string for this Node object."""
        query = ""
        
        # If filtering from a set, prepend the set name (e.g., '.input_set node')
        if self.filter_from_set:
            query += f".{self.filter_from_set} "
        
        # Base node declaration
        query += "node"
        
        # Node ID or IDs
        if self.id is not None:
            query += f"({self.id})"
        elif self.ids:
            query += f"({','.join(map(str, self.ids))})"
        
        # Pivot set
        if self.pivot_set:
            query += f"(pivot.{self.pivot_set})"
        
        # Tag filters (exact match, existence, negation, regex)
        for key, value in self.tags:
            if value == "":
                # Existence or non-existence check
                query += f"[{key}]"
            elif value.startswith("~"):
                # Regex match
                query += f"[{key}{value}]"
            elif value.startswith("!="):
                # Not equal
                query += f"[{key}{value}]"
            else:
                # Exact match
                query += f"[{key}={value}]"
        
        # Custom tag conditions (e.g., '["highway"~"^(primary|secondary)$"]')
        for condition in self.tag_conditions:
            query += condition
        
        # If conditions
        query = self._append_if_conditions(query)
        
        # Spatial filters
        if self.bbox:
            query += f"({','.join(map(str, self.bbox))})"
        if self.area_id is not None:
            query += f"(area:{self.area_id})"
        if self.area_name:
            query += f"(area.{self.area_name})"
        if self.around_point:
            query += f"(around:{','.join(map(str, self.around_point))})"
        if self.around_set:
            query += f"(around.{self.around_set[0]}:{self.around_set[1]})"
        
        # Relation filters
        if self.relation is not None:
            query += f"(r:{self.relation})"
        if self.relation_and_role:
            query += f'(r:{self.relation_and_role[0]},"{self.relation_and_role[1]}")'
        if self.relation_from_set:
            query += f"(r.{self.relation_from_set})"
        
        # Way filters
        if self.way is not None:
            query += f"(w:{self.way})"
        if self.way_from_set:
            query += f"(w.{self.way_from_set})"
        
        # Store as set
        if self.set_name:
            query += f"->.{self.set_name}"
        
        # Terminate the query
        query += ";"
        
        return query