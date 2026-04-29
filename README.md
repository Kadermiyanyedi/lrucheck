# lrucheck

A small static checker that finds memory leaks from `functools.lru_cache` and `functools.cache` in Python code.

## Why

Python's `lru_cache` is easy to use, but it has two common traps:

1. **`@lru_cache` on a method.** The cache holds the `self` argument. Your instance never gets garbage-collected. The longer the program runs, the more memory it uses.
2. **`@lru_cache(maxsize=None)` or `@cache`.** The cache has no size limit. It grows forever as new arguments come in.

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
from functools import lru_cache, cache


class UserService:
    @lru_cache(maxsize=128)
    def find_user(self, user_id):
        return load_user(user_id)

    @cache
    def get_settings(self, user_id):
        return load_settings(user_id)


@lru_cache
def heavy_compute(value):
    return value * value
```

Run lrucheck:

```bash
$ lrucheck service.py
service.py:5:6: LRU001 `@lru_cache` on a method keeps `self` in the cache and leaks the instance
service.py:9:6: LRU001 `@lru_cache` on a method keeps `self` in the cache and leaks the instance
service.py:9:6: LRU002 `@lru_cache(maxsize=None)` or `@cache` has no size limit and can grow forever
service.py:14:2: LRU002 `@lru_cache(maxsize=None)` or `@cache` has no size limit and can grow forever
$ echo $?
1
```

The output format is the same as `flake8` and `ruff`, so editors and CI tools can read it.

## Rules

| Code | What it finds |
|------|---------------|
| `LRU001` | `@lru_cache` or `@cache` on a method. The cache keeps `self`, so the instance is never freed. |
| `LRU002` | `@lru_cache(maxsize=None)` or `@cache`. The cache has no size limit and can grow forever. |

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

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | No problems found. |
| `1` | One or more rule errors found. |
| `2` | A path was missing, a file could not be read, or a file had a syntax error. |

This makes `lrucheck` easy to use in CI: a non-zero exit fails the build.

## Pre-commit (planned)

A pre-commit hook is on the roadmap (see `TODO.md`). For now, you can run `lrucheck` from a script or a Makefile.

## Roadmap

- `LRU003` — `@lru_cache` defined inside a function or closure (a new cache per call)
- `LRU004` — wrong decorator order with `@staticmethod` or `@classmethod`
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

## License

MIT.
