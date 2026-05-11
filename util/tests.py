import unittest
import tempfile
import os
from datetime import date, timedelta
from util.helpers import slugify, truncate, flatten, chunk, timestamp
from util.validators import is_email, is_url, is_phone, is_non_empty, is_in_range, is_min_length
from util.config import Config
from util.date_utils import parse_date, format_date, days_between, add_days, is_past, is_future, start_of_week, end_of_week
from util.math_utils import clamp, lerp, normalize, mean, median, variance, std_dev, round_to, percentage, is_prime
from util.string_utils import (camel_to_snake, snake_to_camel, snake_to_pascal, capitalize_words,
                                remove_whitespace, count_words, reverse, is_palindrome, pad_left, pad_right)
from util.cache_utils import Cache
from util.format_utils import (format_number, format_currency, format_percent, format_filesize,
                                format_duration, format_ordinal, format_list)
from util.type_utils import (is_int, is_float, is_numeric, is_string, is_bool, is_list, is_dict,
                              is_none, safe_int, safe_float, safe_bool, safe_cast, coerce, type_name)
from util.crypto_utils import (hash_md5, hash_sha256, hash_sha512, hash_password, verify_password,
                                hmac_sign, hmac_verify, encode_base64, decode_base64, xor_encrypt, xor_decrypt)
from util.file_utils import (read_text, write_text, read_json, write_json, file_exists,
                              ensure_dir, delete_file, copy_file, list_files)


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


class TestDateUtils(unittest.TestCase):
    def test_parse_date(self):
        self.assertEqual(parse_date("2026-01-15"), date(2026, 1, 15))

    def test_parse_date_custom_fmt(self):
        self.assertEqual(parse_date("15/01/2026", "%d/%m/%Y"), date(2026, 1, 15))

    def test_format_date(self):
        self.assertEqual(format_date(date(2026, 1, 15)), "2026-01-15")

    def test_format_date_custom_fmt(self):
        self.assertEqual(format_date(date(2026, 1, 15), "%d.%m.%Y"), "15.01.2026")

    def test_days_between(self):
        self.assertEqual(days_between(date(2026, 1, 1), date(2026, 1, 11)), 10)

    def test_days_between_negative(self):
        self.assertEqual(days_between(date(2026, 1, 11), date(2026, 1, 1)), -10)

    def test_add_days(self):
        self.assertEqual(add_days(date(2026, 1, 1), 10), date(2026, 1, 11))

    def test_add_days_negative(self):
        self.assertEqual(add_days(date(2026, 1, 11), -10), date(2026, 1, 1))

    def test_is_past(self):
        self.assertTrue(is_past(date(2000, 1, 1)))

    def test_is_past_false(self):
        self.assertFalse(is_past(date(2099, 1, 1)))

    def test_is_future(self):
        self.assertTrue(is_future(date(2099, 1, 1)))

    def test_is_future_false(self):
        self.assertFalse(is_future(date(2000, 1, 1)))

    def test_start_of_week(self):
        # 2026-05-11 is a Monday → start of week is itself
        d = date(2026, 5, 11)
        self.assertEqual(start_of_week(d).weekday(), 0)

    def test_end_of_week(self):
        d = date(2026, 5, 11)
        self.assertEqual(end_of_week(d).weekday(), 6)

    def test_start_end_week_span(self):
        d = date(2026, 5, 13)  # Wednesday
        self.assertEqual(days_between(start_of_week(d), end_of_week(d)), 6)


