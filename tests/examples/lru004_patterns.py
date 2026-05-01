from functools import lru_cache


class WrongOrder:
    @lru_cache(maxsize=128)
    @staticmethod
    def helper(x):
        return x


class WrongOrderWithMaxsizeNone:
    @lru_cache(maxsize=None)
    @staticmethod
    def helper(x):
        return x


class CorrectOrder:
    @staticmethod
    @lru_cache(maxsize=128)
    def helper(x):
        return x


@lru_cache(maxsize=128)
@staticmethod
def top_level_wrong_order(x):
    return x
