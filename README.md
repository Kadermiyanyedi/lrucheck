<p align="center">
  <img src="assets/logo.png" alt="lrucheck logo" width="320">
</p>

# lrucheck

[![PyPI](https://img.shields.io/pypi/v/lrucheck.svg)](https://pypi.org/project/lrucheck/)
[![Python versions](https://img.shields.io/pypi/pyversions/lrucheck.svg)](https://pypi.org/project/lrucheck/)
[![Downloads](https://static.pepy.tech/badge/lrucheck)](https://pepy.tech/project/lrucheck)
[![License: MIT](https://img.shields.io/pypi/l/lrucheck.svg)](https://github.com/Kadermiyanyedi/lrucheck/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

A small static checker that finds memory leaks from `functools.lru_cache` and `functools.cache` in Python code.

## Why

Python's `lru_cache` is easy to use, but it has two common traps:

1. **`@lru_cache` on a method.** The cache holds the `self` argument. Your instance never gets garbage-collected. The longer the program runs, the more memory it uses.
2. **`@lru_cache(maxsize=None)`.** The cache has no size limit. It grows forever as new arguments come in. (`@cache` does the same thing but is fine when you want it on purpose, for example on a method of an `enum.Enum` subclass.)

`lrucheck` reads your code (without running it) and prints a warning when it finds these patterns.

## Install

```bash
uv add lrucheck
```

## Use

Scan a file:

```bash
lrucheck path/to/file.py
```

Scan a folder (recursive):

```bash
lrucheck src/
```

## Example

Given this file `service.py`:

```python
from functools import lru_cache


class UserService:
    @lru_cache(maxsize=None)
    def find_user(self, user_id):
        return load_user(user_id)

    @lru_cache(maxsize=128)
    def get_settings(self, user_id):
        return load_settings(user_id)
```

Run lrucheck:

```bash
$ lrucheck service.py
service.py:5:6: LRU001 `@lru_cache` on a method keeps `self` in the cache and leaks the instance
service.py:5:6: LRU002 `@lru_cache(maxsize=None)` has no size limit and can grow forever. Use `@cache` directly if this is on purpose.
service.py:9:6: LRU001 `@lru_cache` on a method keeps `self` in the cache and leaks the instance
$ echo $?
1
```

The output format is the same as `flake8` and `ruff`, so editors and CI tools can read it.

## Rules

| Code | What it finds |
|------|---------------|
| `LRU001` | `@lru_cache` or `@cache` on a method. The cache keeps `self`, so the instance is never freed. |
| `LRU002` | `@lru_cache(maxsize=None)`. The cache has no size limit and can grow forever. `@cache` is not flagged because it is sometimes the right choice. |
| `LRU003` | `@lru_cache` inside a function or closure. A new cache is made on every outer call, so cache hits are rare. (warning) |
| `LRU004` | `@lru_cache` placed above `@staticmethod`. Wrong decorator order. The reverse breaks on Python 3.9 and is non canonical on later versions. (warning) |

### Bad

```python
from functools import lru_cache

class Service:
    @lru_cache(maxsize=None)   # LRU001 + LRU002
    def fetch(self, key):
        return load(key)
```

### Good

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fetch(key):
    return load(key)
```

If you must keep the cache near a class, use a `@staticmethod` or a top-level function:

```python
class Service:
    @staticmethod
    @lru_cache(maxsize=128)
    def fetch(key):
        return load(key)
```

## Severity

Each rule has a level. **Errors** (`LRU001`, `LRU002`) point to real memory leaks and fail the build. **Warnings** (`LRU003`, `LRU004`) point to less serious problems and do not change the exit code on their own. Warnings still print to the output and start with the `warning:` prefix.

```
service.py:5:6: LRU001 ...                  (error)
service.py:5:6: warning: LRU003 ...         (warning)
```

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | No errors found. Warnings may still be printed. |
| `1` | One or more rule errors found. |
| `2` | A path was missing, a file could not be read, or a file had a syntax error. |

This makes `lrucheck` easy to use in CI: a non-zero exit fails the build.

## Pre-commit (planned)

A pre-commit hook is on the roadmap (see `TODO.md`). For now, you can run `lrucheck` from a script or a Makefile.

## Roadmap

- Read config from `pyproject.toml` `[tool.lrucheck]`
- `# noqa: LRU001` to skip a single line
- `--select` and `--ignore` to turn rules on or off
- JSON output for editors

See [`TODO.md`](TODO.md) for the full list.

## Development

This project uses [`uv`](https://github.com/astral-sh/uv).

```bash
uv sync
uv run pytest
uv run lrucheck tests/examples/
```

### Pre-commit

The project uses [`pre-commit`](https://pre-commit.com/) to run checks before each commit:

- `ruff` for linting and formatting
- `codespell` for spelling
- [`ty`](https://github.com/astral-sh/ty) for type checking
- standard hooks for trailing whitespace, end of file, large files

To set it up once:

```bash
uv run pre-commit install
```

After this, the hooks run on every `git commit`. You can also run them on all files at any time:

```bash
uv run pre-commit run --all-files
```

## License

MIT.
