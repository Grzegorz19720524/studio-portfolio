import unittest
import tempfile
import os
from datetime import date
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
from util.pagination_utils import paginate, page_range
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
import logging
import signal as _signal
from util.logger import get_logger
from util.http_utils import is_ok
from util.event_utils import EventEmitter
from util.queue_utils import Queue, PriorityQueue
from util.decorator_utils import (memoize as deco_memoize, retry as deco_retry,
                                   singleton, deprecated, clamp_result)
from util.observer_utils import Observable, ObservableValue
from util.state_utils import Store, StateMachine
from util.color_utils import (hex_to_rgb, rgb_to_hex, rgb_to_hsl, hsl_to_rgb,
                               luminance, is_light, contrast_color,
                               lighten, darken, mix, complementary, random_color,
                               analogous, triadic)
from util.matrix_utils import (zeros, ones, identity as mat_identity, shape,
                                is_square, transpose, add as mat_add,
                                subtract as mat_sub, scalar_multiply,
                                multiply as mat_mul, trace, determinant,
                                flatten as mat_flatten, reshape,
                                get_row, get_col, map_matrix)
from util.tree_utils import (TreeNode, search as tree_search, delete as tree_delete,
                              inorder, preorder, postorder, level_order,
                              height, size as tree_size, min_node, max_node,
                              is_bst, is_balanced as tree_balanced,
                              from_list as tree_from_list, to_list as tree_to_list)
from util.linked_list_utils import (LinkedList, from_list as ll_from_list,
                                     has_cycle as ll_has_cycle, middle,
                                     merge_sorted, remove_duplicates)
from util.stack_utils import (Stack, is_balanced as stack_balanced,
                               evaluate_rpn, infix_to_rpn,
                               sort_stack, reverse_stack)
from util.functional_utils import (identity as fn_id, always, pipe as fn_pipe,
                                    compose as fn_compose,
                                    curry, flip, tap, complement, juxt,
                                    memoize as fn_memoize,
                                    reduce as fn_reduce, scan, take, drop,
                                    partition, group_by, zip_with,
                                    unique, flatten_iter)
from util.regex_utils import (is_match, find_all, extract, replace as re_replace,
                               split as re_split, named_groups,
                               strip_html, normalize_whitespace, escape,
                               EMAIL_PATTERN, DATE_PATTERN, HEX_COLOR_PATTERN)
from util.statistics_utils import (mean as stat_mean, median as stat_median,
                                    mode, variance as stat_var, stdev,
                                    harmonic_mean, geometric_mean, weighted_mean,
                                    quantile, quartiles, iqr, z_score,
                                    normalize as stat_normalize, covariance,
                                    correlation, moving_average, outliers,
                                    frequency, describe)
from util.ratelimit_utils import (RateLimitExceeded, FixedWindow, SlidingWindow,
                                   TokenBucket, LeakyBucket, try_acquire)
from util.circuit_breaker_utils import (CircuitBreaker, CircuitBreakerOpen,
                                         CircuitBreakerRegistry, State)
from util.event_bus_utils import Event, EventBus
from util.pipeline_utils import Pipeline, compose as pipe_compose, branch
from util.context_utils import suppress, temp_dir, temp_env, ManagedResource
from util.csv_utils import (csv_to_string, string_to_csv, col_values, select_cols,
                             filter_rows, sort_rows, transform_col, rename_col,
                             drop_col, deduplicate, write_csv, read_csv,
                             write_csv_rows, read_csv_rows, get_headers, count_rows,
                             append_row)
from util.iterator_utils import (chunks, sliding_window, pairwise, flatten as iter_flatten,
                                  deep_flatten, interleave, roundrobin,
                                  first, last, nth, count_items, all_equal,
                                  minmax, accumulate, zip_longest,
                                  product, permutations, combinations,
                                  combinations_with_replacement, Peekable)
from util.template_utils import (render, render_safe, register_filter, escape_html, Template)
from util.toml_utils import (parse_string as toml_parse, to_string as toml_to_str,
                              get as toml_get, set_value as toml_set, has_key as toml_has_key,
                              merge as toml_merge, flatten_keys, keys_at, write_toml, read_toml)
from util.xml_utils import (parse_string as xml_parse, to_string as xml_to_str,
                             create_element, add_child, remove_child,
                             find as xml_find, find_all as xml_find_all,
                             get_attr, set_attr, get_text, set_text,
                             get_all_text, element_to_dict, dict_to_element)
from util.ini_utils import (parse_string as ini_parse, to_string as ini_to_str,
                             get as ini_get, get_int as ini_get_int,
                             get_float as ini_get_float, get_bool as ini_get_bool,
                             set_value as ini_set, has_section, has_key as ini_has_key,
                             sections, keys as ini_keys, items as ini_items,
                             to_dict as ini_to_dict, from_dict as ini_from_dict,
                             remove_section, remove_key, merge as ini_merge)
from util.websocket_utils import (WebSocketError, WebSocketClosed, Frame,
                                   WebSocketClient, OP_TEXT, OP_BINARY,
                                   OP_CLOSE, OP_PING, OP_PONG, _encode_frame)
from util.signal_utils import (handle, ignore, reset, current_handler,
                                available_signals, raise_signal,
                                on_sigint, on_sigterm, register_shutdown,
                                SignalCounter, GracefulShutdown)


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
        from unittest.mock import MagicMock
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


class TestWebSocketError(unittest.TestCase):
    def test_is_exception(self):
        with self.assertRaises(WebSocketError):
            raise WebSocketError("something went wrong")

    def test_message(self):
        e = WebSocketError("bad frame")
        self.assertEqual(str(e), "bad frame")


class TestWebSocketClosed(unittest.TestCase):
    def test_inherits_websocket_error(self):
        with self.assertRaises(WebSocketError):
            raise WebSocketClosed(1000, "normal")

    def test_default_code_and_reason(self):
        e = WebSocketClosed()
        self.assertEqual(e.code, 1000)
        self.assertEqual(e.reason, "")

    def test_custom_code_and_reason(self):
        e = WebSocketClosed(1001, "going away")
        self.assertEqual(e.code, 1001)
        self.assertEqual(e.reason, "going away")

    def test_str_contains_code(self):
        e = WebSocketClosed(1008, "policy violation")
        self.assertIn("1008", str(e))
        self.assertIn("policy violation", str(e))


class TestFrame(unittest.TestCase):
    def test_is_text(self):
        f = Frame(OP_TEXT, b"hello")
        self.assertTrue(f.is_text)
        self.assertFalse(f.is_binary)
        self.assertFalse(f.is_close)
        self.assertFalse(f.is_ping)
        self.assertFalse(f.is_pong)

    def test_is_binary(self):
        f = Frame(OP_BINARY, b"\x00\xFF")
        self.assertTrue(f.is_binary)
        self.assertFalse(f.is_text)

    def test_is_close(self):
        f = Frame(OP_CLOSE, b"")
        self.assertTrue(f.is_close)

    def test_is_ping(self):
        f = Frame(OP_PING, b"ping")
        self.assertTrue(f.is_ping)
        self.assertFalse(f.is_pong)

    def test_is_pong(self):
        f = Frame(OP_PONG, b"pong")
        self.assertTrue(f.is_pong)
        self.assertFalse(f.is_ping)

    def test_fin_default_true(self):
        f = Frame(OP_TEXT, b"x")
        self.assertTrue(f.fin)

    def test_fin_false(self):
        f = Frame(OP_TEXT, b"x", fin=False)
        self.assertFalse(f.fin)

    def test_payload_stored(self):
        f = Frame(OP_BINARY, b"\x01\x02\x03")
        self.assertEqual(f.payload, b"\x01\x02\x03")

    def test_repr(self):
        f = Frame(OP_TEXT, b"hello")
        r = repr(f)
        self.assertIn("0x1", r)
        self.assertIn("5", r)


class TestEncodeFrame(unittest.TestCase):
    def test_small_payload_no_mask_length(self):
        frame = _encode_frame(OP_TEXT, b"hi", mask=False)
        self.assertEqual(frame[0], 0x80 | OP_TEXT)
        self.assertEqual(frame[1], 2)
        self.assertEqual(frame[2:], b"hi")

    def test_opcode_binary_no_mask(self):
        frame = _encode_frame(OP_BINARY, b"\xFF", mask=False)
        self.assertEqual(frame[0] & 0x0F, OP_BINARY)

    def test_fin_bit_set(self):
        frame = _encode_frame(OP_TEXT, b"x", mask=False)
        self.assertTrue(frame[0] & 0x80)

    def test_medium_payload_126_encoding(self):
        payload = b"x" * 200
        frame = _encode_frame(OP_TEXT, payload, mask=False)
        self.assertEqual(frame[1], 126)
        import struct
        length = struct.unpack("!H", frame[2:4])[0]
        self.assertEqual(length, 200)

    def test_masked_frame_has_mask_bit(self):
        frame = _encode_frame(OP_TEXT, b"hello", mask=True)
        self.assertTrue(frame[1] & 0x80)

    def test_masked_frame_longer_than_unmasked(self):
        unmasked = _encode_frame(OP_TEXT, b"hello", mask=False)
        masked = _encode_frame(OP_TEXT, b"hello", mask=True)
        self.assertEqual(len(masked), len(unmasked) + 4)

    def test_empty_payload(self):
        frame = _encode_frame(OP_PING, b"", mask=False)
        self.assertEqual(frame[1] & 0x7F, 0)

    def test_close_frame_opcode(self):
        frame = _encode_frame(OP_CLOSE, b"", mask=False)
        self.assertEqual(frame[0] & 0x0F, OP_CLOSE)


