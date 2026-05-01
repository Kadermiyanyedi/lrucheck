from functools import cache, lru_cache


def with_lru_cache_inside():
    @lru_cache(maxsize=128)
    def inner(x):
        return x

    return inner(1)


def with_cache_inside():
    @cache
    def inner(x):
        return x

    return inner(1)


def with_async_inside():
    @lru_cache(maxsize=64)
    async def inner(x):
        return x

    return inner


def factory():
    def middle():
        @lru_cache(maxsize=32)
        def deepest(x):
            return x

        return deepest

    return middle
