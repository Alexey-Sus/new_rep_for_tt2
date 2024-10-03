import datetime
import json
import logging

import pandas as pd

file_middle: str = "../data/operations_11.xls"
file_long: str = "../data/operations.xls"

# Напишите функцию для анализа выгодности категорий повышенного кешбэка.
# На вход функции поступают данные для анализа, год и месяц.

# прописываем логгер
services_logger = logging.getLogger(__name__)
services_logger.setLevel(logging.INFO)
cons_handler = logging.StreamHandler()
services_logger.addHandler(cons_handler)

yr: int = 2021
mnth: int = 11


def get_best_cashbacks(file_name: str, year: int, month: int) -> str:
    """Функция на вход принимает название файла, год и месяц, за который нужно сделать расчет,
    и возвращает json-строку со словарем с категориями и суммами полученного кэшбэка по ним"""

    try:
        with open(file_name, "r"):
            excel_data = pd.read_excel(file_name)
            excel_data_dict: dict | list = excel_data.to_dict(orient="records")
            services_logger.info(
                "Начало работы функции по получению расходов по категориям и " "суммами полученного кэшбэка по ним"
            )
            services_logger.info("Читаем данные для составления словаря...")
            services_logger.info("...и выводим готовый словарь:")

    except FileNotFoundError as exp:
        services_logger.info(f"Ошибка; файл {file_name} не найден: {exp}")
        excel_data_dict = {}

    needed_date_start = datetime.datetime(year, month, 1)
    if month != 12:
        needed_date_end = datetime.datetime(year, month + 1, 1)
    else:
        needed_date_end = datetime.datetime(year + 1, 1, 1)

    # пишем цикл для составления списка тех транзакций, которые попадают в указанный нами месяц:

    if excel_data_dict != {}:
        list_trans_needed: list = []
        for i in excel_data_dict:
            str_aux: str = i["Дата операции"]
            str_aux_datetime = datetime.datetime.strptime(str_aux, "%d.%m.%Y %H:%M:%S")

            if needed_date_start < str_aux_datetime < needed_date_end:
                list_trans_needed.append(i)

        # отфильтруем из этого списка операции пополнения счета
        list_trans_filtered: list = []

        for i in list_trans_needed:
            if (
                "Пополнени" not in str(i.get("Категория"))
                and "Переводы" not in str(i.get("Категория"))
                and "Другое" not in str(i.get("Категория"))
                and "Бонусы" not in str(i.get("Категория"))
            ):
                list_trans_filtered.append(i)
            else:
                pass

        # составляем список уникальных названий категорий по транзакциям в месяце данном:
        list_trans_categ: list = []
        for i in list_trans_filtered:
            if i["Категория"] not in list_trans_categ:
                list_trans_categ.append(i["Категория"])
            else:
                pass

        # считаем кэшбэк по каждой категории и составляем словарик с таким этим кэшбэком
        dict_for_cashback: dict = {}
        for i in list_trans_categ:
            amnt_cashback: float = 0.0
            for j in list_trans_filtered:
                if j["Категория"] == i:
                    if "." not in str(j.get("Кэшбэк")):
                        # if j.get('Кэшбэк') == nan:
                        pass
                    else:
                        amnt_cashback += j.get("Кэшбэк")
            dict_for_cashback[i] = amnt_cashback

        # сортируем этот словарь по убыванию значений, чтобы потом уже составить готовый словарь из 3 категорий кэшбэка
        srted: list = sorted(dict_for_cashback.items(), key=lambda value: value[1], reverse=True)

        counter: int = 1
        dict_final: dict = {}
        for i in srted:
            dict_final[i[0]] = i[1]
            counter += 1
            if counter > 3:
                break

        for i in dict_final.keys():
            i.encode("utf-16")

        result: str = json.dumps(dict_final, ensure_ascii=False)

    else:
        services_logger.info("Завершение работы. Словарь не составлен - некорректные входные данные")
        return 'Словарь не составлен'

    return result


if __name__ == "__main__":
    print(get_best_cashbacks(file_long, yr, mnth))
