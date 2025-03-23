import unittest
from op_query_builder.elements.way import Way

class TestWay(unittest.TestCase):
    def setUp(self):
        """Set up a basic Way instance for each test."""
        self.way = Way()
        self.tagged_way = Way().with_tags([("highway", "primary")])

    def test_store_as_set(self):
        way = self.way.store_as_set("output_set")
        self.assertEqual(str(way), "way->.output_set;")
        self.assertIsInstance(way, Way, "store_as_set should return Way instance")

    def test_complex_query(self):
        way = self.way
        print("After init:", way)
        way = way.from_set("input")
        print("After from_set:", way)
        way = way.with_id(123)
        print("After with_id:", way)
        way = way.with_tags([("highway", "primary")])
        print("After with_tags:", way)
        way = way.with_user("JohnDoe")
        print("After with_user:", way)
        way = way.store_as_set("output")
        print("After store_as_set:", way)
        self.assertEqual(str(way), ".input way(123)[highway=primary][user=JohnDoe]->.output;")

    def test_with_user_alone(self):
        way = self.way.with_user("JohnDoe")
        self.assertEqual(str(way), "way[user=JohnDoe];")

    def test_with_id(self):
        for way_id in [123, 456, 789]:
            with self.subTest(way_id=way_id):
                way = self.way.with_id(way_id)
                self.assertEqual(str(way), f"way({way_id});")

    def test_with_id_invalid_type(self):
        with self.assertRaises(TypeError):
            self.way.with_id("123")

    def test_with_id_negative(self):
        with self.assertRaises(ValueError):
            self.way.with_id(-1)

    def test_with_id_conflict_with_ids(self):
        way = self.way.with_ids([1, 2])
        with self.assertRaises(ValueError):
            way.with_id(3)

    def test_with_ids(self):
        for ids in [[1, 2, 3], [10, 20], [100]]:
            with self.subTest(ids=ids):
                way = self.way.with_ids(ids)
                expected = f"way({','.join(map(str, ids))});"
                self.assertEqual(str(way), expected)

    def test_with_ids_invalid_type(self):
        with self.assertRaises(TypeError):
            self.way.with_ids(["1", "2"])

    def test_with_ids_empty(self):
        with self.assertRaises(ValueError):
            self.way.with_ids([])

    def test_with_ids_conflict_with_id(self):
        way = self.way.with_id(1)
        with self.assertRaises(ValueError):
            way.with_ids([2, 3])

    def test_with_tags(self):
        way = self.tagged_way.with_tags([("highway", "primary"), ("access", "public")])
        self.assertEqual(str(way), "way[highway=primary][access=public];")

    def test_with_tags_invalid_type(self):
        with self.assertRaises(TypeError):
            self.way.with_tags([("key", 1)])

    def test_with_tags_invalid_length(self):
        with self.assertRaises(ValueError):
            self.way.with_tags([("key",)])

    def test_with_bbox(self):
        way = self.way.with_bbox((51.0, -0.2, 51.1, -0.1))
        self.assertEqual(str(way), "way(51.0,-0.2,51.1,-0.1);")

    def test_with_bbox_invalid(self):
        with self.assertRaises(ValueError):
            self.way.with_bbox((91, 0, 92, 1))  # Invalid latitude

    def test_with_bbox_exclusivity(self):
        way = self.way.with_bbox((51, -0.2, 51.1, -0.1))
        with self.assertRaises(ValueError):
            way.with_area_by_id(3600000000)

    def test_with_node(self):
        way = self.way.with_node(123)
        self.assertEqual(str(way), "way(n:123);")

    def test_with_node_from_set(self):
        way = self.way.with_node_from_set("nodes")
        self.assertEqual(str(way), "way(n.nodes);")

    def test_with_node_exclusivity(self):
        way = self.way.with_node(123)
        with self.assertRaises(ValueError):
            way.with_node_from_set("nodes")

    def test_with_closed(self):
        way = self.way.with_closed(True)
        self.assertEqual(str(way), "way[is_closed=true];")
        way = self.way.with_closed(False)
        self.assertEqual(str(way), "way[is_closed=false];")

    def test_with_min_length(self):
        way = self.way.with_min_length(100)
        self.assertEqual(str(way), "way[if:length()>100];")

    def test_with_min_nodes(self):
        way = self.way.with_min_nodes(10)
        self.assertEqual(str(way), "way[if:count(nodes)>10];")

    def test_with_nodes(self):
        way = self.tagged_way.with_nodes()
        self.assertEqual(str(way), "(way[highway=primary];>);")

    def test_with_parents(self):
        way = self.tagged_way.with_parents()
        self.assertEqual(str(way), "(way[highway=primary];<);")

    def test_with_nodes_and_parents(self):
        way = self.tagged_way.with_nodes().with_parents()
        self.assertEqual(str(way), "(way[highway=primary];>;<);")

    def test_with_area_by_id(self):
        way = self.way.with_area_by_id(3600000000)
        self.assertEqual(str(way), "way(area:3600000000);")

    def test_with_area_by_name(self):
        way = self.way.with_area_by_name("Berlin")
        self.assertEqual(str(way), "way(area.Berlin);")

    def test_with_around_point(self):
        way = self.way.with_around_point(50, 51.5, -0.1)
        self.assertEqual(str(way), "way(around:50,51.5,-0.1);")

    def test_with_around_set(self):
        way = self.way.with_around_set("roads", 100)
        self.assertEqual(str(way), "way(around.roads:100);")

    def test_with_relation(self):
        way = self.way.with_relation(1234)
        self.assertEqual(str(way), "way(r:1234);")

    def test_with_relation_and_role(self):
        way = self.way.with_relation_and_role(1234, "stop")
        self.assertEqual(str(way), 'way(r:1234,"stop");')

    def test_with_relation_from_set(self):
        way = self.way.with_relation_from_set("routes")
        self.assertEqual(str(way), "way(r.routes);")

    def test_from_set(self):
        way = self.way.from_set("input_set")
        self.assertEqual(str(way), ".input_set way;")

    def test_with_tag_exists(self):
        way = self.way.with_tag_exists("highway")
        self.assertEqual(str(way), "way[highway];")

    def test_with_tag_not_exists(self):
        way = self.way.with_tag_not_exists("access")
        self.assertEqual(str(way), "way[!access];")

    def test_with_tag_not(self):
        way = self.way.with_tag_not("highway", "primary")
        self.assertEqual(str(way), "way[highway!=primary];")

    def test_with_tag_regex(self):
        way = self.way.with_tag_regex("highway", "^primary|secondary$")
        self.assertEqual(str(way), "way[highway~^primary|secondary$];")

    def test_with_tag_condition(self):
        way = self.way.with_tag_condition('["highway"~"primary"]')
        self.assertEqual(str(way), 'way["highway"~"primary"];')
        with self.assertRaises(ValueError):
            way.with_tag_condition("invalid")  # Missing brackets
        with self.assertRaises(ValueError):
            way.with_tag_condition('["key"=value]')  # Unquoted value
        with self.assertRaises(ValueError):
            way.with_tag_condition('["key"]')  # Missing operator

    def test_with_if_condition(self):
        way = self.way.with_if_condition('length() > 1000')
        self.assertEqual(str(way), 'way[if:length() > 1000];')

    def test_with_if_and_tags(self):
        way = self.tagged_way.with_if_condition('count_tags() > 3')
        self.assertEqual(str(way), 'way[highway=primary][if:count_tags() > 3];')

    def test_with_pivot(self):
        way = self.way.with_pivot("boundary_set")
        self.assertEqual(str(way), "way(pivot.boundary_set);")

    def test_with_uid(self):
        way = self.way.with_uid(12345)
        self.assertEqual(str(way), "way[uid=12345];")

    def test_with_newer(self):
        way = self.way.with_newer("2023-01-01T00:00:00Z")
        self.assertEqual(str(way), 'way[newer="2023-01-01T00:00:00Z"];')

    def test_with_version(self):
        way = self.way.with_version(2)
        self.assertEqual(str(way), "way[version=2];")

if __name__ == "__main__":
    unittest.main()