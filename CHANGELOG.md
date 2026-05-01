# Changelog

All notable changes to this project go here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project follows [Semantic Versioning](https://semver.org/).

## [0.2.0]

### Added

* Rule LRU003 to find `@lru_cache` inside a function or closure. This is a warning.
* Rule LRU004 to find `@lru_cache` placed above `@staticmethod`. This is a warning.
* Severity levels for rules. Errors fail the build with exit code 1. Warnings only print and do not change the exit code on their own.
* Output format: warnings start with the `warning:` prefix.

### Changed

* LRU002 now flags only `@lru_cache(maxsize=None)`. Plain `@cache` and bare `@lru_cache` are no longer flagged. `@cache` is sometimes the right choice (for example on a method of an `enum.Enum` subclass) and bare `@lru_cache` defaults to a bounded cache, not an unbounded one.
* LRU002 message updated to point users to `@cache` when an unbounded cache is on purpose.

## [0.1.0] (April 30, 2026)

### Added

* First public release on PyPI.
* Rule LRU001 to find `@lru_cache` and `@cache` on a method.
* Rule LRU002 to find `@lru_cache(maxsize=None)` and `@cache` with no size limit.
* CLI to scan a single file or a folder.
* Exit codes 0 for clean, 1 for rule errors, 2 for missing files or syntax errors.
* README, MIT license, and PyPI metadata.

[0.1.0]: https://github.com/Kadermiyanyedi/lrucheck/releases/tag/v0.1.0
