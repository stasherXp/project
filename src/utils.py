"""
Вспомогательные функции: валидация, экспорт/импорт CSV/JSON, сортировка.
"""
import re
import csv
import json
from typing import List, Dict, Any, Callable, Optional


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Проверяет российский номер телефона.
    Должен содержать 11 цифр и начинаться с 7 или 8.
    """
    digits = re.sub(r"\D", "", phone)
    return len(digits) == 11 and digits[0] in ('7', '8')


def export_to_csv(data: List[Dict[str, Any]], filename: str, headers: List[str]):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        raise IOError(f"Ошибка записи CSV: {e}")


def import_from_csv(filename: str) -> List[Dict[str, Any]]:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        return []
    except Exception as e:
        raise IOError(f"Ошибка чтения CSV: {e}")


def export_to_json(data: List[Dict[str, Any]], filename: str):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        raise IOError(f"Ошибка записи JSON: {e}")


def import_from_json(filename: str) -> List[Dict[str, Any]]:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        raise IOError(f"Ошибка чтения JSON: {e}")


def quick_sort(arr: List[Dict], key_func: Callable, reverse: bool = False) -> List[Dict]:
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    left, right = [], []
    for item in arr[1:]:
        if reverse:
            if key_func(item) > key_func(pivot):
                left.append(item)
            else:
                right.append(item)
        else:
            if key_func(item) < key_func(pivot):
                left.append(item)
            else:
                right.append(item)
    return quick_sort(left, key_func, reverse) + [pivot] + quick_sort(right, key_func, reverse)


def sort_orders(orders: List[Dict], by: str = 'date', reverse: bool = False) -> List[Dict]:
    if by == 'date':
        key = lambda x: x.get('order_date', '')
    elif by == 'total':
        key = lambda x: float(x.get('total_price', 0))
    else:
        raise ValueError("by must be 'date' or 'total'")
    return quick_sort(orders, key, reverse)