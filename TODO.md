# TODO

## Rules

- [x] **LRU001** — `@lru_cache` / `@cache` on a method (instance leak via `self`)
- [x] **LRU002** — `@lru_cache(maxsize=None)` or `@cache` (no size limit)
- [ ] **LRU003** — `@lru_cache` defined inside a function or closure (a new cache per call, no real hits)
- [ ] **LRU004** — `@staticmethod` placed below `@lru_cache` (wrong decorator order), or `@classmethod` combined with `@lru_cache` (problematic in any order)

## Features

- [ ] Read config from `pyproject.toml` `[tool.lrucheck]`
- [ ] Inline suppression with `# noqa: LRU001`
- [ ] `--select` / `--ignore` flags to enable or disable rules
- [ ] `--exclude` flag to skip paths
- [ ] JSON output mode for editor integrations
- [ ] Provide `.pre-commit-hooks.yaml` so other projects can use lrucheck as a pre-commit hook

## Release

- [ ] Phase 2 — TestPyPI upload, then PyPI upload
- [ ] Phase 3 — GitHub Actions for tests and Trusted Publishing
