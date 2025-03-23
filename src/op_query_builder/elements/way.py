from typing import Tuple, Optional, List, Union
from .base import Element

class Way(Element):
    def __init__(self) -> None:
        super().__init__()
        self.id: Optional[int] = None
        self.ids: List[int] = []
        self.tags: List[Tuple[str, str]] = []
        self.bbox: Optional[Tuple[float, float, float, float]] = None
        self.area_id: Optional[int] = None
        self.area_name: Optional[str] = None
        self.around_point: Optional[Tuple[float, float, float]] = None  # (radius, lat, lon)
        self.around_set: Optional[Tuple[str, float]] = None  # (set_name, radius)
        self.node: Optional[int] = None  # way(n:node_id)
        self.node_from_set: Optional[str] = None  # way(n.set_name)
        self.relation: Optional[int] = None
        self.relation_and_role: Optional[Tuple[int, str]] = None
        self.relation_from_set: Optional[str] = None
        self._store_as_set_name: Optional[str] = None
        self.filter_from_set: Optional[str] = None
        self.is_closed: Optional[bool] = None  # Filter for closed ways
        self.min_length: Optional[float] = None  # Filter by length
        self.min_nodes: Optional[int] = None  # Filter by node count
        self.include_nodes: bool = False  # Downward recursion
        self.include_parents: bool = False  # Upward recursion

    # Helper methods for filter exclusivity
    def _has_spatial_filter(self) -> bool:
        return any([self.bbox, self.area_id, self.area_name, self.around_point, self.around_set])

    def _has_relation_filter(self) -> bool:
        return any([self.relation, self.relation_and_role, self.relation_from_set])

    def _has_node_filter(self) -> bool:
        return any([self.node, self.node_from_set])

    def with_id(self, id: int) -> 'Way':
        if not isinstance(id, int):
            raise TypeError("id must be of type int")
        if id < 0:
            raise ValueError("id must be a non-negative integer")
        if self.ids:
            raise ValueError("Cannot set id, field ids is already set. Choose one or the other")
        self.id = id
        return self

    def with_ids(self, ids: List[int]) -> 'Way':
        if not isinstance(ids, list):
            raise TypeError("ids must be of type list")
        if not ids:
            raise ValueError("ids list cannot be empty")
        for id in ids:
            if not isinstance(id, int):
                raise TypeError("All values in ids must be of type int")
            if id < 0:
                raise ValueError("All values in ids must be non-negative integers")
        if self.id is not None:
            raise ValueError("Cannot set ids, field id is already set. Choose one or the other")
        self.ids = ids
        return self

    def with_tags(self, tags: List[Tuple[str, str]]) -> 'Way':
        if not isinstance(tags, list):
            raise TypeError("tags must be of type list")
        for tag in tags:
            if not isinstance(tag, tuple):
                raise TypeError("Each tag in tags must be of type tuple")
            if len(tag) != 2:
                raise ValueError("Each tag in tags must be a tuple of length 2")
            for el in tag:
                if not isinstance(el, str):
                    raise TypeError("Tag key and value must be of type str")
        self.tags = tags
        return self

    def with_bbox(self, bbox: Tuple[float, float, float, float]) -> 'Way':
        if not isinstance(bbox, tuple) or len(bbox) != 4:
            raise ValueError("bbox must be a tuple of length 4")
        south, west, north, east = bbox
        if not all(isinstance(v, (int, float)) for v in bbox):
            raise TypeError("bbox values must be int or float")
        if not (-90 <= south <= north <= 90) or not (-180 <= west <= east <= 180):
            raise ValueError("Invalid bbox coordinates")
        if self._has_spatial_filter():
            raise ValueError("Only one spatial filter (bbox, area, around) can be set")
        self.bbox = bbox
        return self

    def with_area_by_id(self, area_id: int) -> 'Way':
        if not isinstance(area_id, int):
            raise TypeError("area_id must be of type int")
        if area_id < 0:
            raise ValueError("area_id must be a non-negative integer")
        if self._has_spatial_filter():
            raise ValueError("Only one spatial filter (bbox, area, around) can be set")
        self.area_id = area_id
        return self

    def with_area_by_name(self, area_name: str) -> 'Way':
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

    def with_around_point(self, radius: Union[int, float], lat: Union[int, float], lon: Union[int, float]) -> 'Way':
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

    def with_around_set(self, set_name: str, radius: Union[int, float]) -> 'Way':
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

    def with_node(self, node_id: int) -> 'Way':
        """Filter ways that contain a specific node (e.g., 'way(n:node_id)')."""
        if not isinstance(node_id, int):
            raise TypeError("node_id must be of type int")
        if node_id < 0:
            raise ValueError("node_id must be a non-negative integer")
        if self._has_node_filter():
            raise ValueError("Cannot set node filter when another node filter is set")
        self.node = node_id
        return self

    def with_node_from_set(self, set_name: str) -> 'Way':
        """Filter ways that contain nodes from a set (e.g., 'way(n.set_name)')."""
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError("set_name contains invalid characters")
        if self._has_node_filter():
            raise ValueError("Cannot set node filter when another node filter is set")
        self.node_from_set = set_name
        return self

    def with_relation(self, relation_id: int) -> 'Way':
        if not isinstance(relation_id, int):
            raise TypeError("relation_id must be of type int")
        if relation_id < 0:
            raise ValueError("relation_id must be a non-negative integer")
        if self._has_relation_filter():
            raise ValueError("Cannot set relation filter when another relation filter is set")
        self.relation = relation_id
        return self

    def with_relation_and_role(self, relation_id: int, role: str) -> 'Way':
        if not isinstance(relation_id, int):
            raise TypeError("relation_id must be of type int")
        if relation_id < 0:
            raise ValueError("relation_id must be a non-negative integer")
        if not isinstance(role, str) or not role.strip():
            raise ValueError("role must be a non-empty string")
        if self._has_relation_filter():
            raise ValueError("Cannot set relation filter when another relation filter is set")
        self.relation_and_role = (relation_id, role)
        return self

    def with_relation_from_set(self, set_name: str) -> 'Way':
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError("set_name contains invalid characters")
        if self._has_relation_filter():
            raise ValueError("Cannot set relation filter when another relation filter is set")
        self.relation_from_set = set_name
        return self

    def with_closed(self, is_closed: bool = True) -> 'Way':
        """Filter for closed ways (e.g., polygons)."""
        self.is_closed = is_closed
        return self

    def with_min_length(self, length: float) -> 'Way':
        """Filter ways with a minimum length in meters."""
        if not isinstance(length, (int, float)):
            raise TypeError("length must be an int or float")
        if length < 0:
            raise ValueError("length must be non-negative")
        self.min_length = length
        return self

    def with_min_nodes(self, node_count: int) -> 'Way':
        """Filter ways with a minimum number of nodes."""
        if not isinstance(node_count, int):
            raise TypeError("node_count must be an int")
        if node_count < 1:
            raise ValueError("node_count must be a positive integer")
        self.min_nodes = node_count
        return self

    def with_nodes(self) -> 'Way':
        """Include all nodes of the way (downward recursion)."""
        self.include_nodes = True
        return self

    def with_parents(self) -> 'Way':
        """Include parent relations of the way (upward recursion)."""
        self.include_parents = True
        return self

    def from_set(self, set_name: str) -> 'Way':
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError("set_name contains invalid characters for Overpass QL")
        self.filter_from_set = set_name
        return self

    def with_tag_exists(self, key: str) -> 'Way':
        if not isinstance(key, str):
            raise TypeError("key must be of type str")
        if not key.strip():
            raise ValueError("key cannot be empty or whitespace")
        self.tags.append((key, ""))
        return self

    def with_tag_not_exists(self, key: str) -> 'Way':
        if not isinstance(key, str):
            raise TypeError("key must be of type str")
        if not key.strip():
            raise ValueError("key cannot be empty or whitespace")
        self.tags.append((f"!{key}", ""))
        return self

    def with_tag_not(self, key: str, value: str) -> 'Way':
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("key and value must be of type str")
        if not key.strip() or not value.strip():
            raise ValueError("key and value cannot be empty or whitespace")
        self.tags.append((key, f"!={value}"))
        return self

    def with_tag_regex(self, key: str, regex: str) -> 'Way':
        if not isinstance(key, str) or not isinstance(regex, str):
            raise TypeError("key and regex must be of type str")
        if not key.strip() or not regex.strip():
            raise ValueError("key and regex cannot be empty or whitespace")
        self.tags.append((key, f"~{regex}"))
        return self

    def with_tag_condition(self, condition: str) -> 'Way':
        if not isinstance(condition, str):
            raise TypeError("condition must be of type str")
        self.validate_tag_condition(condition)
        self.tag_conditions.append(condition)
        return self

    def with_user(self, username: str) -> 'Way':
        if not isinstance(username, str):
            raise TypeError("username must be of type str")
        if not username.strip():
            raise ValueError("username cannot be empty or whitespace")
        self.tags.append(("user", username))
        return self

    def with_uid(self, uid: int) -> 'Way':
        if not isinstance(uid, int):
            raise TypeError("uid must be of type int")
        if uid < 0:
            raise ValueError("uid must be a non-negative integer")
        self.tags.append(("uid", str(uid)))
        return self

    def with_newer(self, timestamp: str) -> 'Way':
        if not isinstance(timestamp, str):
            raise TypeError("timestamp must be of type str")
        if not timestamp.strip():
            raise ValueError("timestamp cannot be empty or whitespace")
        if 'T' not in timestamp or 'Z' not in timestamp:
            raise ValueError("timestamp must be in ISO 8601 format (e.g., '2023-01-01T00:00:00Z')")
        self.tags.append(("newer", f'"{timestamp}"'))
        return self

    def with_version(self, version: int) -> 'Way':
        if not isinstance(version, int):
            raise TypeError("version must be of type int")
        if version < 1:
            raise ValueError("version must be a positive integer")
        self.tags.append(("version", str(version)))
        return self

    def store_as_set(self, set_name: str) -> 'Way':
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError("set_name contains invalid characters for Overpass QL")
        self._store_as_set_name = set_name
        return self

    def __str__(self) -> str:
        query = ""
        if self.filter_from_set:
            query += f".{self.filter_from_set} "
        query += "way"
        if self.id is not None:
            query += f"({self.id})"
        elif self.ids:
            query += f"({','.join(map(str, self.ids))})"
        if self.pivot_set:
            query += f"(pivot.{self.pivot_set})"
        for key, value in self.tags:
            if value == "":
                query += f"[{key}]"
            elif value.startswith("~"):
                query += f"[{key}{value}]"
            elif value.startswith("!="):
                query += f"[{key}{value}]"
            else:
                query += f"[{key}={value}]"
        for condition in self.tag_conditions:
            query += condition
        query = self._append_if_conditions(query)
        if self.is_closed is not None:
            query += f"[is_closed={'true' if self.is_closed else 'false'}]"
        if self.min_length is not None:
            query += f"[if:length()>{self.min_length}]"
        if self.min_nodes is not None:
            query += f"[if:count(nodes)>{self.min_nodes}]"
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
        if self.node is not None:
            query += f"(n:{self.node})"
        if self.node_from_set:
            query += f"(n.{self.node_from_set})"
        if self.relation is not None:
            query += f"(r:{self.relation})"
        if self.relation_and_role:
            query += f'(r:{self.relation_and_role[0]},"{self.relation_and_role[1]}")'
        if self.relation_from_set:
            query += f"(r.{self.relation_from_set})"
        
        # Handle recursion (include_nodes or include_parents)
        if self.include_nodes or self.include_parents:
            query = f"({query};"
            if self.include_nodes:
                query += ">"
                if self.include_parents:
                    query += ";"  # Add semicolon between > and <
            if self.include_parents:
                query += "<"
            query += ")"
        
        # Store as set
        if self._store_as_set_name:
            query += f"->.{self._store_as_set_name}"
        
        query += ";"  # Final semicolon for the entire statement
        return query