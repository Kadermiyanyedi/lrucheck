from pathlib import Path

from lrucheck.checker import check_source

EXAMPLES_DIR = Path(__file__).parent / "examples"


def errors_in(example_name: str):
    path = EXAMPLES_DIR / example_name
    errors = check_source(path.read_text(encoding="utf-8"), str(path))
    return errors, str(path)


def test_safe_patterns_produce_no_errors():
    errors, _ = errors_in("safe_patterns.py")

    assert errors == []


def test_no_functools_import_produces_no_errors():
    errors, _ = errors_in("no_functools_import.py")

    assert errors == []


def test_lru001_only_patterns_report_each_method_at_its_decorator_line():
    errors, expected_path = errors_in("lru001_only_patterns.py")

    assert all(error.path == expected_path for error in errors)
    assert [(error.line, error.rule.code) for error in errors] == [
        (6, "LRU001"),
        (12, "LRU001"),
        (18, "LRU001"),
        (25, "LRU001"),
    ]


def test_unbounded_patterns_report_lru001_and_lru002_at_each_decorator_line():
    errors, expected_path = errors_in("unbounded_patterns.py")

    assert all(error.path == expected_path for error in errors)
    assert [(error.line, error.rule.code) for error in errors] == [
        (6, "LRU001"),
        (6, "LRU002"),
        (12, "LRU001"),
        (12, "LRU002"),
        (18, "LRU001"),
        (18, "LRU002"),
        (24, "LRU001"),
        (24, "LRU002"),
        (29, "LRU002"),
    ]


def test_lru003_fires_for_cache_decorators_inside_a_function():
    errors, expected_path = errors_in("lru003_patterns.py")

    assert all(error.path == expected_path for error in errors)
    assert [(error.line, error.rule.code) for error in errors] == [
        (5, "LRU003"),
        (13, "LRU002"),
        (13, "LRU003"),
        (21, "LRU003"),
        (30, "LRU003"),
    ]
