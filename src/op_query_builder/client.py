from typing import Optional, Dict, Any
import overpy
import time
from functools import lru_cache
from op_query_builder.query import Query
from op_query_builder.elements.relation import Relation
from op_query_builder.derived.area import Area
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OverpassError(Exception):
    """Base exception for Overpass API errors."""
    pass

class OverpassSyntaxError(OverpassError):
    """Raised when the query has a syntax error."""
    pass

class OverpassRateLimitError(OverpassError):
    """Raised when the Overpass API rate limit is exceeded."""
    pass

class OverpassTimeoutError(OverpassError):
    """Raised when the Overpass API times out."""
    pass

class QueryClient:
    def __init__(
        self,
        url: str = "https://overpass-api.de/api/interpreter",
        max_retries: int = 3,
        retry_delay: float = 5.0,
    ) -> None:
        """
        Initialize the QueryClient with configurable Overpass API settings.

        Args:
            url (str): The Overpass API URL.
            max_retries (int): Maximum number of retries for transient failures.
            retry_delay (float): Delay between retries in seconds.
        """
        self.api = overpy.Overpass(url=url)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._cache: Dict[str, overpy.Result] = {}

    def execute_query(self, query: Query, use_cache: bool = True, return_raw: bool = False) -> Any:
        """
        Execute an Overpass query and return the result.

        Args:
            query (Query): The query to execute.
            use_cache (bool): Whether to use cached results if available.
            return_raw (bool): If True, return the raw response as a string; otherwise, return an overpy.Result.

        Returns:
            Any: overpy.Result object or raw response string if return_raw is True.

        Raises:
            OverpassSyntaxError: If the query has a syntax error.
            OverpassRateLimitError: If the API rate limit is exceeded.
            OverpassTimeoutError: If the API times out.
            OverpassError: For other Overpass API errors.
        """
        query_str = str(query)
        logger.info(f"Executing query: {query_str}")

        # Check cache
        if use_cache and query_str in self._cache:
            logger.info("Returning cached result")
            result = self._cache[query_str]
            return result.result if return_raw else result

        # Retry logic
        for attempt in range(self.max_retries + 1):
            try:
                result = self.api.query(query_str)
                # Cache the result
                if use_cache:
                    self._cache[query_str] = result
                return result.result if return_raw else result

            except overpy.exception.OverpassBadRequest as e:
                logger.error(f"Syntax error in query: {e}")
                raise OverpassSyntaxError(f"Syntax error: {e}")
            except overpy.exception.OverpassTooManyRequests as e:
                if attempt == self.max_retries:
                    logger.error("Rate limit exceeded after maximum retries")
                    raise OverpassRateLimitError("Rate limit exceeded")
                logger.warning(f"Rate limit exceeded, retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
            except overpy.exception.OverpassGatewayTimeout as e:
                if attempt == self.max_retries:
                    logger.error("Gateway timeout after maximum retries")
                    raise OverpassTimeoutError("Gateway timeout")
                logger.warning(f"Gateway timeout, retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise OverpassError(f"Unexpected error: {e}")

    def validate_query(self, query: Query) -> bool:
        """
        Validate the syntax of an Overpass query without executing it.

        Args:
            query (Query): The query to validate.

        Returns:
            bool: True if the query is syntactically valid, False otherwise.
        """
        query_str = str(query)
        logger.info(f"Validating query: {query_str}")
        try:
            # Use execute_query with caching to avoid redundant execution
            self.execute_query(query, use_cache=True)
            return True
        except OverpassSyntaxError:
            return False
        except OverpassError:
            # Other errors (e.g., rate limit, timeout) don't necessarily mean the syntax is invalid
            return True

    def get_admin_level(self, lat: float, lon: float, admin_level: Optional[int] = None) -> Optional[overpy.Relation]:
        """
        Find the administrative boundary containing the given point and optionally filter by admin level.

        Args:
            lat (float): Latitude of the point.
            lon (float): Longitude of the point.
            admin_level (int, optional): Specific admin level to filter (e.g., 2 for country, 4 for state).

        Returns:
            Optional[overpy.Relation]: The relation representing the administrative boundary, or None if not found.
        """
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude must be between -180 and 180")

        # Build a query to find administrative boundaries containing the point
        query = Query()
        # First, create an area from the point using a relation with boundary=administrative
        relation = Relation().with_tags([("boundary", "administrative")])
        if admin_level is not None:
            relation = relation.with_tags([("boundary", "administrative"), ("admin_level", str(admin_level))])
        query.add_relation(relation.store_as_set("admin_boundaries"))

        # Use the area to filter relations
        area = Area().from_set("admin_boundaries").with_pivot("admin_boundaries").store_as_set("area")
        query.add_area(area)

        # Query for relations containing the point
        point_relation = Relation().with_around_point(0, lat, lon).with_tags([("boundary", "administrative")])
        query.add_relation(point_relation)

        try:
            result = self.execute_query(query)
            relations = result.relations
            if not relations:
                logger.info(f"No administrative boundary found at ({lat}, {lon})")
                return None
            # Return the first matching relation (you can add logic to select the most specific if needed)
            return relations[0]
        except OverpassError as e:
            logger.error(f"Error finding admin level: {e}")
            return None

    def clear_cache(self) -> None:
        """Clear the query result cache."""
        self._cache.clear()
        logger.info("Cache cleared")