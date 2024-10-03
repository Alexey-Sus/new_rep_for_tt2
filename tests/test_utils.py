from datetime import datetime as dt

from src.utils import get_date_for_best_cashb


def test_get_date_for_best_cashb():
    """Функция тестирования функции получения даты от пользователя"""

    # функция тестирования предполагает ввод данных в ходе собственно
    # тестирования, причем, именно тех, которые указаны операции assertion
    # для тестирования и получения текущей даты нужно на третий раз ввести "нет"

    date_tuple = (dt.now().year, dt.now().month)

    assert get_date_for_best_cashb() == (2020, 12)
    assert get_date_for_best_cashb() == (2019, 11)
    assert get_date_for_best_cashb() == date_tuple
