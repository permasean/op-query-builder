import unittest
from unittest.mock import patch, PropertyMock
import overpy
from op_query_builder.query import Query
from op_query_builder.elements.way import Way
from op_query_builder.client import QueryClient, OverpassSyntaxError, OverpassRateLimitError, OverpassTimeoutError

class TestQueryClient(unittest.TestCase):
    def setUp(self):
        """Set up a QueryClient instance for each test."""
        self.client = QueryClient(max_retries=2, retry_delay=0.1)

    def test_execute_query_success(self):
        query = Query()
        way = Way().with_tags([("highway", "primary")])
        query.add_way(way)

        with patch.object(overpy.Overpass, 'query', return_value=overpy.Result()) as mock_query:
            result = self.client.execute_query(query)
            self.assertIsInstance(result, overpy.Result)
            mock_query.assert_called_once_with(str(query))

    def test_execute_query_with_timeout(self):
        query = Query().with_timeout(60)
        way = Way().with_tags([("highway", "primary")])
        query.add_way(way)

        with patch.object(overpy.Overpass, 'query', return_value=overpy.Result()) as mock_query:
            result = self.client.execute_query(query)
            self.assertIsInstance(result, overpy.Result)
            expected_query = "[out:json timeout:60];\nway[highway=primary];\nout body;"
            mock_query.assert_called_once_with(expected_query)

    def test_execute_query_with_cache(self):
        query = Query()
        way = Way().with_tags([("highway", "primary")])
        query.add_way(way)

        with patch.object(overpy.Overpass, 'query', return_value=overpy.Result()) as mock_query:
            # First execution: should call the API
            result1 = self.client.execute_query(query, use_cache=True)
            self.assertIsInstance(result1, overpy.Result)
            mock_query.assert_called_once_with(str(query))

            # Second execution: should use cache
            result2 = self.client.execute_query(query, use_cache=True)
            self.assertIs(result1, result2)  # Same object (cached)
            mock_query.assert_called_once()  # No additional API call

    def test_execute_query_syntax_error(self):
        query = Query()  # Invalid query (empty)
        with patch.object(overpy.Overpass, 'query', side_effect=overpy.exception.OverpassBadRequest("Invalid query")):
            with self.assertRaises(OverpassSyntaxError):
                self.client.execute_query(query)

    def test_execute_query_rate_limit_with_retry(self):
        query = Query()
        way = Way().with_tags([("highway", "primary")])
        query.add_way(way)

        with patch.object(overpy.Overpass, 'query', side_effect=[overpy.exception.OverpassTooManyRequests(), overpy.Result()]) as mock_query:
            result = self.client.execute_query(query)
            self.assertIsInstance(result, overpy.Result)
            self.assertEqual(mock_query.call_count, 2)  # Retried once

    def test_execute_query_rate_limit_exceeded(self):
        query = Query()
        way = Way().with_tags([("highway", "primary")])
        query.add_way(way)

        with patch.object(overpy.Overpass, 'query', side_effect=overpy.exception.OverpassTooManyRequests()):
            with self.assertRaises(OverpassRateLimitError):
                self.client.execute_query(query)

    def test_execute_query_timeout_with_retry(self):
        query = Query()
        way = Way().with_tags([("highway", "primary")])
        query.add_way(way)

        with patch.object(overpy.Overpass, 'query', side_effect=[overpy.exception.OverpassGatewayTimeout(), overpy.Result()]) as mock_query:
            result = self.client.execute_query(query)
            self.assertIsInstance(result, overpy.Result)
            self.assertEqual(mock_query.call_count, 2)  # Retried once

    def test_validate_query_valid(self):
        query = Query()
        way = Way().with_tags([("highway", "primary")])
        query.add_way(way)

        with patch.object(overpy.Overpass, 'query', return_value=overpy.Result()):
            self.assertTrue(self.client.validate_query(query))

    def test_validate_query_invalid(self):
        query = Query()
        with patch.object(overpy.Overpass, 'query', side_effect=overpy.exception.OverpassBadRequest("Invalid query")):
            self.assertFalse(self.client.validate_query(query))

    def test_get_admin_level(self):
        # Mock a result with a relation
        mock_relation = overpy.Relation(attributes={"id": 123}, tags={"boundary": "administrative", "admin_level": "2"})
        mock_result = overpy.Result()
        with patch('overpy.Result.relations', new_callable=PropertyMock, return_value=[mock_relation]):
            with patch.object(overpy.Overpass, 'query', return_value=mock_result):
                result = self.client.get_admin_level(51.5, -0.1, admin_level=2)
                self.assertIsNotNone(result)
                self.assertEqual(result.attributes["id"], 123)
                self.assertEqual(result.tags["admin_level"], "2")

    def test_get_admin_level_not_found(self):
        mock_result = overpy.Result()
        with patch('overpy.Result.relations', new_callable=PropertyMock, return_value=[]):
            with patch.object(overpy.Overpass, 'query', return_value=mock_result):
                result = self.client.get_admin_level(51.5, -0.1)
                self.assertIsNone(result)

    def test_clear_cache(self):
        query = Query()
        way = Way().with_tags([("highway", "primary")])
        query.add_way(way)

        with patch.object(overpy.Overpass, 'query', return_value=overpy.Result()) as mock_query:
            # First execution: should call the API
            self.client.execute_query(query, use_cache=True)
            mock_query.assert_called_once()

            # Clear cache
            self.client.clear_cache()

            # Second execution: should call the API again (cache cleared)
            self.client.execute_query(query, use_cache=True)
            self.assertEqual(mock_query.call_count, 2)

if __name__ == "__main__":
    unittest.main()