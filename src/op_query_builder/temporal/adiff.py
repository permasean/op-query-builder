from typing import Optional, Union

class Adiff:
    def __init__(self, start_time: Optional[Union[str, int]] = None, end_time: Optional[Union[str, int]] = None) -> None:
        self.start_time = start_time
        self.end_time = end_time
        self._validate()

    def _validate(self) -> None:
        if self.start_time is None and self.end_time is None:
            raise ValueError("At least one of start_time or end_time must be provided")
        for time in (self.start_time, self.end_time):
            if time is None:
                continue
            if isinstance(time, str):
                if 'T' not in time or 'Z' not in time:
                    raise ValueError("Timestamps must be in ISO 8601 format (e.g., '2023-01-01T00:00:00Z')")
            elif not isinstance(time, int):
                raise TypeError("Time must be a string (ISO 8601) or an integer (version)")

    def __str__(self) -> str:
        def format_time(time: Optional[Union[str, int]]) -> str:
            if time is None:
                return ""
            return f'"{time}"' if isinstance(time, str) else str(time)

        start = format_time(self.start_time)
        end = format_time(self.end_time)
        return f"adiff({start},{end});"