class TestMathUtils(unittest.TestCase):
    def test_clamp_within(self):
        self.assertEqual(clamp(5, 0, 10), 5)

    def test_clamp_below(self):
        self.assertEqual(clamp(-5, 0, 10), 0)

    def test_clamp_above(self):
        self.assertEqual(clamp(15, 0, 10), 10)

    def test_lerp_start(self):
        self.assertEqual(lerp(0, 100, 0), 0)

    def test_lerp_end(self):
        self.assertEqual(lerp(0, 100, 1), 100)

    def test_lerp_mid(self):
        self.assertEqual(lerp(0, 100, 0.5), 50)

    def test_normalize_basic(self):
        result = normalize([0, 5, 10])
        self.assertAlmostEqual(result[0], 0.0)
        self.assertAlmostEqual(result[1], 0.5)
        self.assertAlmostEqual(result[2], 1.0)

    def test_normalize_all_equal(self):
        self.assertEqual(normalize([3, 3, 3]), [0.0, 0.0, 0.0])

    def test_mean(self):
        self.assertEqual(mean([1, 2, 3, 4, 5]), 3.0)

    def test_median_odd(self):
        self.assertEqual(median([1, 3, 5]), 3)

    def test_median_even(self):
        self.assertEqual(median([1, 2, 3, 4]), 2.5)

    def test_variance(self):
        self.assertAlmostEqual(variance([2, 4, 4, 4, 5, 5, 7, 9]), 4.0)

    def test_std_dev(self):
        self.assertAlmostEqual(std_dev([2, 4, 4, 4, 5, 5, 7, 9]), 2.0)

    def test_round_to(self):
        self.assertEqual(round_to(3.14159, 2), 3.14)

    def test_percentage_normal(self):
        self.assertAlmostEqual(percentage(25, 200), 12.5)

    def test_percentage_zero_total(self):
        self.assertEqual(percentage(10, 0), 0.0)

    def test_is_prime_true(self):
        for p in (2, 3, 5, 7, 11, 13, 23):
            self.assertTrue(is_prime(p), f"{p} should be prime")

    def test_is_prime_false(self):
        for n in (0, 1, 4, 6, 9, 15, 42):
            self.assertFalse(is_prime(n), f"{n} should not be prime")


class TestStringUtils(unittest.TestCase):
    def test_camel_to_snake(self):
        self.assertEqual(camel_to_snake("myVariableName"), "my_variable_name")

    def test_camel_to_snake_acronym(self):
        self.assertEqual(camel_to_snake("parseHTMLDocument"), "parse_html_document")

    def test_snake_to_camel(self):
        self.assertEqual(snake_to_camel("my_variable_name"), "myVariableName")

    def test_snake_to_camel_single(self):
        self.assertEqual(snake_to_camel("word"), "word")

    def test_snake_to_pascal(self):
        self.assertEqual(snake_to_pascal("my_variable_name"), "MyVariableName")

    def test_capitalize_words(self):
        self.assertEqual(capitalize_words("hello world"), "Hello World")

    def test_remove_whitespace(self):
        self.assertEqual(remove_whitespace("h e l l o"), "hello")

    def test_count_words(self):
        self.assertEqual(count_words("the quick brown fox"), 4)

    def test_reverse(self):
        self.assertEqual(reverse("Claude"), "edualC")

    def test_is_palindrome_true(self):
        self.assertTrue(is_palindrome("A man a plan a canal Panama"))

    def test_is_palindrome_false(self):
        self.assertFalse(is_palindrome("hello"))

    def test_is_palindrome_simple(self):
        self.assertTrue(is_palindrome("racecar"))

    def test_pad_left(self):
        self.assertEqual(pad_left("42", 6, "0"), "000042")

    def test_pad_right(self):
        self.assertEqual(pad_right("hi", 5, "-"), "hi---")


class TestCacheUtils(unittest.TestCase):
    def test_set_and_get(self):
        c = Cache()
        c.set("k", "v")
        self.assertEqual(c.get("k"), "v")

    def test_get_missing_default(self):
        c = Cache()
        self.assertIsNone(c.get("missing"))
        self.assertEqual(c.get("missing", "fallback"), "fallback")

    def test_delete(self):
        c = Cache()
        c.set("k", 1)
        self.assertTrue(c.delete("k"))
        self.assertIsNone(c.get("k"))

    def test_delete_missing(self):
        c = Cache()
        self.assertFalse(c.delete("nope"))

    def test_has(self):
        c = Cache()
        c.set("x", 42)
        self.assertTrue(c.has("x"))
        self.assertFalse(c.has("y"))

    def test_clear(self):
        c = Cache()
        c.set("a", 1)
        c.set("b", 2)
        c.clear()
        self.assertEqual(c.size(), 0)

    def test_size(self):
        c = Cache()
        self.assertEqual(c.size(), 0)
        c.set("a", 1)
        c.set("b", 2)
        self.assertEqual(c.size(), 2)

    def test_ttl_expiry(self):
        import time
        c = Cache()
        c.set("k", "v", ttl=0.05)
        time.sleep(0.1)
        self.assertIsNone(c.get("k"))

    def test_purge_expired(self):
        import time
        c = Cache()
        c.set("a", 1, ttl=0.05)
        c.set("b", 2)
        time.sleep(0.1)
        purged = c.purge_expired()
        self.assertEqual(purged, 1)
        self.assertEqual(c.size(), 1)


