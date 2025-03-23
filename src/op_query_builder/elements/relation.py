from typing import Tuple, Optional, List, Union
from .base import Element

class Relation(Element):
    def __init__(self) -> None:
        super().__init__()
        self.bbox: Optional[Tuple[float, float, float, float]] = None
        self.area_id: Optional[int] = None
        self.area_name: Optional[str] = None
        self.around_point: Optional[Tuple[float, float, float]] = None  # (radius, lat, lon)
        self.around_set: Optional[Tuple[str, float]] = None  # (set_name, radius)
        self.node: Optional[int] = None  # relation(n:node_id)
        self.node_from_set: Optional[str] = None  # relation(n.set_name)
        self.way: Optional[int] = None  # relation(w:way_id)
        self.way_from_set: Optional[str] = None  # relation(w.set_name)
        self.relation: Optional[int] = None  # relation(r:relation_id)
        self.relation_and_role: Optional[Tuple[int, str]] = None  # relation(r:relation_id,"role")
        self.relation_from_set: Optional[str] = None  # relation(r.set_name)
        self.min_members: Optional[int] = None  # Filter by minimum member count
        self.min_role_count: Optional[Tuple[str, int]] = None  # (role, min_count)
        self.include_members: bool = False  # Downward recursion
        self.include_parents: bool = False  # Upward recursion

    # Helper methods for filter exclusivity
    def _has_spatial_filter(self) -> bool:
        return any([self.bbox, self.area_id, self.area_name, self.around_point, self.around_set])

    def _has_node_filter(self) -> bool:
        return any([self.node, self.node_from_set])

    def _has_way_filter(self) -> bool:
        return any([self.way, self.way_from_set])

    def _has_relation_filter(self) -> bool:
        return any([self.relation, self.relation_and_role, self.relation_from_set])

    def with_type(self, relation_type: str) -> 'Relation':
        """Filter by relation type (e.g., 'relation[type=multipolygon]').

        Args:
            relation_type (str): The type of relation to filter by (e.g., 'multipolygon', 'boundary').

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If relation_type is not a string.
            ValueError: If relation_type is empty or whitespace.
        """
        if not isinstance(relation_type, str):
            raise TypeError(f"relation_type must be a string, got {type(relation_type).__name__}")
        if not relation_type.strip():
            raise ValueError("relation_type cannot be empty or whitespace")
        self.tags.append(("type", relation_type))
        return self

    def with_min_members(self, count: int) -> 'Relation':
        """Filter relations with a minimum number of members (e.g., 'relation[if:count(members)>10]').

        Args:
            count (int): The minimum number of members required for the relation.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If count is not an integer.
            ValueError: If count is less than 1.
        """
        if not isinstance(count, int):
            raise TypeError(f"count must be an integer, got {type(count).__name__}")
        if count < 1:
            raise ValueError(f"count must be a positive integer, got {count}")
        self.min_members = count
        return self

    def with_min_role_count(self, role: str, count: int) -> 'Relation':
        """Filter relations with a minimum number of members with a specific role (e.g., 'relation[if:count_by_role("outer")>1]').

        Args:
            role (str): The role to count (e.g., 'outer', 'inner').
            count (int): The minimum number of members with the specified role.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If role is not a string or count is not an integer.
            ValueError: If role is empty or count is less than 1.
        """
        if not isinstance(role, str):
            raise TypeError(f"role must be a string, got {type(role).__name__}")
        if not role.strip():
            raise ValueError("role cannot be empty or whitespace")
        if not isinstance(count, int):
            raise TypeError(f"count must be an integer, got {type(count).__name__}")
        if count < 1:
            raise ValueError(f"count must be a positive integer, got {count}")
        self.min_role_count = (role, count)
        return self

    def with_bbox(self, bbox: Tuple[float, float, float, float]) -> 'Relation':
        """Set a bounding box to filter relations geographically.

        Args:
            bbox (Tuple[float, float, float, float]): A tuple of (south, west, north, east) coordinates.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            ValueError: If bbox is not a tuple of length 4 or if coordinates are invalid.
            TypeError: If bbox values are not numbers.
        """
        if not isinstance(bbox, tuple) or len(bbox) != 4:
            raise ValueError(f"bbox must be a tuple of length 4 (south, west, north, east), got {bbox}")
        south, west, north, east = bbox
        if not all(isinstance(v, (int, float)) for v in bbox):
            raise TypeError(f"bbox values must be numbers (int or float), got {bbox}")
        if not (-90 <= south <= north <= 90) or not (-180 <= west <= east <= 180):
            raise ValueError(f"Invalid bbox coordinates: south={south}, west={west}, north={north}, east={east}. South and north must be between -90 and 90, west and east between -180 and 180, with south <= north and west <= east.")
        if self._has_spatial_filter():
            raise ValueError("Only one spatial filter (bbox, area, around) can be set at a time. Unset the current spatial filter before setting a new one.")
        self.bbox = bbox
        return self

    def with_area_by_id(self, area_id: int) -> 'Relation':
        """Filter relations within a specific area by area ID.

        Args:
            area_id (int): The area ID to filter by.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If area_id is not an integer.
            ValueError: If area_id is negative or another spatial filter is already set.
        """
        if not isinstance(area_id, int):
            raise TypeError(f"area_id must be an integer, got {type(area_id).__name__}")
        if area_id < 0:
            raise ValueError(f"area_id must be a non-negative integer, got {area_id}")
        if self._has_spatial_filter():
            raise ValueError("Only one spatial filter (bbox, area, around) can be set at a time. Unset the current spatial filter before setting a new one.")
        self.area_id = area_id
        return self

    def with_area_by_name(self, area_name: str) -> 'Relation':
        """Filter relations within a named area.

        Args:
            area_name (str): The name of the area set to filter by.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If area_name is not a string.
            ValueError: If area_name is empty, contains invalid characters, or another spatial filter is set.
        """
        if not isinstance(area_name, str):
            raise TypeError(f"area_name must be a string, got {type(area_name).__name__}")
        if not area_name.strip():
            raise ValueError("area_name cannot be empty or whitespace")
        if any(char in area_name for char in '[]{}();'):
            raise ValueError(f"area_name contains invalid characters for Overpass QL: {area_name}. Avoid using [], {{}}, (), or ;.")
        if self._has_spatial_filter():
            raise ValueError("Only one spatial filter (bbox, area, around) can be set at a time. Unset the current spatial filter before setting a new one.")
        self.area_name = area_name
        return self

    def with_around_point(self, radius: Union[int, float], lat: Union[int, float], lon: Union[int, float]) -> 'Relation':
        """Filter relations within a radius of a specific point.

        Args:
            radius (int | float): The radius in meters.
            lat (int | float): The latitude of the center point.
            lon (int | float): The longitude of the center point.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If radius, lat, or lon is not a number.
            ValueError: If radius is negative, lat/lon are out of range, or another spatial filter is set.
        """
        if not all(isinstance(v, (int, float)) for v in (radius, lat, lon)):
            raise TypeError(f"radius, lat, and lon must be numbers (int or float), got radius={type(radius).__name__}, lat={type(lat).__name__}, lon={type(lon).__name__}")
        if radius < 0:
            raise ValueError(f"radius must be non-negative, got {radius}")
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ValueError(f"lat must be between -90 and 90, lon between -180 and 180, got lat={lat}, lon={lon}")
        if self._has_spatial_filter():
            raise ValueError("Only one spatial filter (bbox, area, around) can be set at a time. Unset the current spatial filter before setting a new one.")
        self.around_point = (radius, lat, lon)
        return self

    def with_around_set(self, set_name: str, radius: Union[int, float]) -> 'Relation':
        """Filter relations within a radius of a set of elements.

        Args:
            set_name (str): The name of the set to use as the center.
            radius (int | float): The radius in meters.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If set_name is not a string or radius is not a number.
            ValueError: If set_name is empty, radius is negative, or another spatial filter is set.
        """
        if not isinstance(set_name, str):
            raise TypeError(f"set_name must be a string, got {type(set_name).__name__}")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if not isinstance(radius, (int, float)) or radius < 0:
            raise ValueError(f"radius must be a non-negative number, got {radius} of type {type(radius).__name__}")
        if self._has_spatial_filter():
            raise ValueError("Only one spatial filter (bbox, area, around) can be set at a time. Unset the current spatial filter before setting a new one.")
        self.around_set = (set_name, radius)
        return self

    def with_node(self, node_id: int) -> 'Relation':
        """Filter relations that contain a specific node (e.g., 'relation(n:node_id)').

        Args:
            node_id (int): The ID of the node.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If node_id is not an integer.
            ValueError: If node_id is negative or another node filter is set.
        """
        if not isinstance(node_id, int):
            raise TypeError(f"node_id must be an integer, got {type(node_id).__name__}")
        if node_id < 0:
            raise ValueError(f"node_id must be a non-negative integer, got {node_id}")
        if self._has_node_filter():
            raise ValueError("Cannot set a node filter because another node filter is already set. Use only one node filter at a time.")
        self.node = node_id
        return self

    def with_node_from_set(self, set_name: str) -> 'Relation':
        """Filter relations that contain nodes from a set (e.g., 'relation(n.set_name)').

        Args:
            set_name (str): The name of the set containing nodes.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If set_name is not a string.
            ValueError: If set_name is empty, contains invalid characters, or another node filter is set.
        """
        if not isinstance(set_name, str):
            raise TypeError(f"set_name must be a string, got {type(set_name).__name__}")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError(f"set_name contains invalid characters for Overpass QL: {set_name}. Avoid using [], {{}}, (), or ;.")
        if self._has_node_filter():
            raise ValueError("Cannot set a node filter because another node filter is already set. Use only one node filter at a time.")
        self.node_from_set = set_name
        return self

    def with_way(self, way_id: int) -> 'Relation':
        """Filter relations that contain a specific way (e.g., 'relation(w:way_id)').

        Args:
            way_id (int): The ID of the way.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If way_id is not an integer.
            ValueError: If way_id is negative or another way filter is set.
        """
        if not isinstance(way_id, int):
            raise TypeError(f"way_id must be an integer, got {type(way_id).__name__}")
        if way_id < 0:
            raise ValueError(f"way_id must be a non-negative integer, got {way_id}")
        if self._has_way_filter():
            raise ValueError("Cannot set a way filter because another way filter is already set. Use only one way filter at a time.")
        self.way = way_id
        return self

    def with_way_from_set(self, set_name: str) -> 'Relation':
        """Filter relations that contain ways from a set (e.g., 'relation(w.set_name)').

        Args:
            set_name (str): The name of the set containing ways.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If set_name is not a string.
            ValueError: If set_name is empty, contains invalid characters, or another way filter is set.
        """
        if not isinstance(set_name, str):
            raise TypeError(f"set_name must be a string, got {type(set_name).__name__}")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError(f"set_name contains invalid characters for Overpass QL: {set_name}. Avoid using [], {{}}, (), or ;.")
        if self._has_way_filter():
            raise ValueError("Cannot set a way filter because another way filter is already set. Use only one way filter at a time.")
        self.way_from_set = set_name
        return self

    def with_relation(self, relation_id: int) -> 'Relation':
        """Filter relations that are members of a specific relation (e.g., 'relation(r:<relation_id>)').

        Args:
            relation_id (int): The ID of the parent relation.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If relation_id is not an integer.
            ValueError: If relation_id is negative or another relation filter is set.
        """
        if not isinstance(relation_id, int):
            raise TypeError(f"relation_id must be an integer, got {type(relation_id).__name__}")
        if relation_id < 0:
            raise ValueError(f"relation_id must be a non-negative integer, got {relation_id}")
        if self._has_relation_filter():
            raise ValueError("Cannot set a relation filter because another relation filter is already set. Use only one relation filter at a time.")
        self.relation = relation_id
        return self

    def with_relation_and_role(self, relation_id: int, role: str) -> 'Relation':
        """Filter relations that are members of a relation with a specific role (e.g., 'relation(r:<relation_id>,"role")').

        Args:
            relation_id (int): The ID of the parent relation.
            role (str): The role to filter by.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If relation_id is not an integer or role is not a string.
            ValueError: If relation_id is negative, role is empty, or another relation filter is set.
        """
        if not isinstance(relation_id, int):
            raise TypeError(f"relation_id must be an integer, got {type(relation_id).__name__}")
        if relation_id < 0:
            raise ValueError(f"relation_id must be a non-negative integer, got {relation_id}")
        if not isinstance(role, str) or not role.strip():
            raise ValueError("role must be a non-empty string")
        if self._has_relation_filter():
            raise ValueError("Cannot set a relation filter because another relation filter is already set. Use only one relation filter at a time.")
        self.relation_and_role = (relation_id, role)
        return self

    def with_relation_from_set(self, set_name: str) -> 'Relation':
        """Filter relations that are members of relations in a set (e.g., 'relation(r.<set_name>)').

        Args:
            set_name (str): The name of the set containing parent relations.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If set_name is not a string.
            ValueError: If set_name is empty, contains invalid characters, or another relation filter is set.
        """
        if not isinstance(set_name, str):
            raise TypeError(f"set_name must be a string, got {type(set_name).__name__}")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError(f"set_name contains invalid characters for Overpass QL: {set_name}. Avoid using [], {{}}, (), or ;.")
        if self._has_relation_filter():
            raise ValueError("Cannot set a relation filter because another relation filter is already set. Use only one relation filter at a time.")
        self.relation_from_set = set_name
        return self

    def with_members(self) -> 'Relation':
        """Include all members of the relation (downward recursion).

        Returns:
            Relation: Self, for method chaining.
        """
        self.include_members = True
        return self

    def with_parents(self) -> 'Relation':
        """Include parent relations of the relation (upward recursion).

        Returns:
            Relation: Self, for method chaining.
        """
        self.include_parents = True
        return self

    def with_user(self, username: str) -> 'Relation':
        """Filter relations edited by a specific user (e.g., '[user:username]').

        Args:
            username (str): The username to filter by.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If username is not a string.
            ValueError: If username is empty or whitespace.
        """
        if not isinstance(username, str):
            raise TypeError(f"username must be a string, got {type(username).__name__}")
        if not username.strip():
            raise ValueError("username cannot be empty or whitespace")
        self.tags.append(("user", username))
        return self

    def with_uid(self, uid: int) -> 'Relation':
        """Filter relations edited by a specific user ID (e.g., '[uid:123]').

        Args:
            uid (int): The user ID to filter by.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If uid is not an integer.
            ValueError: If uid is negative.
        """
        if not isinstance(uid, int):
            raise TypeError(f"uid must be an integer, got {type(uid).__name__}")
        if uid < 0:
            raise ValueError(f"uid must be a non-negative integer, got {uid}")
        self.tags.append(("uid", str(uid)))
        return self

    def with_newer(self, timestamp: str) -> 'Relation':
        """Filter relations newer than a timestamp (e.g., '[newer:\"2023-01-01T00:00:00Z\"]').

        Args:
            timestamp (str): The timestamp in ISO 8601 format.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If timestamp is not a string.
            ValueError: If timestamp is empty or not in ISO 8601 format.
        """
        if not isinstance(timestamp, str):
            raise TypeError(f"timestamp must be a string, got {type(timestamp).__name__}")
        if not timestamp.strip():
            raise ValueError("timestamp cannot be empty or whitespace")
        if 'T' not in timestamp or 'Z' not in timestamp:
            raise ValueError(f"timestamp must be in ISO 8601 format, e.g., '2023-01-01T00:00:00Z', got {timestamp}")
        self.tags.append(("newer", f'"{timestamp}"'))
        return self

    def with_version(self, version: int) -> 'Relation':
        """Filter relations with a specific version (e.g., '[version=2]').

        Args:
            version (int): The version number to filter by.

        Returns:
            Relation: Self, for method chaining.

        Raises:
            TypeError: If version is not an integer.
            ValueError: If version is less than 1.
        """
        if not isinstance(version, int):
            raise TypeError(f"version must be an integer, got {type(version).__name__}")
        if version < 1:
            raise ValueError(f"version must be a positive integer, got {version}")
        self.tags.append(("version", str(version)))
        return self

    def __str__(self) -> str:
        """Generate the Overpass QL query string for this Relation object.

        Returns:
            str: The Overpass QL query string.
        """
        query = ""
        if self.filter_from_set:
            query += f".{self.filter_from_set} "
        query += "relation"
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
        if self.min_members is not None:
            query += f"[if:count(members)>{self.min_members}]"
        if self.min_role_count is not None:
            role, count = self.min_role_count
            query += f'[if:count_by_role("{role}")>{count}]'
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
        if self.way is not None:
            query += f"(w:{self.way})"
        if self.way_from_set:
            query += f"(w.{self.way_from_set})"
        if self.relation is not None:
            query += f"(r:{self.relation})"
        if self.relation_and_role:
            query += f'(r:{self.relation_and_role[0]},"{self.relation_and_role[1]}")'
        if self.relation_from_set:
            query += f"(r.{self.relation_from_set})"
        
        # Handle recursion (include_members or include_parents)
        if self.include_members or self.include_parents:
            query = f"({query};"
            if self.include_members:
                query += ">"
                if self.include_parents:
                    query += ";"
            if self.include_parents:
                query += "<"
            query += ")"
        
        # Store as set
        if self._store_as_set_name:
            query += f"->.{self._store_as_set_name}"
        
        query += ";"
        return query