import json
import logging
import os
from datetime import datetime as dt

from dotenv import load_dotenv

from src.reports import spending_by_category
from src.services import get_best_cashbacks
from src.utils import get_date_for_best_cashb
from src.views import get_curr_rates, get_stock_prices, get_user_settings, output_list, output_top5_trans

file_to_write: str = "../data/optional_file.txt"

load_dotenv()
KEY_API_exchrate: str = str(os.getenv("API_KEY_exchrate"))
KEY_API_alphvntg: str = str(os.getenv("API_KEY_alphvntg"))

main_logger = logging.getLogger(__name__)
main_logger.setLevel(logging.INFO)
cons_handler = logging.StreamHandler()
main_logger.addHandler(cons_handler)

# пишем блок определения времени суток (утро-день-вечер-ночь):
curr_tme = dt.now().time()

time_night = dt.strptime("00:00:01", "%H:%M:%S").time()
time_morning = dt.strptime("05:00:01", "%H:%M:%S").time()
time_day = dt.strptime("10:30:01", "%H:%M:%S").time()
time_evening = dt.strptime("19:30:01", "%H:%M:%S").time()
time_night_2 = dt.strptime("22:59:59", "%H:%M:%S").time()

if time_night < curr_tme < time_morning:
    greetings: str = "Спокойной ночи!"
elif time_morning < curr_tme < time_day:
    greetings = "Доброе утро"
elif time_day < curr_tme < time_evening:
    greetings = "Добрый день"
elif time_evening < curr_tme < time_night_2:
    greetings = "Добрый вечер"
else:
    greetings = "Спокойной ночи!"

# делаем вызов функции get_user_settings для получения пользовательских настроек
file_json: str = "../user_settings.json"
file_long: str = "../data/operations.xls"
file_middle: str = "../data/operations_11.xls"
file_short: str = "../data/operations_three.xls"

# получаем списки валют и акций из пользовательских настроек, для дальнейшего использования в
# функции вывода общего словарика данных JSON

user_currencies: list = get_user_settings(file_json)["user_currencies"]
user_stocks: list = get_user_settings(file_json)["user_stocks"]

# прописываем базовую, основную функцию, в которой будем составлять итоговый список словариков
# для этого получаем результаты всех других, маленьких, функций, для их ввода в основную функцию:


def main_logic(grts, rows_3, trans_5, curr_r, st_pr) -> str:
    """Функция компонует итоговый словарь для вывода в формате JSON, с учетом времени суток"""

    main_logger.info("Начинаю работу функции по выводу словарика JSON с данными")
    try:

        dict_output: dict = {
            "greetings": grts,
            "cards": rows_3,
            "top_transactions": trans_5,
            "currency_rates": curr_r,
            "stock_prices": st_pr,
        }
    except Exception:
        main_logger.warning("Something went wrong; an empty string has been returned:")
        return "Something went wrong so no dict has been returned"

    main_logger.info("Все входные данные получены; вывожу итоговый словарь JSON с данными:")
    result = json.dumps(dict_output, ensure_ascii=False)

    return result


# пишем блок ввода года и месяца от пользователя, с которого помощью будем передавать
# эти полученные значения в функцию для вычисления категорий кэшбэка get_best_cashbacks

print("Начинаем работу функции для подсчета выгодного кэшбэка.")
print("Для вычисления кэшбэка нужно будет ввести отчетные месяц и год.")

year_month: tuple = get_date_for_best_cashb()
year: int = year_month[0]
month: int = year_month[1]

# делаем вызов функции получения кэшбэков с полученными значениями месяца и года
if year and month:
    main_logger.info("Дата от пользователя получена, вызываем функцию подсчета кэшбэка...")

# функция записи значений расходов по категории вызывается здесь же, за счет импорта этих функций
# в main. Сама запись вызова функции приведена в модуле reports - том же модуле, где сама функция
# и декораторы к ней прописаны

if __name__ == "__main__":
    outpt_3rows: list = output_list(file_middle)  # рез-т  ф-ии со слов. по картам по 3 строчки
    top5_trans: list = output_top5_trans(file_middle)  # рез-т ф-ии с 5 макс. транзакциями
    curr_rates: list = get_curr_rates(user_currencies, KEY_API_exchrate)  # рез-т ф-ии с курсами валют
    stock_prices: list = get_stock_prices(user_stocks, KEY_API_alphvntg)  # рез-т ф-ии с ценами акций
    print(main_logic(greetings, outpt_3rows, top5_trans, curr_rates, stock_prices))
    print(get_best_cashbacks(file_long, year, month))
    print(spending_by_category())
