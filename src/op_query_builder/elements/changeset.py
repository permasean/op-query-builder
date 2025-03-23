from typing import Tuple, Optional, List, Union
from .base import Element

class Changeset(Element):
    def __init__(self) -> None:
        super().__init__()
        self.id: Optional[int] = None
        self.ids: List[int] = []
        self.tags: List[Tuple[str, str]] = []
        self.bbox: Optional[Tuple[float, float, float, float]] = None
        self.time_range: Optional[Tuple[str, str]] = None  # (start_time, end_time)
        self._store_as_set_name: Optional[str] = None
        self.filter_from_set: Optional[str] = None

    # Helper methods for filter exclusivity
    def _has_spatial_filter(self) -> bool:
        return self.bbox is not None

    def _has_time_filter(self) -> bool:
        return any(tag[0] == "time" for tag in self.tags) or self.time_range is not None

    def _update_or_append_tag(self, key: str, value: str) -> None:
        """Helper method to update an existing tag or append a new one."""
        for i, (existing_key, _) in enumerate(self.tags):
            if existing_key == key:
                self.tags[i] = (key, value)
                return
        self.tags.append((key, value))

    def with_id(self, id: int) -> 'Changeset':
        if not isinstance(id, int):
            raise TypeError("id must be of type int")
        if id < 0:
            raise ValueError("id must be a non-negative integer")
        if self.ids:
            raise ValueError("Cannot set id, field ids is already set. Choose one or the other")
        self.id = id
        return self

    def with_ids(self, ids: List[int]) -> 'Changeset':
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

    def with_tags(self, tags: List[Tuple[str, str]]) -> 'Changeset':
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

    def with_bbox(self, bbox: Tuple[float, float, float, float]) -> 'Changeset':
        if not isinstance(bbox, tuple) or len(bbox) != 4:
            raise ValueError("bbox must be a tuple of length 4")
        south, west, north, east = bbox
        if not all(isinstance(v, (int, float)) for v in bbox):
            raise TypeError("bbox values must be int or float")
        if not (-90 <= south <= north <= 90) or not (-180 <= west <= east <= 180):
            raise ValueError("Invalid bbox coordinates")
        if self._has_spatial_filter():
            raise ValueError("Only one spatial filter (bbox) can be set for changesets")
        self.bbox = bbox
        return self

    def with_user(self, username: str) -> 'Changeset':
        if not isinstance(username, str):
            raise TypeError("username must be of type str")
        if not username.strip():
            raise ValueError("username cannot be empty or whitespace")
        self._update_or_append_tag("user", username)
        return self

    def with_uid(self, uid: int) -> 'Changeset':
        if not isinstance(uid, int):
            raise TypeError("uid must be of type int")
        if uid < 0:
            raise ValueError("uid must be a non-negative integer")
        self._update_or_append_tag("uid", str(uid))
        return self

    def with_open(self, is_open: bool) -> 'Changeset':
        self._update_or_append_tag("open", "true" if is_open else "false")
        return self

    def with_time(self, timestamp: str) -> 'Changeset':
        if not isinstance(timestamp, str):
            raise TypeError("timestamp must be of type str")
        if not timestamp.strip():
            raise ValueError("timestamp cannot be empty or whitespace")
        if 'T' not in timestamp or 'Z' not in timestamp:
            raise ValueError("timestamp must be in ISO 8601 format (e.g., '2023-01-01T00:00:00Z')")
        if self._has_time_filter():
            raise ValueError("Cannot set time filter when another time filter is set")
        self._update_or_append_tag("time", f'"{timestamp}"')
        return self

    def with_time_range(self, start_time: str, end_time: str) -> 'Changeset':
        if not isinstance(start_time, str) or not isinstance(end_time, str):
            raise TypeError("start_time and end_time must be of type str")
        if not start_time.strip() or not end_time.strip():
            raise ValueError("start_time and end_time cannot be empty or whitespace")
        if 'T' not in start_time or 'Z' not in start_time or 'T' not in end_time or 'Z' not in end_time:
            raise ValueError("start_time and end_time must be in ISO 8601 format (e.g., '2023-01-01T00:00:00Z')")
        if self._has_time_filter():
            raise ValueError("Cannot set time range filter when another time filter is set")
        self.time_range = (start_time, end_time)
        return self

    def with_comment(self, comment: str) -> 'Changeset':
        if not isinstance(comment, str):
            raise TypeError("comment must be of type str")
        if not comment.strip():
            raise ValueError("comment cannot be empty or whitespace")
        self._update_or_append_tag("comment", f'"{comment}"')
        return self

    def with_created_by(self, editor: str) -> 'Changeset':
        if not isinstance(editor, str):
            raise TypeError("editor must be of type str")
        if not editor.strip():
            raise ValueError("editor cannot be empty or whitespace")
        self._update_or_append_tag("created_by", editor)
        return self

    def with_tag_exists(self, key: str) -> 'Changeset':
        if not isinstance(key, str):
            raise TypeError("key must be of type str")
        if not key.strip():
            raise ValueError("key cannot be empty or whitespace")
        self._update_or_append_tag(key, "")
        return self

    def with_tag_not_exists(self, key: str) -> 'Changeset':
        if not isinstance(key, str):
            raise TypeError("key must be of type str")
        if not key.strip():
            raise ValueError("key cannot be empty or whitespace")
        self._update_or_append_tag(f"!{key}", "")
        return self

    def with_tag_not(self, key: str, value: str) -> 'Changeset':
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("key and value must be of type str")
        if not key.strip() or not value.strip():
            raise ValueError("key and value cannot be empty or whitespace")
        self._update_or_append_tag(key, f"!={value}")
        return self

    def with_tag_regex(self, key: str, regex: str) -> 'Changeset':
        if not isinstance(key, str) or not isinstance(regex, str):
            raise TypeError("key and regex must be of type str")
        if not key.strip() or not regex.strip():
            raise ValueError("key and regex cannot be empty or whitespace")
        self._update_or_append_tag(key, f"~{regex}")
        return self

    def with_tag_condition(self, condition: str) -> 'Changeset':
        if not isinstance(condition, str):
            raise TypeError("condition must be of type str")
        if not condition.strip():
            raise ValueError("condition cannot be empty or whitespace")
        if not condition.startswith('[') or not condition.endswith(']'):
            raise ValueError("condition must be formatted as a tag filter, e.g., '[key=value]'")
        self.tag_conditions.append(condition)
        return self

    def from_set(self, set_name: str) -> 'Changeset':
        if not isinstance(set_name, str):
            raise TypeError("set_name must be of type str")
        if not set_name.strip():
            raise ValueError("set_name cannot be empty or whitespace")
        if any(char in set_name for char in '[]{}();'):
            raise ValueError("set_name contains invalid characters for Overpass QL")
        self.filter_from_set = set_name
        return self

    def store_as_set(self, set_name: str) -> 'Changeset':
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