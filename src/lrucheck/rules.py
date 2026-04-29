from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    code: str
    message: str


@dataclass(frozen=True)
class RuleError:
    path: str
    line: int
    column: int
    rule: Rule

    def format(self) -> str:
        return f"{self.path}:{self.line}:{self.column}: {self.rule.code} {self.rule.message}"


LRU001 = Rule(
    code="LRU001",
    message="`@lru_cache` on a method keeps `self` in the cache and leaks the instance",
)

LRU002 = Rule(
    code="LRU002",
    message="`@lru_cache(maxsize=None)` or `@cache` has no size limit and can grow forever",
)
