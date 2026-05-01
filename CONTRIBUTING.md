# Contributing to lrucheck

Thank you for your interest in lrucheck. This guide shows you how to help.

## What you can contribute

You can help in many ways.

* Open an issue if you find a bug or a false warning.
* Suggest a new rule. See the rule proposal section below.
* Improve the README or the docs.
* Send a pull request with a fix or a new feature.

## Setup

This project uses [`uv`](https://github.com/astral-sh/uv).

```bash
uv sync
```

This command installs the runtime and the dev tools.

## Run the tests

```bash
uv run pytest
```

All tests should pass before you send a pull request.

## Code style

This project uses `ruff` for linting and formatting.

```bash
uv run ruff check
uv run ruff format
```

A `pre-commit` hook runs these on each commit. Install it once.

```bash
uv run pre-commit install
```

## Propose a new rule

A new rule needs three things.

1. A short code like `LRU005`.
2. A clear description of the bad pattern.
3. Test cases with bad and safe code samples.

Please open an issue first so we can talk about the idea before you write the code.

## Pull request flow

1. Fork the repo and create a branch.
2. Make your change.
3. Add tests for any new behavior.
4. Run `uv run pytest` and `uv run pre-commit run --all-files`.
5. Open a pull request. Write a short note about what you changed and why.

The maintainer reviews most pull requests within a few days.

## Code of conduct

Be kind. Treat other people with respect.
