import json
import logging
import os
import os.path
from datetime import datetime as dt

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
KEY_API_exchrate: str = str(os.getenv("API_KEY_exchrate"))
KEY_API_alphvntg: str = str(os.getenv("API_KEY_alphvntg"))

file_long: str = "../data/operations.xls"
file_middle: str = "../data/operations_11.xls"
file_short: str = "../data/operations_three.xls"
file_json: str = "../user_settings.json"

# прописываем логгер
views_logger = logging.getLogger(__name__)
views_logger.setLevel(logging.INFO)
cons_handler = logging.StreamHandler()
views_logger.addHandler(cons_handler)


# пишем функцию для получения списка всех пользовательских настроек - его валют и акций из файла
# user_settings.json. Возвращать будем словарик вида {'currencies': list_of_curr, 'stocks': list_of_stocks}


def get_user_settings(file_name: str) -> dict:
    """Функция получения словаря пользовательских настройек вида
    {'currencies': [list_of_curr], 'stocks': [list_of_stocks]} из соотв-го json-файла"""

    if os.path.isfile(file_name):
        with open(file_name, "r") as file:
            new_dict: dict = json.load(file)
    else:
        new_dict = {}
        views_logger.warning(f"Такой файл {file_name} не найден")

    return new_dict


# в случае отсутствия файла возвращается пустой словарь {}
user_currencies: list = get_user_settings(file_json)['user_currencies']
user_stocks: list = get_user_settings(file_json)['user_stocks']


# print(get_user_settings(file_json))


# пишем функцию для получения списка уникальных словариков (по 3 строчки по каждой карте)
def output_list(file_name: str) -> list:
    """Функция для вывода списка словариков по картам; каждый словарик - это 3 строчки"""

    if os.path.isfile(file_name):
        excel_data = pd.read_excel(file_name, engine="calamine")
        excel_data_dict = excel_data.to_dict(orient="records")

        # cоздаем список уникальных номеров карт, чтобы по этому списку дальше работать:
        list_card_number: list = []
        for i in excel_data_dict:
            if i["Номер карты"] not in list_card_number:
                if str(i["Номер карты"]).startswith("*"):
                    list_card_number.append(i["Номер карты"])
            else:
                pass

        # делаем прогон по каждой карте из списка и составляем для нее словарик из last_digits, total_spent и кэшбэка
        list_for_card: list = []
        for j in list_card_number:
            last_digits: str = j[1:5]
            total_spent_card: float = 0.0

            for i in excel_data_dict:
                if float(i["Сумма операции"]) < 0 and i["Номер карты"] == j:
                    total_spent_card += float(i["Сумма операции"])

                if total_spent_card < 0:
                    total_spent_card = round((total_spent_card * (-1)), 2)
                else:
                    total_spent_card = round(total_spent_card, 2)

                cashback: float = round((total_spent_card / 100), 2)

                dict_for_card: dict = {
                    "last_digits": last_digits,
                    "total_spent": total_spent_card,
                    "cashback": cashback,
                }

            list_for_card.append(dict_for_card)

    else:
        views_logger.warning("Файл не найден; возвращаю пустой список")
        list_for_card = []

    return list_for_card


# эта функция (по выводу словариков с данными по расходам по карте) работает хорошо

# пишем функцию для получения ТОП-5 списка транзакций по максимальной сумме транзакций