class TestWebSocketClient(unittest.TestCase):
    def test_repr_not_connected(self):
        ws = WebSocketClient("ws://example.com/ws")
        r = repr(ws)
        self.assertIn("example.com", r)
        self.assertIn("False", r)

    def test_is_connected_false_initially(self):
        ws = WebSocketClient("ws://example.com/ws")
        self.assertFalse(ws.is_connected)

    def test_callbacks_stored(self):
        def on_msg(m): pass
        def on_cls(c, r): pass
        def on_err(e): pass
        def on_png(d): pass
        ws = WebSocketClient(
            "ws://example.com/ws",
            on_message=on_msg,
            on_close=on_cls,
            on_error=on_err,
            on_ping=on_png,
        )
        self.assertIs(ws.on_message, on_msg)
        self.assertIs(ws.on_close, on_cls)
        self.assertIs(ws.on_error, on_err)
        self.assertIs(ws.on_ping, on_png)

    def test_extra_headers_stored(self):
        ws = WebSocketClient("ws://example.com/ws", extra_headers={"X-Auth": "token"})
        self.assertEqual(ws._extra_headers["X-Auth"], "token")

    def test_extra_headers_default_empty(self):
        ws = WebSocketClient("ws://example.com/ws")
        self.assertEqual(ws._extra_headers, {})

    def test_send_raises_when_not_connected(self):
        ws = WebSocketClient("ws://example.com/ws")
        with self.assertRaises(WebSocketClosed):
            ws.send("hello")

    def test_send_binary_raises_when_not_connected(self):
        ws = WebSocketClient("ws://example.com/ws")
        with self.assertRaises(WebSocketClosed):
            ws.send_binary(b"\x01\x02")

    def test_ping_raises_when_not_connected(self):
        ws = WebSocketClient("ws://example.com/ws")
        with self.assertRaises(WebSocketClosed):
            ws.ping()

    def test_pong_raises_when_not_connected(self):
        ws = WebSocketClient("ws://example.com/ws")
        with self.assertRaises(WebSocketClosed):
            ws.pong()

    def test_recv_raises_when_not_connected(self):
        ws = WebSocketClient("ws://example.com/ws")
        with self.assertRaises(WebSocketClosed):
            ws.recv()

    def test_close_idempotent(self):
        ws = WebSocketClient("ws://example.com/ws")
        ws._closed = True
        ws.close()

    def test_close_calls_on_close_callback(self):
        called = []
        ws = WebSocketClient("ws://example.com/ws", on_close=lambda c, r: called.append((c, r)))
        ws._closed = False
        ws.close(1001, "bye")
        self.assertEqual(called, [(1001, "bye")])

    def test_url_stored(self):
        ws = WebSocketClient("wss://secure.example.com/chat")
        self.assertEqual(ws.url, "wss://secure.example.com/chat")

    def test_connect_fails_on_unreachable_host(self):
        ws = WebSocketClient("ws://localhost:19998/ws", timeout=1.0)
        with self.assertRaises(Exception):
            ws.connect()


class TestSignalHandle(unittest.TestCase):
    def setUp(self):
        self._original = _signal.getsignal(_signal.SIGINT)

    def tearDown(self):
        _signal.signal(_signal.SIGINT, self._original)

    def test_handle_installs_handler(self):
        received = []
        handle(_signal.SIGINT, lambda s, f: received.append(s))
        raise_signal(_signal.SIGINT)
        self.assertEqual(received, [_signal.SIGINT])

    def test_handle_returns_old_handler(self):
        original = _signal.getsignal(_signal.SIGINT)
        old = handle(_signal.SIGINT, _signal.SIG_IGN)
        self.assertIs(old, original)

    def test_ignore_installs_sig_ign(self):
        ignore(_signal.SIGINT)
        self.assertIs(current_handler(_signal.SIGINT), _signal.SIG_IGN)

    def test_reset_installs_sig_dfl(self):
        ignore(_signal.SIGINT)
        reset(_signal.SIGINT)
        self.assertIs(current_handler(_signal.SIGINT), _signal.SIG_DFL)

    def test_current_handler_returns_handler(self):
        def fn(s, f): pass
        handle(_signal.SIGINT, fn)
        self.assertIs(current_handler(_signal.SIGINT), fn)

    def test_raise_signal_triggers_handler(self):
        fired = []
        handle(_signal.SIGINT, lambda s, f: fired.append(True))
        raise_signal(_signal.SIGINT)
        self.assertTrue(fired)

    def test_on_sigint_installs_handler(self):
        called = []
        on_sigint(lambda: called.append(1))
        raise_signal(_signal.SIGINT)
        self.assertEqual(called, [1])

    def test_on_sigterm_installs_handler(self):
        original_term = _signal.getsignal(_signal.SIGTERM)
        called = []
        try:
            on_sigterm(lambda: called.append(1))
            raise_signal(_signal.SIGTERM)
            self.assertEqual(called, [1])
        finally:
            _signal.signal(_signal.SIGTERM, original_term)

    def test_register_shutdown_handles_sigint(self):
        original_term = _signal.getsignal(_signal.SIGTERM)
        called = []
        try:
            register_shutdown(lambda: called.append("shutdown"))
            raise_signal(_signal.SIGINT)
            self.assertIn("shutdown", called)
        finally:
            _signal.signal(_signal.SIGTERM, original_term)


class TestAvailableSignals(unittest.TestCase):
    def test_returns_dict(self):
        sigs = available_signals()
        self.assertIsInstance(sigs, dict)

    def test_contains_sigint(self):
        sigs = available_signals()
        self.assertIn("SIGINT", sigs)
        self.assertEqual(sigs["SIGINT"], _signal.SIGINT)

    def test_values_are_ints(self):
        for name, num in available_signals().items():
            self.assertIsInstance(num, int)

    def test_no_sig_underscore_prefix(self):
        for name in available_signals():
            self.assertFalse(name.startswith("SIG_"))


class TestSignalCounter(unittest.TestCase):
    def setUp(self):
        self._original = _signal.getsignal(_signal.SIGINT)

    def tearDown(self):
        _signal.signal(_signal.SIGINT, self._original)

    def test_initial_count_zero(self):
        counter = SignalCounter(_signal.SIGINT)
        self.assertEqual(counter.count, 0)

    def test_count_increments_on_signal(self):
        counter = SignalCounter(_signal.SIGINT)
        raise_signal(_signal.SIGINT)
        raise_signal(_signal.SIGINT)
        self.assertEqual(counter.count, 2)

    def test_reset_count(self):
        counter = SignalCounter(_signal.SIGINT)
        raise_signal(_signal.SIGINT)
        counter.reset_count()
        self.assertEqual(counter.count, 0)

    def test_sig_stored(self):
        counter = SignalCounter(_signal.SIGINT)
        self.assertEqual(counter.sig, _signal.SIGINT)


class TestGracefulShutdown(unittest.TestCase):
    def setUp(self):
        self._orig_int = _signal.getsignal(_signal.SIGINT)
        self._orig_term = _signal.getsignal(_signal.SIGTERM)

    def tearDown(self):
        _signal.signal(_signal.SIGINT, self._orig_int)
        _signal.signal(_signal.SIGTERM, self._orig_term)

    def test_not_shutdown_initially(self):
        gs = GracefulShutdown()
        self.assertFalse(gs.is_shutdown)

    def test_is_shutdown_after_sigint(self):
        gs = GracefulShutdown()
        raise_signal(_signal.SIGINT)
        self.assertTrue(gs.is_shutdown)

    def test_on_shutdown_callback_called(self):
        called = []
        gs = GracefulShutdown()
        gs.on_shutdown(lambda: called.append(True))
        raise_signal(_signal.SIGINT)
        self.assertTrue(called)

    def test_multiple_callbacks(self):
        results = []
        gs = GracefulShutdown()
        gs.on_shutdown(lambda: results.append(1))
        gs.on_shutdown(lambda: results.append(2))
        raise_signal(_signal.SIGINT)
        self.assertEqual(sorted(results), [1, 2])

    def test_wait_returns_true_when_shutdown(self):
        gs = GracefulShutdown()
        raise_signal(_signal.SIGINT)
        result = gs.wait(timeout=0.1)
        self.assertTrue(result)

    def test_wait_returns_false_when_not_shutdown(self):
        gs = GracefulShutdown()
        result = gs.wait(timeout=0.05)
        self.assertFalse(result)


class TestLogger(unittest.TestCase):
    def test_returns_logger(self):
        log = get_logger("test.logger")
        self.assertIsInstance(log, logging.Logger)

    def test_name_matches(self):
        log = get_logger("test.myapp")
        self.assertEqual(log.name, "test.myapp")

    def test_level_set(self):
        log = get_logger("test.level", level=logging.WARNING)
        self.assertEqual(log.level, logging.WARNING)

    def test_no_duplicate_handlers(self):
        get_logger("test.dedup")
        count_first = len(logging.getLogger("test.dedup").handlers)
        get_logger("test.dedup")
        count_second = len(logging.getLogger("test.dedup").handlers)
        self.assertEqual(count_first, count_second)

    def test_has_handler(self):
        log = get_logger("test.handler")
        self.assertGreater(len(log.handlers), 0)

    def test_default_level_is_debug(self):
        log = get_logger("test.default_level")
        self.assertEqual(log.level, logging.DEBUG)

    def test_file_handler_added(self):
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.log")
            log = get_logger("test.filehandler", log_file=path)
            handler_types = [type(h) for h in log.handlers]
            for h in log.handlers:
                h.close()
            log.handlers.clear()
            self.assertIn(logging.FileHandler, handler_types)

    def test_log_file_created(self):
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "subdir", "app.log")
            log = get_logger("test.filecreated", log_file=path)
            log.info("hello")
            exists = os.path.exists(path)
            for h in log.handlers:
                h.close()
            log.handlers.clear()
            self.assertTrue(exists)


class TestHttpUtils(unittest.TestCase):
    def test_is_ok_200(self):
        self.assertTrue(is_ok({"status": 200}))

    def test_is_ok_201(self):
        self.assertTrue(is_ok({"status": 201}))

    def test_is_ok_299(self):
        self.assertTrue(is_ok({"status": 299}))

    def test_is_ok_400(self):
        self.assertFalse(is_ok({"status": 400}))

    def test_is_ok_404(self):
        self.assertFalse(is_ok({"status": 404}))

    def test_is_ok_500(self):
        self.assertFalse(is_ok({"status": 500}))

    def test_is_ok_none_status(self):
        self.assertFalse(is_ok({"status": None}))

    def test_is_ok_missing_status(self):
        self.assertFalse(is_ok({}))


