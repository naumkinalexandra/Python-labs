import unittest
from unittest.mock import patch, MagicMock
import io
import json
import logging
import requests
import sys
import functools


def logger(func=None, *, handle=sys.stdout):
    if func is None:
        return lambda f: logger(f, handle=handle)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        is_logging_obj = isinstance(handle, logging.Logger)
        func_name = func.__name__

        start_msg = f"INFO: Started '{func_name}'. args: {args}, kwargs: {kwargs}"
        if is_logging_obj:
            handle.info(start_msg)
        else:
            handle.write(f"INFO: Started '{func_name}'. args: {args}, kwargs: {kwargs}\n")

        try:
            result = func(*args, **kwargs)

            success_msg = f"Finished '{func_name}'. Result: {result}"
            if is_logging_obj:
                handle.info(success_msg)
            else:
                handle.write(f"INFO: Finished '{func_name}'. Result: {result}\n")

            return result

        except Exception as e:
            error_msg = f"ERROR: Failed '{func_name}'. Error: {type(e).__name__} - {e}"
            if is_logging_obj:
                handle.error(error_msg)
            else:
                handle.write(f"ERROR: Failed '{func_name}'. Error: {type(e).__name__} - {e}\n")

            raise e

    return wrapper


def get_currencies(currency_codes: list, url: str = "https://www.cbr-xml-daily.ru/daily_json.js") -> dict:
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as e:
        raise ConnectionError(f"API недоступен или ошибка сети: {e}")

    try:
        data = response.json()
    except json.JSONDecodeError:
        raise ValueError("некорректным JSON")

    if "Valute" not in data:
        raise KeyError("В ответе API отсутствует ключ 'Valute'")

    valute_data = data["Valute"]
    result = {}

    for code in currency_codes:
        if code not in valute_data:
            raise KeyError(f"Валюта '{code}' не найдена в данных ЦБ")

        val_record = valute_data[code]
        rate = val_record.get("Value")

        if not isinstance(rate, (int, float)):
            raise TypeError(f"Курс валюты '{code}' не является числом: {rate}")

        result[code] = rate

    return result


class TestCurrencyBusinessLogic(unittest.TestCase):

    def setUp(self):
        self.mock_data = {
            "Valute": {
                "USD": {"Value": 90.5, "Nominal": 1, "Name": "Доллар США"},
                "EUR": {"Value": 100.2, "Nominal": 1, "Name": "Евро"},
                "GBP": {"Value": 115.0, "Nominal": 1, "Name": "Фунт стерлингов"}
            }
        }

    @patch('requests.get')
    def test_get_currencies_success(self, mock_get):
        """Проверка корректного возврата курсов"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.mock_data

        result = get_currencies(["USD", "EUR"], url="mock_url")
        self.assertEqual(result, {"USD": 90.5, "EUR": 100.2})
        self.assertIsInstance(result, dict)

    @patch('requests.get', side_effect=requests.ConnectionError("Network Failed"))
    def test_get_currencies_connection_error(self, mock_get):
        """Проверка выброса ConnectionError при ошибке сети"""
        with self.assertRaisesRegex(ConnectionError, "API недоступен"):
            get_currencies(["USD"], url="mock_url")

    @patch('requests.get')
    def test_get_currencies_http_error(self, mock_get):
        """Проверка выброса ConnectionError при HTTP-ошибке (например, 404)"""
        mock_get.return_value.status_code = 404
        mock_get.return_value.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        with self.assertRaisesRegex(ConnectionError, "API недоступен"):
            get_currencies(["USD"], url="mock_url")

    @patch('requests.get')
    def test_get_currencies_invalid_json(self, mock_get):
        """Проверка выброса ValueError при некорректном JSON"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.side_effect = json.JSONDecodeError("msg", "doc", 0)
        with self.assertRaisesRegex(ValueError, "некорректным JSON"):
            get_currencies(["USD"], url="mock_url")

    @patch('requests.get')
    def test_get_currencies_missing_valute_key(self, mock_get):
        """Проверка выброса KeyError при отсутствии ключа 'Valute'"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"Date": "...", "OtherKey": {}}
        with self.assertRaisesRegex(KeyError, "отсутствует ключ 'Valute'"):
            get_currencies(["USD"], url="mock_url")

    @patch('requests.get')
    def test_get_currencies_missing_currency_code(self, mock_get):
        """Проверка выброса KeyError при несуществующей валюте"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.mock_data
        with self.assertRaisesRegex(KeyError, "не найдена"):
            get_currencies(["USD", "XXX"], url="mock_url")

    @patch('requests.get')
    def test_get_currencies_invalid_rate_type(self, mock_get):
        """Проверка выброса TypeError если курс не число"""
        mock_data_invalid = {
            "Valute": {
                "USD": {"Value": "90.5", "Nominal": 1, "Name": "Доллар США"}  # Rate is string
            }
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_data_invalid
        with self.assertRaisesRegex(TypeError, "не является числом"):
            get_currencies(["USD"], url="mock_url")


class TestLoggerDecorator(unittest.TestCase):
    def setUp(self):
        self.stream = io.StringIO()

        @logger(handle=self.stream)
        def success_func(x):
            return x * 2

        @logger(handle=self.stream)
        def error_func(x):
            if x < 0:
                raise ValueError("Value cannot be negative")
            return x

        self.success_func = success_func
        self.error_func = error_func

    def test_logging_success_info(self):
        """Проверка логов INFO при успешном выполнении"""
        result = self.success_func(10)
        logs = self.stream.getvalue()

        self.assertIn("INFO: Started 'success_func'. args: (10,), kwargs: {}", logs)

        self.assertIn("INFO: Finished 'success_func'. Result: 20", logs)

        self.assertEqual(result, 20)

    def test_logging_error_and_rethrow(self):
        """Проверка логов ERROR и проброса исключения"""

        with self.assertRaises(ValueError):
            self.error_func(-5)

        logs = self.stream.getvalue()

        self.assertIn("ERROR: Failed 'error_func'. Error: ValueError - Value cannot be negative", logs)

        self.assertNotIn("Finished 'error_func'", logs)

        self.assertIn("INFO: Started 'error_func'", logs)

    @patch('requests.get', side_effect=requests.ConnectionError("Mocked Connection Error"))
    def test_logging_error_with_currency_context(self, mock_get):
        self.stream.truncate(0)
        self.stream.seek(0)

        @logger(handle=self.stream)
        def wrapped_get_currencies():
            return get_currencies(['USD'], url="https://invalid-url-address.com")

        with self.assertRaises(ConnectionError):
            wrapped_get_currencies()

        logs = self.stream.getvalue()

        self.assertIn("ERROR", logs)
        self.assertIn("ConnectionError", logs)
        self.assertIn("Failed 'wrapped_get_currencies'", logs)

    def test_logger_with_logging_obj(self):
        """Проверка работы декоратора с logging.Logger"""
        mock_logger = MagicMock(spec=logging.Logger)

        @logger(handle=mock_logger)
        def sum_two(a, b):
            return a + b

        sum_two(1, 2)
        self.assertTrue(mock_logger.info.called)
        self.assertEqual(mock_logger.info.call_count, 2)
        self.assertFalse(mock_logger.error.called)


if __name__ == "__main__":
    unittest.main()