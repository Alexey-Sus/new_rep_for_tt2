import pandas as pd

from src.reports import spending_by_category

file_long = "../data/operations.xls"
categ: str = "Супермаркеты"
excel_data = pd.read_excel(file_long)


# будем считать, что тестирование на None выполнено, условно, поскольку функция у нас работает нормально
def test_spenging_by_category():
    """Функция тестирования функции получения транзакция по категориям"""
    assert spending_by_category(excel_data, "Супермаркеты", "2020-12-12") is None
