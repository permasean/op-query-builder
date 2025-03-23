from typing import Tuple, Optional
from .base import Element

class Node(Element):
    def __init__(self) -> None:
        super().__init__()
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

    # Helper method to check spatial filter exclusivity
    def _has_spatial_filter(self) -> bool:
        return any([self.bbox, self.area_id, self.area_name, self.around_point, self.around_set])

    # Helper method to check relation/way filter exclusivity
    def _has_relation_filter(self) -> bool:
        return any([self.relation, self.relation_and_role, self.relation_from_set])

    def _has_way_filter(self) -> bool:
        return any([self.way, self.way_from_set])

    def with_bbox(self, bbox: Tuple[int | float, int | float, int | float, int | float]) -> 'Node':
        """Set a bounding box to filter nodes geographically.

        Args:
            bbox (Tuple[float, float, float, float]): A tuple of (south, west, north, east) coordinates.

        Returns:
            Node: Self, for method chaining.

        Raises:
            ValueError: If bbox is not a tuple of length 4 or if coordinates are invalid.
            TypeError: If bbox values are not numbers.
        """
        if not isinstance(bbox, Tuple) or len(bbox) != 4:
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
    
    def with_area_by_id(self, area_id: int) -> 'Node':
        """Filter nodes within a specific area by area ID.

        Args:
            area_id (int): The area ID to filter by.

        Returns:
            Node: Self, for method chaining.

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
    
    def with_area_by_name(self, area_name: str) -> 'Node':
        """Filter nodes within a named area.

        Args:
            area_name (str): The name of the area set to filter by.

        Returns:
            Node: Self, for method chaining.

        Raises:
            TypeError: If area_name is not a string.
            ValueError: If area_name is empty, whitespace, contains invalid characters, or another spatial filter is set.
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
    
    def with_around_point(self, radius: int|float, lat: int|float, lon: int|float) -> 'Node':
        """Filter nodes within a radius of a specific point.

        Args:
            radius (int | float): The radius in meters.
            lat (int | float): The latitude of the center point.
            lon (int | float): The longitude of the center point.

        Returns:
            Node: Self, for method chaining.

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
    
    def with_around_set(self, set_name: str, radius: int | float) -> 'Node':
        """Filter nodes within a radius of a set of elements.

        Args:
            set_name (str): The name of the set to use as the center.
            radius (int | float): The radius in meters.

        Returns:
            Node: Self, for method chaining.

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
    
    def with_relation(self, relation_id: int) -> 'Node':
        """Filter nodes that are members of a specific relation (e.g., 'node(r:<relation_id>)').

        Args:
            relation_id (int): The ID of the relation.

        Returns:
            Node: Self, for method chaining.

        Raises:
            TypeError: If relation_id is not an integer.
            ValueError: If relation_id is negative or another relation/way filter is set.
        """
        if not isinstance(relation_id, int):
            raise TypeError(f"relation_id must be an integer, got {type(relation_id).__name__}")
        if relation_id < 0:
            raise ValueError(f"relation_id must be a non-negative integer, got {relation_id}")
        if self._has_relation_filter() or self._has_way_filter():
            raise ValueError("Cannot set a relation filter because another relation or way filter is already set. Use only one relation or way filter at a time.")
        self.relation = relation_id
        return self
    
    def with_relation_and_role(self, relation_id: int, role: str) -> 'Node':
        """Filter nodes that are members of a relation with a specific role (e.g., 'node(r:<relation_id>,"role")').

        Args:
            relation_id (int): The ID of the relation.
            role (str): The role to filter by.

        Returns:
            Node: Self, for method chaining.

        Raises:
            TypeError: If relation_id is not an integer or role is not a string.
            ValueError: If relation_id is negative, role is empty, or another relation/way filter is set.
        """
        if not isinstance(relation_id, int):
            raise TypeError(f"relation_id must be an integer, got {type(relation_id).__name__}")
        if relation_id < 0:
            raise ValueError(f"relation_id must be a non-negative integer, got {relation_id}")
        if not isinstance(role, str) or not role.strip():
            raise ValueError("role must be a non-empty string")
        if self._has_relation_filter() or self._has_way_filter():
            raise ValueError("Cannot set a relation filter because another relation or way filter is already set. Use only one relation or way filter at a time.")
        self.relation_and_role = (relation_id, role)
        return self
    
    def with_relation_from_set(self, set_name: str) -> 'Node':
        """Filter nodes that are members of relations in a set (e.g., 'node(r.<set_name>)').

        Args:
            set_name (str): The name of the set containing relations.

        Returns:
            Node: Self, for method chaining.

        Raises:
            TypeError: If set_name is not a string.
            ValueError: If set_name is empty, contains invalid characters, or another relation/way filter is set.
        """
        if not isinstance(set_name, str):
            raise TypeError(f"set_name must be a string, got {type(set_name).__name__}")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError(f"set_name contains invalid characters for Overpass QL: {set_name}. Avoid using [], {{}}, (), or ;.")
        if self._has_relation_filter() or self._has_way_filter():
            raise ValueError("Cannot set a relation filter because another relation or way filter is already set. Use only one relation or way filter at a time.")
        self.relation_from_set = set_name
        return self
    
    def with_way(self, way_id: int) -> 'Node':
        """Filter nodes that are part of a specific way (e.g., 'node(w:<way_id>)').

        Args:
            way_id (int): The ID of the way.

        Returns:
            Node: Self, for method chaining.

        Raises:
            TypeError: If way_id is not an integer.
            ValueError: If way_id is negative or another way/relation filter is set.
        """
        if not isinstance(way_id, int):
            raise TypeError(f"way_id must be an integer, got {type(way_id).__name__}")
        if way_id < 0:
            raise ValueError(f"way_id must be a non-negative integer, got {way_id}")
        if self._has_way_filter() or self._has_relation_filter():
            raise ValueError("Cannot set a way filter because another way or relation filter is already set. Use only one way or relation filter at a time.")
        self.way = way_id
        return self
    
    def with_way_from_set(self, set_name: str) -> 'Node':
        """Filter nodes that are part of ways in a set (e.g., 'node(w.<set_name>)').

        Args:
            set_name (str): The name of the set containing ways.

        Returns:
            Node: Self, for method chaining.

        Raises:
            TypeError: If set_name is not a string.
            ValueError: If set_name is empty, contains invalid characters, or another way/relation filter is set.
        """
        if not isinstance(set_name, str):
            raise TypeError(f"set_name must be a string, got {type(set_name).__name__}")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError(f"set_name contains invalid characters for Overpass QL: {set_name}. Avoid using [], {{}}, (), or ;.")
        if self._has_way_filter() or self._has_relation_filter():
            raise ValueError("Cannot set a way filter because another way or relation filter is already set. Use only one way or relation filter at a time.")
        self.way_from_set = set_name
        return self
    
    def with_user(self, username: str) -> 'Node':
        """Filter nodes edited by a specific user (e.g., '[user:username]').

        Args:
            username (str): The username to filter by.

        Returns:
            Node: Self, for method chaining.

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

    def with_uid(self, uid: int) -> 'Node':
        """Filter nodes edited by a specific user ID (e.g., '[uid:123]').

        Args:
            uid (int): The user ID to filter by.

        Returns:
            Node: Self, for method chaining.

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

    def with_newer(self, timestamp: str) -> 'Node':
        """Filter nodes newer than a timestamp (e.g., '[newer:\"2023-01-01T00:00:00Z\"]').

        Args:
            timestamp (str): The timestamp in ISO 8601 format.

        Returns:
            Node: Self, for method chaining.

        Raises:
            TypeError: If timestamp is not a string.
            ValueError: If timestamp is empty or not in ISO 8601 format.
        """
        if not isinstance(timestamp, str):
            raise TypeError(f"timestamp must be a string, got {type(timestamp).__name__}")
        if not timestamp.strip():
            raise ValueError("timestamp cannot be empty or whitespace")
        # Basic ISO 8601 check (could be stricter with regex)
        if 'T' not in timestamp or 'Z' not in timestamp:
            raise ValueError("timestamp must be in ISO 8601 format, e.g., '2023-01-01T00:00:00Z', got {timestamp}")
        self.tags.append(("newer", f'"{timestamp}"'))
        return self

    def with_version(self, version: int) -> 'Node':
        """Filter nodes with a specific version (e.g., '[version=2]').

        Args:
            version (int): The version number to filter by.

        Returns:
            Node: Self, for method chaining.

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
        """Generate the Overpass QL query string for this Node object.

        Returns:
            str: The Overpass QL query string.
        """
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
        if self._store_as_set_name:
            query += f"->.{self._store_as_set_name}"
        
        # Terminate the query
        query += ";"
        
        return query