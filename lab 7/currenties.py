import requests
import json
def get_currencies(currency_codes: list, url="https://www.cbr-xml-daily.ru/daily_json.js") -> dict:
    """
    Получает курсы валют с API Центробанка России.

    Args:
        currency_codes (list): Список символьных кодов валют (например, ['USD', 'EUR']).
    """
    if not isinstance(currency_codes, list):
        raise TypeError("currency_codes должен быть списком")

    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка статуса HTTP (4xx, 5xx)
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