from __future__ import annotations

import ast
from collections.abc import Iterable

from lrucheck.rules import LRU001, LRU002, RuleError


CACHE_NAMES = frozenset({"lru_cache", "cache"})


class Checker(ast.NodeVisitor):
    def __init__(self, path: str) -> None:
        self.path = path
        self.rule_errors: list[RuleError] = []
        self._functools_aliases: set[str] = set()
        self._direct_aliases: dict[str, str] = {}
        self._class_depth = 0

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name == "functools":
                self._functools_aliases.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module == "functools":
            for alias in node.names:
                if alias.name in CACHE_NAMES:
                    self._direct_aliases[alias.asname or alias.name] = alias.name
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_depth += 1
        try:
            self.generic_visit(node)
        finally:
            self._class_depth -= 1

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        in_class = self._class_depth > 0
        skip_self_leak = self._has_static_or_class_decorator(node.decorator_list)

        for decorator in node.decorator_list:
            cache_name = self._resolve_cache_decorator(decorator)
            if cache_name is None:
                continue

            line, col = self._decorator_position(decorator)

            if in_class and not skip_self_leak:
                self.rule_errors.append(RuleError(self.path, line, col, LRU001))

            if self._is_unbounded(decorator, cache_name):
                self.rule_errors.append(RuleError(self.path, line, col, LRU002))

    def _has_static_or_class_decorator(self, decorators: Iterable[ast.expr]) -> bool:
        for decorator in decorators:
            if isinstance(decorator, ast.Name) and decorator.id in {"staticmethod", "classmethod"}:
                return True
        return False

    def _resolve_cache_decorator(self, decorator: ast.expr) -> str | None:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator

        if isinstance(target, ast.Name):
            return self._direct_aliases.get(target.id)

        if (
            isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id in self._functools_aliases
            and target.attr in CACHE_NAMES
        ):
            return target.attr

        return None

    def _is_unbounded(self, decorator: ast.expr, cache_name: str) -> bool:
        if cache_name == "cache":
            return True

        if not isinstance(decorator, ast.Call):
            return True

        for keyword in decorator.keywords:
            if keyword.arg == "maxsize":
                return self._is_none_literal(keyword.value)

        if decorator.args:
            return self._is_none_literal(decorator.args[0])

        return True

    @staticmethod
    def _is_none_literal(node: ast.expr) -> bool:
        return isinstance(node, ast.Constant) and node.value is None

    @staticmethod
    def _decorator_position(decorator: ast.expr) -> tuple[int, int]:
        return decorator.lineno, decorator.col_offset + 1


def check_source(source: str, path: str) -> list[RuleError]:
    tree = ast.parse(source, filename=path)
    checker = Checker(path)
    checker.visit(tree)
    return checker.rule_errors