class TestEventEmitter(unittest.TestCase):
    def setUp(self):
        self.emitter = EventEmitter()

    def test_on_and_emit(self):
        received = []
        self.emitter.on("data", lambda x: received.append(x))
        self.emitter.emit("data", 42)
        self.assertEqual(received, [42])

    def test_emit_returns_count(self):
        self.emitter.on("x", lambda: None)
        self.emitter.on("x", lambda: None)
        self.assertEqual(self.emitter.emit("x"), 2)

    def test_once_fires_once(self):
        received = []
        self.emitter.once("ping", lambda: received.append(1))
        self.emitter.emit("ping")
        self.emitter.emit("ping")
        self.assertEqual(received, [1])

    def test_off_removes_listener(self):
        def fn(x): pass
        self.emitter.on("evt", fn)
        removed = self.emitter.off("evt", fn)
        self.assertTrue(removed)
        self.assertEqual(self.emitter.emit("evt", 1), 0)

    def test_off_not_registered(self):
        self.assertFalse(self.emitter.off("missing", lambda: None))

    def test_no_listeners_emit_returns_zero(self):
        self.assertEqual(self.emitter.emit("nothing"), 0)

    def test_listeners_includes_on_and_once(self):
        def f1(): pass
        def f2(): pass
        self.emitter.on("e", f1)
        self.emitter.once("e", f2)
        self.assertIn(f1, self.emitter.listeners("e"))
        self.assertIn(f2, self.emitter.listeners("e"))

    def test_clear_specific_event(self):
        self.emitter.on("a", lambda: None)
        self.emitter.on("b", lambda: None)
        self.emitter.clear("a")
        self.assertEqual(self.emitter.emit("a"), 0)
        self.assertEqual(self.emitter.emit("b"), 1)

    def test_clear_all(self):
        self.emitter.on("a", lambda: None)
        self.emitter.on("b", lambda: None)
        self.emitter.clear()
        self.assertEqual(self.emitter.emit("a"), 0)
        self.assertEqual(self.emitter.emit("b"), 0)

    def test_repr(self):
        self.emitter.on("login", lambda: None)
        self.assertIn("EventEmitter", repr(self.emitter))


class TestQueue(unittest.TestCase):
    def test_enqueue_dequeue(self):
        q = Queue()
        q.enqueue("a")
        self.assertEqual(q.dequeue(), "a")

    def test_fifo_order(self):
        q = Queue()
        for v in [1, 2, 3]:
            q.enqueue(v)
        self.assertEqual([q.dequeue() for _ in range(3)], [1, 2, 3])

    def test_peek(self):
        q = Queue()
        q.enqueue("x")
        self.assertEqual(q.peek(), "x")
        self.assertEqual(q.size(), 1)

    def test_is_empty(self):
        q = Queue()
        self.assertTrue(q.is_empty())
        q.enqueue(1)
        self.assertFalse(q.is_empty())

    def test_maxsize_rejects(self):
        q = Queue(maxsize=2)
        q.enqueue(1)
        q.enqueue(2)
        self.assertFalse(q.enqueue(3))
        self.assertTrue(q.is_full())

    def test_clear(self):
        q = Queue()
        q.enqueue(1)
        q.clear()
        self.assertTrue(q.is_empty())

    def test_dequeue_empty_raises(self):
        with self.assertRaises(IndexError):
            Queue().dequeue()

    def test_peek_empty_raises(self):
        with self.assertRaises(IndexError):
            Queue().peek()

    def test_repr(self):
        q = Queue(maxsize=5)
        self.assertIn("Queue", repr(q))


class TestPriorityQueue(unittest.TestCase):
    def test_push_pop_order(self):
        pq = PriorityQueue()
        pq.push("low", priority=10)
        pq.push("high", priority=1)
        pq.push("mid", priority=5)
        self.assertEqual(pq.pop(), "high")
        self.assertEqual(pq.pop(), "mid")
        self.assertEqual(pq.pop(), "low")

    def test_peek(self):
        pq = PriorityQueue()
        pq.push("only", priority=3)
        self.assertEqual(pq.peek(), "only")
        self.assertEqual(pq.size(), 1)

    def test_is_empty(self):
        pq = PriorityQueue()
        self.assertTrue(pq.is_empty())
        pq.push("x")
        self.assertFalse(pq.is_empty())

    def test_pop_empty_raises(self):
        with self.assertRaises(IndexError):
            PriorityQueue().pop()

    def test_repr(self):
        pq = PriorityQueue()
        pq.push("a")
        self.assertIn("PriorityQueue", repr(pq))


class TestDecoratorUtils(unittest.TestCase):
    def test_memoize_caches(self):
        calls = []
        @deco_memoize
        def fn(x):
            calls.append(x)
            return x * 2
        fn(5)
        fn(5)
        self.assertEqual(len(calls), 1)

    def test_memoize_different_args(self):
        @deco_memoize
        def fn(x):
            return x + 1
        self.assertEqual(fn(1), 2)
        self.assertEqual(fn(2), 3)

    def test_retry_succeeds(self):
        @deco_retry(attempts=3)
        def ok():
            return "done"
        self.assertEqual(ok(), "done")

    def test_retry_exhausted_raises(self):
        @deco_retry(attempts=2, exceptions=(ValueError,))
        def always_fail():
            raise ValueError("oops")
        with self.assertRaises(ValueError):
            always_fail()

    def test_retry_succeeds_after_failure(self):
        state = {"count": 0}
        @deco_retry(attempts=3, exceptions=(RuntimeError,))
        def flaky():
            state["count"] += 1
            if state["count"] < 3:
                raise RuntimeError("not yet")
            return "ok"
        self.assertEqual(flaky(), "ok")

    def test_singleton_same_instance(self):
        @singleton
        class MyService:
            pass
        self.assertIs(MyService(), MyService())

    def test_deprecated_raises_warning(self):
        import warnings
        @deprecated("Use new_func instead.")
        def old():
            return 1
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old()
        self.assertEqual(result, 1)
        self.assertTrue(any(issubclass(x.category, DeprecationWarning) for x in w))

    def test_clamp_result(self):
        @clamp_result(0, 100)
        def score(x):
            return x * 10
        self.assertEqual(score(15), 100)
        self.assertEqual(score(-5), 0)
        self.assertEqual(score(5), 50)


class TestObservable(unittest.TestCase):
    def test_subscribe_and_notify(self):
        obs = Observable()
        received = []
        obs.subscribe(lambda x: received.append(x))
        obs.notify("event")
        self.assertEqual(received, ["event"])

    def test_subscribe_no_duplicates(self):
        obs = Observable()
        def fn(): pass
        obs.subscribe(fn)
        obs.subscribe(fn)
        self.assertEqual(obs.observer_count(), 1)

    def test_unsubscribe(self):
        obs = Observable()
        def fn(x): pass
        obs.subscribe(fn)
        removed = obs.unsubscribe(fn)
        self.assertTrue(removed)
        self.assertEqual(obs.observer_count(), 0)

    def test_unsubscribe_not_subscribed(self):
        self.assertFalse(Observable().unsubscribe(lambda: None))

    def test_repr(self):
        obs = Observable()
        self.assertIn("Observable", repr(obs))


class TestObservableValue(unittest.TestCase):
    def test_initial_value(self):
        ov = ObservableValue(42)
        self.assertEqual(ov.value, 42)

    def test_setter_notifies(self):
        changes = []
        ov = ObservableValue(0)
        ov.subscribe(lambda new, old: changes.append((new, old)))
        ov.value = 5
        self.assertEqual(changes, [(5, 0)])

    def test_no_notify_when_same(self):
        changes = []
        ov = ObservableValue(10)
        ov.subscribe(lambda n, o: changes.append(1))
        ov.value = 10
        self.assertEqual(changes, [])

    def test_unsubscribe(self):
        def fn(n, o): pass
        ov = ObservableValue(0)
        ov.subscribe(fn)
        self.assertTrue(ov.unsubscribe(fn))

    def test_repr(self):
        ov = ObservableValue("hello")
        self.assertIn("hello", repr(ov))


class TestStore(unittest.TestCase):
    def setUp(self):
        self.store = Store({"x": 1, "y": 2})

    def test_get(self):
        self.assertEqual(self.store.get("x"), 1)

    def test_get_default(self):
        self.assertIsNone(self.store.get("missing"))
        self.assertEqual(self.store.get("missing", 99), 99)

    def test_set_updates_state(self):
        self.store.set("x", 10)
        self.assertEqual(self.store.get("x"), 10)

    def test_update(self):
        self.store.update({"x": 5, "z": 3})
        self.assertEqual(self.store.get("x"), 5)
        self.assertEqual(self.store.get("z"), 3)

    def test_reset_restores_initial(self):
        self.store.set("x", 99)
        self.store.reset()
        self.assertEqual(self.store.get("x"), 1)

    def test_undo(self):
        self.store.set("x", 42)
        self.store.undo()
        self.assertEqual(self.store.get("x"), 1)

    def test_undo_at_initial_returns_false(self):
        self.assertFalse(self.store.undo())

    def test_subscribe_notified_on_set(self):
        events = []
        self.store.subscribe(lambda s: events.append(s))
        self.store.set("x", 7)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["x"], 7)

    def test_state_property(self):
        s = self.store.state
        self.assertIsInstance(s, dict)
        self.assertEqual(s["x"], 1)

    def test_repr(self):
        self.assertIn("Store", repr(self.store))


class TestStateMachine(unittest.TestCase):
    def setUp(self):
        self.sm = StateMachine(
            "idle",
            {"idle": ["running"], "running": ["stopped"], "stopped": []}
        )

    def test_initial_state(self):
        self.assertEqual(self.sm.current, "idle")

    def test_valid_transition(self):
        self.assertTrue(self.sm.transition("running"))
        self.assertEqual(self.sm.current, "running")

    def test_invalid_transition(self):
        self.assertFalse(self.sm.transition("stopped"))
        self.assertEqual(self.sm.current, "idle")

    def test_can(self):
        self.assertTrue(self.sm.can("running"))
        self.assertFalse(self.sm.can("stopped"))

    def test_on_enter_callback(self):
        entered = []
        self.sm.on_enter("running", lambda s: entered.append(s))
        self.sm.transition("running")
        self.assertEqual(entered, ["running"])

    def test_on_exit_callback(self):
        exited = []
        self.sm.on_exit("idle", lambda s: exited.append(s))
        self.sm.transition("running")
        self.assertEqual(exited, ["idle"])

    def test_repr(self):
        self.assertIn("idle", repr(self.sm))


