import sys
import logging
import functools
import requests
import json
import math


def logger(func=None, *, handle=sys.stdout):
    """
    Параметризуемый декоратор для логирования выполнения функции.
    """
    if func is None:
        return lambda f: logger(f, handle=handle)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        is_logging_obj = isinstance(handle, logging.Logger)
        func_name = func.__name__
        args_repr = f"args: {args}, kwargs: {kwargs}"

        # Логирование старта (INFO)
        start_msg = f"INFO: Started '{func_name}'. {args_repr}"
        if is_logging_obj:
            handle.info(start_msg)
        else:
            handle.write(f"INFO: Started '{func_name}'. {args_repr}\n")

        try:
            result = func(*args, **kwargs)

            # Логирование успеха (INFO)
            success_msg = f"Finished '{func_name}'. Result: {result}"
            if is_logging_obj:
                handle.info(success_msg)
            else:
                handle.write(f"INFO: Finished '{func_name}'. Result: {result}\n")

            return result

        except Exception as e:
            #  Логирование ошибки (ERROR)
            error_msg = f"Failed '{func_name}'. Error: {type(e).__name__} - {e}"
            if is_logging_obj:
                handle.error(error_msg)
            else:
                handle.write(f"ERROR: Failed '{func_name}'. Error: {type(e).__name__} - {e}\n")

            # Повторный выброс исключения
            raise e

    return wrapper


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Создаем и настраиваем логгер для файла
file_logger = logging.getLogger("currency_file")
file_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("currencies.log", mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
if not file_logger.handlers:  # Избегаем дублирования обработчиков при повторном запуске
    file_logger.addHandler(file_handler)


@logger(handle=file_logger)
def get_currencies(currency_codes: list, url="https://www.cbr-xml-daily.ru/daily_json.js") -> dict:
    """
    Получает курсы валют с API Центробанка России.

    Args:
        currency_codes (list): Список символьных кодов валют (например, ['USD', 'EUR']).

    Returns:
        dict: Словарь, где ключи - символьные коды валют, а значения - их курсы.
              Возвращает None в случае ошибки запроса.
    """
    if not isinstance(currency_codes, list):
        raise TypeError("currency_codes должен быть списком")

    try:
        response = requests.get(url)
        response.raise_for_status()
    except (requests.ConnectionError, requests.Timeout):
        raise ConnectionError(f"API недоступен: {url}")
    except requests.HTTPError:
        raise ConnectionError(f"Ошибка HTTP при доступе к {url}")

    try:
        data = response.json()
    except json.JSONDecodeError:
        raise ValueError("Получен некорректный JSON")

    if "Valute" not in data:
        raise KeyError("В ответе API отсутствует ключ 'Valute'")

    result = {}
    valute_data = data["Valute"]

    for code in currency_codes:
        if code not in valute_data:
            raise KeyError(f"Валюта '{code}' отсутствует в данных")

        valute_info = valute_data[code]
        rate = valute_info.get("Value")

        if not isinstance(rate, (int, float)):
            raise TypeError(f"Курс валюты '{code}' имеет неверный тип: {type(rate)}")

        result[code] = rate

    return result


# Логгер квадратного уравнения
quad_logger = logging.getLogger("QuadraticSolver")
quad_logger.setLevel(logging.INFO)


@logger(handle=quad_logger)
def solve_quadratic(a, b, c):
    """
    Решает квадратное уравнение, ошибки, перехватывает декоратором.
    """
    if not all(isinstance(x, (int, float)) for x in [a, b, c]):
        raise TypeError("Все коэффициенты должны быть числами (a, b, c)")

    if a == 0 and b == 0:
        raise ValueError("Уравнение не существует (a=0, b=0)")
    if a == 0:
        return -c / b

    D = b ** 2 - 4 * a * c

    if D < 0:
        quad_logger.warning(f"Discriminant is negative (D={D}). No real roots.")
        return None

    x1 = (-b + math.sqrt(D)) / (2 * a)
    x2 = (-b - math.sqrt(D)) / (2 * a)

    return (x1, x2)


if __name__ == "__main__":

    print("get_currencies (логирование в currencies.log)")

    try:
        get_currencies(['USD', 'EUR'])
        print("\nУспешный вызов get_currencies. Проверьте файл currencies.log")
    except Exception:
        pass

    try:
        get_currencies(['USD', 'ZZZ'])
    except KeyError:
        print("\nВызов с KeyError. Проверьте файл currencies.log (должен быть ERROR)")
    except Exception:
        pass

    try:
        get_currencies(['USD'], url="https://invalid-url-address.com/api")
    except ConnectionError:
        print("\nВызов с ConnectionError. Проверьте файл currencies.log (должен быть ERROR)")
    except Exception:
        pass

    print("solve_quadratic (логирование в консоль через quad_logger)")

    print("\nТест 1: Два корня (a=1, b=5, c=6)")
    solve_quadratic(1, 5, 6)

    print("\nТест 2: Нет корней (a=1, b=0, c=1)")
    solve_quadratic(1, 0, 1)

    print("\nТест 3: TypeError (a='abc')")
    try:
        solve_quadratic("abc", 1, 1)
    except TypeError:
        print("TypeError")

    print("\nТест 4: ValueError (a=0, b=0)")
    try:
        solve_quadratic(0, 0, 5)
    except ValueError:
        print("ValueError")