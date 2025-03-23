from typing import Optional, Union

class Adiff:
    def __init__(self, start_time: Optional[Union[str, int]] = None, end_time: Optional[Union[str, int]] = None) -> None:
        """Initialize an Adiff statement for augmented diff queries in Overpass QL.

        Args:
            start_time (Optional[Union[str, int]]): The start time or version. Can be an ISO 8601 timestamp (str) or a version number (int). Defaults to None.
            end_time (Optional[Union[str, int]]): The end time or version. Can be an ISO 8601 timestamp (str) or a version number (int). Defaults to None.

        Raises:
            ValueError: If neither start_time nor end_time is provided, or if timestamps are not in ISO 8601 format.
            TypeError: If start_time or end_time is neither a string nor an integer.
        """
        self.start_time = start_time
        self.end_time = end_time
        self._validate()

    def _validate(self) -> None:
        """Validate the Adiff statement parameters.

        Raises:
            ValueError: If neither start_time nor end_time is provided, or if timestamps are not in ISO 8601 format.
            TypeError: If start_time or end_time is neither a string nor an integer.
        """
        if self.start_time is None and self.end_time is None:
            raise ValueError("At least one of start_time or end_time must be provided for an Adiff statement.")
        for time in (self.start_time, self.end_time):
            if time is None:
                continue
            if isinstance(time, str):
                if 'T' not in time or 'Z' not in time:
                    raise ValueError(f"Timestamps must be in ISO 8601 format, e.g., '2023-01-01T00:00:00Z', got {time}")
            elif not isinstance(time, int):
                raise TypeError(f"Time must be a string (ISO 8601) or an integer (version), got {time} of type {type(time).__name__}")

    def __str__(self) -> str:
        """Generate the Overpass QL query string for this Adiff statement.

        Returns:
            str: The Overpass QL query string.
        """
        def format_time(time: Optional[Union[str, int]]) -> str:
            if time is None:
                return ""
            return f'"{time}"' if isinstance(time, str) else str(time)

        start = format_time(self.start_time)
        end = format_time(self.end_time)
        return f"adiff({start},{end});"