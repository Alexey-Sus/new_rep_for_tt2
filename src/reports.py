import logging
from datetime import datetime as dt
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

# прописываем логгер
reports_logger = logging.getLogger(__name__)
reports_logger.setLevel(logging.INFO)
cons_handler = logging.StreamHandler()
reports_logger.addHandler(cons_handler)

file_long: str = "../data/operations.xls"
file_middle: str = "../data/operations_11.xls"
file_short: str = "../data/operations_three.xls"


def define_date_by_user() -> str:
    """Функция определения даты от пользователя, для использования в функции
    вывода суммы транзакций в файл. Для использования текущей даты пользователь
    вводит "нет" """
    day: str = input(
        "Введите день даты для функции вывода данных по категории в файл; только цифры\n"
        'и не более 2-х. Для текущей даты введите "нет": '
    )

    if day == "нет":
        curr_date = dt.now()

    else:
        if day.isdigit() is False or int(day) > 31:
            while True:
                day = input("Неверный ввод. Вводите только число," "от 1 до 31: ")
                if day.isdigit() and 0 < int(day) <= 31:
                    break

        month: str = input("Введите номер месяца, от 1 до 12: ")
        if month.isdigit() is False or int(month) > 12:
            while True:
                month = input("Неверный ввод. Вводите только цифры месяца, " "не более 2-х: ")
                if month.isdigit() and (0 < int(month) <= 12):
                    break

        year: str = input("Введите номер года, от 2018: ")
        if year.isdigit() is False or len(year) != 4 or int(year) <= 2017:
            while True:
                year = input("Неверный ввод. Только число больше " "2000, 4 цифры: ")
                if year.isdigit() and len(year) == 4 and int(year) >= 2018:
                    break

    if day != "нет":
        date: str = f"{year}-{month}-{day}"
        reports_logger.info(f"Ввод даты окончен; введена дата от пользователя {date}")
        return date
    else:
        date = dt.strftime(curr_date, format="%Y-%m-%d")
        reports_logger.info(f"Дата пользователем не введена; будет использована текущая дата {date}")
        return date


excel_data = pd.read_excel(file_long)

new_var = excel_data.to_dict(orient="records")
new_list: list = []

for dicts in new_var:
    if dicts.get("Категория") not in new_list:
        new_list.append(dicts.get("Категория"))

print("Для подсчета транзакций по категории введите категорию из следующего списка:")
print(new_list)

categ: str = str(input())

date_1: str = define_date_by_user()


# пишем сначала декоратор без параметров
def my_decorator_no_arg(func):
    """Декоратор для вызова функции записи данных в файл; без параметров.
    Этот декоратор только записывает данные в жестко заданный файл, который прописан
    в аргументах метода with open... as"""

    def inner_function(*args, **kwargs):
        try:
            with open("../data/file_for_data.txt", "w", encoding="utf-8") as text_file:

                result = func(excel_data, categ, date_1)
                text_file.write(str(result))

                reports_logger.info("Вызываем функцию без параметров внешнего декоратора...")
                reports_logger.info("Пишем вывод данных о транзакциях по категории в файл по умолчанию...")
                reports_logger.info(f"Запись в файл с именем по умолчанию " f"{text_file.name} произведена")

        except Exception as exp:
            reports_logger.warning(f"Записать в файл не удалось" f" ввиду ошибки: {exp}")
            print(f"Записать в файл не удалось ввиду ошибки: {exp}")
        reports_logger.info("Работа функции по записи в файл по умолчанию окончена\n" "")

        return result

    return inner_function


# пишем для этой функции декоратор с параметрами
def my_decorator_with_args(file_to_write):
    """Этот декоратор вызываем с заданным файлом в качестве аргумента.
    Результаты функции будут записаны в этот файл; файл можно менять по необходимости"""

    def my_decorator(func):

        def inner_function(*args, **kwargs):

            f = file_to_write

            try:

                with open(f, "w", encoding="utf-8") as text_file:

                    result = func(excel_data, categ, date_1)

                    text_file.write(str(result))

                    reports_logger.info(f"Вызываем функцию с записью в файл {f}, который задан в кач-ве аргумента")
                    reports_logger.info(
                        f"Выводим данные о транзакциях по категории в файл {f}, кот. задан как аргумент"
                    )
                    reports_logger.info(f"Запись в файл с именем {f} успешно произведена")

            except Exception as exp:
                reports_logger.warning(f"Данные в файл не записаны ввиду ошибки {exp}")
                print(f"Записать в файл не удалось ввиду ошибки: {exp}")

            reports_logger.info("Работа функции записи в файл в кач-ве аргумента окончена\n" "")
            return result

        return inner_function

    return my_decorator


# делаем вызов этих двух декораторов и функции
@my_decorator_no_arg
@my_decorator_with_args(file_to_write="../data/optional_file.txt")
# def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> str:
def spending_by_category(transactions: pd.DataFrame, category: str, date: str) -> str:
    """Функция для подсчета транзакций по данной категории за три прошедших месяца, начиная от
    поданной на вход даты"""
    excel_data_dict = transactions.to_dict(orient="records")

    if not date:
        # date: dt = dt.now()
        date = str(dt.now())

    try:

        date_original: dt = dt.strptime(date, "%Y-%m-%d")
        date_start = date_original + relativedelta(months=-3)

        amnt: float = 0.0
        for i in excel_data_dict:
            if (
                i["Категория"] == category
                and date_start <= dt.strptime(i["Дата операции"], "%d.%m.%Y %H:%M:%S") <= date_original
            ):
                amnt += float(i["Сумма операции"]) * (-1)

    except Exception as exp:

        return f"Дата некорректная введена {date}: {exp}"

    if amnt == 0.0:
        return f'За указанный период времени транзакций в категории "{category}" нет'

    else:
        return f'Сумма расходов по категории "{category}" в период с {date_start} по {date_original}: {round(amnt, 2)}'


if __name__ == "__main__":
    spending_by_category()
