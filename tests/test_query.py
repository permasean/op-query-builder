import unittest
from op_query_builder.query import Query
from op_query_builder.elements.node import Node
from op_query_builder.elements.way import Way
from op_query_builder.elements.relation import Relation
from op_query_builder.elements.changeset import Changeset
from op_query_builder.derived.area import Area
from op_query_builder.temporal.adiff import Adiff
from op_query_builder.temporal.timeline import Timeline
from op_query_builder.temporal.diff import Diff
from op_query_builder.temporal.recurse import Recurse

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

    def test_with_sort_order(self):
        self.query.with_sort_order("qt")
        way = Way().with_tags([("highway", "primary")])
        self.query.add_way(way)
        expected = "[out:json];\nway[highway=primary];\nout body qt;"
        self.assertEqual(str(self.query), expected)

    def test_with_limit(self):
        self.query.with_limit(100)
        way = Way().with_tags([("highway", "primary")])
        self.query.add_way(way)
        expected = "[out:json];\nway[highway=primary];\nout body 100;"
        self.assertEqual(str(self.query), expected)

    def test_with_output_mode_count(self):
        self.query.with_output_mode("count")
        way = Way().with_tags([("highway", "primary")])
        self.query.add_way(way)
        expected = "[out:json];\nway[highway=primary];\nout count;"
        self.assertEqual(str(self.query), expected)

    def test_with_output_mode_ids(self):
        self.query.with_output_mode("ids")
        way = Way().with_tags([("highway", "primary")])
        self.query.add_way(way)
        expected = "[out:json];\nway[highway=primary];\nout ids;"
        self.assertEqual(str(self.query), expected)

    def test_combined_out_modifiers(self):
        self.query.with_output_detail("geom").with_sort_order("qt").with_limit(50)
        way = Way().with_tags([("highway", "primary")])
        self.query.add_way(way)
        expected = "[out:json];\nway[highway=primary];\nout geom qt 50;"
        self.assertEqual(str(self.query), expected)

    def test_with_setting_maxsize(self):
        self.query.with_setting("maxsize", "1000000")
        way = Way().with_tags([("highway", "primary")])
        self.query.add_way(way)
        expected = "[out:json maxsize:1000000];\nway[highway=primary];\nout body;"
        self.assertEqual(str(self.query), expected)

    def test_with_setting_diff(self):
        self.query.with_setting("diff", "2023-01-01T00:00:00Z")
        way = Way().with_tags([("highway", "primary")])
        self.query.add_way(way)
        expected = '[out:json diff:"2023-01-01T00:00:00Z"];\nway[highway=primary];\nout body;'
        self.assertEqual(str(self.query), expected)

    def test_add_adiff(self):
        adiff = Adiff("2023-01-01T00:00:00Z", "2023-12-31T23:59:59Z")
        self.query.add_adiff(adiff)
        expected = '[out:json];\nadiff("2023-01-01T00:00:00Z","2023-12-31T23:59:59Z");\nout body;'
        self.assertEqual(str(self.query), expected)

    def test_add_timeline(self):
        node = Node().with_id(123)
        timeline = Timeline(node)
        self.query.add_timeline(timeline)
        expected = "[out:json];\ntimeline(node(123));\nout body;"
        self.assertEqual(str(self.query), expected)

    def test_add_diff(self):
        diff = Diff("2023-01-01T00:00:00Z", "2023-12-31T23:59:59Z")
        self.query.add_diff(diff)
        expected = '[out:json];\ndiff("2023-01-01T00:00:00Z","2023-12-31T23:59:59Z");\nout body;'
        self.assertEqual(str(self.query), expected)

    def test_add_recurse(self):
        recurse = Recurse(">>", "boundary_set")
        self.query.add_recurse(recurse)
        expected = "[out:json];\n.boundary_set >>;\nout body;"
        self.assertEqual(str(self.query), expected)

    def test_combined_elements_with_temporal(self):
        node = Node().with_id(123)
        timeline = Timeline(node)
        way = Way().with_tags([("highway", "primary")])
        self.query.add_timeline(timeline).add_way(way)
        expected = "[out:json];\ntimeline(node(123));\nway[highway=primary];\nout body;"
        self.assertEqual(str(self.query), expected)

    def test_combined_elements_with_diff(self):
        node = Node().with_id(123)
        diff = Diff("2023-01-01T00:00:00Z", "2023-12-31T23:59:59Z")
        self.query.add_diff(diff).add_node(node)
        expected = '[out:json];\ndiff("2023-01-01T00:00:00Z","2023-12-31T23:59:59Z");\nnode(123);\nout body;'
        self.assertEqual(str(self.query), expected)

    def test_combined_elements_with_recurse(self):
        relation = Relation().with_tags([("type", "boundary")])
        recurse = Recurse(">>")
        self.query.add_relation(relation).add_recurse(recurse)
        expected = '[out:json];\nrelation[type=boundary];\n>>;\nout body;'
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