import pytest

from lrucheck.rules import LRU001, LRU002, RuleError


@pytest.mark.parametrize(
    ("path", "line", "column", "rule", "expected"),
    [
        ("foo.py", 5, 2, LRU001, f"foo.py:5:2: LRU001 {LRU001.message}"),
        ("src/bar.py", 12, 9, LRU002, f"src/bar.py:12:9: LRU002 {LRU002.message}"),
    ],
    ids=["lru001_at_foo", "lru002_at_bar"],
)
def test_format_uses_lint_style(path, line, column, rule, expected):
    error = RuleError(path=path, line=line, column=column, rule=rule)

    assert error.format() == expected


@pytest.mark.parametrize(
    ("first", "second", "should_be_equal"),
    [
        (
            RuleError("foo.py", 1, 1, LRU001),
            RuleError("foo.py", 1, 1, LRU001),
            True,
        ),
        (
            RuleError("foo.py", 1, 1, LRU001),
            RuleError("foo.py", 10, 1, LRU001),
            False,
        ),
        (
            RuleError("foo.py", 1, 1, LRU001),
            RuleError("foo.py", 1, 1, LRU002),
            False,
        ),
        (
            RuleError("foo.py", 1, 1, LRU001),
            RuleError("bar.py", 1, 1, LRU001),
            False,
        ),
    ],
    ids=["same_fields", "different_line", "different_rule", "different_path"],
)
def test_equality_compares_all_fields(first, second, should_be_equal):
    assert (first == second) is should_be_equal


def test_rule_error_can_be_used_in_a_set():
    first = RuleError("foo.py", 1, 1, LRU001)
    same = RuleError("foo.py", 1, 1, LRU001)

    assert {first, same} == {first}
