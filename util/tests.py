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
from util.env_utils import get_env, require_env, get_bool, get_int, get_float, get_list, is_production, is_development
from util.retry_utils import retry, with_fallback
from util.token_utils import (generate_token, generate_urlsafe_token, generate_uuid,
                               generate_short_id, create_signed_token, verify_signed_token, hash_token)
from util.pagination_utils import Page, paginate, page_range
from util.search_utils import filter_by, search_by_key, sort_by, fuzzy_match, highlight, multi_search
from util.serializer_utils import to_json, from_json, to_csv, from_csv, to_flat, from_flat, pick, omit
from util.compression_utils import (zlib_compress, zlib_decompress, gzip_compress, gzip_decompress,
                                     bz2_compress, bz2_decompress, lzma_compress, lzma_decompress,
                                     compression_ratio)
from util.diff_utils import (diff_ratio, is_similar, added_lines, removed_lines,
                              common_lines, dict_diff, lcs, close_matches)
from util.geo_utils import (haversine, distance_miles, is_valid_lat, is_valid_lon, is_valid_coords,
                             bbox, point_in_bbox, km_to_miles, miles_to_km, decimal_to_dms, dms_to_decimal)
from util.sort_utils import (is_sorted, bubble_sort, selection_sort, insertion_sort, merge_sort,
                              quick_sort, heap_sort, counting_sort, binary_search)
from util.graph_utils import (Graph, bfs, dfs, shortest_path, dijkstra, has_cycle, is_connected,
                               topological_sort)
from util.validation_utils import (ValidationError, ValidationResult, validate, validate_type,
                                    validate_range, validate_length, validate_pattern,
                                    validate_choices, validate_required, Validator)
from util.http_client_utils import (HttpError, Response, HttpClient,
                                     build_url, encode_params, parse_url)
from util.smtp_utils import (SmtpError, Attachment, EmailMessage, SmtpClient, message)


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


class TestEnvUtils(unittest.TestCase):
    def setUp(self):
        os.environ["_TEST_STR"] = "hello"
        os.environ["_TEST_BOOL_TRUE"] = "true"
        os.environ["_TEST_BOOL_FALSE"] = "false"
        os.environ["_TEST_INT"] = "42"
        os.environ["_TEST_FLOAT"] = "3.14"
        os.environ["_TEST_LIST"] = "a, b, c"

    def tearDown(self):
        for key in ("_TEST_STR", "_TEST_BOOL_TRUE", "_TEST_BOOL_FALSE",
                    "_TEST_INT", "_TEST_FLOAT", "_TEST_LIST", "APP_ENV"):
            os.environ.pop(key, None)

    def test_get_env_existing(self):
        self.assertEqual(get_env("_TEST_STR"), "hello")

    def test_get_env_missing_default(self):
        self.assertEqual(get_env("_MISSING_XYZ", "fallback"), "fallback")

    def test_require_env_exists(self):
        self.assertEqual(require_env("_TEST_STR"), "hello")

    def test_require_env_missing_raises(self):
        with self.assertRaises(KeyError):
            require_env("_MISSING_XYZ")

    def test_get_bool_true(self):
        self.assertTrue(get_bool("_TEST_BOOL_TRUE"))

    def test_get_bool_false(self):
        self.assertFalse(get_bool("_TEST_BOOL_FALSE"))

    def test_get_bool_missing_default(self):
        self.assertFalse(get_bool("_MISSING_XYZ", False))

    def test_get_int(self):
        self.assertEqual(get_int("_TEST_INT"), 42)

    def test_get_int_missing(self):
        self.assertEqual(get_int("_MISSING_XYZ", 99), 99)

    def test_get_float(self):
        self.assertAlmostEqual(get_float("_TEST_FLOAT"), 3.14)

    def test_get_list(self):
        self.assertEqual(get_list("_TEST_LIST"), ["a", "b", "c"])

    def test_get_list_missing(self):
        self.assertEqual(get_list("_MISSING_XYZ"), [])

    def test_is_production_true(self):
        os.environ["APP_ENV"] = "production"
        self.assertTrue(is_production())

    def test_is_production_false(self):
        os.environ["APP_ENV"] = "development"
        self.assertFalse(is_production())

    def test_is_development_true(self):
        os.environ["APP_ENV"] = "development"
        self.assertTrue(is_development())


