import unittest
from op_query_builder.derived.area import Area

class TestArea(unittest.TestCase):
    def setUp(self):
        """Set up a basic Area instance for each test."""
        self.area = Area()
        self.tagged_area = Area().with_tags([("boundary", "administrative")])

    def test_store_as_set(self):
        area = self.area.store_as_set("output_set")
        self.assertEqual(str(area), "area->.output_set;")
        self.assertIsInstance(area, Area, "store_as_set should return Area instance")

    def test_complex_query(self):
        area = self.area
        print("After init:", area)
        area = area.from_set("input")
        print("After from_set:", area)
        area = area.with_id(3600000000)
        print("After with_id:", area)
        area = area.with_tags([("boundary", "administrative")])
        print("After with_tags:", area)
        area = area.store_as_set("output")
        print("After store_as_set:", area)
        self.assertEqual(str(area), ".input area(3600000000)[boundary=administrative]->.output;")

    def test_with_id(self):
        for area_id in [3600000000, 3600000001]:
            with self.subTest(area_id=area_id):
                area = self.area.with_id(area_id)
                self.assertEqual(str(area), f"area({area_id});")

    def test_with_id_invalid_type(self):
        with self.assertRaises(TypeError):
            self.area.with_id("3600000000")

    def test_with_id_negative(self):
        with self.assertRaises(ValueError):
            self.area.with_id(-1)

    def test_with_id_below_minimum(self):
        with self.assertRaises(ValueError):
            self.area.with_id(2399999999)  # Below 2400000000

    def test_with_tags(self):
        area = self.tagged_area.with_tags([("boundary", "administrative"), ("name", "Berlin")])
        self.assertEqual(str(area), "area[boundary=administrative][name=Berlin];")

    def test_with_tags_invalid_type(self):
        with self.assertRaises(TypeError):
            self.area.with_tags([("key", 1)])

    def test_with_tags_invalid_length(self):
        with self.assertRaises(ValueError):
            self.area.with_tags([("key",)])

    def test_with_boundary(self):
        area = self.area.with_boundary("administrative")
        self.assertEqual(str(area), "area[boundary=administrative];")

    def test_with_name(self):
        area = self.area.with_name("Berlin")
        self.assertEqual(str(area), "area[name=Berlin];")

    def test_with_boundary_and_name(self):
        area = self.area.with_boundary("administrative").with_name("Berlin")
        self.assertEqual(str(area), "area[boundary=administrative][name=Berlin];")

    def test_with_boundary_multiple_calls(self):
        area = self.area.with_boundary("administrative").with_boundary("political")
        self.assertEqual(str(area), "area[boundary=political];")

    def test_with_pivot(self):
        area = self.area.with_pivot("boundary_set")
        self.assertEqual(str(area), "area(pivot.boundary_set);")

    def test_with_pivot_exclusivity(self):
        area = self.area.with_id(3600000000)
        with self.assertRaises(ValueError):
            area.with_pivot("boundary_set")

    def test_from_set(self):
        area = self.area.from_set("input_set")
        self.assertEqual(str(area), ".input_set area;")

    def test_with_tag_exists(self):
        area = self.area.with_tag_exists("boundary")
        self.assertEqual(str(area), "area[boundary];")

    def test_with_tag_not_exists(self):
        area = self.area.with_tag_not_exists("access")
        self.assertEqual(str(area), "area[!access];")

    def test_with_tag_not(self):
        area = self.area.with_tag_not("boundary", "administrative")
        self.assertEqual(str(area), "area[boundary!=administrative];")

    def test_with_tag_regex(self):
        area = self.area.with_tag_regex("boundary", "^administrative|political$")
        self.assertEqual(str(area), "area[boundary~^administrative|political$];")

    def test_with_tag_condition(self):
        area = self.area.with_tag_condition('["boundary"~"administrative"]')
        self.assertEqual(str(area), 'area["boundary"~"administrative"];')

    def test_with_if_condition(self):
        area = self.area.with_if_condition('count_tags() > 2')
        self.assertEqual(str(area), 'area[if:count_tags() > 2];')

    def test_with_if_and_tags(self):
        area = self.tagged_area.with_if_condition('count_tags() > 1')
        self.assertEqual(str(area), 'area[boundary=administrative][if:count_tags() > 1];')

    def test_with_tag_multiple_calls(self):
        area = self.area.with_tag_exists("boundary").with_tag_not_exists("boundary")
        self.assertEqual(str(area), "area[!boundary];")

    def test_with_tag_not_then_exists(self):
        area = self.area.with_tag_not("boundary", "administrative").with_tag_exists("boundary")
        self.assertEqual(str(area), "area[boundary];")

if __name__ == "__main__":
    unittest.main()