class TestColorUtils(unittest.TestCase):
    def test_hex_to_rgb(self):
        self.assertEqual(hex_to_rgb("#ffffff"), (255, 255, 255))
        self.assertEqual(hex_to_rgb("#000000"), (0, 0, 0))

    def test_hex_to_rgb_shorthand(self):
        self.assertEqual(hex_to_rgb("#fff"), (255, 255, 255))

    def test_rgb_to_hex(self):
        self.assertEqual(rgb_to_hex(255, 255, 255), "#ffffff")
        self.assertEqual(rgb_to_hex(0, 0, 0), "#000000")

    def test_round_trip_hex_rgb(self):
        original = "#3498db"
        r, g, b = hex_to_rgb(original)
        self.assertEqual(rgb_to_hex(r, g, b), original)

    def test_rgb_to_hsl_white(self):
        h, s, lightness = rgb_to_hsl(255, 255, 255)
        self.assertAlmostEqual(lightness, 100, places=0)

    def test_hsl_to_rgb_round_trip(self):
        h, s, lightness = rgb_to_hsl(100, 150, 200)
        r, g, b = hsl_to_rgb(h, s, lightness)
        self.assertAlmostEqual(r, 100, delta=2)
        self.assertAlmostEqual(g, 150, delta=2)
        self.assertAlmostEqual(b, 200, delta=2)

    def test_luminance_black(self):
        self.assertAlmostEqual(luminance(0, 0, 0), 0.0)

    def test_luminance_white(self):
        self.assertAlmostEqual(luminance(255, 255, 255), 1.0, places=3)

    def test_is_light_white(self):
        self.assertTrue(is_light("#ffffff"))

    def test_is_light_black(self):
        self.assertFalse(is_light("#000000"))

    def test_contrast_color_light(self):
        self.assertEqual(contrast_color("#ffffff"), "#000000")

    def test_contrast_color_dark(self):
        self.assertEqual(contrast_color("#000000"), "#ffffff")

    def test_lighten_increases_lightness(self):
        result = lighten("#808080", 20)
        _, _, l_orig = rgb_to_hsl(*hex_to_rgb("#808080"))
        _, _, l_new = rgb_to_hsl(*hex_to_rgb(result))
        self.assertGreater(l_new, l_orig)

    def test_darken_decreases_lightness(self):
        result = darken("#808080", 20)
        _, _, l_orig = rgb_to_hsl(*hex_to_rgb("#808080"))
        _, _, l_new = rgb_to_hsl(*hex_to_rgb(result))
        self.assertLess(l_new, l_orig)

    def test_mix_equal_ratio(self):
        result = mix("#000000", "#ffffff", 0.5)
        r, g, b = hex_to_rgb(result)
        self.assertAlmostEqual(r, 128, delta=1)

    def test_complementary_returns_hex(self):
        result = complementary("#ff0000")
        self.assertTrue(result.startswith("#"))
        self.assertEqual(len(result), 7)

    def test_random_color_format(self):
        c = random_color()
        self.assertTrue(c.startswith("#"))
        self.assertEqual(len(c), 7)

    def test_analogous_returns_two(self):
        a, b = analogous("#ff0000")
        self.assertTrue(a.startswith("#"))
        self.assertTrue(b.startswith("#"))

    def test_triadic_returns_two(self):
        a, b = triadic("#ff0000")
        self.assertTrue(a.startswith("#"))
        self.assertTrue(b.startswith("#"))


class TestMatrixUtils(unittest.TestCase):
    def test_zeros(self):
        m = zeros(2, 3)
        self.assertEqual(m, [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])

    def test_ones(self):
        self.assertEqual(ones(2, 2), [[1.0, 1.0], [1.0, 1.0]])

    def test_identity(self):
        m = mat_identity(3)
        self.assertEqual(m[0][0], 1.0)
        self.assertEqual(m[0][1], 0.0)
        self.assertEqual(m[1][1], 1.0)

    def test_shape(self):
        self.assertEqual(shape([[1, 2, 3], [4, 5, 6]]), (2, 3))

    def test_is_square_true(self):
        self.assertTrue(is_square([[1, 2], [3, 4]]))

    def test_is_square_false(self):
        self.assertFalse(is_square([[1, 2, 3], [4, 5, 6]]))

    def test_transpose(self):
        self.assertEqual(transpose([[1, 2], [3, 4]]), [[1, 3], [2, 4]])

    def test_add(self):
        self.assertEqual(mat_add([[1, 2], [3, 4]], [[5, 6], [7, 8]]),
                         [[6, 8], [10, 12]])

    def test_subtract(self):
        self.assertEqual(mat_sub([[5, 6], [7, 8]], [[1, 2], [3, 4]]),
                         [[4, 4], [4, 4]])

    def test_scalar_multiply(self):
        self.assertEqual(scalar_multiply([[1, 2], [3, 4]], 2),
                         [[2, 4], [6, 8]])

    def test_multiply(self):
        a = [[1, 2], [3, 4]]
        b = [[5, 6], [7, 8]]
        result = mat_mul(a, b)
        self.assertEqual(result[0][0], 19)
        self.assertEqual(result[1][1], 50)

    def test_multiply_incompatible_raises(self):
        with self.assertRaises(ValueError):
            mat_mul([[1, 2, 3]], [[1, 2], [3, 4]])

    def test_trace(self):
        self.assertEqual(trace([[1, 2], [3, 4]]), 5)

    def test_trace_non_square_raises(self):
        with self.assertRaises(ValueError):
            trace([[1, 2, 3], [4, 5, 6]])

    def test_determinant_2x2(self):
        self.assertAlmostEqual(determinant([[1, 2], [3, 4]]), -2.0)

    def test_determinant_1x1(self):
        self.assertEqual(determinant([[7]]), 7)

    def test_flatten(self):
        self.assertEqual(mat_flatten([[1, 2], [3, 4]]), [1, 2, 3, 4])

    def test_reshape(self):
        self.assertEqual(reshape([1, 2, 3, 4], 2, 2), [[1, 2], [3, 4]])

    def test_reshape_wrong_size_raises(self):
        with self.assertRaises(ValueError):
            reshape([1, 2, 3], 2, 2)

    def test_get_row(self):
        self.assertEqual(get_row([[1, 2], [3, 4]], 1), [3, 4])

    def test_get_col(self):
        self.assertEqual(get_col([[1, 2], [3, 4]], 0), [1, 3])

    def test_map_matrix(self):
        self.assertEqual(map_matrix(lambda x: x * 2, [[1, 2], [3, 4]]),
                         [[2, 4], [6, 8]])


class TestTreeUtils(unittest.TestCase):
    def setUp(self):
        self.root = tree_from_list([5, 3, 7, 1, 4, 6, 8])

    def test_inorder_sorted(self):
        self.assertEqual(inorder(self.root), [1, 3, 4, 5, 6, 7, 8])

    def test_preorder_root_first(self):
        result = preorder(self.root)
        self.assertEqual(result[0], 5)

    def test_postorder_root_last(self):
        result = postorder(self.root)
        self.assertEqual(result[-1], 5)

    def test_level_order(self):
        levels = level_order(self.root)
        self.assertEqual(levels[0], [5])

    def test_height(self):
        self.assertGreaterEqual(height(self.root), 3)

    def test_size(self):
        self.assertEqual(tree_size(self.root), 7)

    def test_search_found(self):
        node = tree_search(self.root, 4)
        self.assertIsNotNone(node)
        self.assertEqual(node.value, 4)

    def test_search_not_found(self):
        self.assertIsNone(tree_search(self.root, 99))

    def test_delete_leaf(self):
        root = tree_delete(self.root, 1)
        self.assertIsNone(tree_search(root, 1))

    def test_min_node(self):
        self.assertEqual(min_node(self.root).value, 1)

    def test_max_node(self):
        self.assertEqual(max_node(self.root).value, 8)

    def test_is_bst(self):
        self.assertTrue(is_bst(self.root))

    def test_is_balanced(self):
        self.assertTrue(tree_balanced(self.root))

    def test_to_list_sorted(self):
        self.assertEqual(tree_to_list(self.root), sorted([5, 3, 7, 1, 4, 6, 8]))

    def test_tree_node_repr(self):
        n = TreeNode(42)
        self.assertIn("42", repr(n))

    def test_empty_tree(self):
        self.assertEqual(inorder(None), [])
        self.assertEqual(height(None), 0)
        self.assertEqual(tree_size(None), 0)


class TestLinkedList(unittest.TestCase):
    def test_append_and_to_list(self):
        ll = ll_from_list([1, 2, 3])
        self.assertEqual(ll.to_list(), [1, 2, 3])

    def test_prepend(self):
        ll = ll_from_list([2, 3])
        ll.prepend(1)
        self.assertEqual(ll.to_list(), [1, 2, 3])

    def test_len(self):
        ll = ll_from_list([1, 2, 3])
        self.assertEqual(len(ll), 3)

    def test_pop(self):
        ll = ll_from_list([1, 2, 3])
        self.assertEqual(ll.pop(), 3)
        self.assertEqual(len(ll), 2)

    def test_popleft(self):
        ll = ll_from_list([1, 2, 3])
        self.assertEqual(ll.popleft(), 1)

    def test_find(self):
        ll = ll_from_list([1, 2, 3])
        self.assertEqual(ll.find(2).value, 2)
        self.assertIsNone(ll.find(99))

    def test_remove(self):
        ll = ll_from_list([1, 2, 3])
        self.assertTrue(ll.remove(2))
        self.assertEqual(ll.to_list(), [1, 3])

    def test_remove_not_found(self):
        ll = ll_from_list([1, 2])
        self.assertFalse(ll.remove(99))

    def test_reverse(self):
        ll = ll_from_list([1, 2, 3])
        ll.reverse()
        self.assertEqual(ll.to_list(), [3, 2, 1])

    def test_iter(self):
        ll = ll_from_list([10, 20, 30])
        self.assertEqual(list(ll), [10, 20, 30])

    def test_has_cycle_false(self):
        ll = ll_from_list([1, 2, 3])
        self.assertFalse(ll_has_cycle(ll))

    def test_middle(self):
        ll = ll_from_list([1, 2, 3, 4, 5])
        self.assertEqual(middle(ll), 3)

    def test_merge_sorted(self):
        a = ll_from_list([1, 3, 5])
        b = ll_from_list([2, 4, 6])
        merged = merge_sorted(a, b)
        self.assertEqual(merged.to_list(), [1, 2, 3, 4, 5, 6])

    def test_remove_duplicates(self):
        ll = ll_from_list([1, 2, 2, 3, 3])
        remove_duplicates(ll)
        self.assertEqual(ll.to_list(), [1, 2, 3])

    def test_pop_empty_raises(self):
        with self.assertRaises(IndexError):
            LinkedList().pop()


