import unittest
from op_query_builder.elements.relation import Relation

class TestRelation(unittest.TestCase):
    def setUp(self):
        """Set up a basic Relation instance for each test."""
        self.relation = Relation()
        self.tagged_relation = Relation().with_tags([("boundary", "administrative")])

    def test_store_as_set(self):
        relation = self.relation.store_as_set("output_set")
        self.assertEqual(str(relation), "relation->.output_set;")
        self.assertIsInstance(relation, Relation, "store_as_set should return Relation instance")

    def test_complex_query(self):
        relation = self.relation
        print("After init:", relation)
        relation = relation.from_set("input")
        print("After from_set:", relation)
        relation = relation.with_id(123)
        print("After with_id:", relation)
        relation = relation.with_tags([("boundary", "administrative")])
        print("After with_tags:", relation)
        relation = relation.with_user("JohnDoe")
        print("After with_user:", relation)
        relation = relation.store_as_set("output")
        print("After store_as_set:", relation)
        self.assertEqual(str(relation), ".input relation(123)[boundary=administrative][user=JohnDoe]->.output;")

    def test_with_user_alone(self):
        relation = self.relation.with_user("JohnDoe")
        self.assertEqual(str(relation), "relation[user=JohnDoe];")

    def test_with_id(self):
        for relation_id in [123, 456, 789]:
            with self.subTest(relation_id=relation_id):
                relation = self.relation.with_id(relation_id)
                self.assertEqual(str(relation), f"relation({relation_id});")

    def test_with_id_invalid_type(self):
        with self.assertRaises(TypeError):
            self.relation.with_id("123")

    def test_with_id_negative(self):
        with self.assertRaises(ValueError):
            self.relation.with_id(-1)

    def test_with_id_conflict_with_ids(self):
        relation = self.relation.with_ids([1, 2])
        with self.assertRaises(ValueError):
            relation.with_id(3)

    def test_with_ids(self):
        for ids in [[1, 2, 3], [10, 20], [100]]:
            with self.subTest(ids=ids):
                relation = self.relation.with_ids(ids)
                expected = f"relation({','.join(map(str, ids))});"
                self.assertEqual(str(relation), expected)

    def test_with_ids_invalid_type(self):
        with self.assertRaises(TypeError):
            self.relation.with_ids(["1", "2"])

    def test_with_ids_empty(self):
        with self.assertRaises(ValueError):
            self.relation.with_ids([])

    def test_with_ids_conflict_with_id(self):
        relation = self.relation.with_id(1)
        with self.assertRaises(ValueError):
            relation.with_ids([2, 3])

    def test_with_tags(self):
        relation = self.tagged_relation.with_tags([("boundary", "administrative"), ("name", "Berlin")])
        self.assertEqual(str(relation), "relation[boundary=administrative][name=Berlin];")

    def test_with_tags_invalid_type(self):
        with self.assertRaises(TypeError):
            self.relation.with_tags([("key", 1)])

    def test_with_tags_invalid_length(self):
        with self.assertRaises(ValueError):
            self.relation.with_tags([("key",)])

    def test_with_bbox(self):
        relation = self.relation.with_bbox((51.0, -0.2, 51.1, -0.1))
        self.assertEqual(str(relation), "relation(51.0,-0.2,51.1,-0.1);")

    def test_with_bbox_invalid(self):
        with self.assertRaises(ValueError):
            self.relation.with_bbox((91, 0, 92, 1))  # Invalid latitude

    def test_with_bbox_exclusivity(self):
        relation = self.relation.with_bbox((51, -0.2, 51.1, -0.1))
        with self.assertRaises(ValueError):
            relation.with_area_by_id(3600000000)

    def test_with_node(self):
        relation = self.relation.with_node(123)
        self.assertEqual(str(relation), "relation(n:123);")

    def test_with_node_from_set(self):
        relation = self.relation.with_node_from_set("nodes")
        self.assertEqual(str(relation), "relation(n.nodes);")

    def test_with_node_exclusivity(self):
        relation = self.relation.with_node(123)
        with self.assertRaises(ValueError):
            relation.with_node_from_set("nodes")

    def test_with_way(self):
        relation = self.relation.with_way(456)
        self.assertEqual(str(relation), "relation(w:456);")

    def test_with_way_from_set(self):
        relation = self.relation.with_way_from_set("ways")
        self.assertEqual(str(relation), "relation(w.ways);")

    def test_with_way_exclusivity(self):
        relation = self.relation.with_way(456)
        with self.assertRaises(ValueError):
            relation.with_way_from_set("ways")

    def test_with_relation(self):
        relation = self.relation.with_relation(789)
        self.assertEqual(str(relation), "relation(r:789);")

    def test_with_relation_and_role(self):
        relation = self.relation.with_relation_and_role(789, "outer")
        self.assertEqual(str(relation), 'relation(r:789,"outer");')

    def test_with_relation_from_set(self):
        relation = self.relation.with_relation_from_set("relations")
        self.assertEqual(str(relation), "relation(r.relations);")

    def test_with_relation_exclusivity(self):
        relation = self.relation.with_relation(789)
        with self.assertRaises(ValueError):
            relation.with_relation_from_set("relations")

    def test_with_members(self):
        relation = self.tagged_relation.with_members()
        self.assertEqual(str(relation), "(relation[boundary=administrative];>);")

    def test_with_parents(self):
        relation = self.tagged_relation.with_parents()
        self.assertEqual(str(relation), "(relation[boundary=administrative];<);")

    def test_with_members_and_parents(self):
        relation = self.tagged_relation.with_members().with_parents()
        self.assertEqual(str(relation), "(relation[boundary=administrative];>;<);")

    def test_with_members_and_set(self):
        relation = self.tagged_relation.with_members().store_as_set("areas")
        self.assertEqual(str(relation), "(relation[boundary=administrative];>)->.areas;")

    def test_with_parents_and_set(self):
        relation = self.tagged_relation.with_parents().store_as_set("parents")
        self.assertEqual(str(relation), "(relation[boundary=administrative];<)->.parents;")

    def test_with_members_parents_and_set(self):
        relation = self.tagged_relation.with_members().with_parents().store_as_set("combined")
        self.assertEqual(str(relation), "(relation[boundary=administrative];>;<)->.combined;")

    def test_with_area_by_id(self):
        relation = self.relation.with_area_by_id(3600000000)
        self.assertEqual(str(relation), "relation(area:3600000000);")

    def test_with_area_by_name(self):
        relation = self.relation.with_area_by_name("Berlin")
        self.assertEqual(str(relation), "relation(area.Berlin);")

    def test_with_around_point(self):
        relation = self.relation.with_around_point(50, 51.5, -0.1)
        self.assertEqual(str(relation), "relation(around:50,51.5,-0.1);")

    def test_with_around_set(self):
        relation = self.relation.with_around_set("roads", 100)
        self.assertEqual(str(relation), "relation(around.roads:100);")

    def test_from_set(self):
        relation = self.relation.from_set("input_set")
        self.assertEqual(str(relation), ".input_set relation;")

    def test_with_tag_exists(self):
        relation = self.relation.with_tag_exists("boundary")
        self.assertEqual(str(relation), "relation[boundary];")

    def test_with_tag_not_exists(self):
        relation = self.relation.with_tag_not_exists("access")
        self.assertEqual(str(relation), "relation[!access];")

    def test_with_tag_not(self):
        relation = self.relation.with_tag_not("boundary", "administrative")
        self.assertEqual(str(relation), "relation[boundary!=administrative];")

    def test_with_tag_regex(self):
        relation = self.relation.with_tag_regex("boundary", "^administrative|political$")
        self.assertEqual(str(relation), "relation[boundary~^administrative|political$];")

    def test_with_tag_condition(self):
        relation = self.relation.with_tag_condition('["boundary"~"administrative"]')
        self.assertEqual(str(relation), 'relation["boundary"~"administrative"];')
        with self.assertRaises(ValueError):
            relation.with_tag_condition("invalid")  # Missing brackets
        with self.assertRaises(ValueError):
            relation.with_tag_condition('["key"=value]')  # Unquoted value
        with self.assertRaises(ValueError):
            relation.with_tag_condition('["key"]')  # Missing operator

    def test_with_if_condition(self):
        relation = self.relation.with_if_condition('count(members) > 10')
        self.assertEqual(str(relation), 'relation[if:count(members) > 10];')

    def test_with_if_and_tags(self):
        relation = self.tagged_relation.with_if_condition('count_tags() > 2')
        self.assertEqual(str(relation), 'relation[boundary=administrative][if:count_tags() > 2];')

    def test_with_pivot(self):
        relation = self.relation.with_pivot("boundary_set")
        self.assertEqual(str(relation), "relation(pivot.boundary_set);")

    def test_with_uid(self):
        relation = self.relation.with_uid(12345)
        self.assertEqual(str(relation), "relation[uid=12345];")

    def test_with_newer(self):
        relation = self.relation.with_newer("2023-01-01T00:00:00Z")
        self.assertEqual(str(relation), 'relation[newer="2023-01-01T00:00:00Z"];')

    def test_with_version(self):
        relation = self.relation.with_version(2)
        self.assertEqual(str(relation), "relation[version=2];")

    def test_with_type(self):
        relation = self.relation.with_type("multipolygon")
        self.assertEqual(str(relation), "relation[type=multipolygon];")

    def test_with_min_members(self):
        relation = self.relation.with_min_members(10)
        self.assertEqual(str(relation), "relation[if:count(members)>10];")

    def test_with_min_role_count(self):
        relation = self.relation.with_min_role_count("outer", 2)
        self.assertEqual(str(relation), 'relation[if:count_by_role("outer")>2];')

    def test_with_min_members_and_tags(self):
        relation = self.tagged_relation.with_min_members(5)
        self.assertEqual(str(relation), "relation[boundary=administrative][if:count(members)>5];")

if __name__ == "__main__":
    unittest.main()