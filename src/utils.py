# src/utils.py

import re
import csv
import json
from datetime import datetime
from tkinter import messagebox

# ---------- Отладочный флаг ----------
DEBUG = True

def debug_print(*args, **kwargs):
    if DEBUG:
        print("[DEBUG]", *args, **kwargs)


# ---------- Регулярные выражения ----------
def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    digits = re.sub(r'\D', '', phone)
    return len(digits) in (10, 11) and digits.startswith(('7', '8'))


# ---------- Экспорт в CSV ----------
def export_to_csv(data: list, filename: str, headers: list = None) -> bool:
    debug_print(f"export_to_csv called with filename={filename}, data length={len(data) if data else 0}")
    try:
        if not data:
            raise ValueError("Нет данных для экспорта")
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = headers or data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        debug_print("export_to_csv success")
        return True
    except Exception as e:
        debug_print(f"export_to_csv error: {e}")
        messagebox.showerror("Ошибка экспорта CSV", str(e))
        return False


# ---------- Импорт из CSV ----------
def import_from_csv(filename: str) -> list | None:
    debug_print(f"import_from_csv called with filename={filename}")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            debug_print(f"import_from_csv read {len(data)} rows")
            return data
    except FileNotFoundError:
        debug_print("import_from_csv: FileNotFoundError")
        messagebox.showerror("Ошибка", f"Файл не найден: {filename}")
        return None
    except Exception as e:
        debug_print(f"import_from_csv error: {e}")
        messagebox.showerror("Ошибка импорта CSV", str(e))
        return None


# ---------- Импорт из JSON (только чтение) ----------
def import_from_json(filepath: str) -> dict | None:
    debug_print(f"import_from_json called with filepath={filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        debug_print(f"import_from_json: successfully loaded JSON, keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
        return data
    except FileNotFoundError:
        debug_print("import_from_json: FileNotFoundError")
        messagebox.showerror("Ошибка", f"Файл не найден: {filepath}")
        return None
    except json.JSONDecodeError as e:
        debug_print(f"import_from_json: JSONDecodeError: {e}")
        messagebox.showerror("Ошибка формата JSON", str(e))
        return None
    except Exception as e:
        debug_print(f"import_from_json: unexpected error: {e}")
        messagebox.showerror("Ошибка чтения файла", str(e))
        return None


# ---------- Экспорт в JSON ----------
def export_to_json(data: dict | list, filename: str) -> bool:
    debug_print(f"export_to_json called with filename={filename}, data type={type(data)}")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        debug_print("export_to_json success")
        return True
    except Exception as e:
        debug_print(f"export_to_json error: {e}")
        messagebox.showerror("Ошибка экспорта JSON", str(e))
        return False


# ---------- Собственная сортировка заказов ----------
def sort_orders(orders: list, key_func, reverse: bool = False) -> list:
    debug_print(f"sort_orders called with {len(orders)} orders, reverse={reverse}")
    if len(orders) <= 1:
        return orders
    pivot = orders[0]
    left = [x for x in orders[1:] if key_func(x) <= key_func(pivot)]
    right = [x for x in orders[1:] if key_func(x) > key_func(pivot)]
    if reverse:
        return sort_orders(right, key_func, reverse) + [pivot] + sort_orders(left, key_func, reverse)
    else:
        return sort_orders(left, key_func, reverse) + [pivot] + sort_orders(right, key_func, reverse)