class TestStack(unittest.TestCase):
    def test_push_pop(self):
        s = Stack()
        s.push(1)
        s.push(2)
        self.assertEqual(s.pop(), 2)

    def test_peek(self):
        s = Stack()
        s.push(42)
        self.assertEqual(s.peek(), 42)
        self.assertEqual(len(s), 1)

    def test_is_empty(self):
        s = Stack()
        self.assertTrue(s.is_empty())
        s.push(1)
        self.assertFalse(s.is_empty())

    def test_clear(self):
        s = Stack()
        s.push(1)
        s.clear()
        self.assertTrue(s.is_empty())

    def test_to_list_top_first(self):
        s = Stack()
        for v in [1, 2, 3]:
            s.push(v)
        self.assertEqual(s.to_list(), [3, 2, 1])

    def test_pop_empty_raises(self):
        with self.assertRaises(IndexError):
            Stack().pop()

    def test_is_balanced_valid(self):
        self.assertTrue(stack_balanced("({[]})"))
        self.assertTrue(stack_balanced(""))

    def test_is_balanced_invalid(self):
        self.assertFalse(stack_balanced("({[}])"))
        self.assertFalse(stack_balanced("((())"))

    def test_evaluate_rpn(self):
        self.assertAlmostEqual(evaluate_rpn(["3", "4", "+", "2", "*"]), 14.0)

    def test_infix_to_rpn(self):
        tokens = infix_to_rpn("3 + 4 * 2")
        result = evaluate_rpn(tokens)
        self.assertAlmostEqual(result, 11.0)

    def test_sort_stack(self):
        s = Stack()
        for v in [3, 1, 4, 2]:
            s.push(v)
        sorted_s = sort_stack(s)
        items = sorted_s.to_list()
        self.assertEqual(sorted(items), [1, 2, 3, 4])

    def test_reverse_stack(self):
        s = Stack()
        for v in [1, 2, 3]:
            s.push(v)
        rev = reverse_stack(s)
        self.assertEqual(rev.to_list(), [1, 2, 3])