def output_top5_trans(file_name: str) -> list:
    """Функция для получения ТОП-5 списка транзакций из всей выборки"""

    if os.path.isfile(file_name):
        with open(file_name, "r"):
            excel_data = pd.read_excel(file_name)
            excel_data_dict = excel_data.to_dict(orient="records")

        # делаем сначала словарь со всеми положительными расходами. Приводим все отрицательные расходы к положительным

        for i in excel_data_dict:
            if float(i["Сумма операции"]) < 0:
                i["Сумма операции"] = float(i["Сумма операции"]) * (-1)
            else:
                pass

        # с помощью лямбда-функции:
        af: list = sorted(excel_data_dict, key=lambda n: n["Сумма операции"], reverse=True)

        # теперь делаем цикл и составляем уже выходной список
        list_for_card: list = []
        j: int = 0

        while j < 5:
            dict_for_card = {}

            # преобразуем дату и время в дату нужного формата, как по задани, с помощью datetime
            time_trans: dt = dt.strptime(af[j]["Дата операции"], "%d.%m.%Y %H:%M:%S")
            time_for_dict: str = time_trans.strftime("%d.%m.%Y")

            dict_for_card["date"] = time_for_dict
            dict_for_card["amount"] = af[j]["Сумма операции"]
            dict_for_card["category"] = af[j]["Категория"]
            dict_for_card["description"] = af[j]["Описание"]
            list_for_card.append(dict_for_card)
            j += 1

    else:
        views_logger.warning("Файл не найден; вывожу пустой список:")
        list_for_card = []

    return list_for_card


# пишем функцию для запроса данных с курсом валют по API и вывода его в виде словарика


def get_curr_rates(curr_list: list, api_key: str) -> list:
    """Функция возвращает курсы по отношению к рублю тех валют, которые заданы в файле user_settings.json.
    Обращается к стороннему API и от него получает нужные URL-ы с котировками"""

    if curr_list:
        views_logger.info("Входные данные котировок валют валидны; включаю их в список")
        list_for_curr: list = []
        list_output: list = []
        dict_for_curr: dict = {}

        for i in curr_list:
            url_frmtted = "https://v6.exchangerate-api.com/v6/" + api_key + "/latest/" + i
            r = requests.get(url_frmtted)
            data = r.json()
            list_for_curr.append(data)

        # теперь составляем словарьеГКГ с курсами валют в нужном формате, как требуется по заданию:
        # сначала дергаем API-шку и просто составляем списочеГКГ котировок
        for i in list_for_curr:
            dict_for_curr = {}
            dict_for_curr["currency"] = str(i["base_code"])
            dict_for_curr["rate"] = float(i["conversion_rates"]["RUB"])
            list_output.append(dict_for_curr)

    else:
        views_logger.warning("Данные невалидны; вывожу список пустой на экран:")
        list_output = []

    return list_output


# пишем функцию для получения списка котировок акций. Функция потом будет вызываться в main

def get_stock_prices(stock_list: list, api_key: str) -> list:
    """Функция обращается к стороннему сервису API и получает из него котировки акций, после
    чего возвращает словарик вида {'stock': 'stock_name', 'price': stock_price}"""

    if stock_list:

        list_for_stocks: list = []
        lst_stck: list = []

        url_frmtted = ("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + stock_list[0] + "&apikey="
                       + api_key)
        r = requests.get(url_frmtted)
        data = r.json()
        if len(data) == 1:
            # print('The API service refused to give stock prices, an empty list has been returned')
            return ['No stock prices due to invalid API response']

        else:
            views_logger.info("Котировки акций присутствуют; включаю их в список")
            for i in stock_list:
                url_frmtted = ("https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=" + i + "&apikey=" +
                               api_key)
                r = requests.get(url_frmtted)
                data = r.json()
                list_for_stocks.append(data)

            # теперь так же, как в функции выше (где про котировки валют)

            for i in list_for_stocks:
                dict_for_stock = {"stock": str(i["Global Quote"]["01. symbol"]),
                                  "price": float(i["Global Quote"]["05. price"])}

                lst_stck.append(dict_for_stock)

            return lst_stck

    else:
        views_logger.info("На вход поданы невалидные данные; вывожу пустой список котировок акций")
        return []


if __name__ == '__main__':
    list_stocks = get_user_settings(file_json)['user_stocks']
    print(get_stock_prices(user_stocks, KEY_API_alphvntg))
    print(output_list(file_long))
    print(output_top5_trans(file_middle))
    print(get_curr_rates(user_currencies, KEY_API_exchrate))
