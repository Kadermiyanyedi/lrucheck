import pytest

from lrucheck.checker import check_source
from lrucheck.noqa import is_suppressed, parse_noqa


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("x = 1  # noqa: LRU001\n", {1: frozenset({"LRU001"})}),
        ("x = 1  # noqa\n", {1: None}),
        ("x = 1  # noqa: LRU001, LRU002\n", {1: frozenset({"LRU001", "LRU002"})}),
        ("x = 1  # NOQA: lru001\n", {1: frozenset({"LRU001"})}),
        ("x = 1  # this is just a comment\n", {}),
    ],
    ids=[
        "specific_code",
        "bare_marker",
        "multiple_codes",
        "case_insensitive",
        "unrelated_comment",
    ],
)
def test_parse_noqa_extracts_expected_map(source, expected):
    assert parse_noqa(source) == expected


@pytest.mark.parametrize(
    ("line", "code", "noqa_map", "expected"),
    [
        (5, "LRU001", {5: frozenset({"LRU001"})}, True),
        (5, "LRU002", {5: frozenset({"LRU001"})}, False),
        (7, "LRU001", {5: frozenset({"LRU001"})}, False),
        (5, "LRU001", {5: None}, True),
        (5, "LRU002", {5: None}, True),
    ],
    ids=[
        "specific_code_matches",
        "specific_code_does_not_match_other_code",
        "specific_code_does_not_match_other_line",
        "bare_marker_matches_first_code",
        "bare_marker_matches_any_code",
    ],
)
def test_is_suppressed_for_each_case(line, code, noqa_map, expected):
    assert is_suppressed(line, code, noqa_map) is expected


SOURCE_TEMPLATE = (
    "from functools import lru_cache\n"
    "\n"
    "class Foo:\n"
    "    @lru_cache(maxsize=None)  {comment}\n"
    "    def method(self, x):\n"
    "        return x\n"
)


@pytest.mark.parametrize(
    ("comment", "expected_codes"),
    [
        ("# noqa: LRU001, LRU002", []),
        ("# noqa: LRU001", ["LRU002"]),
        ("# noqa", []),
        ("", ["LRU001", "LRU002"]),
    ],
    ids=[
        "both_codes_listed_drops_all",
        "only_one_code_listed_keeps_the_other",
        "bare_marker_drops_all",
        "no_marker_keeps_all",
    ],
)
def test_check_source_respects_noqa_on_decorator_line(comment, expected_codes):
    source = SOURCE_TEMPLATE.format(comment=comment)

    errors = check_source(source, "foo.py")

    assert sorted(error.rule.code for error in errors) == sorted(expected_codes)