class TestFunctionalUtils(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(fn_id(42), 42)
        self.assertEqual(fn_id("hello"), "hello")

    def test_always(self):
        fn = always(99)
        self.assertEqual(fn(), 99)
        self.assertEqual(fn(1, 2, 3), 99)

    def test_pipe(self):
        process = fn_pipe(lambda x: x + 1, lambda x: x * 2)
        self.assertEqual(process(3), 8)

    def test_compose(self):
        process = fn_compose(lambda x: x * 2, lambda x: x + 1)
        self.assertEqual(process(3), 8)

    def test_curry(self):
        add = curry(lambda a, b, c: a + b + c)
        self.assertEqual(add(1)(2)(3), 6)
        self.assertEqual(add(1, 2)(3), 6)

    def test_flip(self):
        sub = flip(lambda a, b: a - b)
        self.assertEqual(sub(3, 10), 7)

    def test_tap_returns_value(self):
        side = []
        log = tap(lambda x: side.append(x))
        self.assertEqual(log(42), 42)
        self.assertEqual(side, [42])

    def test_complement(self):
        def is_even(x): return x % 2 == 0
        is_odd = complement(is_even)
        self.assertTrue(is_odd(3))
        self.assertFalse(is_odd(4))

    def test_juxt(self):
        stats = juxt(min, max, sum)
        self.assertEqual(stats([1, 2, 3]), [1, 3, 6])

    def test_memoize(self):
        calls = []
        @fn_memoize
        def fn(x):
            calls.append(x)
            return x * 2
        fn(5)
        fn(5)
        self.assertEqual(len(calls), 1)

    def test_reduce(self):
        self.assertEqual(fn_reduce(lambda a, b: a + b, [1, 2, 3, 4]), 10)

    def test_scan(self):
        self.assertEqual(scan(lambda a, b: a + b, [1, 2, 3], 0), [0, 1, 3, 6])

    def test_take(self):
        self.assertEqual(take(3, range(10)), [0, 1, 2])

    def test_drop(self):
        self.assertEqual(drop(3, range(6)), [3, 4, 5])

    def test_partition(self):
        evens, odds = partition(lambda x: x % 2 == 0, range(6))
        self.assertEqual(evens, [0, 2, 4])
        self.assertEqual(odds, [1, 3, 5])

    def test_group_by(self):
        result = group_by(lambda x: x % 2, [1, 2, 3, 4])
        self.assertEqual(result[0], [2, 4])
        self.assertEqual(result[1], [1, 3])

    def test_zip_with(self):
        self.assertEqual(zip_with(lambda a, b: a + b, [1, 2], [3, 4]), [4, 6])

    def test_unique(self):
        self.assertEqual(unique([1, 2, 2, 3, 1]), [1, 2, 3])

    def test_unique_with_key(self):
        result = unique(["foo", "FOO", "bar"], key=str.lower)
        self.assertEqual(len(result), 2)

    def test_flatten_iter(self):
        self.assertEqual(flatten_iter([[1, [2, 3]], [4]], depth=1), [1, [2, 3], 4])
        self.assertEqual(flatten_iter([[1, [2, 3]], [4]], depth=2), [1, 2, 3, 4])


class TestRegexUtils(unittest.TestCase):
    def test_is_match_slug(self):
        from util.regex_utils import SLUG_PATTERN
        self.assertTrue(is_match(SLUG_PATTERN, "hello-world"))
        self.assertFalse(is_match(SLUG_PATTERN, "Hello World"))

    def test_find_all_emails(self):
        text = "contact hello@example.com and support@test.org"
        results = find_all(EMAIL_PATTERN, text)
        self.assertIn("hello@example.com", results)
        self.assertIn("support@test.org", results)

    def test_find_all_dates(self):
        text = "dates: 2024-01-15 and 2025-12-31"
        results = find_all(DATE_PATTERN, text)
        self.assertIn("2024-01-15", results)

    def test_find_all_hex_colors(self):
        text = "colors: #fff and #3498db"
        results = find_all(HEX_COLOR_PATTERN, text)
        self.assertGreaterEqual(len(results), 2)

    def test_extract(self):
        result = extract(r"(\d+)", "abc 123 def")
        self.assertEqual(result, "123")

    def test_replace(self):
        self.assertEqual(re_replace(r"\d+", "NUM", "foo 123 bar 456"), "foo NUM bar NUM")

    def test_split(self):
        result = re_split(r"\s*,\s*", "a, b,c")
        self.assertEqual(result, ["a", "b", "c"])

    def test_named_groups(self):
        pattern = r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
        result = named_groups(pattern, "2025-05-11")
        self.assertEqual(result["year"], "2025")
        self.assertEqual(result["month"], "05")

    def test_named_groups_no_match(self):
        self.assertIsNone(named_groups(r"(?P<x>\d+)", "abc"))

    def test_strip_html(self):
        self.assertEqual(strip_html("<h1>Hello <b>World</b></h1>"), "Hello World")

    def test_normalize_whitespace(self):
        self.assertEqual(normalize_whitespace("  too   many  spaces  "), "too many spaces")

    def test_escape(self):
        result = escape("1+1=2?")
        self.assertNotIn("+", result.replace("\\+", ""))


class TestStatisticsUtils(unittest.TestCase):
    DATA = [2, 4, 4, 4, 5, 5, 7, 9]

    def test_mean(self):
        self.assertAlmostEqual(stat_mean(self.DATA), 5.0)

    def test_median(self):
        self.assertAlmostEqual(stat_median(self.DATA), 4.5)

    def test_mode(self):
        self.assertEqual(mode(self.DATA), 4)

    def test_variance(self):
        self.assertGreater(stat_var(self.DATA), 0)

    def test_stdev(self):
        self.assertGreater(stdev(self.DATA), 0)

    def test_harmonic_mean(self):
        self.assertGreater(harmonic_mean([1, 2, 4]), 0)

    def test_geometric_mean(self):
        self.assertAlmostEqual(geometric_mean([1, 2, 4]), 2.0, places=4)

    def test_weighted_mean(self):
        result = weighted_mean([1, 2, 3], [1, 1, 1])
        self.assertAlmostEqual(result, 2.0)

    def test_quantile(self):
        q = quantile(sorted(self.DATA), 0.5)
        self.assertAlmostEqual(q, 4.5)

    def test_quartiles(self):
        q1, q2, q3 = quartiles(self.DATA)
        self.assertLess(q1, q2)
        self.assertLess(q2, q3)

    def test_iqr(self):
        self.assertGreater(iqr(self.DATA), 0)

    def test_z_score(self):
        z = z_score(5.0, self.DATA)
        self.assertIsInstance(z, float)

    def test_normalize(self):
        result = stat_normalize([0, 5, 10])
        self.assertAlmostEqual(result[0], 0.0)
        self.assertAlmostEqual(result[-1], 1.0)

    def test_covariance(self):
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        self.assertGreater(covariance(x, y), 0)

    def test_correlation_perfect(self):
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        self.assertAlmostEqual(correlation(x, y), 1.0, places=5)

    def test_moving_average(self):
        result = moving_average([1, 2, 3, 4, 5], 3)
        self.assertEqual(len(result), 3)
        self.assertAlmostEqual(result[0], 2.0)

    def test_outliers(self):
        data = [2, 2, 2, 2, 2, 2, 2, 2, 2, 100]
        result = outliers(data, threshold=1.5)
        self.assertIn(100, result)

    def test_frequency(self):
        result = frequency([1, 2, 2, 3])
        self.assertEqual(result[2]["count"], 2)

    def test_describe_keys(self):
        result = describe(self.DATA)
        for key in ("count", "mean", "median", "stdev", "min", "max"):
            self.assertIn(key, result)


class TestRateLimitUtils(unittest.TestCase):
    def test_rate_limit_exceeded_attributes(self):
        e = RateLimitExceeded(1.5)
        self.assertAlmostEqual(e.retry_after, 1.5)

    def test_fixed_window_allows_within_limit(self):
        fw = FixedWindow(limit=3, window=10.0)
        self.assertTrue(fw.allow())
        self.assertTrue(fw.allow())
        self.assertTrue(fw.allow())

    def test_fixed_window_rejects_over_limit(self):
        fw = FixedWindow(limit=2, window=10.0)
        fw.allow()
        fw.allow()
        self.assertFalse(fw.allow())

    def test_fixed_window_remaining(self):
        fw = FixedWindow(limit=3, window=10.0)
        fw.allow()
        self.assertEqual(fw.remaining(), 2)

    def test_fixed_window_acquire_raises(self):
        fw = FixedWindow(limit=1, window=10.0)
        fw.acquire()
        with self.assertRaises(RateLimitExceeded):
            fw.acquire()

    def test_fixed_window_repr(self):
        self.assertIn("FixedWindow", repr(FixedWindow(5, 1.0)))

    def test_sliding_window_allows(self):
        sw = SlidingWindow(limit=3, window=10.0)
        self.assertTrue(sw.allow())

    def test_sliding_window_rejects_over_limit(self):
        sw = SlidingWindow(limit=2, window=10.0)
        sw.allow()
        sw.allow()
        self.assertFalse(sw.allow())

    def test_sliding_window_repr(self):
        self.assertIn("SlidingWindow", repr(SlidingWindow(5, 1.0)))

    def test_token_bucket_allows_within_capacity(self):
        tb = TokenBucket(capacity=5, rate=1.0)
        for _ in range(5):
            self.assertTrue(tb.allow())

    def test_token_bucket_rejects_when_empty(self):
        tb = TokenBucket(capacity=2, rate=0.1)
        tb.allow()
        tb.allow()
        self.assertFalse(tb.allow())

    def test_token_bucket_tokens_property(self):
        tb = TokenBucket(capacity=10, rate=1.0)
        self.assertAlmostEqual(tb.tokens, 10.0, places=1)

    def test_token_bucket_repr(self):
        self.assertIn("TokenBucket", repr(TokenBucket(5, 1.0)))

    def test_leaky_bucket_allows(self):
        lb = LeakyBucket(capacity=3, rate=1.0)
        self.assertTrue(lb.allow())

    def test_leaky_bucket_rejects_when_full(self):
        lb = LeakyBucket(capacity=2, rate=0.01)
        lb.allow()
        lb.allow()
        self.assertFalse(lb.allow())

    def test_leaky_bucket_repr(self):
        self.assertIn("LeakyBucket", repr(LeakyBucket(3, 1.0)))

    def test_try_acquire_token_bucket(self):
        tb = TokenBucket(capacity=1, rate=0.01)
        self.assertTrue(try_acquire(tb))
        self.assertFalse(try_acquire(tb))


class TestCircuitBreaker(unittest.TestCase):
    def _make(self, **kw):
        return CircuitBreaker(name="test", failure_threshold=3,
                              recovery_timeout=60.0, **kw)

    def test_initial_state_closed(self):
        cb = self._make()
        self.assertTrue(cb.is_closed)
        self.assertEqual(cb.state, State.CLOSED)

    def test_successful_call(self):
        cb = self._make()
        result = cb.call(lambda: "ok")
        self.assertEqual(result, "ok")

    def test_opens_after_failure_threshold(self):
        cb = self._make()
        for _ in range(3):
            try:
                cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
            except RuntimeError:
                pass
        self.assertTrue(cb.is_open)

    def test_open_rejects_calls(self):
        cb = self._make()
        cb.trip()
        with self.assertRaises(CircuitBreakerOpen):
            cb.call(lambda: "ok")

    def test_trip_opens_immediately(self):
        cb = self._make()
        cb.trip()
        self.assertTrue(cb.is_open)

    def test_reset_closes(self):
        cb = self._make()
        cb.trip()
        cb.reset()
        self.assertTrue(cb.is_closed)

    def test_stats_keys(self):
        cb = self._make()
        stats = cb.stats
        for key in ("name", "state", "total_calls", "total_failures"):
            self.assertIn(key, stats)

    def test_circuit_breaker_open_attributes(self):
        e = CircuitBreakerOpen("svc", 5.0)
        self.assertEqual(e.name, "svc")
        self.assertAlmostEqual(e.retry_after, 5.0)

    def test_repr(self):
        cb = self._make()
        self.assertIn("test", repr(cb))

    def test_as_decorator(self):
        cb = self._make()
        @cb
        def fn():
            return "data"
        self.assertEqual(fn(), "data")

    def test_on_open_callback(self):
        events = []
        cb = CircuitBreaker("cb2", failure_threshold=2, recovery_timeout=60.0,
                            on_open=lambda c: events.append("opened"))
        for _ in range(2):
            try:
                cb.call(lambda: (_ for _ in ()).throw(RuntimeError()))
            except RuntimeError:
                pass
        self.assertIn("opened", events)


class TestCircuitBreakerRegistry(unittest.TestCase):
    def test_get_or_create(self):
        registry = CircuitBreakerRegistry()
        cb = registry.get_or_create("svc1")
        self.assertIsInstance(cb, CircuitBreaker)

    def test_same_name_returns_same(self):
        registry = CircuitBreakerRegistry()
        cb1 = registry.get_or_create("svc")
        cb2 = registry.get_or_create("svc")
        self.assertIs(cb1, cb2)

    def test_get_existing(self):
        registry = CircuitBreakerRegistry()
        registry.get_or_create("svc")
        self.assertIsNotNone(registry.get("svc"))

    def test_get_missing(self):
        registry = CircuitBreakerRegistry()
        self.assertIsNone(registry.get("missing"))

    def test_names(self):
        registry = CircuitBreakerRegistry()
        registry.get_or_create("a")
        registry.get_or_create("b")
        self.assertIn("a", registry.names())
        self.assertIn("b", registry.names())

    def test_reset_all(self):
        registry = CircuitBreakerRegistry()
        cb = registry.get_or_create("svc")
        cb.trip()
        registry.reset_all()
        self.assertTrue(cb.is_closed)


class TestEvent(unittest.TestCase):
    def test_attributes(self):
        e = Event("user.login", {"user": "alice"}, source="web")
        self.assertEqual(e.name, "user.login")
        self.assertEqual(e.data, {"user": "alice"})
        self.assertEqual(e.source, "web")

    def test_not_stopped_initially(self):
        self.assertFalse(Event("x").is_stopped)

    def test_stop_propagation(self):
        e = Event("x")
        e.stop_propagation()
        self.assertTrue(e.is_stopped)

    def test_repr(self):
        e = Event("ping", 42)
        self.assertIn("ping", repr(e))


class TestEventBus(unittest.TestCase):
    def setUp(self):
        self.bus = EventBus()

    def test_subscribe_and_publish(self):
        received = []
        self.bus.subscribe("evt", lambda e: received.append(e.data))
        self.bus.publish("evt", 42)
        self.assertEqual(received, [42])

    def test_once_fires_once(self):
        received = []
        self.bus.once("ping", lambda e: received.append(1))
        self.bus.publish("ping")
        self.bus.publish("ping")
        self.assertEqual(received, [1])

    def test_unsubscribe(self):
        def fn(e): pass
        self.bus.subscribe("x", fn)
        removed = self.bus.unsubscribe("x", fn)
        self.assertTrue(removed)
        self.assertEqual(self.bus.listener_count("x"), 0)

    def test_priority_order(self):
        order = []
        self.bus.subscribe("t", lambda e: order.append("low"), priority=1)
        self.bus.subscribe("t", lambda e: order.append("high"), priority=10)
        self.bus.publish("t")
        self.assertEqual(order, ["high", "low"])

    def test_stop_propagation(self):
        reached = []
        def stopper(e):
            reached.append("first")
            e.stop_propagation()
        self.bus.subscribe("e", stopper, priority=10)
        self.bus.subscribe("e", lambda e: reached.append("second"), priority=1)
        self.bus.publish("e")
        self.assertEqual(reached, ["first"])

    def test_wildcard(self):
        caught = []
        self.bus.subscribe("user.*", lambda e: caught.append(e.name))
        self.bus.publish("user.login")
        self.bus.publish("user.logout")
        self.bus.publish("order.placed")
        self.assertEqual(caught, ["user.login", "user.logout"])

    def test_catch_all(self):
        caught = []
        self.bus.subscribe("*", lambda e: caught.append(e.name))
        self.bus.publish("a")
        self.bus.publish("b")
        self.assertEqual(caught, ["a", "b"])

    def test_clear(self):
        self.bus.subscribe("x", lambda e: None)
        self.bus.clear("x")
        self.assertEqual(self.bus.listener_count("x"), 0)

    def test_listener_count(self):
        self.bus.subscribe("x", lambda e: None)
        self.bus.subscribe("x", lambda e: None)
        self.assertEqual(self.bus.listener_count("x"), 2)

    def test_wait_for(self):
        import threading
        def trigger():
            import time
            time.sleep(0.05)
            self.bus.publish("ready", 99)
        threading.Thread(target=trigger, daemon=True).start()
        event = self.bus.wait_for("ready", timeout=2.0)
        self.assertIsNotNone(event)
        self.assertEqual(event.data, 99)

    def test_wait_for_timeout(self):
        result = self.bus.wait_for("never", timeout=0.05)
        self.assertIsNone(result)

    def test_repr(self):
        self.assertIn("EventBus", repr(self.bus))


class TestPipeline(unittest.TestCase):
    def test_run(self):
        p = Pipeline(lambda x: x + 1, lambda x: x * 2)
        self.assertEqual(p.run(3), 8)

    def test_call(self):
        p = Pipeline(str.upper)
        self.assertEqual(p("hello"), "HELLO")

    def test_pipe_extends(self):
        p1 = Pipeline(lambda x: x + 1)
        p2 = p1.pipe(lambda x: x * 2)
        self.assertEqual(p2.run(3), 8)

    def test_len(self):
        p = Pipeline(str.strip, str.lower)
        self.assertEqual(len(p), 2)

    def test_repr(self):
        p = Pipeline(str.strip)
        self.assertIn("strip", repr(p))

    def test_compose(self):
        fn = pipe_compose(lambda x: x + 1, lambda x: x * 2)
        self.assertEqual(fn(3), 8)

    def test_branch_true(self):
        step = branch(lambda x: x > 0, lambda x: "positive", lambda x: "non-positive")
        self.assertEqual(step(5), "positive")

    def test_branch_false(self):
        step = branch(lambda x: x > 0, lambda x: "positive", lambda x: "non-positive")
        self.assertEqual(step(-1), "non-positive")


class TestContextUtils(unittest.TestCase):
    def test_suppress_swallows_exception(self):
        with suppress(ZeroDivisionError):
            _ = 1 / 0

    def test_suppress_lets_other_through(self):
        with self.assertRaises(ValueError):
            with suppress(ZeroDivisionError):
                raise ValueError("not suppressed")

    def test_temp_dir_creates_path(self):
        with temp_dir() as d:
            self.assertTrue(d.exists())
            (d / "test.txt").write_text("hello")

    def test_temp_dir_cleaned_up(self):
        with temp_dir() as d:
            path = d
        self.assertFalse(path.exists())

    def test_temp_env_sets_var(self):
        with temp_env(MY_TEST_VAR="hello"):
            self.assertEqual(os.environ.get("MY_TEST_VAR"), "hello")

    def test_temp_env_restores_var(self):
        with temp_env(MY_TEST_VAR="hello"):
            pass
        self.assertIsNone(os.environ.get("MY_TEST_VAR"))

    def test_managed_resource_active(self):
        res = ManagedResource("db")
        with res:
            self.assertTrue(res.active)
        self.assertFalse(res.active)

    def test_managed_resource_repr(self):
        res = ManagedResource("cache")
        self.assertIn("cache", repr(res))


class TestCsvUtils(unittest.TestCase):
    ROWS = [
        {"name": "Alice", "age": "30", "city": "Warsaw"},
        {"name": "Bob",   "age": "25", "city": "Berlin"},
        {"name": "Carol", "age": "35", "city": "Paris"},
        {"name": "Dave",  "age": "25", "city": "Warsaw"},
    ]

    def test_csv_to_string_has_header(self):
        s = csv_to_string(self.ROWS)
        self.assertIn("name", s)
        self.assertIn("Alice", s)

    def test_string_to_csv_round_trip(self):
        s = csv_to_string(self.ROWS)
        result = string_to_csv(s)
        self.assertEqual(result[0]["name"], "Alice")
        self.assertEqual(len(result), 4)

    def test_csv_to_string_empty(self):
        self.assertEqual(csv_to_string([]), "")

    def test_col_values(self):
        self.assertEqual(col_values(self.ROWS, "name"), ["Alice", "Bob", "Carol", "Dave"])

    def test_col_values_missing_key(self):
        rows = [{"a": 1}, {"b": 2}]
        self.assertEqual(col_values(rows, "a"), [1])

    def test_select_cols(self):
        result = select_cols(self.ROWS, ["name", "city"])
        self.assertEqual(list(result[0].keys()), ["name", "city"])

    def test_filter_rows(self):
        result = filter_rows(self.ROWS, lambda r: r["age"] == "25")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Bob")

    def test_sort_rows_ascending(self):
        result = sort_rows(self.ROWS, "name")
        self.assertEqual(result[0]["name"], "Alice")
        self.assertEqual(result[-1]["name"], "Dave")

    def test_sort_rows_descending(self):
        result = sort_rows(self.ROWS, "name", reverse=True)
        self.assertEqual(result[0]["name"], "Dave")

    def test_transform_col(self):
        result = transform_col(self.ROWS, "age", int)
        self.assertEqual(result[0]["age"], 30)

    def test_rename_col(self):
        result = rename_col(self.ROWS, "city", "location")
        self.assertIn("location", result[0])
        self.assertNotIn("city", result[0])

    def test_drop_col(self):
        result = drop_col(self.ROWS, "age")
        self.assertNotIn("age", result[0])
        self.assertIn("name", result[0])

    def test_deduplicate(self):
        result = deduplicate(self.ROWS, "age")
        ages = col_values(result, "age")
        self.assertEqual(len(ages), len(set(ages)))

    def test_write_and_read_csv(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            tmp = f.name
        try:
            write_csv(tmp, self.ROWS)
            rows = read_csv(tmp)
            self.assertEqual(len(rows), 4)
            self.assertEqual(rows[0]["name"], "Alice")
        finally:
            os.unlink(tmp)

    def test_write_csv_empty_does_nothing(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            tmp = f.name
        try:
            write_csv(tmp, [])
            self.assertEqual(os.path.getsize(tmp), 0)
        finally:
            os.unlink(tmp)

    def test_get_headers(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            tmp = f.name
        try:
            write_csv(tmp, self.ROWS)
            self.assertEqual(get_headers(tmp), ["name", "age", "city"])
        finally:
            os.unlink(tmp)

    def test_count_rows(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            tmp = f.name
        try:
            write_csv(tmp, self.ROWS)
            self.assertEqual(count_rows(tmp), 4)
        finally:
            os.unlink(tmp)

    def test_write_and_read_csv_rows(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            tmp = f.name
        try:
            write_csv_rows(tmp, [["a", "b"], ["1", "2"]])
            rows = read_csv_rows(tmp)
            self.assertEqual(rows[0], ["a", "b"])
        finally:
            os.unlink(tmp)

    def test_append_row_dict(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            tmp = f.name
        try:
            append_row(tmp, {"x": "1", "y": "2"})
            content = open(tmp, encoding="utf-8").read()
            self.assertIn("1", content)
        finally:
            os.unlink(tmp)


class TestIteratorUtils(unittest.TestCase):
    def test_chunks_even(self):
        self.assertEqual(list(chunks([1, 2, 3, 4], 2)), [[1, 2], [3, 4]])

    def test_chunks_uneven(self):
        result = list(chunks([1, 2, 3, 4, 5], 2))
        self.assertEqual(result[-1], [5])

    def test_chunks_empty(self):
        self.assertEqual(list(chunks([], 3)), [])

    def test_sliding_window(self):
        self.assertEqual(list(sliding_window([1, 2, 3, 4], 2)),
                         [(1, 2), (2, 3), (3, 4)])

    def test_sliding_window_size_equals_len(self):
        self.assertEqual(list(sliding_window([1, 2, 3], 3)), [(1, 2, 3)])

    def test_pairwise(self):
        self.assertEqual(list(pairwise([1, 2, 3])), [(1, 2), (2, 3)])

    def test_flatten(self):
        self.assertEqual(iter_flatten([[1, 2], [3], [4, 5]]), [1, 2, 3, 4, 5])

    def test_deep_flatten(self):
        self.assertEqual(deep_flatten([1, [2, [3, [4]]], 5]), [1, 2, 3, 4, 5])

    def test_deep_flatten_mixed(self):
        self.assertEqual(deep_flatten([1, (2, 3), {4}]), [1, 2, 3, 4])

    def test_interleave(self):
        self.assertEqual(interleave([1, 3], [2, 4]), [1, 2, 3, 4])

    def test_roundrobin(self):
        self.assertEqual(roundrobin("AB", "CD"), ["A", "C", "B", "D"])

    def test_first(self):
        self.assertEqual(first([10, 20, 30]), 10)

    def test_first_empty_default(self):
        self.assertIsNone(first([]))

    def test_last(self):
        self.assertEqual(last([10, 20, 30]), 30)

    def test_last_empty_default(self):
        self.assertIsNone(last([]))

    def test_nth(self):
        self.assertEqual(nth(iter([10, 20, 30]), 1), 20)

    def test_nth_out_of_range(self):
        self.assertIsNone(nth(iter([1, 2]), 5))

    def test_count_items(self):
        self.assertEqual(count_items(range(7)), 7)

    def test_all_equal_true(self):
        self.assertTrue(all_equal([1, 1, 1]))

    def test_all_equal_false(self):
        self.assertFalse(all_equal([1, 2, 1]))

    def test_all_equal_single(self):
        self.assertTrue(all_equal([42]))

    def test_minmax(self):
        self.assertEqual(minmax([3, 1, 4, 1, 5, 9, 2]), (1, 9))

    def test_accumulate(self):
        self.assertEqual(accumulate([1, 2, 3, 4]), [1, 3, 6, 10])

    def test_zip_longest(self):
        result = zip_longest([1, 2, 3], [4, 5], fillvalue=0)
        self.assertEqual(result, [(1, 4), (2, 5), (3, 0)])

    def test_product(self):
        self.assertEqual(product([1, 2], ["a", "b"]),
                         [(1, "a"), (1, "b"), (2, "a"), (2, "b")])

    def test_permutations(self):
        self.assertEqual(len(permutations([1, 2, 3], 2)), 6)

    def test_combinations(self):
        self.assertEqual(combinations([1, 2, 3], 2), [(1, 2), (1, 3), (2, 3)])

    def test_combinations_with_replacement(self):
        result = combinations_with_replacement([1, 2], 2)
        self.assertIn((1, 1), result)

    def test_peekable_peek(self):
        p = Peekable([1, 2, 3])
        self.assertEqual(p.peek(), 1)
        self.assertEqual(next(p), 1)

    def test_peekable_exhausted(self):
        p = Peekable([])
        self.assertIsNone(p.peek())

    def test_peekable_iteration(self):
        self.assertEqual(list(Peekable([10, 20, 30])), [10, 20, 30])


class TestTemplateUtils(unittest.TestCase):
    def test_variable_substitution(self):
        self.assertEqual(render("Hello, {{ name }}!", {"name": "World"}), "Hello, World!")

    def test_missing_variable_renders_empty(self):
        self.assertEqual(render("{{ missing }}", {}), "")

    def test_filter_upper(self):
        self.assertEqual(render("{{ x | upper }}", {"x": "hello"}), "HELLO")

    def test_filter_lower(self):
        self.assertEqual(render("{{ x | lower }}", {"x": "HELLO"}), "hello")

    def test_filter_title(self):
        self.assertEqual(render("{{ x | title }}", {"x": "hello world"}), "Hello World")

    def test_filter_escape(self):
        result = render("{{ x | escape }}", {"x": "<b>bold</b>"})
        self.assertIn("&lt;", result)

    def test_filter_length(self):
        self.assertEqual(render("{{ x | length }}", {"x": [1, 2, 3]}), "3")

    def test_if_true_branch(self):
        t = "{% if flag %}yes{% endif %}"
        self.assertEqual(render(t, {"flag": True}), "yes")

    def test_if_false_branch(self):
        t = "{% if flag %}yes{% else %}no{% endif %}"
        self.assertEqual(render(t, {"flag": False}), "no")

    def test_if_elif(self):
        t = "{% if x > 10 %}big{% elif x > 5 %}medium{% else %}small{% endif %}"
        self.assertEqual(render(t, {"x": 7}), "medium")

    def test_for_loop(self):
        t = "{% for item in items %}{{ item }} {% endfor %}"
        self.assertEqual(render(t, {"items": ["a", "b", "c"]}), "a b c ")

    def test_comment_ignored(self):
        self.assertEqual(render("hi {# comment #} there", {}), "hi  there")

    def test_render_safe_substitution(self):
        self.assertEqual(render_safe("{{ x }}", {"x": "ok"}), "ok")

    def test_render_safe_missing_renders_empty(self):
        self.assertEqual(render_safe("{{ missing }}", {}), "")

    def test_escape_html(self):
        self.assertEqual(escape_html("<script>"), "&lt;script&gt;")

    def test_register_filter(self):
        register_filter("shout", lambda s: s.upper() + "!")
        self.assertEqual(render("{{ msg | shout }}", {"msg": "hi"}), "HI!")

    def test_template_class_render(self):
        t = Template("Dear {{ name }}")
        self.assertEqual(t.render({"name": "Alice"}), "Dear Alice")

    def test_template_class_no_context(self):
        t = Template("static text")
        self.assertEqual(t.render(), "static text")


TOML_TEXT = """
[project]
name = "MyApp"
version = "1.0"
debug = false
tags = ["python", "util"]

[database]
host = "localhost"
port = 5432

[database.pool]
min = 2
max = 10
"""

INI_TEXT = """
[database]
host = localhost
port = 5432
debug = true

[server]
host = 0.0.0.0
port = 8080
timeout = 30.5
"""

XML_TEXT = """<library>
    <book id="1" genre="fiction">
        <title>The Great Gatsby</title>
        <author>F. Scott Fitzgerald</author>
    </book>
    <book id="2" genre="sci-fi">
        <title>Dune</title>
        <author>Frank Herbert</author>
    </book>
</library>"""


class TestTomlUtils(unittest.TestCase):
    def setUp(self):
        self.data = toml_parse(TOML_TEXT)

    def test_parse_string_returns_dict(self):
        self.assertIsInstance(self.data, dict)

    def test_get_scalar(self):
        self.assertEqual(toml_get(self.data, "project.name"), "MyApp")

    def test_get_nested(self):
        self.assertEqual(toml_get(self.data, "database.pool.max"), 10)

    def test_get_missing_returns_default(self):
        self.assertIsNone(toml_get(self.data, "missing.key"))
        self.assertEqual(toml_get(self.data, "missing.key", "N/A"), "N/A")

    def test_has_key_true(self):
        self.assertTrue(toml_has_key(self.data, "database.host"))

    def test_has_key_false(self):
        self.assertFalse(toml_has_key(self.data, "cache.ttl"))

    def test_set_value_new_key(self):
        toml_set(self.data, "cache.ttl", 300)
        self.assertEqual(toml_get(self.data, "cache.ttl"), 300)

    def test_set_value_overwrite(self):
        toml_set(self.data, "database.port", 5433)
        self.assertEqual(toml_get(self.data, "database.port"), 5433)

    def test_merge_overrides(self):
        override = {"database": {"port": 9999}}
        merged = toml_merge(self.data, override)
        self.assertEqual(toml_get(merged, "database.port"), 9999)

    def test_merge_preserves_base(self):
        override = {"new_key": "value"}
        merged = toml_merge(self.data, override)
        self.assertEqual(toml_get(merged, "project.name"), "MyApp")

    def test_flatten_keys(self):
        flat = flatten_keys(self.data)
        self.assertIn("database.host", flat)
        self.assertIn("database.pool.min", flat)

    def test_keys_at(self):
        result = keys_at(self.data, "database")
        self.assertIn("host", result)
        self.assertIn("port", result)

    def test_keys_at_missing_returns_empty(self):
        self.assertEqual(keys_at(self.data, "nonexistent"), [])

    def test_to_string_contains_key(self):
        s = toml_to_str({"app": {"name": "Test"}, "port": 8000})
        self.assertIn("port", s)
        self.assertIn("8000", s)

    def test_write_and_read_toml(self):
        with tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False) as f:
            tmp = f.name
        try:
            write_toml(tmp, {"x": 1, "y": "hello"})
            result = read_toml(tmp)
            self.assertEqual(result["x"], 1)
            self.assertEqual(result["y"], "hello")
        finally:
            os.unlink(tmp)


class TestXmlUtils(unittest.TestCase):
    def setUp(self):
        self.root = xml_parse(XML_TEXT)

    def test_parse_string_tag(self):
        self.assertEqual(self.root.tag, "library")

    def test_find_first(self):
        book = xml_find(self.root, "book")
        self.assertIsNotNone(book)
        self.assertEqual(book.tag, "book")

    def test_find_all(self):
        books = xml_find_all(self.root, "book")
        self.assertEqual(len(books), 2)

    def test_get_attr(self):
        book = xml_find(self.root, "book")
        self.assertEqual(get_attr(book, "id"), "1")

    def test_get_attr_default(self):
        book = xml_find(self.root, "book")
        self.assertIsNone(get_attr(book, "missing"))

    def test_set_attr(self):
        book = xml_find(self.root, "book")
        set_attr(book, "year", "1925")
        self.assertEqual(get_attr(book, "year"), "1925")

    def test_get_text(self):
        book = xml_find(self.root, "book")
        title = xml_find(book, "title")
        self.assertEqual(get_text(title), "The Great Gatsby")

    def test_get_text_none_returns_default(self):
        self.assertEqual(get_text(None, "default"), "default")

    def test_set_text(self):
        book = xml_find(self.root, "book")
        title = xml_find(book, "title")
        set_text(title, "New Title")
        self.assertEqual(get_text(title), "New Title")

    def test_get_all_text(self):
        book = xml_find(self.root, "book")
        text = get_all_text(book)
        self.assertIn("Gatsby", text)
        self.assertIn("Fitzgerald", text)

    def test_create_element(self):
        el = create_element("item", text="hello", id="42")
        self.assertEqual(el.tag, "item")
        self.assertEqual(el.text, "hello")
        self.assertEqual(el.get("id"), "42")

    def test_add_child(self):
        root = create_element("root")
        child = add_child(root, "child", text="value")
        self.assertEqual(len(list(root)), 1)
        self.assertEqual(child.text, "value")

    def test_remove_child(self):
        root = create_element("root")
        child = add_child(root, "child")
        remove_child(root, child)
        self.assertEqual(len(list(root)), 0)

    def test_to_string_contains_tag(self):
        el = create_element("note", text="hi")
        s = xml_to_str(el)
        self.assertIn("note", s)
        self.assertIn("hi", s)

    def test_element_to_dict_has_attrs(self):
        book = xml_find(self.root, "book")
        d = element_to_dict(book)
        self.assertIn("@attrs", d)
        self.assertEqual(d["@attrs"]["id"], "1")

    def test_element_to_dict_has_children(self):
        book = xml_find(self.root, "book")
        d = element_to_dict(book)
        self.assertIn("title", d)

    def test_dict_to_element(self):
        data = {"@attrs": {"id": "5"}, "title": "Test"}
        el = dict_to_element("book", data)
        self.assertEqual(el.tag, "book")
        self.assertEqual(el.get("id"), "5")


class TestIniUtils(unittest.TestCase):
    def setUp(self):
        self.config = ini_parse(INI_TEXT)

    def test_sections(self):
        self.assertIn("database", sections(self.config))
        self.assertIn("server", sections(self.config))

    def test_get_string(self):
        self.assertEqual(ini_get(self.config, "database", "host"), "localhost")

    def test_get_missing_returns_default(self):
        self.assertEqual(ini_get(self.config, "missing", "key", "N/A"), "N/A")

    def test_get_int(self):
        self.assertEqual(ini_get_int(self.config, "database", "port"), 5432)

    def test_get_int_missing_returns_default(self):
        self.assertEqual(ini_get_int(self.config, "missing", "key", 99), 99)

    def test_get_float(self):
        self.assertAlmostEqual(ini_get_float(self.config, "server", "timeout"), 30.5)

    def test_get_bool_true(self):
        self.assertTrue(ini_get_bool(self.config, "database", "debug"))

    def test_get_bool_missing_returns_default(self):
        self.assertFalse(ini_get_bool(self.config, "missing", "key"))

    def test_has_section_true(self):
        self.assertTrue(has_section(self.config, "server"))

    def test_has_section_false(self):
        self.assertFalse(has_section(self.config, "cache"))

    def test_has_key_true(self):
        self.assertTrue(ini_has_key(self.config, "database", "host"))

    def test_has_key_false(self):
        self.assertFalse(ini_has_key(self.config, "database", "missing"))

    def test_set_value_new_section(self):
        ini_set(self.config, "cache", "ttl", "300")
        self.assertEqual(ini_get(self.config, "cache", "ttl"), "300")

    def test_set_value_existing(self):
        ini_set(self.config, "database", "host", "remotehost")
        self.assertEqual(ini_get(self.config, "database", "host"), "remotehost")

    def test_keys(self):
        k = ini_keys(self.config, "database")
        self.assertIn("host", k)
        self.assertIn("port", k)

    def test_keys_missing_section(self):
        self.assertEqual(ini_keys(self.config, "nonexistent"), [])

    def test_items(self):
        it = ini_items(self.config, "server")
        self.assertIn("port", it)

    def test_items_missing_section(self):
        self.assertEqual(ini_items(self.config, "nonexistent"), {})

    def test_to_dict(self):
        d = ini_to_dict(self.config)
        self.assertIn("database", d)
        self.assertEqual(d["database"]["host"], "localhost")

    def test_from_dict(self):
        cfg = ini_from_dict({"app": {"name": "MyApp", "version": "1.0"}})
        self.assertEqual(ini_get(cfg, "app", "name"), "MyApp")

    def test_remove_section(self):
        remove_section(self.config, "server")
        self.assertFalse(has_section(self.config, "server"))

    def test_remove_key(self):
        remove_key(self.config, "database", "debug")
        self.assertFalse(ini_has_key(self.config, "database", "debug"))

    def test_merge(self):
        override = ini_parse("[server]\nport = 9090\n[cache]\nttl = 600\n")
        merged = ini_merge(self.config, override)
        self.assertEqual(ini_get(merged, "server", "port"), "9090")
        self.assertEqual(ini_get(merged, "cache", "ttl"), "600")

    def test_to_string(self):
        cfg = ini_from_dict({"section": {"key": "val"}})
        s = ini_to_str(cfg)
        self.assertIn("section", s)
        self.assertIn("key", s)


if __name__ == "__main__":
    unittest.main(verbosity=2)
