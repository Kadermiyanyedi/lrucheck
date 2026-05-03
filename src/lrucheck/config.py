from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


VALID_KEYS = frozenset({"ignore"})


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Config:
    ignore: frozenset[str] = field(default_factory=frozenset)


def find_pyproject(start: Path) -> Path | None:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    while True:
        candidate = current / "pyproject.toml"
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            return None
        current = parent


def load_config(start: Path) -> Config:
    pyproject = find_pyproject(start)
    if pyproject is None:
        return Config()
    try:
        with open(pyproject, "rb") as file:
            data = tomllib.load(file)
    except OSError as error:
        raise ConfigError(f"cannot read {pyproject}: {error}") from error
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"cannot parse {pyproject}: {error}") from error

    section = data.get("tool", {}).get("lrucheck", {})
    if not isinstance(section, dict):
        raise ConfigError(f"{pyproject}: [tool.lrucheck] must be a table")

    return _parse_section(section, pyproject)


def _parse_section(section: dict[str, Any], source: Path) -> Config:
    unknown = set(section) - VALID_KEYS
    if unknown:
        valid = ", ".join(sorted(VALID_KEYS))
        first = sorted(unknown)[0]
        raise ConfigError(
            f"{source}: unknown key `{first}` in [tool.lrucheck]. Valid keys: {valid}"
        )

    raw_ignore = section.get("ignore", [])
    if not isinstance(raw_ignore, list):
        raise ConfigError(f"{source}: `ignore` must be a list of rule codes")

    ignore: set[str] = set()
    for item in raw_ignore:
        if not isinstance(item, str):
            raise ConfigError(
                f"{source}: `ignore` entries must be strings, got {type(item).__name__}"
            )
        ignore.add(item.upper())

    return Config(ignore=frozenset(ignore))
