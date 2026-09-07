"""
src/utils.py

Модуль вспомогательных утилит для проекта:
- Валидация email и телефона с помощью регулярных выражений.
- Экспорт и импорт данных в форматы CSV и JSON.
- Собственная реализация сортировки заказов (быстрая сортировка) с поддержкой лямбда-ключей.
- Прочие вспомогательные функции.
"""

import csv
import json
import re
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime


# ------------------- Регулярные выражения -------------------

def validate_email(email: str) -> bool:
    """
    Проверяет корректность email-адреса с помощью регулярного выражения.

    Parameters
    ----------
    email : str
        Адрес электронной почты.

    Returns
    -------
    bool
        True, если email соответствует формату, иначе False.

    Examples
    --------
    >>> validate_email("user@example.com")
    True
    >>> validate_email("invalid-email")
    False
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Проверяет корректность номера телефона.
    Допустимые форматы:
    - +7 999 123-45-67
    - 8-999-123-45-67
    - +7 (999) 123-45-67
    - 9991234567 (10 цифр)
    - и другие вариации с разделителями.

    Parameters
    ----------
    phone : str
        Строка с номером телефона.

    Returns
    -------
    bool
        True, если номер соответствует одному из шаблонов.
    """
    # Удаляем все нецифровые символы, оставляем только цифры и знак '+'
    cleaned = re.sub(r"[^\d+]", "", phone)
    # Проверяем, что номер содержит 10-15 цифр и начинается с '+' или цифры
    # Допустим: +7XXXXXXXXXX, 8XXXXXXXXXX, XXXXXXXXXX (10 цифр)
    if re.match(r"^\+?\d{10,15}$", cleaned):
        # Проверяем, что если есть '+', то после него не более 15 цифр
        return True
    # Дополнительно можно проверить наличие скобок и дефисов, но упростим
    # Возвращаем True, если после очистки получилось 10-15 цифр
    return False


# ------------------- Экспорт и импорт -------------------

def export_to_csv(data: List[Dict[str, Any]], filename: str) -> None:
    """
    Экспортирует список словарей в CSV-файл.

    Parameters
    ----------
    data : List[Dict[str, Any]]
        Список записей для экспорта.
    filename : str
        Путь к выходному CSV-файлу.

    Raises
    ------
    IOError
        При ошибке записи файла.
    """
    if not data:
        # Если данных нет, создаём пустой файл с заголовками (по первому словарю)
        # Но лучше просто записать пустой файл
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([])  # пустая строка
        return

    try:
        # Заголовки берём из ключей первого словаря
        fieldnames = list(data[0].keys())
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    except IOError as e:
        raise IOError(f"Ошибка записи CSV-файла: {e}")


def import_from_csv(filename: str) -> List[Dict[str, Any]]:
    """
    Импортирует данные из CSV-файла в список словарей.

    Parameters
    ----------
    filename : str
        Путь к CSV-файлу.

    Returns
    -------
    List[Dict[str, Any]]
        Список записей.

    Raises
    ------
    FileNotFoundError
        Если файл не найден.
    IOError
        При ошибке чтения.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return [row for row in reader]
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл {filename} не найден.")
    except IOError as e:
        raise IOError(f"Ошибка чтения CSV-файла: {e}")


def export_to_json(data: List[Dict[str, Any]], filename: str, indent: int = 4) -> None:
    """
    Экспортирует список словарей в JSON-файл.

    Parameters
    ----------
    data : List[Dict[str, Any]]
        Данные для экспорта.
    filename : str
        Путь к JSON-файлу.
    indent : int, optional
        Отступ для форматирования (по умолчанию 4).
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
    except IOError as e:
        raise IOError(f"Ошибка записи JSON-файла: {e}")


