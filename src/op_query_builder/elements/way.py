from typing import Tuple, Optional, List, Union
from .base import Element

class Way(Element):
    def __init__(self) -> None:
        super().__init__()
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

    def with_bbox(self, bbox: Tuple[float, float, float, float]) -> 'Way':
        """Set a bounding box to filter ways geographically.

        Args:
            bbox (Tuple[float, float, float, float]): A tuple of (south, west, north, east) coordinates.

        Returns:
            Way: Self, for method chaining.

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

    def with_area_by_id(self, area_id: int) -> 'Way':
        """Filter ways within a specific area by area ID.

        Args:
            area_id (int): The area ID to filter by.

        Returns:
            Way: Self, for method chaining.

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

    def with_area_by_name(self, area_name: str) -> 'Way':
        """Filter ways within a named area.

        Args:
            area_name (str): The name of the area set to filter by.

        Returns:
            Way: Self, for method chaining.

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

    def with_around_point(self, radius: Union[int, float], lat: Union[int, float], lon: Union[int, float]) -> 'Way':
        """Filter ways within a radius of a specific point.

        Args:
            radius (int | float): The radius in meters.
            lat (int | float): The latitude of the center point.
            lon (int | float): The longitude of the center point.

        Returns:
            Way: Self, for method chaining.

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

    def with_around_set(self, set_name: str, radius: Union[int, float]) -> 'Way':
        """Filter ways within a radius of a set of elements.

        Args:
            set_name (str): The name of the set to use as the center.
            radius (int | float): The radius in meters.

        Returns:
            Way: Self, for method chaining.

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

    def with_node(self, node_id: int) -> 'Way':
        """Filter ways that contain a specific node (e.g., 'way(n:node_id)').

        Args:
            node_id (int): The ID of the node.

        Returns:
            Way: Self, for method chaining.

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

    def with_node_from_set(self, set_name: str) -> 'Way':
        """Filter ways that contain nodes from a set (e.g., 'way(n.set_name)').

        Args:
            set_name (str): The name of the set containing nodes.

        Returns:
            Way: Self, for method chaining.

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

    def with_relation(self, relation_id: int) -> 'Way':
        """Filter ways that are members of a specific relation (e.g., 'way(r:<relation_id>)').

        Args:
            relation_id (int): The ID of the relation.

        Returns:
            Way: Self, for method chaining.

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

    def with_relation_and_role(self, relation_id: int, role: str) -> 'Way':
        """Filter ways that are members of a relation with a specific role (e.g., 'way(r:<relation_id>,"role")').

        Args:
            relation_id (int): The ID of the relation.
            role (str): The role to filter by.

        Returns:
            Way: Self, for method chaining.

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

    def with_relation_from_set(self, set_name: str) -> 'Way':
        """Filter ways that are members of relations in a set (e.g., 'way(r.<set_name>)').

        Args:
            set_name (str): The name of the set containing relations.

        Returns:
            Way: Self, for method chaining.

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

    def with_closed(self, is_closed: bool = True) -> 'Way':
        """Filter for closed ways (e.g., polygons).

        Args:
            is_closed (bool, optional): Whether to filter for closed ways (True) or non-closed ways (False). Defaults to True.

        Returns:
            Way: Self, for method chaining.
        """
        self.is_closed = is_closed
        return self

    def with_min_length(self, length: float) -> 'Way':
        """Filter ways with a minimum length in meters.

        Args:
            length (float): The minimum length in meters.

        Returns:
            Way: Self, for method chaining.

        Raises:
            TypeError: If length is not a number.
            ValueError: If length is negative.
        """
        if not isinstance(length, (int, float)):
            raise TypeError(f"length must be a number (int or float), got {type(length).__name__}")
        if length < 0:
            raise ValueError(f"length must be non-negative, got {length}")
        self.min_length = length
        return self

    def with_min_nodes(self, node_count: int) -> 'Way':
        """Filter ways with a minimum number of nodes.

        Args:
            node_count (int): The minimum number of nodes.

        Returns:
            Way: Self, for method chaining.

        Raises:
            TypeError: If node_count is not an integer.
            ValueError: If node_count is less than 1.
        """
        if not isinstance(node_count, int):
            raise TypeError(f"node_count must be an integer, got {type(node_count).__name__}")
        if node_count < 1:
            raise ValueError(f"node_count must be a positive integer, got {node_count}")
        self.min_nodes = node_count
        return self

    def with_nodes(self) -> 'Way':
        """Include all nodes of the way (downward recursion).

        Returns:
            Way: Self, for method chaining.
        """
        self.include_nodes = True
        return self

    def with_parents(self) -> 'Way':
        """Include parent relations of the way (upward recursion).

        Returns:
            Way: Self, for method chaining.
        """
        self.include_parents = True
        return self

    def with_user(self, username: str) -> 'Way':
        """Filter ways edited by a specific user (e.g., '[user:username]').

        Args:
            username (str): The username to filter by.

        Returns:
            Way: Self, for method chaining.

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

    def with_uid(self, uid: int) -> 'Way':
        """Filter ways edited by a specific user ID (e.g., '[uid:123]').

        Args:
            uid (int): The user ID to filter by.

        Returns:
            Way: Self, for method chaining.

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

    def with_newer(self, timestamp: str) -> 'Way':
        """Filter ways newer than a timestamp (e.g., '[newer:\"2023-01-01T00:00:00Z\"]').

        Args:
            timestamp (str): The timestamp in ISO 8601 format.

        Returns:
            Way: Self, for method chaining.

        Raises:
            TypeError: If timestamp is not a string.
            ValueError: If timestamp is empty or not in ISO 8601 format.
        """
        if not isinstance(timestamp, str):
            raise TypeError(f"timestamp must be a string, got {type(timestamp).__name__}")
        if not timestamp.strip():
            raise ValueError("timestamp cannot be empty or whitespace")
        if 'T' not in timestamp or 'Z' not in timestamp:
            raise ValueError("timestamp must be in ISO 8601 format, e.g., '2023-01-01T00:00:00Z', got {timestamp}")
        self.tags.append(("newer", f'"{timestamp}"'))
        return self

    def with_version(self, version: int) -> 'Way':
        """Filter ways with a specific version (e.g., '[version=2]').

        Args:
            version (int): The version number to filter by.

        Returns:
            Way: Self, for method chaining.

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
        """Generate the Overpass QL query string for this Way object.

        Returns:
            str: The Overpass QL query string.
        """
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
                    query += ";"
            if self.include_parents:
                query += "<"
            query += ")"
        
        # Store as set
        if self._store_as_set_name:
            query += f"->.{self._store_as_set_name}"
        
        query += ";"
        return query