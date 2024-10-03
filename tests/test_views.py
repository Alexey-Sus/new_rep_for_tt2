import os
from unittest.mock import patch

from dotenv import load_dotenv

from src.views import get_curr_rates, get_stock_prices, get_user_settings, output_list, output_top5_trans

load_dotenv()
KEY_API_exchrate = os.getenv("API_KEY_exchrate")
KEY_API_alphvntg = os.getenv("API_KEY_alphvntg")

return_dict = {
    "result": "success",
    "documentation": "https://www.exchangerate-api.com/docs",
    "terms_of_use": "https://www.exchangerate-api.com/terms",
    "time_last_update_unix": 1720224001,
    "time_last_update_utc": "Sat, 06 Jul 2024 00:00:01 +0000",
    "time_next_update_unix": 1720310401,
    "time_next_update_utc": "Sun, 07 Jul 2024 00:00:01 +0000",
    "base_code": "EUR",
    "conversion_rates": {"EUR": 1, "RUB": 95.7741},
}

dict_for_stocks: dict = {
    "Global Quote": {
        "01. symbol": "TSLA",
        "02. open": "249.8100",
        "03. high": "252.3700",
        "04. low": "242.4601",
        "05. price": "251.5200",
        "06. volume": "154501152",
        "07. latest trading day": "2024-07-05",
        "08. previous close": "246.3900",
        "09. change": "5.1300",
        "10. change percent": "2.0821%",
    }
}

file_json: str = "../user_settings.json"
file_long: str = "../data/operations.xls"
file_middle: str = "../data/operations_11.xls"


# этот тест (что ниже) уже работает, все хорошо, все норм
def test_get_user_settings():
    """Функция проверки функции получения пользовательских настроек из файла"""
    assert get_user_settings(file_json) == {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"],
    }
    assert get_user_settings("../data/some_unknown_file.json") == {}


# этот тест тоже норм
def test_output_top5_trans():
    """Функция тестирования функции для вывода ТОП-5 транзакций по картам"""
    assert output_top5_trans(file_middle) == [
        {
            "date": "30.12.2021",
            "amount": 174000.0,
            "category": "Пополнения",
            "description": "Пополнение через Газпромбанк",
        },
        {
            "date": "22.12.2021",
            "amount": 28001.94,
            "category": "Переводы",
            "description": "Перевод Кредитная карта. ТП 10.2 RUR",
        },
        {
            "date": "22.12.2021",
            "amount": 28001.94,
            "category": "Переводы",
            "description": "Перевод Кредитная карта. ТП 10.2 RUR",
        },
        {"date": "30.12.2021", "amount": 20000.0, "category": "Переводы", "description": "Константин Л."},
        {"date": "23.12.2021", "amount": 20000.0, "category": "Другое", "description": "Иван С."},
    ]
    assert output_top5_trans("../data/some_unknown_file.xlsx") == []


def test_output_list():
    """Функция тестирования функции вывода словариков по картам"""
    assert output_list(file_long) == [
        {"last_digits": "7197", "total_spent": 401373.11, "cashback": 4013.73},
        {"last_digits": "5091", "total_spent": -5916.26, "cashback": -59.16},
        {"last_digits": "4556", "total_spent": -159636.6, "cashback": -1596.37},
        {"last_digits": "1112", "total_spent": -26000.0, "cashback": -260.0},
        {"last_digits": "5507", "total_spent": -0.0, "cashback": -0.0},
        {"last_digits": "6002", "total_spent": 35200.0, "cashback": 352.0},
        {"last_digits": "5441", "total_spent": 23755.12, "cashback": 237.55},
    ]
    assert output_list("../data/some_nonexistent_file.xlsx") == []


# тестируем функцию получения котировок валют. Здесь мокируем запрос к серверу и его ответ
@patch("requests.get")
def test_get_curr_rates(mock_get):
    """Функция тестирования функции получения котировок валют"""
    mock_response = return_dict
    mock_get.return_value.json.return_value = mock_response
    dict_output: dict = {}
    list_l: list = []

    dict_output["currency"] = mock_response["base_code"]
    dict_output["rate"] = mock_response["conversion_rates"]["RUB"]
    list_l.append(dict_output)

    assert get_curr_rates(["EUR"], KEY_API_exchrate) == list_l
    assert get_curr_rates([], "63839ed6d9261266d4a05a65") == []
    assert get_curr_rates(None, "63839ed6d9261266d4a05a65") == []


# теперь тестируем функцию получения курсов акций, на примере, например, акций TSLA
@patch("requests.get")
def test_get_stock_prices(mock_get):
    """Функция тестирования функции получения котировок валют"""
    mock_response = dict_for_stocks
    mock_get.return_value.json.return_value = mock_response
    dict_output: dict = {}
    list_l: list = []

    dict_output["stock"] = mock_response["Global Quote"]["01. symbol"]
    dict_output["price"] = float(mock_response["Global Quote"]["05. price"])
    list_l.append(dict_output)

    assert get_stock_prices(["TSLA"], KEY_API_alphvntg) == list_l
    assert get_stock_prices([], "CGTNI2F0NXU0M0FX") == []
    assert get_stock_prices(None, "CGTNI2F0NXU0M0FX") == []