class TestFormatUtils(unittest.TestCase):
    def test_format_number(self):
        self.assertEqual(format_number(1234567.89), "1,234,567.89")

    def test_format_number_custom_sep(self):
        self.assertEqual(format_number(1000.0, decimals=0, sep="."), "1.000")

    def test_format_currency(self):
        self.assertEqual(format_currency(9.99), "$9.99")

    def test_format_currency_symbol(self):
        self.assertIn("€", format_currency(100, symbol="€"))

    def test_format_percent(self):
        self.assertEqual(format_percent(75.3), "75.3%")

    def test_format_filesize_bytes(self):
        self.assertEqual(format_filesize(500), "500.0 B")

    def test_format_filesize_kb(self):
        self.assertEqual(format_filesize(2048), "2.0 KB")

    def test_format_filesize_mb(self):
        self.assertIn("MB", format_filesize(1_500_000))

    def test_format_duration_zero(self):
        self.assertEqual(format_duration(0), "0s")

    def test_format_duration_seconds(self):
        self.assertEqual(format_duration(90), "1m 30s")

    def test_format_duration_hours(self):
        self.assertEqual(format_duration(3725), "1h 2m 5s")

    def test_format_ordinal_st(self):
        self.assertEqual(format_ordinal(1), "1st")

    def test_format_ordinal_nd(self):
        self.assertEqual(format_ordinal(2), "2nd")

    def test_format_ordinal_rd(self):
        self.assertEqual(format_ordinal(3), "3rd")

    def test_format_ordinal_th(self):
        self.assertEqual(format_ordinal(11), "11th")
        self.assertEqual(format_ordinal(12), "12th")
        self.assertEqual(format_ordinal(13), "13th")

    def test_format_ordinal_21st(self):
        self.assertEqual(format_ordinal(21), "21st")

    def test_format_list_empty(self):
        self.assertEqual(format_list([]), "")

    def test_format_list_one(self):
        self.assertEqual(format_list(["a"]), "a")

    def test_format_list_two(self):
        self.assertEqual(format_list(["a", "b"]), "a and b")

    def test_format_list_three(self):
        self.assertEqual(format_list(["a", "b", "c"]), "a, b and c")


class TestTypeUtils(unittest.TestCase):
    def test_is_int(self):
        self.assertTrue(is_int(42))
        self.assertFalse(is_int(True))
        self.assertFalse(is_int(3.14))

    def test_is_float(self):
        self.assertTrue(is_float(3.14))
        self.assertFalse(is_float(42))

    def test_is_numeric(self):
        self.assertTrue(is_numeric(42))
        self.assertTrue(is_numeric(3.14))
        self.assertFalse(is_numeric(True))
        self.assertFalse(is_numeric("42"))

    def test_is_string(self):
        self.assertTrue(is_string("hi"))
        self.assertFalse(is_string(42))

    def test_is_bool(self):
        self.assertTrue(is_bool(True))
        self.assertFalse(is_bool(1))

    def test_is_list(self):
        self.assertTrue(is_list([]))
        self.assertFalse(is_list((1, 2)))

    def test_is_dict(self):
        self.assertTrue(is_dict({}))
        self.assertFalse(is_dict([]))

    def test_is_none(self):
        self.assertTrue(is_none(None))
        self.assertFalse(is_none(0))

    def test_safe_int_valid(self):
        self.assertEqual(safe_int("42"), 42)

    def test_safe_int_invalid(self):
        self.assertEqual(safe_int("oops", default=-1), -1)

    def test_safe_float_valid(self):
        self.assertAlmostEqual(safe_float("3.14"), 3.14)

    def test_safe_float_invalid(self):
        self.assertEqual(safe_float("x"), 0.0)

    def test_safe_bool_true_strings(self):
        for val in ("true", "yes", "1", "on"):
            self.assertTrue(safe_bool(val), f"safe_bool({val!r}) should be True")

    def test_safe_bool_false_string(self):
        self.assertFalse(safe_bool("false"))

    def test_safe_cast_success(self):
        self.assertEqual(safe_cast("7", int), 7)

    def test_safe_cast_failure(self):
        self.assertIsNone(safe_cast("abc", int))

    def test_coerce_bool(self):
        self.assertIs(coerce("true"), True)
        self.assertIs(coerce("false"), False)

    def test_coerce_none(self):
        self.assertIsNone(coerce("null"))

    def test_coerce_int(self):
        self.assertEqual(coerce("42"), 42)

    def test_coerce_float(self):
        self.assertAlmostEqual(coerce("3.14"), 3.14)

    def test_coerce_passthrough(self):
        self.assertEqual(coerce("hello"), "hello")

    def test_type_name(self):
        self.assertEqual(type_name(42), "int")
        self.assertEqual(type_name([]), "list")
        self.assertEqual(type_name(None), "NoneType")


