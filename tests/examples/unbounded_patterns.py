import functools
from functools import cache, lru_cache


class WithMaxsizeNone:
    @lru_cache(maxsize=None)
    def method(self, x):
        return x


class WithoutParens:
    @lru_cache
    def method(self, x):
        return x


class WithCacheDecorator:
    @cache
    def method(self, x):
        return x


class WithFunctoolsAttribute:
    @functools.lru_cache(maxsize=None)
    def method(self, x):
        return x


@lru_cache
def top_level_unbounded(x):
    return x
