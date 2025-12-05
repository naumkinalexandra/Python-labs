import requests
import xml.etree.ElementTree as ET
from typing import Dict
from models.currency import Currency

CBR_DAILY_URL = "http://www.cbr.ru/scripts/XML_daily.asp"


def get_currencies() -> Dict[str, Currency]:
    """
    Получает актуальные курсы валют с API ЦБ РФ и преобразует их в словарь объектов Currency.

    Возвращает:
        Dict[str, Currency]: Словарь
    """
    try:
        response = requests.get(CBR_DAILY_URL, timeout=5)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        currencies: Dict[str, Currency] = {}

        for valute in root.findall('Valute'):
            try:
                currency_id = valute.get('ID')
                num_code = valute.find('NumCode').text
                char_code = valute.find('CharCode').text
                nominal = int(valute.find('Nominal').text)
                name = valute.find('Name').text
                value_str = valute.find('Value').text

                currency = Currency(
                    currency_id=currency_id,
                    num_code=num_code,
                    char_code=char_code,
                    name=name,
                    value=value_str,
                    nominal=nominal
                )

                currencies[currency.char_code] = currency

            except Exception as e:
                print(f"Ошибка при парсинге валюты: {e}")

        rub = Currency(
            currency_id="R00000", num_code="643", char_code="RUB",
            name="Российский рубль", value=1.0, nominal=1
        )
        currencies['RUB'] = rub

        return currencies

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return {}
    except ET.ParseError as e:
        print(f"Ошибка парсинга XML: {e}")
        return {}


if __name__ == '__main__':
    currencies_data = get_currencies()
    print(f"\nПолучено {len(currencies_data)} валют.")