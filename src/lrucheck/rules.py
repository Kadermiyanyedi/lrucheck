from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Rule:
    code: str
    message: str
    severity: Severity = field(default=Severity.ERROR)


@dataclass(frozen=True)
class RuleError:
    path: str
    line: int
    column: int
    rule: Rule

    def format(self) -> str:
        prefix = ""
        if self.rule.severity is Severity.WARNING:
            prefix = "warning: "
        return (
            f"{self.path}:{self.line}:{self.column}: {prefix}{self.rule.code} {self.rule.message}"
        )


LRU001 = Rule(
    code="LRU001",
    message="`@lru_cache` on a method keeps `self` in the cache and leaks the instance",
)

LRU002 = Rule(
    code="LRU002",
    message=(
        "`@lru_cache(maxsize=None)` has no size limit and can grow forever. "
        "Use `@cache` directly if this is on purpose."
    ),
)

LRU003 = Rule(
    code="LRU003",
    message="`@lru_cache` inside a function makes a new cache on every call and rarely hits",
    severity=Severity.WARNING,
)

LRU004 = Rule(
    code="LRU004",
    message="`@lru_cache` must be below `@staticmethod`, the reverse breaks on Python 3.9",
    severity=Severity.WARNING,
)
