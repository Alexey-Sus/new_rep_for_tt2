import json

from src.services import get_best_cashbacks

file_long: str = "../data/operations.xls"
yr: int = 2021
mnth: int = 11


def test_get_best_cashbacks():
    """Функция тестирования функции получения макс. кэшбэка по трем категориям"""
    assert get_best_cashbacks(file_long, yr, mnth) == json.dumps(
        ({"Супермаркеты": 570.0, "Аптеки": 175.0, "Дом и ремонт": 52.0}), ensure_ascii=False
    )
    assert get_best_cashbacks("../data/some_nonexistent_file.xlsx", yr, mnth) == {}
