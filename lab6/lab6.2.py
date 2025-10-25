from bin_rec import build_tree_recursive, left_branch, right_branch
from bin_non_rec import build_tree_iterative

import timeit
import matplotlib.pyplot as plt
import random

'''
    bin_rec: рекурсивная реализация дерева
    bin_non_rec: итеративная реализация дерева
    timeit: для измерения времени выполнения
    matplotlib.pyplot: для построения графиков
    '''

def benchmark(func, n, repeat=5):
    """Возвращает среднее время выполнения func(n)"""
    times = timeit.repeat(lambda: func(n), number=1, repeat=repeat)
    return min(times)
    '''
       Выполняет функцию func и возвращает минимальное среднее время выполнения.
       Параметры:
       func: функция, которую необходимо протестировать
       n: размер данных
       repeat: количество повторений замера
      '''

def main():
    # Фиксированный набор данных
    random.seed(2)
    # Создание тестовых данных: числа с шагом 2
    test_data = list(range(2, 20, 2))

    # Списки для хранения результатов
    res_recursive = []
    res_iterative = []

    for n in test_data:
      res_recursive.append(benchmark(build_tree_recursive,n)) # Замеры времени для рекурсивной генерации
      res_iterative.append(benchmark(build_tree_iterative,n)) # Замеры времени для итеративной генерации

    # Визуализация
    plt.plot(test_data, res_recursive, label="Рекурсивный")
    plt.plot(test_data, res_iterative, label="Итеративный")
    plt.xlabel("n")
    plt.ylabel("Время (сек)")
    plt.title("Сравнение рекурсивного и итеративного дерева")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()