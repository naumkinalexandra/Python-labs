import timeit
import matplotlib.pyplot as plt
import random
from functools import lru_cache




def fact_recursive(n: int) -> int:
    """Рекурсивный факториал"""
    if n == 0:
        return 1
    return n * fact_recursive(n - 1)


def fact_iterative(n: int) -> int:
    """Нерекурсивный факториал"""
    res = 1
    for i in range(1, n + 1):
        res *= i
    return res

@lru_cache
def fact_recursive_cache(n: int) -> int:
    """Рекурсивный факториал"""
    if n == 0:
        return 1
    return n * fact_recursive(n - 1)

@lru_cache
def fact_iterative_cache(n: int) -> int:
    """Нерекурсивный факториал"""
    res = 1
    for i in range(1, n + 1):
        res *= i
    return res


def benchmark(func, n, repeat=5):
    """Возвращает среднее время выполнения func(n)"""
    times = timeit.repeat(lambda: func(n), number=1, repeat=repeat)
    return min(times)



def main():
    # фиксированный набор данных
    random.seed(42)
    test_data = list(range(10, 300, 10))

    res_recursive = []
    res_iterative = []
    res_recursive_cache = []
    res_iterative_cache = []

    for n in test_data:
      res_recursive.append(benchmark(fact_recursive, n))
      res_iterative.append(benchmark(fact_iterative, n))
      res_recursive_cache.append(benchmark(fact_recursive_cache, n))
      res_iterative_cache.append(benchmark(fact_iterative_cache, n))

    # Визуализация
    plt.plot(test_data, res_recursive, label="Рекурсивный")
    plt.plot(test_data, res_iterative, label="Итеративный")
    plt.plot(test_data, res_recursive_cache, label="Рекурсивный с lru_cache")
    plt.plot(test_data, res_iterative_cache, label="Итеративный с lru_cache")
    plt.xlabel("n")
    plt.ylabel("Время (сек)")
    plt.title("Сравнение рекурсивного и итеративного факториала")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()