def import_from_json(filename: str) -> List[Dict[str, Any]]:
    """
    Импортирует данные из JSON-файла.

    Parameters
    ----------
    filename : str
        Путь к JSON-файлу.

    Returns
    -------
    List[Dict[str, Any]]
        Данные из файла.

    Raises
    ------
    FileNotFoundError
        Если файл не найден.
    json.JSONDecodeError
        При ошибке парсинга JSON.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл {filename} не найден.")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Ошибка парсинга JSON: {e}", e.doc, e.pos)


# ------------------- Собственная сортировка (быстрая сортировка) -------------------

def quicksort(
    arr: List[Any],
    key: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False
) -> List[Any]:
    """
    Реализация быстрой сортировки (рекурсивная) с поддержкой ключа сортировки.

    Parameters
    ----------
    arr : List[Any]
        Список для сортировки.
    key : Optional[Callable], default=None
        Функция, возвращающая значение для сравнения (аналогично sorted).
    reverse : bool, default=False
        Если True, сортировка по убыванию.

    Returns
    -------
    List[Any]
        Отсортированный список (создаётся новый).

    Examples
    --------
    >>> quicksort([3, 1, 2])
    [1, 2, 3]
    >>> quicksort([(1, 'b'), (2, 'a')], key=lambda x: x[1])
    [(2, 'a'), (1, 'b')]
    """
    if len(arr) <= 1:
        return arr[:]  # возвращаем копию

    pivot = arr[0]
    left = []
    right = []
    equal = [pivot]

    # Определяем функцию сравнения
    def get_value(item):
        return key(item) if key is not None else item

    pivot_val = get_value(pivot)

    for item in arr[1:]:
        item_val = get_value(item)
        if item_val < pivot_val:
            left.append(item)
        elif item_val > pivot_val:
            right.append(item)
        else:
            equal.append(item)

    # Рекурсивно сортируем левую и правую части
    sorted_left = quicksort(left, key, reverse)
    sorted_right = quicksort(right, key, reverse)

    # Объединяем с учётом reverse
    if reverse:
        return sorted_right + equal + sorted_left
    else:
        return sorted_left + equal + sorted_right


def sort_orders(
    orders: List[Dict[str, Any]],
    sort_by: str = "order_date",
    reverse: bool = False
) -> List[Dict[str, Any]]:
    """
    Сортирует заказы по указанному полю с использованием собственной сортировки.

    Parameters
    ----------
    orders : List[Dict[str, Any]]
        Список заказов (каждый заказ – словарь с ключами).
    sort_by : str, optional
        Имя поля для сортировки (по умолчанию "order_date").
        Допустимые значения: "order_date", "total_price", "id".
    reverse : bool, optional
        По убыванию, если True.

    Returns
    -------
    List[Dict[str, Any]]
        Отсортированный список заказов.

    Raises
    ------
    ValueError
        Если указано недопустимое поле.
    """
    allowed_fields = {"order_date", "total_price", "id"}
    if sort_by not in allowed_fields:
        raise ValueError(f"Недопустимое поле для сортировки: {sort_by}. "
                         f"Допустимые: {allowed_fields}")

    # Определяем ключевую функцию: извлекаем значение из словаря
    key_func = lambda order: order.get(sort_by)

    # Используем нашу быструю сортировку
    return quicksort(orders, key=key_func, reverse=reverse)


# ------------------- Дополнительные утилиты -------------------

def convert_date_format(date_str: str, from_format: str = "%Y-%m-%d",
                        to_format: str = "%d.%m.%Y") -> str:
    """
    Преобразует строку даты из одного формата в другой.

    Parameters
    ----------
    date_str : str
        Строка с датой.
    from_format : str
        Текущий формат (по умолчанию YYYY-MM-DD).
    to_format : str
        Желаемый формат (по умолчанию DD.MM.YYYY).

    Returns
    -------
    str
        Преобразованная строка даты.
    """
    try:
        dt = datetime.strptime(date_str, from_format)
        return dt.strftime(to_format)
    except ValueError:
        # Если не удалось распарсить, возвращаем исходную строку
        return date_str