class TestCryptoUtils(unittest.TestCase):
    def test_hash_md5(self):
        self.assertEqual(len(hash_md5("hello")), 32)
        self.assertEqual(hash_md5("hello"), hash_md5("hello"))

    def test_hash_sha256(self):
        self.assertEqual(len(hash_sha256("hello")), 64)

    def test_hash_sha512(self):
        self.assertEqual(len(hash_sha512("hello")), 128)

    def test_hash_password_and_verify(self):
        hashed, salt = hash_password("secret")
        self.assertTrue(verify_password("secret", hashed, salt))
        self.assertFalse(verify_password("wrong", hashed, salt))

    def test_hash_password_different_salts(self):
        h1, s1 = hash_password("same")
        h2, s2 = hash_password("same")
        self.assertNotEqual(s1, s2)

    def test_hmac_sign_and_verify(self):
        sig = hmac_sign("message", "key")
        self.assertTrue(hmac_verify("message", sig, "key"))
        self.assertFalse(hmac_verify("tampered", sig, "key"))

    def test_encode_decode_base64(self):
        original = "Hello, World!"
        encoded = encode_base64(original)
        self.assertEqual(decode_base64(encoded), original)

    def test_xor_encrypt_decrypt(self):
        token = xor_encrypt("secret", "key")
        self.assertEqual(xor_decrypt(token, "key"), "secret")


class TestFileUtils(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _path(self, name):
        return os.path.join(self.tmp, name)

    def test_write_and_read_text(self):
        p = self._path("hello.txt")
        write_text(p, "Hello!")
        self.assertEqual(read_text(p), "Hello!")

    def test_write_and_read_json(self):
        p = self._path("data.json")
        write_json(p, {"key": "value", "n": 42})
        data = read_json(p)
        self.assertEqual(data["key"], "value")
        self.assertEqual(data["n"], 42)

    def test_file_exists_true(self):
        p = self._path("f.txt")
        write_text(p, "x")
        self.assertTrue(file_exists(p))

    def test_file_exists_false(self):
        self.assertFalse(file_exists(self._path("nope.txt")))

    def test_ensure_dir(self):
        p = self._path("a/b/c")
        ensure_dir(p)
        self.assertTrue(os.path.isdir(p))

    def test_delete_file(self):
        p = self._path("del.txt")
        write_text(p, "bye")
        self.assertTrue(delete_file(p))
        self.assertFalse(file_exists(p))

    def test_delete_file_missing(self):
        self.assertFalse(delete_file(self._path("ghost.txt")))

    def test_copy_file(self):
        src = self._path("src.txt")
        dst = self._path("dst.txt")
        write_text(src, "copy me")
        copy_file(src, dst)
        self.assertEqual(read_text(dst), "copy me")

    def test_list_files(self):
        for name in ("a.txt", "b.txt", "c.txt"):
            write_text(self._path(name), "")
        files = list_files(self.tmp, "*.txt")
        self.assertEqual(len(files), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
