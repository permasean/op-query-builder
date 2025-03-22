import unittest
from op_query_builder.elements.node import Node

class TestNode(unittest.TestCase):
    def test_with_id(self):
        node = Node().with_id(123)
        self.assertEqual(str(node), "node(123);")
        with self.assertRaises(TypeError):
            Node().with_id("123")
        with self.assertRaises(ValueError):
            Node().with_id(-1)
        with self.assertRaises(ValueError):
            Node().with_ids([1, 2]).with_id(3)

    def test_with_ids(self):
        node = Node().with_ids([1, 2, 3])
        self.assertEqual(str(node), "node(1|2|3);")
        with self.assertRaises(TypeError):
            Node().with_ids(["1", "2"])
        with self.assertRaises(ValueError):
            Node().with_ids([])
        with self.assertRaises(ValueError):
            Node().with_id(1).with_ids([2, 3])

    def test_with_tags(self):
        node = Node().with_tags([("highway", "primary"), ("access", "public")])
        self.assertEqual(str(node), "node[highway=primary][access=public];")
        with self.assertRaises(TypeError):
            Node().with_tags([("key", 1)])
        with self.assertRaises(ValueError):
            Node().with_tags([("key",)])

    def test_with_bbox(self):
        node = Node().with_bbox((51.0, -0.2, 51.1, -0.1))
        self.assertEqual(str(node), "node(51.0,-0.2,51.1,-0.1);")
        with self.assertRaises(ValueError):
            Node().with_bbox((91, 0, 92, 1))  # Latitude out of range
        with self.assertRaises(ValueError):
            Node().with_bbox((51, -0.2, 51.1, -0.1)).with_area_by_id(3600000000)  # Exclusivity

    def test_with_area_by_id(self):
        node = Node().with_area_by_id(3600000000)
        self.assertEqual(str(node), "node(area:3600000000);")
        with self.assertRaises(TypeError):
            Node().with_area_by_id("3600000000")
        with self.assertRaises(ValueError):
            Node().with_area_by_id(-1)
        with self.assertRaises(ValueError):
            Node().with_area_by_id(1).with_bbox((0, 0, 1, 1))

    def test_with_area_by_name(self):
        node = Node().with_area_by_name("Berlin")
        self.assertEqual(str(node), "node(area.Berlin);")
        with self.assertRaises(ValueError):
            Node().with_area_by_name("")
        with self.assertRaises(ValueError):
            Node().with_area_by_name("[invalid]")
        with self.assertRaises(ValueError):
            Node().with_area_by_name("Berlin").with_around_point(50, 51.5, -0.1)

    def test_with_around_point(self):
        node = Node().with_around_point(50, 51.5, -0.1)
        self.assertEqual(str(node), "node(around:50,51.5,-0.1);")
        with self.assertRaises(ValueError):
            Node().with_around_point(-1, 51, 0)  # Negative radius
        with self.assertRaises(ValueError):
            Node().with_around_point(50, 91, 0)  # Latitude out of range
        with self.assertRaises(ValueError):
            Node().with_around_point(50, 51, 0).with_area_by_name("London")

    def test_with_around_set(self):
        node = Node().with_around_set("roads", 100)
        self.assertEqual(str(node), "node(around.roads:100);")
        with self.assertRaises(TypeError):
            Node().with_around_set(123, 100)
        with self.assertRaises(ValueError):
            Node().with_around_set("", 100)
        with self.assertRaises(ValueError):
            Node().with_around_set("roads", 100).with_bbox((0, 0, 1, 1))

    def test_with_relation(self):
        node = Node().with_relation(1234)
        self.assertEqual(str(node), "node(r:1234);")
        with self.assertRaises(TypeError):
            Node().with_relation("1234")
        with self.assertRaises(ValueError):
            Node().with_relation(-1)
        with self.assertRaises(ValueError):
            Node().with_relation(1234).with_way(5678)

    def test_with_relation_and_role(self):
        node = Node().with_relation_and_role(1234, "stop")
        self.assertEqual(str(node), 'node(r:1234,"stop");')
        with self.assertRaises(ValueError):
            Node().with_relation_and_role(1234, "")
        with self.assertRaises(ValueError):
            Node().with_relation_and_role(1234, "stop").with_relation_from_set("routes")

    def test_with_relation_from_set(self):
        node = Node().with_relation_from_set("routes")
        self.assertEqual(str(node), "node(r.routes);")
        with self.assertRaises(ValueError):
            Node().with_relation_from_set("[invalid]")
        with self.assertRaises(ValueError):
            Node().with_relation_from_set("routes").with_way_from_set("roads")

    def test_with_way(self):
        node = Node().with_way(5678)
        self.assertEqual(str(node), "node(w:5678);")
        with self.assertRaises(TypeError):
            Node().with_way("5678")
        with self.assertRaises(ValueError):
            Node().with_way(5678).with_relation(1234)

    def test_with_way_from_set(self):
        node = Node().with_way_from_set("roads")
        self.assertEqual(str(node), "node(w.roads);")
        with self.assertRaises(ValueError):
            Node().with_way_from_set("")
        with self.assertRaises(ValueError):
            Node().with_way_from_set("roads").with_relation_and_role(1234, "stop")

    def test_from_set(self):
        node = Node().from_set("input_set")
        self.assertEqual(str(node), ".input_set node;")
        with self.assertRaises(TypeError):
            Node().from_set(123)

    def test_store_as_set(self):
        node = Node().store_as_set("output_set")
        self.assertEqual(str(node), "node->.output_set;")
        with self.assertRaises(ValueError):
            Node().store_as_set("[invalid]")

    def test_with_tag_exists(self):
        node = Node().with_tag_exists("highway")
        self.assertEqual(str(node), "node[highway];")
        with self.assertRaises(ValueError):
            Node().with_tag_exists("")

    def test_with_tag_not_exists(self):
        node = Node().with_tag_not_exists("access")
        self.assertEqual(str(node), "node[!access];")
        with self.assertRaises(ValueError):
            Node().with_tag_not_exists("")

    def test_with_tag_not(self):
        node = Node().with_tag_not("highway", "primary")
        self.assertEqual(str(node), "node[highway!=primary];")
        with self.assertRaises(TypeError):
            Node().with_tag_not("highway", 123)

    def test_with_tag_regex(self):
        node = Node().with_tag_regex("highway", "^primary|secondary$")
        self.assertEqual(str(node), "node[highway~^primary|secondary$];")
        with self.assertRaises(ValueError):
            Node().with_tag_regex("", "regex")

    def test_with_tag_condition(self):
        node = Node().with_tag_condition('["highway"~"primary"]')
        self.assertEqual(str(node), 'node["highway"~"primary"];')
        with self.assertRaises(ValueError):
            Node().with_tag_condition("invalid")

    def test_with_user(self):
        node = Node().with_user("JohnDoe")
        self.assertEqual(str(node), "node[user=JohnDoe];")
        with self.assertRaises(ValueError):
            Node().with_user("")

    def test_with_uid(self):
        node = Node().with_uid(12345)
        self.assertEqual(str(node), "node[uid=12345];")
        with self.assertRaises(TypeError):
            Node().with_uid("12345")

    def test_with_newer(self):
        node = Node().with_newer("2023-01-01T00:00:00Z")
        self.assertEqual(str(node), 'node[newer="2023-01-01T00:00:00Z"];')
        with self.assertRaises(ValueError):
            Node().with_newer("2023-01-01")  # Missing T and Z

    def test_with_version(self):
        node = Node().with_version(2)
        self.assertEqual(str(node), "node[version=2];")
        with self.assertRaises(ValueError):
            Node().with_version(0)

    def test_complex_query(self):
        node = (Node()
                .from_set("input")
                .with_id(123)
                .with_tags([("highway", "primary")])
                .with_user("JohnDoe")
                .store_as_set("output"))
        self.assertEqual(str(node), ".input node(123)[highway=primary][user=JohnDoe]->.output;")

if __name__ == "__main__":
    unittest.main()