"""
src/excel_db.py
Менеджер данных на основе Excel. Заменяет DatabaseManager.
"""

import os
from typing import List, Dict, Any
from src.xlsx_io import read_xlsx, write_xlsx
from src.models import Client, Product, Order

SHEETS = ["Clients", "Products", "Orders", "OrderItems"]
HEADERS = {
    "Clients": ["id", "name", "email", "phone", "registration_date"],
    "Products": ["id", "name", "price", "category"],
    "Orders": ["id", "client_id", "order_date", "total_price"],
    "OrderItems": ["order_id", "product_id", "quantity"],
}


class ExcelDatabaseManager:
    """Хранит все данные в Excel-файле (один файл, четыре листа)."""

    def __init__(self, filepath: str = "data/orders.xlsx") -> None:
        self.filepath = filepath
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        self._load()

    def _load(self) -> None:
        existed = os.path.exists(self.filepath)
        raw = read_xlsx(self.filepath) if existed else {}
        self.data = {}
        for sheet in SHEETS:
            rows = raw.get(sheet, [])
            if not rows or rows[0] != HEADERS[sheet]:
                self.data[sheet] = [HEADERS[sheet]]
            else:
                self.data[sheet] = rows
        if not existed:
            self._save()

    def _save(self) -> None:
        write_xlsx(self.filepath, self.data)

    def _next_id(self, sheet: str) -> int:
        m = 0
        for row in self.data[sheet][1:]:
            if row and row[0] is not None:
                try:
                    m = max(m, int(row[0]))
                except (ValueError, TypeError):
                    pass
        return m + 1

    # ----- Клиенты -----
    def add_client(self, client: Client) -> int:
        new_id = self._next_id("Clients")
        self.data["Clients"].append(
            [new_id, client.name, client.email, client.phone, client.registration_date]
        )
        self._save()
        return new_id

    def get_all_clients(self) -> List[Client]:
        res = []
        for row in self.data["Clients"][1:]:
            if row and row[0] is not None:
                res.append(Client(int(row[0]), row[1], row[2], row[3], row[4]))
        return res

    def delete_client(self, client_id: int) -> bool:
        self.data["Clients"] = [self.data["Clients"][0]] + [
            r for r in self.data["Clients"][1:] if r and r[0] != client_id
        ]
        order_ids = [r[0] for r in self.data["Orders"][1:] if r and r[1] == client_id]
        self.data["Orders"] = [self.data["Orders"][0]] + [
            r for r in self.data["Orders"][1:] if r and r[1] != client_id
        ]
        self.data["OrderItems"] = [self.data["OrderItems"][0]] + [
            r for r in self.data["OrderItems"][1:] if r and r[0] not in order_ids
        ]
        self._save()
        return True

    # ----- Товары -----
    def add_product(self, product: Product) -> int:
        new_id = self._next_id("Products")
        self.data["Products"].append([new_id, product.name, product.price, product.category])
        self._save()
        return new_id

    def get_all_products(self) -> List[Product]:
        res = []
        for row in self.data["Products"][1:]:
            if row and row[0] is not None:
                res.append(Product(int(row[0]), row[1], float(row[2]), row[3]))
        return res

    def delete_product(self, product_id: int) -> bool:
        self.data["Products"] = [self.data["Products"][0]] + [
            r for r in self.data["Products"][1:] if r and r[0] != product_id
        ]
        self.data["OrderItems"] = [self.data["OrderItems"][0]] + [
            r for r in self.data["OrderItems"][1:] if r and r[1] != product_id
        ]
        self._save()
        return True

    # ----- Заказы -----
    def add_order(self, order: Order, product_prices: Dict[int, float]) -> int:
        order.recalculate_total(product_prices)
        new_id = self._next_id("Orders")
        self.data["Orders"].append([new_id, order.client_id, order.order_date, order.total_price])
        for pid, qty in order.items:
            self.data["OrderItems"].append([new_id, pid, qty])
        self._save()
        return new_id

    def get_all_orders(self) -> List[Dict[str, Any]]:
        products = {p.id: p for p in self.get_all_products()}
        res = []
        for row in self.data["Orders"][1:]:
            if not row or row[0] is None:
                continue
            oid = int(row[0])
            items = []
            for ir in self.data["OrderItems"][1:]:
                if ir and ir[0] == oid:
                    pid, qty = int(ir[1]), int(ir[2])
                    prod = products.get(pid)
                    if prod:
                        items.append({
                            "product_id": pid,
                            "product_name": prod.name,
                            "quantity": qty,
                            "price": prod.price,
                        })
            res.append({
                "id": oid,
                "client_id": int(row[1]),
                "order_date": row[2],
                "total_price": float(row[3]),
                "items": items,
            })
        return res

    def delete_order(self, order_id: int) -> bool:
        self.data["Orders"] = [self.data["Orders"][0]] + [
            r for r in self.data["Orders"][1:] if r and r[0] != order_id
        ]
        self.data["OrderItems"] = [self.data["OrderItems"][0]] + [
            r for r in self.data["OrderItems"][1:] if r and r[0] != order_id
        ]
        self._save()
        return True

    def get_orders_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        return [o for o in self.get_all_orders() if start_date <= o["order_date"] <= end_date]

    def clear_all_data(self) -> None:
        for sheet in SHEETS:
            self.data[sheet] = [HEADERS[sheet]]
        self._save()

    def close(self) -> None:
        self._save()