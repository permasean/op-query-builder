import unittest
from op_query_builder.query import Query
from op_query_builder.elements.node import Node
from op_query_builder.elements.way import Way
from op_query_builder.elements.relation import Relation
from op_query_builder.elements.changeset import Changeset
from op_query_builder.derived.area import Area

class TestQuery(unittest.TestCase):
    def setUp(self):
        """Set up a basic Query instance for each test."""
        self.query = Query()

    def test_basic_query(self):
        way = Way().with_tags([("highway", "primary")])
        self.query.add_way(way)
        expected = "[out:json];\nway[highway=primary];\nout body;"
        self.assertEqual(str(self.query), expected)

    def test_with_output(self):
        self.query.with_output("xml")
        way = Way().with_tags([("highway", "primary")])
        self.query.add_way(way)
        expected = "[out:xml];\nway[highway=primary];\nout body;"
        self.assertEqual(str(self.query), expected)

    def test_with_timeout(self):
        self.query.with_timeout(60)
        way = Way().with_tags([("highway", "primary")])
        self.query.add_way(way)
        expected = "[out:json timeout:60];\nway[highway=primary];\nout body;"
        self.assertEqual(str(self.query), expected)

    def test_with_date(self):
        self.query.with_date("2023-01-01T00:00:00Z")
        way = Way().with_tags([("highway", "primary")])
        self.query.add_way(way)
        expected = '[out:json date:"2023-01-01T00:00:00Z"];\nway[highway=primary];\nout body;'
        self.assertEqual(str(self.query), expected)

    def test_with_date_invalid(self):
        with self.assertRaises(ValueError):
            self.query.with_date("2023-01-01")  # Missing 'T' and 'Z'

    def test_with_global_bbox(self):
        self.query.with_global_bbox((51.0, -0.2, 51.1, -0.1))
        way = Way().with_tags([("highway", "primary")])
        self.query.add_way(way)
        expected = "[out:json bbox:51.0,-0.2,51.1,-0.1];\nway[highway=primary];\nout body;"
        self.assertEqual(str(self.query), expected)

    def test_with_output_detail(self):
        self.query.with_output_detail("geom")
        way = Way().with_tags([("highway", "primary")])
        self.query.add_way(way)
        expected = "[out:json];\nway[highway=primary];\nout geom;"
        self.assertEqual(str(self.query), expected)

    def test_add_changeset(self):
        changeset = Changeset().with_user("JohnDoe")
        self.query.add_changeset(changeset)
        expected = "[out:json];\nchangeset[user=JohnDoe];\nout body;"
        self.assertEqual(str(self.query), expected)

    def test_add_union(self):
        way1 = Way().with_tags([("highway", "primary")])
        way2 = Way().with_tags([("highway", "secondary")])
        self.query.add_union(way1, way2)
        expected = "[out:json];\n(way[highway=primary]; way[highway=secondary];);\nout body;"
        self.assertEqual(str(self.query), expected)

    def test_add_union_empty(self):
        with self.assertRaises(ValueError):
            self.query.add_union()

    def test_add_difference(self):
        way1 = Way().with_tags([("highway", "primary")])
        way2 = Way().with_tags([("highway", "secondary")])
        self.query.add_difference(way1, way2)
        expected = "[out:json];\n(way[highway=primary]; - way[highway=secondary];);\nout body;"
        self.assertEqual(str(self.query), expected)

    def test_add_difference_empty_subtract(self):
        way1 = Way().with_tags([("highway", "primary")])
        with self.assertRaises(ValueError):
            self.query.add_difference(way1)

    def test_combined_elements(self):
        area = Area().with_id(3600000000).store_as_set("berlin_area")
        way1 = Way().with_tags([("highway", "primary")]).with_area_by_name("berlin_area")
        way2 = Way().with_tags([("highway", "secondary")]).with_area_by_name("berlin_area")
        self.query.add_area(area).add_union(way1, way2)
        expected = "[out:json];\narea(3600000000)->.berlin_area;\n(way[highway=primary](area.berlin_area); way[highway=secondary](area.berlin_area););\nout body;"
        self.assertEqual(str(self.query), expected)

    def test_add_is_in(self):
        self.query.add_is_in(51.5, -0.1, "areas")
        expected = "[out:json];\nis_in(51.5,-0.1)->.areas;\nout body;"
        self.assertEqual(str(self.query), expected)

    def test_add_foreach(self):
        self.query.with_output_detail(None)  # Disable the top-level out statement
        subquery = Query()
        node = Node().with_tags([("amenity", "restaurant")])
        subquery.add_node(node)
        self.query.add_foreach("ways", subquery)
        expected = "[out:json];\n.ways foreach {\n  node[amenity=restaurant];\n};"
        self.assertEqual(str(self.query), expected)

    def test_add_convert(self):
        self.query.add_convert("node", "converted_nodes", ["::id=way.id", "highway=way.highway"])
        expected = "[out:json];\nconvert node ::id=way.id, highway=way.highway->.converted_nodes;\nout body;"
        self.assertEqual(str(self.query), expected)

if __name__ == "__main__":
    unittest.main()