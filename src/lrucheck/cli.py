from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable
from pathlib import Path

from lrucheck import __version__
from lrucheck.checker import check_source
from lrucheck.config import ConfigError, load_config
from lrucheck.rules import RuleError, Severity

EXIT_OK = 0
EXIT_FOUND_ISSUES = 1
EXIT_PARSE_ERROR = 2


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_config(Path.cwd())
    except ConfigError as error:
        print(f"lrucheck: {error}", file=sys.stderr)
        return EXIT_PARSE_ERROR

    files, missing = _collect_files(args.paths)
    for path in missing:
        print(f"lrucheck: path does not exist: {path}", file=sys.stderr)

    if not files:
        if not missing:
            print("lrucheck: no Python files found", file=sys.stderr)
        return EXIT_PARSE_ERROR if missing else EXIT_OK

    rule_errors: list[RuleError] = []
    parse_failed = bool(missing)

    for path in files:
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as error:
            print(f"lrucheck: cannot read {path}: {error}", file=sys.stderr)
            parse_failed = True
            continue

        try:
            rule_errors.extend(check_source(source, str(path)))
        except SyntaxError as error:
            print(
                f"{path}:{error.lineno}:{error.offset}: syntax error: {error.msg}",
                file=sys.stderr,
            )
            parse_failed = True

    ignore = set(config.ignore) | set(args.ignore)
    select = set(args.select) if args.select is not None else None
    if select is not None or ignore:
        rule_errors = [
            error
            for error in rule_errors
            if (select is None or error.rule.code in select) and error.rule.code not in ignore
        ]

    rule_errors.sort(key=lambda e: (e.path, e.line, e.column, e.rule.code))
    for rule_error in rule_errors:
        print(rule_error.format())

    if parse_failed:
        return EXIT_PARSE_ERROR
    if any(error.rule.severity is Severity.ERROR for error in rule_errors):
        return EXIT_FOUND_ISSUES
    return EXIT_OK


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lrucheck",
        description="Find memory-leak patterns in Python's functools.lru_cache usage.",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Files or directories to scan.",
    )
    parser.add_argument(
        "--select",
        type=_parse_codes,
        default=None,
        metavar="CODES",
        help="Run only these rule codes (comma separated). Overrides the default 'all'.",
    )
    parser.add_argument(
        "--ignore",
        type=_parse_codes,
        default=[],
        metavar="CODES",
        help="Skip these rule codes (comma separated). Adds to any ignore set in pyproject.toml.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def _parse_codes(value: str) -> list[str]:
    return [code.strip().upper() for code in value.split(",") if code.strip()]


def _collect_files(paths: Iterable[Path]) -> tuple[list[Path], list[Path]]:
    seen: set[Path] = set()
    files: list[Path] = []
    missing: list[Path] = []

    for path in paths:
        if path.is_file():
            if path.suffix == ".py" and path not in seen:
                seen.add(path)
                files.append(path)
        elif path.is_dir():
            for found in sorted(path.rglob("*.py")):
                if found not in seen:
                    seen.add(found)
                    files.append(found)
        else:
            missing.append(path)

    return files, missing
