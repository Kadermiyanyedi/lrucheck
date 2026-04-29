from functools import lru_cache


class WithStaticMethod:
    @staticmethod
    @lru_cache(maxsize=128)
    def helper(x):
        return x


class WithClassMethod:
    @classmethod
    @lru_cache(maxsize=128)
    def helper(cls, x):
        return x


@lru_cache(maxsize=256)
def top_level_bounded(x):
    return x


def my_decorator(func):
    return func


class WithUnrelatedDecorator:
    @my_decorator
    def method(self, x):
        return x