class TestRetryUtils(unittest.TestCase):
    def test_retry_succeeds_first_try(self):
        result = retry(lambda: "ok", attempts=3, delay=0)
        self.assertEqual(result, "ok")

    def test_retry_succeeds_after_failures(self):
        calls = []

        def flaky():
            calls.append(1)
            if len(calls) < 3:
                raise ValueError("fail")
            return "done"

        result = retry(flaky, attempts=3, delay=0)
        self.assertEqual(result, "done")
        self.assertEqual(len(calls), 3)

    def test_retry_raises_after_all_attempts(self):
        with self.assertRaises(ValueError):
            retry(lambda: (_ for _ in ()).throw(ValueError("always")),
                  attempts=3, delay=0, exceptions=(ValueError,))

    def test_with_fallback_success(self):
        self.assertEqual(with_fallback(lambda: 42, "fallback"), 42)

    def test_with_fallback_on_error(self):
        def boom():
            raise RuntimeError("oops")
        self.assertEqual(with_fallback(boom, "fallback"), "fallback")


class TestTokenUtils(unittest.TestCase):
    def test_generate_token_length(self):
        token = generate_token(16)
        self.assertEqual(len(token), 32)  # hex → 2 chars per byte

    def test_generate_token_unique(self):
        self.assertNotEqual(generate_token(), generate_token())

    def test_generate_urlsafe_token(self):
        token = generate_urlsafe_token(16)
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)

    def test_generate_uuid_format(self):
        uid = generate_uuid()
        self.assertRegex(uid, r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

    def test_generate_short_id_length(self):
        self.assertEqual(len(generate_short_id(8)), 8)
        self.assertEqual(len(generate_short_id(12)), 12)

    def test_hash_token(self):
        h = hash_token("my-token")
        self.assertEqual(len(h), 64)
        self.assertEqual(h, hash_token("my-token"))

    def test_create_and_verify_signed_token(self):
        payload = {"user_id": 1, "role": "admin"}
        token = create_signed_token(payload, "secret")
        result = verify_signed_token(token, "secret")
        self.assertEqual(result["user_id"], 1)

    def test_verify_signed_token_wrong_secret(self):
        token = create_signed_token({"x": 1}, "secret")
        self.assertIsNone(verify_signed_token(token, "wrong"))

    def test_verify_signed_token_expired(self):
        token = create_signed_token({"x": 1}, "secret", expires_in=-1)
        self.assertIsNone(verify_signed_token(token, "secret"))

    def test_verify_signed_token_tampered(self):
        token = create_signed_token({"x": 1}, "secret")
        tampered = token[:-4] + "xxxx"
        self.assertIsNone(verify_signed_token(tampered, "secret"))


class TestPaginationUtils(unittest.TestCase):
    def setUp(self):
        self.data = list(range(1, 48))  # 47 items

    def test_paginate_first_page(self):
        p = paginate(self.data, page=1, page_size=10)
        self.assertEqual(p.items, list(range(1, 11)))
        self.assertEqual(p.total, 47)
        self.assertEqual(p.total_pages, 5)

    def test_paginate_last_page(self):
        p = paginate(self.data, page=5, page_size=10)
        self.assertEqual(p.items, list(range(41, 48)))

    def test_page_has_next(self):
        self.assertTrue(paginate(self.data, 1, 10).has_next)
        self.assertFalse(paginate(self.data, 5, 10).has_next)

    def test_page_has_prev(self):
        self.assertFalse(paginate(self.data, 1, 10).has_prev)
        self.assertTrue(paginate(self.data, 2, 10).has_prev)

    def test_page_next_prev(self):
        p = paginate(self.data, page=3, page_size=10)
        self.assertEqual(p.next_page, 4)
        self.assertEqual(p.prev_page, 2)

    def test_paginate_clamps_page(self):
        p = paginate(self.data, page=0, page_size=10)
        self.assertEqual(p.page, 1)

    def test_page_range_basic(self):
        result = page_range(10, current=5)
        self.assertIn(5, result)
        self.assertIn(1, result)
        self.assertIn(10, result)

    def test_page_range_single(self):
        self.assertEqual(page_range(1, current=1), [1])

    def test_page_to_dict(self):
        p = paginate(self.data, 2, 10)
        d = p.to_dict()
        self.assertEqual(d["page"], 2)
        self.assertIn("has_next", d)


class TestSearchUtils(unittest.TestCase):
    def setUp(self):
        self.items = [
            {"id": 1, "name": "Laptop Pro", "category": "electronics", "price": 2999},
            {"id": 2, "name": "Wireless Mouse", "category": "electronics", "price": 149},
            {"id": 3, "name": "Standing Desk", "category": "furniture", "price": 1200},
            {"id": 4, "name": "Desk Lamp", "category": "furniture", "price": 89},
        ]

    def test_filter_by_single(self):
        result = filter_by(self.items, category="electronics")
        self.assertEqual(len(result), 2)

    def test_filter_by_multiple(self):
        result = filter_by(self.items, category="furniture", price=89)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Desk Lamp")

    def test_search_by_key(self):
        result = search_by_key(self.items, "name", "desk")
        self.assertEqual(len(result), 2)

    def test_search_by_key_case_sensitive(self):
        result = search_by_key(self.items, "name", "Desk", case_sensitive=True)
        self.assertEqual(len(result), 2)
        result2 = search_by_key(self.items, "name", "desk", case_sensitive=True)
        self.assertEqual(len(result2), 0)

    def test_sort_by(self):
        result = sort_by(self.items, "price")
        self.assertEqual(result[0]["price"], 89)
        self.assertEqual(result[-1]["price"], 2999)

    def test_sort_by_reverse(self):
        result = sort_by(self.items, "price", reverse=True)
        self.assertEqual(result[0]["price"], 2999)

    def test_fuzzy_match_true(self):
        self.assertTrue(fuzzy_match("Laptop Pro", "lpt"))

    def test_fuzzy_match_false(self):
        self.assertFalse(fuzzy_match("Mouse", "lpt"))

    def test_highlight(self):
        result = highlight("Standing Desk and Desk Lamp", "desk")
        self.assertIn("**Desk**", result)

    def test_multi_search(self):
        result = multi_search(self.items, ["name", "category"], "elect")
        self.assertEqual(len(result), 2)


class TestSerializerUtils(unittest.TestCase):
    def test_to_json_basic(self):
        self.assertEqual(from_json(to_json({"a": 1})), {"a": 1})

    def test_to_json_date(self):
        from datetime import date as d
        result = to_json({"born": d(2023, 3, 14)})
        self.assertIn("2023-03-14", result)

    def test_to_csv_round_trip(self):
        records = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        csv_str = to_csv(records)
        result = from_csv(csv_str)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Alice")

    def test_to_csv_empty(self):
        self.assertEqual(to_csv([]), "")

    def test_to_flat(self):
        nested = {"a": {"b": {"c": 1}}}
        self.assertEqual(to_flat(nested), {"a.b.c": 1})

    def test_from_flat(self):
        flat = {"a.b.c": 1}
        self.assertEqual(from_flat(flat), {"a": {"b": {"c": 1}}})

    def test_pick(self):
        d = {"a": 1, "b": 2, "c": 3}
        self.assertEqual(pick(d, ["a", "c"]), {"a": 1, "c": 3})

    def test_omit(self):
        d = {"a": 1, "b": 2, "c": 3}
        self.assertEqual(omit(d, ["b"]), {"a": 1, "c": 3})


class TestCompressionUtils(unittest.TestCase):
    TEXT = "Hello, World! " * 50

    def test_zlib_round_trip(self):
        self.assertEqual(zlib_decompress(zlib_compress(self.TEXT)), self.TEXT)

    def test_gzip_round_trip(self):
        self.assertEqual(gzip_decompress(gzip_compress(self.TEXT)), self.TEXT)

    def test_bz2_round_trip(self):
        self.assertEqual(bz2_decompress(bz2_compress(self.TEXT)), self.TEXT)

    def test_lzma_round_trip(self):
        self.assertEqual(lzma_decompress(lzma_compress(self.TEXT)), self.TEXT)

    def test_zlib_compresses(self):
        compressed = zlib_compress(self.TEXT)
        self.assertLess(len(compressed), len(self.TEXT.encode()))

    def test_compression_ratio(self):
        compressed = gzip_compress(self.TEXT)
        ratio = compression_ratio(self.TEXT, compressed)
        self.assertLess(ratio, 100.0)
        self.assertGreater(ratio, 0.0)

    def test_zlib_accepts_bytes(self):
        data = b"binary data"
        self.assertEqual(zlib_decompress(zlib_compress(data)), "binary data")


class TestDiffUtils(unittest.TestCase):
    def test_diff_ratio_identical(self):
        self.assertEqual(diff_ratio("hello", "hello"), 1.0)

    def test_diff_ratio_different(self):
        self.assertLess(diff_ratio("cat", "dog"), 1.0)

    def test_is_similar_true(self):
        self.assertTrue(is_similar("hello", "helo", 0.7))

    def test_is_similar_false(self):
        self.assertFalse(is_similar("cat", "dog", 0.9))

    def test_added_lines(self):
        a = "line1\nline2"
        b = "line1\nline2\nline3"
        self.assertEqual(added_lines(a, b), ["line3"])

    def test_removed_lines(self):
        a = "line1\nline2\nline3"
        b = "line1\nline2"
        self.assertEqual(removed_lines(a, b), ["line3"])

    def test_common_lines(self):
        a = "foo\nbar\nbaz"
        b = "foo\nbar\nqux"
        self.assertIn("foo", common_lines(a, b))
        self.assertIn("bar", common_lines(a, b))
        self.assertNotIn("baz", common_lines(a, b))

    def test_dict_diff(self):
        a = {"x": 1, "y": 2, "z": 3}
        b = {"x": 1, "y": 99, "w": 4}
        diff = dict_diff(a, b)
        self.assertIn("w", diff["added"])
        self.assertIn("z", diff["removed"])
        self.assertIn("y", diff["changed"])

    def test_lcs(self):
        self.assertEqual(lcs([1, 2, 3, 4], [2, 4, 6]), [2, 4])

    def test_close_matches(self):
        result = close_matches("hellp", ["hello", "world", "help"])
        self.assertIn("hello", result)


class TestGeoUtils(unittest.TestCase):
    # Warsaw and Berlin coordinates
    WAW = (52.2297, 21.0122)
    BER = (52.5200, 13.4050)

    def test_haversine_known_distance(self):
        dist = haversine(*self.WAW, *self.BER)
        self.assertAlmostEqual(dist, 517, delta=5)

    def test_haversine_same_point(self):
        self.assertEqual(haversine(*self.WAW, *self.WAW), 0.0)

    def test_distance_miles(self):
        km = haversine(*self.WAW, *self.BER)
        mi = distance_miles(*self.WAW, *self.BER)
        self.assertAlmostEqual(mi, km * 0.621371, delta=1)

    def test_is_valid_lat(self):
        self.assertTrue(is_valid_lat(52.23))
        self.assertFalse(is_valid_lat(91.0))
        self.assertFalse(is_valid_lat(-91.0))

    def test_is_valid_lon(self):
        self.assertTrue(is_valid_lon(21.01))
        self.assertFalse(is_valid_lon(181.0))

    def test_is_valid_coords(self):
        self.assertTrue(is_valid_coords(52.23, 21.01))
        self.assertFalse(is_valid_coords(91.0, 0.0))

    def test_bbox(self):
        points = [(50.0, 10.0), (52.0, 20.0), (48.0, 15.0)]
        min_lat, min_lon, max_lat, max_lon = bbox(points)
        self.assertEqual(min_lat, 48.0)
        self.assertEqual(max_lon, 20.0)

    def test_point_in_bbox(self):
        box = (48.0, 10.0, 54.0, 25.0)
        self.assertTrue(point_in_bbox(52.23, 21.01, box))
        self.assertFalse(point_in_bbox(0.0, 0.0, box))

    def test_km_to_miles_round_trip(self):
        self.assertAlmostEqual(miles_to_km(km_to_miles(100)), 100, delta=0.01)

    def test_decimal_to_dms_round_trip(self):
        deg, mn, sec = decimal_to_dms(52.2297)
        result = dms_to_decimal(deg, mn, sec)
        self.assertAlmostEqual(result, 52.2297, places=3)


class TestSortUtils(unittest.TestCase):
    DATA = [64, 34, 25, 12, 22, 11, 90]
    SORTED = sorted(DATA)

    def test_is_sorted_true(self):
        self.assertTrue(is_sorted([1, 2, 3]))

    def test_is_sorted_false(self):
        self.assertFalse(is_sorted([3, 1, 2]))

    def test_is_sorted_reverse(self):
        self.assertTrue(is_sorted([3, 2, 1], reverse=True))

    def test_bubble_sort(self):
        self.assertEqual(bubble_sort(self.DATA), self.SORTED)

    def test_selection_sort(self):
        self.assertEqual(selection_sort(self.DATA), self.SORTED)

    def test_insertion_sort(self):
        self.assertEqual(insertion_sort(self.DATA), self.SORTED)

    def test_merge_sort(self):
        self.assertEqual(merge_sort(self.DATA), self.SORTED)

    def test_quick_sort(self):
        self.assertEqual(quick_sort(self.DATA), self.SORTED)

    def test_heap_sort(self):
        self.assertEqual(heap_sort(self.DATA), self.SORTED)

    def test_counting_sort(self):
        self.assertEqual(counting_sort(self.DATA), self.SORTED)

    def test_binary_search_found(self):
        self.assertEqual(binary_search(self.SORTED, 25), self.SORTED.index(25))

    def test_binary_search_not_found(self):
        self.assertEqual(binary_search(self.SORTED, 99), -1)


class TestGraphUtils(unittest.TestCase):
    def _build_graph(self):
        g = Graph()
        for u, v in [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E")]:
            g.add_edge(u, v)
        return g

    def test_add_node_and_edge(self):
        g = Graph()
        g.add_edge("X", "Y")
        self.assertTrue(g.has_node("X"))
        self.assertTrue(g.has_edge("X", "Y"))
        self.assertTrue(g.has_edge("Y", "X"))  # undirected

    def test_directed_no_reverse(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        self.assertTrue(g.has_edge("A", "B"))
        self.assertFalse(g.has_edge("B", "A"))

    def test_bfs_visits_all(self):
        g = self._build_graph()
        result = bfs(g, "A")
        self.assertEqual(set(result), {"A", "B", "C", "D", "E"})

    def test_dfs_visits_all(self):
        g = self._build_graph()
        result = dfs(g, "A")
        self.assertEqual(set(result), {"A", "B", "C", "D", "E"})

    def test_shortest_path(self):
        g = self._build_graph()
        path = shortest_path(g, "A", "E")
        self.assertEqual(path[0], "A")
        self.assertEqual(path[-1], "E")

    def test_shortest_path_no_route(self):
        g = Graph()
        g.add_node("X")
        g.add_node("Y")
        self.assertIsNone(shortest_path(g, "X", "Y"))

    def test_dijkstra(self):
        g = Graph()
        g.add_edge("A", "B", 1)
        g.add_edge("A", "C", 4)
        g.add_edge("B", "C", 2)
        dist = dijkstra(g, "A")
        self.assertEqual(dist["A"], 0.0)
        self.assertEqual(dist["B"], 1.0)
        self.assertEqual(dist["C"], 3.0)

    def test_has_cycle_false(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        self.assertFalse(has_cycle(g))

    def test_has_cycle_true(self):
        g = Graph()
        g.add_edge("X", "Y")
        g.add_edge("Y", "Z")
        g.add_edge("Z", "X")
        self.assertTrue(has_cycle(g))

    def test_is_connected_true(self):
        self.assertTrue(is_connected(self._build_graph()))

    def test_is_connected_false(self):
        g = Graph()
        g.add_node("A")
        g.add_node("B")
        self.assertFalse(is_connected(g))

    def test_topological_sort(self):
        dag = Graph(directed=True)
        for u, v in [("A", "C"), ("B", "C"), ("C", "D")]:
            dag.add_edge(u, v)
        order = topological_sort(dag)
        self.assertLess(order.index("C"), order.index("D"))
        self.assertLess(order.index("A"), order.index("C"))


class TestValidationUtils(unittest.TestCase):
    def test_validate_valid_data(self):
        schema = {"name": {"type": str, "min_length": 2}, "age": {"type": int, "min": 0}}
        result = validate({"name": "Alice", "age": 30}, schema)
        self.assertTrue(result.is_valid)

    def test_validate_missing_required(self):
        schema = {"name": {"type": str}}
        result = validate({}, schema)
        self.assertFalse(result.is_valid)
        self.assertIn("name", result.errors)

    def test_validate_wrong_type(self):
        schema = {"age": {"type": int}}
        result = validate({"age": "thirty"}, schema)
        self.assertFalse(result.is_valid)

    def test_validate_out_of_range(self):
        schema = {"score": {"type": int, "min": 0, "max": 100}}
        result = validate({"score": 150}, schema)
        self.assertFalse(result.is_valid)

    def test_validate_choices(self):
        schema = {"role": {"type": str, "choices": ["admin", "user"]}}
        self.assertFalse(validate({"role": "superuser"}, schema).is_valid)
        self.assertTrue(validate({"role": "admin"}, schema).is_valid)

    def test_validate_type(self):
        self.assertTrue(validate_type(42, int))
        self.assertFalse(validate_type("x", int))

    def test_validate_range(self):
        self.assertTrue(validate_range(50, 0, 100))
        self.assertFalse(validate_range(150, 0, 100))

    def test_validate_length(self):
        self.assertTrue(validate_length("hello", 3, 10))
        self.assertFalse(validate_length("hi", 3, 10))

    def test_validate_pattern(self):
        self.assertTrue(validate_pattern("abc123", r"\w+"))
        self.assertFalse(validate_pattern("abc 123", r"\w+"))

    def test_validate_choices_fn(self):
        self.assertTrue(validate_choices("red", ["red", "green", "blue"]))
        self.assertFalse(validate_choices("yellow", ["red", "green", "blue"]))

    def test_validate_required(self):
        missing = validate_required({"a": 1, "b": None}, ["a", "b"])
        self.assertEqual(missing, ["b"])

    def test_validator_chain_valid(self):
        v = Validator("hello@world.com", "email").required().type(str).min_length(5)
        self.assertTrue(v.is_valid)

    def test_validator_chain_invalid(self):
        v = Validator(17, "age").required().type(int).min(18).max(99)
        self.assertFalse(v.is_valid)
        self.assertTrue(any("18" in e for e in v.errors))

    def test_validator_raises(self):
        v = Validator("", "name").required()
        with self.assertRaises(ValidationError):
            v.raise_if_invalid()

    def test_validation_result_add_and_raise(self):
        vr = ValidationResult()
        vr.add("field", "some error")
        self.assertFalse(vr.is_valid)
        with self.assertRaises(ValidationError):
            vr.raise_if_invalid()


class TestHttpError(unittest.TestCase):
    def test_attributes(self):
        e = HttpError(404, "Not Found", "missing")
        self.assertEqual(e.status, 404)
        self.assertEqual(e.reason, "Not Found")
        self.assertEqual(e.body, "missing")

    def test_str(self):
        e = HttpError(500, "Internal Server Error")
        self.assertIn("500", str(e))
        self.assertIn("Internal Server Error", str(e))

    def test_default_body(self):
        e = HttpError(400, "Bad Request")
        self.assertEqual(e.body, "")

    def test_is_exception(self):
        with self.assertRaises(HttpError):
            raise HttpError(403, "Forbidden")


class TestResponse(unittest.TestCase):
    def _make(self, status=200, reason="OK", headers=None, raw=b"hello", url="http://x.com"):
        return Response(status, reason, headers or {}, raw, url)

    def test_ok_true(self):
        self.assertTrue(self._make(200).ok)
        self.assertTrue(self._make(201).ok)
        self.assertTrue(self._make(299).ok)

    def test_ok_false(self):
        self.assertFalse(self._make(400).ok)
        self.assertFalse(self._make(404).ok)
        self.assertFalse(self._make(500).ok)

    def test_text_utf8(self):
        r = self._make(raw=b"caf\xc3\xa9")
        self.assertEqual(r.text, "café")

    def test_text_charset_from_header(self):
        r = self._make(headers={"content-type": "text/html; charset=latin-1"}, raw="é".encode("latin-1"))
        self.assertIsInstance(r.text, str)

    def test_json(self):
        r = self._make(raw=b'{"key": 1}')
        self.assertEqual(r.json(), {"key": 1})

    def test_raise_for_status_ok(self):
        self._make(200).raise_for_status()

    def test_raise_for_status_error(self):
        with self.assertRaises(HttpError) as ctx:
            self._make(404, "Not Found").raise_for_status()
        self.assertEqual(ctx.exception.status, 404)

    def test_repr(self):
        r = self._make(200, url="http://example.com")
        self.assertIn("200", repr(r))
        self.assertIn("example.com", repr(r))

    def test_attributes(self):
        r = self._make(201, "Created", {"x-id": "abc"}, b"body", "http://y.com")
        self.assertEqual(r.status, 201)
        self.assertEqual(r.reason, "Created")
        self.assertEqual(r.headers, {"x-id": "abc"})
        self.assertEqual(r.content, b"body")
        self.assertEqual(r.url, "http://y.com")


class TestBuildUrl(unittest.TestCase):
    def test_no_path_no_params(self):
        self.assertEqual(build_url("https://api.example.com"), "https://api.example.com")

    def test_with_path(self):
        self.assertEqual(build_url("https://api.example.com", "/users"), "https://api.example.com/users")

    def test_strips_trailing_slash(self):
        self.assertEqual(build_url("https://api.example.com/", "/users"), "https://api.example.com/users")

    def test_with_params(self):
        url = build_url("https://api.example.com", "/search", {"q": "hello", "page": 1})
        self.assertIn("q=hello", url)
        self.assertIn("page=1", url)

    def test_none_params_filtered(self):
        url = build_url("https://api.example.com", "", {"q": "x", "empty": None})
        self.assertNotIn("empty", url)
        self.assertIn("q=x", url)


class TestEncodeParams(unittest.TestCase):
    def test_basic(self):
        result = encode_params({"a": "1", "b": "2"})
        self.assertIn("a=1", result)
        self.assertIn("b=2", result)

    def test_none_filtered(self):
        result = encode_params({"a": "x", "b": None})
        self.assertNotIn("b", result)
        self.assertIn("a=x", result)

    def test_special_chars_encoded(self):
        result = encode_params({"q": "hello world"})
        self.assertIn("hello+world", result)

    def test_empty(self):
        self.assertEqual(encode_params({}), "")


class TestParseUrl(unittest.TestCase):
    def test_full_url(self):
        parts = parse_url("https://api.example.com/v1/users?page=2#top")
        self.assertEqual(parts["scheme"], "https")
        self.assertEqual(parts["host"], "api.example.com")
        self.assertEqual(parts["path"], "/v1/users")
        self.assertEqual(parts["query"], "page=2")
        self.assertEqual(parts["fragment"], "top")

    def test_simple_url(self):
        parts = parse_url("http://localhost:8080/")
        self.assertEqual(parts["scheme"], "http")
        self.assertIn("localhost", parts["host"])

    def test_no_query_no_fragment(self):
        parts = parse_url("https://example.com/path")
        self.assertEqual(parts["query"], "")
        self.assertEqual(parts["fragment"], "")


class TestHttpClient(unittest.TestCase):
    def test_repr(self):
        client = HttpClient(base_url="https://api.example.com", timeout=5.0)
        r = repr(client)
        self.assertIn("api.example.com", r)
        self.assertIn("5.0", r)

    def test_default_headers(self):
        client = HttpClient()
        self.assertIn("Accept", client._headers)
        self.assertIn("User-Agent", client._headers)

    def test_custom_headers(self):
        client = HttpClient(headers={"X-Custom": "value"})
        self.assertEqual(client._headers["X-Custom"], "value")

    def test_set_header(self):
        client = HttpClient()
        client.set_header("X-Token", "abc123")
        self.assertEqual(client._headers["X-Token"], "abc123")

    def test_set_bearer(self):
        client = HttpClient()
        client.set_bearer("my-token")
        self.assertEqual(client._headers["Authorization"], "Bearer my-token")

    def test_set_auth_basic(self):
        import base64
        client = HttpClient()
        client.set_auth("user", "pass")
        token = base64.b64encode(b"user:pass").decode()
        self.assertEqual(client._headers["Authorization"], f"Basic {token}")

    def test_auth_in_constructor(self):
        import base64
        client = HttpClient(auth=("user", "pass"))
        token = base64.b64encode(b"user:pass").decode()
        self.assertEqual(client._headers["Authorization"], f"Basic {token}")

    def test_base_url_strips_slash(self):
        client = HttpClient(base_url="https://example.com/")
        self.assertEqual(client.base_url, "https://example.com")

    def test_retry_on_defaults(self):
        client = HttpClient()
        self.assertIn(500, client.retry_on)
        self.assertIn(503, client.retry_on)


class TestSmtpError(unittest.TestCase):
    def test_is_exception(self):
        with self.assertRaises(SmtpError):
            raise SmtpError("connection failed")

    def test_message(self):
        e = SmtpError("timeout")
        self.assertEqual(str(e), "timeout")


class TestAttachment(unittest.TestCase):
    def test_filename_from_path(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"data")
            path = f.name
        try:
            att = Attachment(path)
            self.assertEqual(att.filename, os.path.basename(path))
            self.assertFalse(att.inline)
            self.assertIsNone(att.cid)
        finally:
            os.unlink(path)

    def test_custom_filename(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"data")
            path = f.name
        try:
            att = Attachment(path, filename="custom.txt")
            self.assertEqual(att.filename, "custom.txt")
        finally:
            os.unlink(path)

    def test_inline_with_cid(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"\x89PNG")
            path = f.name
        try:
            att = Attachment(path, cid="img001")
            self.assertTrue(att.inline)
            self.assertEqual(att.cid, "img001")
        finally:
            os.unlink(path)

    def test_read(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"hello bytes")
            path = f.name
        try:
            att = Attachment(path)
            self.assertEqual(att.read(), b"hello bytes")
        finally:
            os.unlink(path)

    def test_mime_type_txt(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            path = f.name
        try:
            att = Attachment(path)
            main, sub = att.mime_type()
            self.assertEqual(main, "text")
        finally:
            os.unlink(path)

    def test_mime_type_unknown(self):
        with tempfile.NamedTemporaryFile(suffix=".xyzunknown", delete=False) as f:
            path = f.name
        try:
            att = Attachment(path)
            main, sub = att.mime_type()
            self.assertEqual(main, "application")
            self.assertEqual(sub, "octet-stream")
        finally:
            os.unlink(path)


class TestEmailMessage(unittest.TestCase):
    def _basic(self):
        return (
            EmailMessage()
            .from_addr("sender@example.com")
            .to("alice@example.com")
            .subject("Test")
            .text("Hello")
        )

    def test_text_only_mime_type(self):
        mime = self._basic().build()
        self.assertEqual(mime.get_content_type(), "text/plain")

    def test_html_only_mime_type(self):
        mime = (
            EmailMessage()
            .from_addr("a@b.com")
            .to("c@d.com")
            .subject("Hi")
            .html("<b>Bold</b>")
            .build()
        )
        self.assertEqual(mime.get_content_type(), "text/html")

    def test_text_and_html_mime_type(self):
        mime = (
            EmailMessage()
            .from_addr("a@b.com")
            .to("c@d.com")
            .subject("Hi")
            .text("plain")
            .html("<p>html</p>")
            .build()
        )
        self.assertEqual(mime.get_content_type(), "multipart/alternative")

    def test_from_addr_in_headers(self):
        mime = self._basic().build()
        self.assertEqual(mime["From"], "sender@example.com")

    def test_from_addr_with_name(self):
        mime = (
            EmailMessage()
            .from_addr("sender@example.com", "Alice")
            .to("b@b.com")
            .subject("s")
            .text("t")
            .build()
        )
        self.assertIn("Alice", mime["From"])
        self.assertIn("sender@example.com", mime["From"])

    def test_to_in_headers(self):
        mime = self._basic().build()
        self.assertIn("alice@example.com", mime["To"])

    def test_multiple_to(self):
        mime = (
            EmailMessage()
            .from_addr("a@b.com")
            .to("x@x.com", "y@y.com")
            .subject("s")
            .text("t")
            .build()
        )
        self.assertIn("x@x.com", mime["To"])
        self.assertIn("y@y.com", mime["To"])

    def test_cc_in_headers(self):
        mime = (
            EmailMessage()
            .from_addr("a@b.com")
            .to("x@x.com")
            .cc("cc@cc.com")
            .subject("s")
            .text("t")
            .build()
        )
        self.assertIn("cc@cc.com", mime["Cc"])

    def test_reply_to_in_headers(self):
        mime = (
            EmailMessage()
            .from_addr("a@b.com")
            .to("b@b.com")
            .reply_to("noreply@example.com")
            .subject("s")
            .text("t")
            .build()
        )
        self.assertEqual(mime["Reply-To"], "noreply@example.com")

    def test_subject_in_headers(self):
        mime = self._basic().build()
        self.assertEqual(mime["Subject"], "Test")

    def test_custom_header(self):
        mime = (
            EmailMessage()
            .from_addr("a@b.com")
            .to("b@b.com")
            .subject("s")
            .text("t")
            .header("X-Priority", "1")
            .build()
        )
        self.assertEqual(mime["X-Priority"], "1")

    def test_message_id_present(self):
        mime = self._basic().build()
        self.assertIsNotNone(mime["Message-ID"])

    def test_date_present(self):
        mime = self._basic().build()
        self.assertIsNotNone(mime["Date"])

    def test_all_recipients(self):
        msg = (
            EmailMessage()
            .from_addr("a@b.com")
            .to("to@to.com")
            .cc("cc@cc.com")
            .bcc("bcc@bcc.com")
            .subject("s")
            .text("t")
        )
        recipients = msg.all_recipients()
        self.assertIn("to@to.com", recipients)
        self.assertIn("cc@cc.com", recipients)
        self.assertIn("bcc@bcc.com", recipients)

    def test_empty_message_builds(self):
        mime = EmailMessage().build()
        self.assertEqual(mime.get_content_type(), "text/plain")

    def test_builder_chaining(self):
        msg = EmailMessage()
        result = msg.from_addr("a@b.com")
        self.assertIs(result, msg)

    def test_with_file_attachment(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"attachment content")
            path = f.name
        try:
            mime = (
                EmailMessage()
                .from_addr("a@b.com")
                .to("b@b.com")
                .subject("s")
                .text("body")
                .attach(path)
                .build()
            )
            self.assertEqual(mime.get_content_type(), "multipart/mixed")
        finally:
            os.unlink(path)


class TestSmtpClient(unittest.TestCase):
    def test_repr_not_connected(self):
        client = SmtpClient("smtp.example.com", 587)
        r = repr(client)
        self.assertIn("smtp.example.com", r)
        self.assertIn("587", r)
        self.assertIn("False", r)

    def test_send_without_connect_raises(self):
        client = SmtpClient("smtp.example.com")
        msg = EmailMessage().from_addr("a@b.com").to("b@b.com").subject("s").text("t")
        with self.assertRaises(SmtpError):
            client.send(msg)

    def test_send_raw_without_connect_raises(self):
        client = SmtpClient("smtp.example.com")
        with self.assertRaises(SmtpError):
            client.send_raw("a@b.com", ["b@b.com"], "raw mime")

    def test_context_manager_connect_fail(self):
        client = SmtpClient("localhost", 19999, use_tls=False)
        with self.assertRaises((SmtpError, OSError, ConnectionRefusedError)):
            with client:
                pass

    def test_disconnect_when_not_connected(self):
        client = SmtpClient("smtp.example.com")
        client.disconnect()

    def test_send_with_mock(self):
        from unittest.mock import MagicMock, patch
        mock_conn = MagicMock()
        client = SmtpClient("smtp.example.com")
        client._conn = mock_conn
        msg = EmailMessage().from_addr("a@b.com").to("b@b.com").subject("s").text("t")
        client.send(msg)
        mock_conn.sendmail.assert_called_once()

    def test_send_raw_with_mock(self):
        from unittest.mock import MagicMock
        mock_conn = MagicMock()
        client = SmtpClient("smtp.example.com")
        client._conn = mock_conn
        client.send_raw("a@b.com", ["b@b.com"], "raw string")
        mock_conn.sendmail.assert_called_once_with("a@b.com", ["b@b.com"], "raw string")


class TestMessageFactory(unittest.TestCase):
    def test_returns_email_message(self):
        self.assertIsInstance(message(), EmailMessage)

    def test_factory_builds(self):
        mime = message().from_addr("a@b.com").to("b@b.com").subject("s").text("t").build()
        self.assertEqual(mime.get_content_type(), "text/plain")


if __name__ == "__main__":
    unittest.main(verbosity=2)
