import unittest
from unittest.mock import patch
from models import Author, User, Currency, UserCurrency
from utils.currencies_api import get_currencies
import requests


class TestModels(unittest.TestCase):
    """Тестирование моделей предметной области."""
    def test_author_model(self):
        author = Author("Наумкина Александра", "P-3122")
        self.assertEqual(author.name, "Наумкина Александра")
        self.assertEqual(author.group, "P-3122")
        with self.assertRaises(TypeError):
            author.name = 123
        with self.assertRaises(ValueError):
            author.group = " "

        author.name = "Алиса"
        self.assertEqual(author.name, "Саша")

    def test_currency_model(self):
        c1 = Currency("R01239", "840", "USD", "Доллар США", "90,5512", 1)
        self.assertEqual(c1.value, 90.5512)

        c2 = Currency("R01240", "978", "EUR", "Евро", 98.76, 1)
        self.assertEqual(c2.value, 98.76)

        c3 = Currency("R01280", "360", "IDR", "Рупий", "48,6178", 10000)
        self.assertEqual(c3.nominal, 10000)

        with self.assertRaises(ValueError):
            c1.char_code = "US"
        c1.char_code = "aud"
        self.assertEqual(c1.char_code, "AUD")

    def test_user_model(self):
        """
        Тестирование модели User.
        """

        user = User(10, "Светлана")
        self.assertEqual(user.id, 10)
        with self.assertRaises(ValueError):
            User(-1, "Ошибка ID")

        with self.assertRaises(TypeError):
            User(1, 123)

        user_test = User(1, "Тест")
        with self.assertRaises(ValueError):
            user_test.name = "   "

    def test_user_currency_model(self):
        user = User(1, "Тест")
        currency = Currency("R00001", "001", "T1C", "Тест Валюта", "1.0", 1)

        uc = UserCurrency(user, currency, 1)
        self.assertEqual(uc.user.name, "Тест")
        self.assertEqual(uc.currency.char_code, "T1C")

        with self.assertRaises(TypeError):
            UserCurrency("Не юзер", currency, 2)


MOCK_XML_RESPONSE = """
<ValCurs Date="01.01.2025" name="Foreign Currency Market">
    <Valute ID="R01239">
        <NumCode>840</NumCode>
        <CharCode>USD</CharCode>
        <Nominal>1</Nominal>
        <Name>Доллар США</Name>
        <Value>90,0000</Value>
    </Valute>
    <Valute ID="R01240">
        <NumCode>978</NumCode>
        <CharCode>EUR</CharCode>
        <Nominal>1</Nominal>
        <Name>Евро</Name>
        <Value>95,0000</Value>
    </Valute>
</ValCurs>
"""


class MockResponse:
    """Класс-заглушка для имитации ответа requests."""

    def __init__(self, content, status_code=200):
        self.content = content.encode('utf-8')
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.exceptions.RequestException("Mock HTTP Error")


class TestCurrenciesApi(unittest.TestCase):
    """Тестирование утилиты для работы с API курсов валют."""

    @patch('utils.currencies_api.requests.get')
    def test_get_currencies_success(self, mock_get):
        mock_get.return_value = MockResponse(MOCK_XML_RESPONSE)

        currencies = get_currencies()

        mock_get.assert_called_once()

        self.assertEqual(len(currencies), 3)
        self.assertIn('USD', currencies)
        self.assertIn('EUR', currencies)
        self.assertIn('RUB', currencies)

        self.assertEqual(currencies['USD'].value, 90.0)
        self.assertEqual(currencies['EUR'].name, "Евро")
        self.assertEqual(currencies['RUB'].value, 1.0)

    @patch('utils.currencies_api.requests.get')
    def test_get_currencies_api_error(self, mock_get):
        """
        Проверка обработки ошибки HTTP-запроса.
        """
        mock_get.side_effect = requests.exceptions.RequestException("Mock HTTP Error")

        currencies = get_currencies()

        self.assertEqual(currencies, {})


if __name__ == '__main__':
    unittest.main()