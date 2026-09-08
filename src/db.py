"""
src/db.py

Модуль для работы с базой данных SQLite.
Содержит класс DatabaseManager, реализующий CRUD-операции
для клиентов, товаров и заказов.
"""

import sqlite3
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from src.models import Client, Product, Order


class DatabaseManager:
    """
    Менеджер подключения и операций с базой данных SQLite.

    Attributes
    ----------
    db_path : str
        Путь к файлу базы данных.
    connection : sqlite3.Connection
        Объект соединения с БД.
    cursor : sqlite3.Cursor
        Курсор для выполнения запросов.
    """
    def __init__(self, db_path: str = "data/orders.db") -> None:
        """
        Инициализирует менеджер, создаёт подключение и таблицы.

        Parameters
        ----------
        db_path : str, optional
            Путь к файлу БД (по умолчанию "data/orders.db").
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _connect(self) -> None:
        """Устанавливает соединение с БД и создаёт курсор."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # для доступа по именам столбцов
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка подключения к БД: {e}")

    def _create_tables(self) -> None:
        """
        Создаёт таблицы, если они ещё не существуют.
        Таблицы: clients, products, orders, order_items.
        """
        try:
            self.cursor.executescript("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL,
                    registration_date TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    category TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    order_date TEXT NOT NULL,
                    total_price REAL NOT NULL DEFAULT 0,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                );
            """)
            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка создания таблиц: {e}")

    def close(self) -> None:
        """Закрывает соединение с БД."""
        if self.connection:
            self.connection.close()

    # ------------------- Клиенты -------------------

    def add_client(self, client: Client) -> int:
        """
        Добавляет клиента в БД.

        Parameters
        ----------
        client : Client
            Объект клиента (без id, он будет присвоен автоматически).

        Returns
        -------
        int
            ID добавленного клиента.

        Raises
        ------
        ValueError
            Если email уже существует.
        RuntimeError
            При ошибке БД.
        """
        try:
            self.cursor.execute(
                """
                INSERT INTO clients (name, email, phone, registration_date)
                VALUES (?, ?, ?, ?)
                """,
                (client.name, client.email, client.phone, client.registration_date)
            )
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"Клиент с email '{client.email}' уже существует.")
        except sqlite3.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка добавления клиента: {e}")

    def get_client(self, client_id: int) -> Optional[Client]:
        """
        Возвращает клиента по ID.

        Parameters
        ----------
        client_id : int

        Returns
        -------
        Optional[Client]
            Объект Client или None, если не найден.
        """
        try:
            row = self.cursor.execute(
                "SELECT * FROM clients WHERE id = ?", (client_id,)
            ).fetchone()
            if row:
                return Client(
                    client_id=row["id"],
                    name=row["name"],
                    email=row["email"],
                    phone=row["phone"],
                    registration_date=row["registration_date"]
                )
            return None
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка получения клиента: {e}")

    def get_all_clients(self) -> List[Client]:
        """Возвращает список всех клиентов."""
        try:
            rows = self.cursor.execute("SELECT * FROM clients ORDER BY id").fetchall()
            return [
                Client(
                    client_id=row["id"],
                    name=row["name"],
                    email=row["email"],
                    phone=row["phone"],
                    registration_date=row["registration_date"]
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка получения списка клиентов: {e}")

    def update_client(self, client: Client) -> None:
        """
        Обновляет данные клиента.

        Parameters
        ----------
        client : Client
            Объект клиента с уже заполненным id.
        """
        try:
            self.cursor.execute(
                """
                UPDATE clients
                SET name = ?, email = ?, phone = ?, registration_date = ?
                WHERE id = ?
                """,
                (client.name, client.email, client.phone,
                 client.registration_date, client.id)
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Клиент с email '{client.email}' уже существует.")
        except sqlite3.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка обновления клиента: {e}")

    def delete_client(self, client_id: int) -> bool:
        """
        Удаляет клиента по ID.

        Returns
        -------
        bool
            True, если запись удалена, иначе False.
        """
        try:
            self.cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка удаления клиента: {e}")

    # ------------------- Товары -------------------
    def clear_all_data(self) -> None:
        """
        Удаляет все записи из всех таблиц и сбрасывает автоинкремент.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute("DELETE FROM order_items;")
            cursor.execute("DELETE FROM orders;")
            cursor.execute("DELETE FROM products;")
            cursor.execute("DELETE FROM clients;")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='clients';")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='products';")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='orders';")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='order_items';")
            cursor.execute("PRAGMA foreign_keys = ON;")
            self.connection.commit()
            print("[DEBUG] Все данные очищены")
        except Exception as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка при очистке данных: {e}")
    def add_product(self, product: Product) -> int:
        """Добавляет товар."""
        try:
            self.cursor.execute(
                "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
                (product.name, product.price, product.category)
            )
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка добавления товара: {e}")

    def get_product(self, product_id: int) -> Optional[Product]:
        """Возвращает товар по ID."""
        try:
            row = self.cursor.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            ).fetchone()
            if row:
                return Product(
                    product_id=row["id"],
                    name=row["name"],
                    price=row["price"],
                    category=row["category"]
                )
            return None
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка получения товара: {e}")

    def get_all_products(self) -> List[Product]:
        """Возвращает список всех товаров."""
        try:
            rows = self.cursor.execute("SELECT * FROM products ORDER BY id").fetchall()
            return [
                Product(
                    product_id=row["id"],
                    name=row["name"],
                    price=row["price"],
                    category=row["category"]
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка получения списка товаров: {e}")

    def update_product(self, product: Product) -> None:
        """Обновляет товар."""
        try:
            self.cursor.execute(
                "UPDATE products SET name = ?, price = ?, category = ? WHERE id = ?",
                (product.name, product.price, product.category, product.id)
            )
            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка обновления товара: {e}")

    def delete_product(self, product_id: int) -> bool:
        """Удаляет товар."""
        try:
            self.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка удаления товара: {e}")

    # ------------------- Заказы -------------------

    def add_order(self, order: Order, product_prices: Dict[int, float]) -> int:
        """
        Добавляет заказ и связанные позиции.

        Parameters
        ----------
        order : Order
            Объект заказа (без id). Должен содержать client_id и items.
        product_prices : Dict[int, float]
            Словарь цен товаров для пересчёта общей стоимости.

        Returns
        -------
        int
            ID созданного заказа.

        Raises
        ------
        ValueError
            Если клиент не существует или товар не найден.
        RuntimeError
            При ошибке БД.
        """
        try:
            # Проверяем существование клиента
            client_check = self.cursor.execute(
                "SELECT id FROM clients WHERE id = ?", (order.client_id,)
            ).fetchone()
            if not client_check:
                raise ValueError(f"Клиент с ID {order.client_id} не найден.")

            # Пересчитываем общую стоимость
            order.recalculate_total(product_prices)

            # Вставляем заказ
            self.cursor.execute(
                """
                INSERT INTO orders (client_id, order_date, total_price)
                VALUES (?, ?, ?)
                """,
                (order.client_id, order.order_date, order.total_price)
            )
            order_id = self.cursor.lastrowid

            # Вставляем позиции заказа
            for product_id, quantity in order.items:
                # Проверяем существование товара
                product_check = self.cursor.execute(
                    "SELECT id FROM products WHERE id = ?", (product_id,)
                ).fetchone()
                if not product_check:
                    raise ValueError(f"Товар с ID {product_id} не найден.")
                self.cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
                    (order_id, product_id, quantity)
                )

            self.connection.commit()
            return order_id
        except (ValueError, sqlite3.Error) as e:
            self.connection.rollback()
            if isinstance(e, ValueError):
                raise
            raise RuntimeError(f"Ошибка добавления заказа: {e}")

    def get_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        """
        Возвращает заказ с его позициями в виде словаря.

        Returns
        -------
        Optional[Dict]
            Содержит ключи: id, client_id, order_date, total_price, items (список позиций).
            items: список словарей с product_id, product_name, quantity, price.
        """
        try:
            # Получаем основную информацию о заказе
            order_row = self.cursor.execute(
                "SELECT * FROM orders WHERE id = ?", (order_id,)
            ).fetchone()
            if not order_row:
                return None

            # Получаем позиции заказа с названиями и ценами товаров
            items_rows = self.cursor.execute(
                """
                SELECT oi.product_id, p.name AS product_name, oi.quantity, p.price
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = ?
                """,
                (order_id,)
            ).fetchall()

            items = [
                {
                    "product_id": row["product_id"],
                    "product_name": row["product_name"],
                    "quantity": row["quantity"],
                    "price": row["price"]
                }
                for row in items_rows
            ]

            return {
                "id": order_row["id"],
                "client_id": order_row["client_id"],
                "order_date": order_row["order_date"],
                "total_price": order_row["total_price"],
                "items": items
            }
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка получения заказа: {e}")

    def get_all_orders(self) -> List[Dict[str, Any]]:
        """
        Возвращает список всех заказов с их позициями.
        """
        try:
            # Получаем все заказы
            orders_rows = self.cursor.execute(
                "SELECT * FROM orders ORDER BY id"
            ).fetchall()
            orders = []
            for order_row in orders_rows:
                order_id = order_row["id"]
                # Получаем позиции для каждого заказа
                items_rows = self.cursor.execute(
                    """
                    SELECT oi.product_id, p.name AS product_name, oi.quantity, p.price
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.id
                    WHERE oi.order_id = ?
                    """,
                    (order_id,)
                ).fetchall()
                items = [
                    {
                        "product_id": row["product_id"],
                        "product_name": row["product_name"],
                        "quantity": row["quantity"],
                        "price": row["price"]
                    }
                    for row in items_rows
                ]
                orders.append({
                    "id": order_row["id"],
                    "client_id": order_row["client_id"],
                    "order_date": order_row["order_date"],
                    "total_price": order_row["total_price"],
                    "items": items
                })
            return orders
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка получения списка заказов: {e}")

    def delete_order(self, order_id: int) -> bool:
        """Удаляет заказ (каскадно удаляются позиции)."""
        try:
            self.cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка удаления заказа: {e}")

    # ------------------- Дополнительные методы -------------------

    def get_clients_by_name(self, name_part: str) -> List[Client]:
        """Поиск клиентов по части имени."""
        try:
            rows = self.cursor.execute(
                "SELECT * FROM clients WHERE name LIKE ? ORDER BY id",
                (f"%{name_part}%",)
            ).fetchall()
            return [
                Client(
                    client_id=row["id"],
                    name=row["name"],
                    email=row["email"],
                    phone=row["phone"],
                    registration_date=row["registration_date"]
                )
                for row in rows
            ]
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка поиска клиентов: {e}")

    def get_orders_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Возвращает заказы в заданном диапазоне дат."""
        try:
            rows = self.cursor.execute(
                "SELECT * FROM orders WHERE order_date BETWEEN ? AND ? ORDER BY order_date",
                (start_date, end_date)
            ).fetchall()
            orders = []
            for row in rows:
                # можно подгрузить позиции, но для простоты вернём только основные поля
                orders.append({
                    "id": row["id"],
                    "client_id": row["client_id"],
                    "order_date": row["order_date"],
                    "total_price": row["total_price"]
                })
            return orders
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка получения заказов по датам: {e}")