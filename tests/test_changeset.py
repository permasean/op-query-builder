import unittest
from op_query_builder.elements.changeset import Changeset

class TestChangeset(unittest.TestCase):
    def setUp(self):
        """Set up a basic Changeset instance for each test."""
        self.changeset = Changeset()
        self.tagged_changeset = Changeset().with_tags([("user", "JohnDoe")])

    def test_store_as_set(self):
        changeset = self.changeset.store_as_set("output_set")
        self.assertEqual(str(changeset), "changeset->.output_set;")
        self.assertIsInstance(changeset, Changeset, "store_as_set should return Changeset instance")

    def test_complex_query(self):
        changeset = self.changeset
        print("After init:", changeset)
        changeset = changeset.from_set("input")
        print("After from_set:", changeset)
        changeset = changeset.with_id(123)
        print("After with_id:", changeset)
        changeset = changeset.with_user("JohnDoe")
        print("After with_user:", changeset)
        changeset = changeset.with_open(True)
        print("After with_open:", changeset)
        changeset = changeset.store_as_set("output")
        print("After store_as_set:", changeset)
        self.assertEqual(str(changeset), ".input changeset(123)[user=JohnDoe][open=true]->.output;")

    def test_with_user_alone(self):
        changeset = self.changeset.with_user("JohnDoe")
        self.assertEqual(str(changeset), "changeset[user=JohnDoe];")

    def test_with_id(self):
        for changeset_id in [123, 456, 789]:
            with self.subTest(changeset_id=changeset_id):
                changeset = self.changeset.with_id(changeset_id)
                self.assertEqual(str(changeset), f"changeset({changeset_id});")

    def test_with_id_invalid_type(self):
        with self.assertRaises(TypeError):
            self.changeset.with_id("123")

    def test_with_id_negative(self):
        with self.assertRaises(ValueError):
            self.changeset.with_id(-1)

    def test_with_id_conflict_with_ids(self):
        changeset = self.changeset.with_ids([1, 2])
        with self.assertRaises(ValueError):
            changeset.with_id(3)

    def test_with_ids(self):
        for ids in [[1, 2, 3], [10, 20], [100]]:
            with self.subTest(ids=ids):
                changeset = self.changeset.with_ids(ids)
                expected = f"changeset({','.join(map(str, ids))});"
                self.assertEqual(str(changeset), expected)

    def test_with_ids_invalid_type(self):
        with self.assertRaises(TypeError):
            self.changeset.with_ids(["1", "2"])

    def test_with_ids_empty(self):
        with self.assertRaises(ValueError):
            self.changeset.with_ids([])

    def test_with_ids_conflict_with_id(self):
        changeset = self.changeset.with_id(1)
        with self.assertRaises(ValueError):
            changeset.with_ids([2, 3])

    def test_with_tags(self):
        changeset = self.tagged_changeset.with_tags([("user", "JohnDoe"), ("source", "manual")])
        self.assertEqual(str(changeset), "changeset[user=JohnDoe][source=manual];")

    def test_with_tags_invalid_type(self):
        with self.assertRaises(TypeError):
            self.changeset.with_tags([("key", 1)])

    def test_with_tags_invalid_length(self):
        with self.assertRaises(ValueError):
            self.changeset.with_tags([("key",)])

    def test_with_bbox(self):
        changeset = self.changeset.with_bbox((51.0, -0.2, 51.1, -0.1))
        self.assertEqual(str(changeset), "changeset(51.0,-0.2,51.1,-0.1);")

    def test_with_bbox_invalid(self):
        with self.assertRaises(ValueError):
            self.changeset.with_bbox((91, 0, 92, 1))  # Invalid latitude

    def test_with_bbox_exclusivity(self):
        changeset = self.changeset.with_bbox((51, -0.2, 51.1, -0.1))
        with self.assertRaises(ValueError):
            changeset.with_bbox((52, -0.3, 52.1, -0.2))  # Only one bbox allowed

    def test_with_uid(self):
        changeset = self.changeset.with_uid(12345)
        self.assertEqual(str(changeset), "changeset[uid=12345];")

    def test_with_open(self):
        changeset = self.changeset.with_open(True)
        self.assertEqual(str(changeset), "changeset[open=true];")
        changeset = self.changeset.with_open(False)
        self.assertEqual(str(changeset), "changeset[open=false];")

    def test_with_time(self):
        changeset = self.changeset.with_time("2023-01-01T00:00:00Z")
        self.assertEqual(str(changeset), 'changeset[time="2023-01-01T00:00:00Z"];')

    def test_with_time_invalid(self):
        with self.assertRaises(ValueError):
            self.changeset.with_time("2023-01-01")  # Missing 'T' and 'Z'

    def test_with_time_range(self):
        changeset = self.changeset.with_time_range("2023-01-01T00:00:00Z", "2023-12-31T23:59:59Z")
        self.assertEqual(str(changeset), 'changeset[time>="2023-01-01T00:00:00Z"][time<="2023-12-31T23:59:59Z"];')

    def test_with_time_range_invalid(self):
        with self.assertRaises(ValueError):
            self.changeset.with_time_range("2023-01-01", "2023-12-31")  # Missing 'T' and 'Z'

    def test_with_time_range_exclusivity(self):
        changeset = self.changeset.with_time("2023-01-01T00:00:00Z")
        with self.assertRaises(ValueError):
            changeset.with_time_range("2023-01-01T00:00:00Z", "2023-12-31T23:59:59Z")

    def test_with_comment(self):
        changeset = self.changeset.with_comment("Added new roads")
        self.assertEqual(str(changeset), 'changeset[comment="Added new roads"];')

    def test_with_created_by(self):
        changeset = self.changeset.with_created_by("JOSM")
        self.assertEqual(str(changeset), "changeset[created_by=JOSM];")

    def test_from_set(self):
        changeset = self.changeset.from_set("input_set")
        self.assertEqual(str(changeset), ".input_set changeset;")

    def test_with_tag_exists(self):
        changeset = self.changeset.with_tag_exists("source")
        self.assertEqual(str(changeset), "changeset[source];")

    def test_with_tag_not_exists(self):
        changeset = self.changeset.with_tag_not_exists("comment")
        self.assertEqual(str(changeset), "changeset[!comment];")

    def test_with_tag_not(self):
        changeset = self.changeset.with_tag_not("user", "JohnDoe")
        self.assertEqual(str(changeset), "changeset[user!=JohnDoe];")

    def test_with_tag_regex(self):
        changeset = self.changeset.with_tag_regex("comment", "^Added.*")
        self.assertEqual(str(changeset), "changeset[comment~^Added.*];")

    def test_with_tag_condition(self):
        changeset = self.changeset.with_tag_condition('["user"~"John.*"]')
        self.assertEqual(str(changeset), 'changeset["user"~"John.*"];')

    def test_with_if_condition(self):
        changeset = self.changeset.with_if_condition('count_tags() > 2')
        self.assertEqual(str(changeset), 'changeset[if:count_tags() > 2];')

    def test_with_if_and_tags(self):
        changeset = self.tagged_changeset.with_if_condition('count_tags() > 1')
        self.assertEqual(str(changeset), 'changeset[user=JohnDoe][if:count_tags() > 1];')

    def test_with_user_multiple_calls(self):
        changeset = self.changeset.with_user("JohnDoe").with_user("JaneDoe")
        self.assertEqual(str(changeset), "changeset[user=JaneDoe];")

    def test_with_uid_multiple_calls(self):
        changeset = self.changeset.with_uid(12345).with_uid(67890)
        self.assertEqual(str(changeset), "changeset[uid=67890];")

    def test_with_comment_multiple_calls(self):
        changeset = self.changeset.with_comment("Added roads").with_comment("Updated tags")
        self.assertEqual(str(changeset), 'changeset[comment="Updated tags"];')

    def test_with_created_by_multiple_calls(self):
        changeset = self.changeset.with_created_by("JOSM").with_created_by("iD")
        self.assertEqual(str(changeset), "changeset[created_by=iD];")

if __name__ == "__main__":
    unittest.main()