from datetime import datetime


# пишем функцию ввода данных от пользователя для подачи выходных данных в функцию
# подсчета выгодного кэшбэка get_best_cashbacks


def get_date_for_best_cashb() -> tuple:
    """Функция ввода даты от пользователя для расчета выгодного кэшбэка по категориям"""

    year: str = input(
        "Введите год отчетного месяца для подсчета кэшбэка по категориям."
        "Вводите только четыре цифры. Для использования "
        'текущей даты введите "нет": '
    )
    if year == "нет":
        current_date = datetime.now().strftime("%Y-%m-%d")

    else:
        if not year.isdigit() or len(year) != 4:
            while True:
                year = input("Вы ввели некорректное значение. Вводите только 4 цифры года: ")
                if year.isdigit() and len(year) == 4:
                    # year = int(year)
                    break
        else:
            # year = int(year)
            pass

        month_m: str = str(input("Введите отчетный месяц. Вводите только месяц в имен. падеже или число от 1 до 12: "))
        list_month: list = [
            "январь",
            "февраль",
            "март",
            "апрель",
            "май",
            "июнь",
            "июль",
            "август",
            "сентябрь",
            "октябрь",
            "ноябрь",
            "декабрь",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
        ]

        if month_m not in list_month:
            while True:
                month_m = input("Неправильный ввод. Вводите только месяц в имен. падеже ИЛИ число от 1 до 12: ")
                if month_m in list_month:
                    break

        list_month_str: list = [
            "январь",
            "февраль",
            "март",
            "апрель",
            "май",
            "июнь",
            "июль",
            "август",
            "сентябрь",
            "октябрь",
            "ноябрь",
            "декабрь",
        ]

        if month_m in list_month_str:
            # month: int = list_month_str.index(month_m) + 1
            month = str(list_month_str.index(month_m) + 1)
        else:
            # month = int(month_m)
            month = str(month_m)

    if year == "нет":
        # year = int(current_date[0:4])
        year = current_date[0:4]
        # month = int(current_date[5:7])
        month = current_date[5:7]
    else:
        pass

    return int(year), int(month)


if __name__ == '__main__':
    print(get_date_for_best_cashb())
