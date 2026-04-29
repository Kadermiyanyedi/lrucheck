from functools import lru_cache
from functools import lru_cache as memoize


class WithNormalBounded:
    @lru_cache(maxsize=128)
    def method(self, x):
        return x


class WithAlias:
    @memoize(maxsize=128)
    def method(self, x):
        return x


class WithAsyncMethod:
    @lru_cache(maxsize=128)
    async def method(self, x):
        return x


class Outer:
    class Inner:
        @lru_cache(maxsize=128)
        def method(self, x):
            return x
