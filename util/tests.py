import unittest
from util.helpers import slugify, truncate, flatten, chunk, timestamp
from util.validators import is_email, is_url, is_phone, is_non_empty, is_in_range, is_min_length
from util.config import Config


class TestHelpers(unittest.TestCase):
    def test_slugify_basic(self):
        self.assertEqual(slugify("Hello World"), "hello-world")

    def test_slugify_special_chars(self):
        self.assertEqual(slugify("Hello World! This is a Test."), "hello-world-this-is-a-test")

    def test_truncate_short(self):
        self.assertEqual(truncate("hi", 10), "hi")

    def test_truncate_long(self):
        result = truncate("A very long string", 10)
        self.assertLessEqual(len(result), 10)
        self.assertTrue(result.endswith("..."))

    def test_flatten(self):
        self.assertEqual(flatten([1, [2, [3, 4]], 5]), [1, 2, 3, 4, 5])

    def test_flatten_already_flat(self):
        self.assertEqual(flatten([1, 2, 3]), [1, 2, 3])

    def test_chunk(self):
        self.assertEqual(chunk([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]])

    def test_timestamp_format(self):
        ts = timestamp("%Y-%m-%d")
        self.assertRegex(ts, r"^\d{4}-\d{2}-\d{2}$")


class TestValidators(unittest.TestCase):
    def test_valid_email(self):
        self.assertTrue(is_email("user@example.com"))

    def test_invalid_email(self):
        self.assertFalse(is_email("not-an-email"))

    def test_valid_url(self):
        self.assertTrue(is_url("https://example.com"))

    def test_invalid_url(self):
        self.assertFalse(is_url("ftp://bad.com"))

    def test_valid_phone(self):
        self.assertTrue(is_phone("+48 123 456 789"))

    def test_invalid_phone(self):
        self.assertFalse(is_phone("abc"))

    def test_non_empty_true(self):
        self.assertTrue(is_non_empty("hello"))

    def test_non_empty_false(self):
        self.assertFalse(is_non_empty("   "))

    def test_in_range_true(self):
        self.assertTrue(is_in_range(5, 1, 10))

    def test_in_range_false(self):
        self.assertFalse(is_in_range(15, 1, 10))

    def test_min_length_true(self):
        self.assertTrue(is_min_length("hello", 3))

    def test_min_length_false(self):
        self.assertFalse(is_min_length("hi", 5))


class TestConfig(unittest.TestCase):
    def test_get_default(self):
        cfg = Config()
        self.assertIsNone(cfg.get("nonexistent_key_xyz"))

    def test_get_with_default(self):
        cfg = Config()
        self.assertEqual(cfg.get("nonexistent_key_xyz", "fallback"), "fallback")

    def test_require_raises(self):
        cfg = Config()
        with self.assertRaises(KeyError):
            cfg.require("nonexistent_key_xyz")

    def test_env_loaded(self):
        cfg = Config()
        self.assertIsNotNone(cfg.get("path"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
