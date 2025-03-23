from typing import Tuple, Optional, List, Union
from .base import Element

class Changeset(Element):
    def __init__(self) -> None:
        super().__init__()
        self.bbox: Optional[Tuple[float, float, float, float]] = None
        self.time_range: Optional[Tuple[str, str]] = None  # (start_time, end_time)

    # Helper methods for filter exclusivity
    def _has_spatial_filter(self) -> bool:
        return self.bbox is not None

    def _has_time_filter(self) -> bool:
        return any(tag[0] == "time" for tag in self.tags) or self.time_range is not None

    def with_bbox(self, bbox: Tuple[float, float, float, float]) -> 'Changeset':
        """Set a bounding box to filter changesets geographically.

        Args:
            bbox (Tuple[float, float, float, float]): A tuple of (south, west, north, east) coordinates.

        Returns:
            Changeset: Self, for method chaining.

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
            raise ValueError("Only one spatial filter (bbox) can be set for changesets. Unset the current bbox before setting a new one.")
        self.bbox = bbox
        return self

    def with_user(self, username: str) -> 'Changeset':
        """Filter changesets edited by a specific user (e.g., '[user:username]').

        Args:
            username (str): The username to filter by.

        Returns:
            Changeset: Self, for method chaining.

        Raises:
            TypeError: If username is not a string.
            ValueError: If username is empty or whitespace.
        """
        if not isinstance(username, str):
            raise TypeError(f"username must be a string, got {type(username).__name__}")
        if not username.strip():
            raise ValueError("username cannot be empty or whitespace")
        self._update_or_append_tag("user", username)
        return self

    def with_uid(self, uid: int) -> 'Changeset':
        """Filter changesets edited by a specific user ID (e.g., '[uid:123]').

        Args:
            uid (int): The user ID to filter by.

        Returns:
            Changeset: Self, for method chaining.

        Raises:
            TypeError: If uid is not an integer.
            ValueError: If uid is negative.
        """
        if not isinstance(uid, int):
            raise TypeError(f"uid must be an integer, got {type(uid).__name__}")
        if uid < 0:
            raise ValueError(f"uid must be a non-negative integer, got {uid}")
        self._update_or_append_tag("uid", str(uid))
        return self

    def with_open(self, is_open: bool) -> 'Changeset':
        """Filter changesets based on whether they are open or closed (e.g., '[open=true]').

        Args:
            is_open (bool): True to filter for open changesets, False for closed changesets.

        Returns:
            Changeset: Self, for method chaining.
        """
        self._update_or_append_tag("open", "true" if is_open else "false")
        return self

    def with_time(self, timestamp: str) -> 'Changeset':
        """Filter changesets active at a specific timestamp (e.g., '[time:"2023-01-01T00:00:00Z"]').

        Args:
            timestamp (str): The timestamp in ISO 8601 format.

        Returns:
            Changeset: Self, for method chaining.

        Raises:
            TypeError: If timestamp is not a string.
            ValueError: If timestamp is empty, not in ISO 8601 format, or another time filter is set.
        """
        if not isinstance(timestamp, str):
            raise TypeError(f"timestamp must be a string, got {type(timestamp).__name__}")
        if not timestamp.strip():
            raise ValueError("timestamp cannot be empty or whitespace")
        if 'T' not in timestamp or 'Z' not in timestamp:
            raise ValueError(f"timestamp must be in ISO 8601 format, e.g., '2023-01-01T00:00:00Z', got {timestamp}")
        if self._has_time_filter():
            raise ValueError("Cannot set a time filter because another time filter (time or time_range) is already set. Use only one time filter at a time.")
        self._update_or_append_tag("time", f'"{timestamp}"')
        return self

    def with_time_range(self, start_time: str, end_time: str) -> 'Changeset':
        """Filter changesets active within a specific time range (e.g., '[time>="2023-01-01T00:00:00Z"][time<="2023-12-31T23:59:59Z"]').

        Args:
            start_time (str): The start timestamp in ISO 8601 format.
            end_time (str): The end timestamp in ISO 8601 format.

        Returns:
            Changeset: Self, for method chaining.

        Raises:
            TypeError: If start_time or end_time is not a string.
            ValueError: If timestamps are empty, not in ISO 8601 format, or another time filter is set.
        """
        if not isinstance(start_time, str) or not isinstance(end_time, str):
            raise TypeError(f"start_time and end_time must be strings, got start_time={type(start_time).__name__}, end_time={type(end_time).__name__}")
        if not start_time.strip() or not end_time.strip():
            raise ValueError("start_time and end_time cannot be empty or whitespace")
        if 'T' not in start_time or 'Z' not in start_time or 'T' not in end_time or 'Z' not in end_time:
            raise ValueError(f"start_time and end_time must be in ISO 8601 format, e.g., '2023-01-01T00:00:00Z', got start_time={start_time}, end_time={end_time}")
        if self._has_time_filter():
            raise ValueError("Cannot set a time range filter because another time filter (time or time_range) is already set. Use only one time filter at a time.")
        self.time_range = (start_time, end_time)
        return self

    def with_comment(self, comment: str) -> 'Changeset':
        """Filter changesets with a specific comment (e.g., '[comment:"Added new roads"]').

        Args:
            comment (str): The comment to filter by.

        Returns:
            Changeset: Self, for method chaining.

        Raises:
            TypeError: If comment is not a string.
            ValueError: If comment is empty or whitespace.
        """
        if not isinstance(comment, str):
            raise TypeError(f"comment must be a string, got {type(comment).__name__}")
        if not comment.strip():
            raise ValueError("comment cannot be empty or whitespace")
        self._update_or_append_tag("comment", f'"{comment}"')
        return self

    def with_created_by(self, editor: str) -> 'Changeset':
        """Filter changesets created by a specific editor (e.g., '[created_by:JOSM]').

        Args:
            editor (str): The editor name to filter by (e.g., 'JOSM', 'iD').

        Returns:
            Changeset: Self, for method chaining.

        Raises:
            TypeError: If editor is not a string.
            ValueError: If editor is empty or whitespace.
        """
        if not isinstance(editor, str):
            raise TypeError(f"editor must be a string, got {type(editor).__name__}")
        if not editor.strip():
            raise ValueError("editor cannot be empty or whitespace")
        self._update_or_append_tag("created_by", editor)
        return self

    def __str__(self) -> str:
        """Generate the Overpass QL query string for this Changeset object.

        Returns:
            str: The Overpass QL query string.
        """
        query = ""
        if self.filter_from_set:
            query += f".{self.filter_from_set} "
        query += "changeset"
        if self.id is not None:
            query += f"({self.id})"
        elif self.ids:
            query += f"({','.join(map(str, self.ids))})"
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
        if self.time_range:
            start_time, end_time = self.time_range
            query += f'[time>="{start_time}"][time<="{end_time}"]'
        if self.bbox:
            query += f"({','.join(map(str, self.bbox))})"
        if self._store_as_set_name:
            query += f"->.{self._store_as_set_name}"
        query += ";"
        return query