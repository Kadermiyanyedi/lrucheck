# TODO

## Rules

- [x] **LRU001** — `@lru_cache` / `@cache` on a method (instance leak via `self`)
- [x] **LRU002** — `@lru_cache(maxsize=None)` or `@cache` (no size limit)
- [x] **LRU003** — `@lru_cache` defined inside a function or closure (a new cache per call, no real hits)
- [x] **LRU004** — Wrong decorator order with `@staticmethod`. `@lru_cache` must be the inner decorator and `@staticmethod` must be the outer one. The reverse breaks on Python 3.9 and is non canonical on later versions.

## Features

- [ ] Read config from `pyproject.toml` `[tool.lrucheck]`
- [ ] Inline suppression with `# noqa: LRU001`
- [ ] `--select` / `--ignore` flags to enable or disable rules
- [ ] `--exclude` flag to skip paths
- [ ] JSON output mode for editor integrations
- [ ] Provide `.pre-commit-hooks.yaml` so other projects can use lrucheck as a pre-commit hook

## Rule changes

- [ ] Rewrite LRU002: stop flagging plain `@cache`. Only flag `@lru_cache(maxsize=None)`. New message: "no size limit, the cache can grow forever and may cause a memory leak. If you want a cache with no limit on purpose, use `@cache` directly." Reason: `@cache` is fine in some cases — for example on a method of an `enum.Enum` subclass, where the set of instances is fixed and small.

## Testing

- [ ] Add `tox` config to run tests across Python 3.9-3.13 locally. Catches version-specific issues before push, without waiting for CI.

## Documentation

- [ ] Per-rule docs pages with stable URLs (e.g. `https://lrucheck.dev/rules/LRU001`). Include the link in each error line so users can click from the terminal to read why the rule fires and how to fix it. Use MkDocs or a small Astro site on GitHub Pages.
- [x] `CHANGELOG.md` in [Keep a Changelog](https://keepachangelog.com/) format. One entry per release with Added / Changed / Fixed sections.
- [x] `CONTRIBUTING.md` with how to run tests, code style, how to propose a new rule, and the PR review flow.
- [ ] Issue and pull request templates in `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md`. Templates for bug report, rule proposal, and feature request.

## Release

- [x] Phase 2 — TestPyPI upload, then PyPI upload
- [ ] Phase 3 — GitHub Actions for tests and Trusted Publishing
