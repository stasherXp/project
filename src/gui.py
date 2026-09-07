"""
src/gui.py

Главный модуль графического интерфейса на tkinter.
Реализует три вкладки: Клиенты, Товары, Заказы.
Использует DatabaseManager для работы с БД,
utils для валидации и экспорта/импорта,
analysis для вызова окон аналитики.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from src.db import DatabaseManager
from src.models import Client, Product, Order
from src.utils import (
    validate_email,
    validate_phone,
    export_to_csv,
    import_from_csv,
    export_to_json,
    import_from_json,
    sort_orders,
)
from src.analysis import show_analysis_window


class MainApp:
    """Главное окно приложения."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Система управления заказами")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # Подключение к БД
        self.db = DatabaseManager()

        # Создание интерфейса
        self._setup_menu()
        self._setup_notebook()

        # Обновление таблиц при запуске
        self.refresh_all_tables()

    def _setup_menu(self) -> None:
        """Создаёт меню в верхней части окна."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Экспорт в CSV", command=self.export_csv)
        file_menu.add_command(label="Импорт из CSV", command=self.import_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Экспорт в JSON", command=self.export_json)
        file_menu.add_command(label="Импорт из JSON", command=self.import_json)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        analytics_menu = tk.Menu(menubar, tearoff=0)
        analytics_menu.add_command(label="Показать аналитику", command=self.show_analytics)
        menubar.add_cascade(label="Аналитика", menu=analytics_menu)

    def _setup_notebook(self) -> None:
        """Создаёт вкладки."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Вкладка "Клиенты"
        self.clients_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.clients_frame, text="Клиенты")
        self._setup_clients_tab()

        # Вкладка "Товары"
        self.products_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.products_frame, text="Товары")
        self._setup_products_tab()

        # Вкладка "Заказы"
        self.orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text="Заказы")
        self._setup_orders_tab()

    # ------------------- Вкладка "Клиенты" -------------------
    def _setup_clients_tab(self) -> None:
        """Настройка вкладки клиентов."""
        # Форма добавления
        form_frame = ttk.LabelFrame(self.clients_frame, text="Добавить клиента", padding=5)
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(form_frame, text="Имя:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.client_name_entry = ttk.Entry(form_frame, width=30)
        self.client_name_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.client_email_entry = ttk.Entry(form_frame, width=30)
        self.client_email_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(form_frame, text="Телефон:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.client_phone_entry = ttk.Entry(form_frame, width=30)
        self.client_phone_entry.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(form_frame, text="Дата регистрации (ГГГГ-ММ-ДД):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.client_date_entry = ttk.Entry(form_frame, width=30)
        self.client_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.client_date_entry.grid(row=3, column=1, padx=5, pady=2)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=5)
        ttk.Button(btn_frame, text="Добавить клиента", command=self.add_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить поля", command=self.clear_client_form).pack(side=tk.LEFT, padx=5)

        # Поиск и фильтр
        search_frame = ttk.Frame(self.clients_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(search_frame, text="Поиск по имени:").pack(side=tk.LEFT, padx=5)
        self.client_search_entry = ttk.Entry(search_frame, width=30)
        self.client_search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Найти", command=self.search_clients).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Сбросить", command=self.refresh_clients_table).pack(side=tk.LEFT, padx=5)

        # Таблица клиентов
        table_frame = ttk.LabelFrame(self.clients_frame, text="Список клиентов", padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("id", "name", "email", "phone", "registration_date")
        self.clients_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.clients_tree.heading("id", text="ID")
        self.clients_tree.heading("name", text="Имя")
        self.clients_tree.heading("email", text="Email")
        self.clients_tree.heading("phone", text="Телефон")
        self.clients_tree.heading("registration_date", text="Дата регистрации")
        self.clients_tree.column("id", width=50)
        self.clients_tree.column("name", width=150)
        self.clients_tree.column("email", width=200)
        self.clients_tree.column("phone", width=120)
        self.clients_tree.column("registration_date", width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.clients_tree.pack(fill=tk.BOTH, expand=True)

        # Кнопки управления таблицей
        control_frame = ttk.Frame(self.clients_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(control_frame, text="Удалить выбранного", command=self.delete_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Обновить список", command=self.refresh_clients_table).pack(side=tk.LEFT, padx=5)

    # ------------------- Вкладка "Товары" -------------------
    def _setup_products_tab(self) -> None:
        """Настройка вкладки товаров."""
        # Форма добавления
        form_frame = ttk.LabelFrame(self.products_frame, text="Добавить товар", padding=5)
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.product_name_entry = ttk.Entry(form_frame, width=30)
        self.product_name_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(form_frame, text="Цена:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.product_price_entry = ttk.Entry(form_frame, width=30)
        self.product_price_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(form_frame, text="Категория:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.product_category_entry = ttk.Entry(form_frame, width=30)
        self.product_category_entry.grid(row=2, column=1, padx=5, pady=2)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Button(btn_frame, text="Добавить товар", command=self.add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить поля", command=self.clear_product_form).pack(side=tk.LEFT, padx=5)

        # Таблица товаров
        table_frame = ttk.LabelFrame(self.products_frame, text="Список товаров", padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("id", "name", "price", "category")
        self.products_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.products_tree.heading("id", text="ID")
        self.products_tree.heading("name", text="Название")
        self.products_tree.heading("price", text="Цена")
        self.products_tree.heading("category", text="Категория")
        self.products_tree.column("id", width=50)
        self.products_tree.column("name", width=200)
        self.products_tree.column("price", width=100)
        self.products_tree.column("category", width=150)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.products_tree.pack(fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(self.products_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(control_frame, text="Удалить выбранный", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Обновить список", command=self.refresh_products_table).pack(side=tk.LEFT, padx=5)

    # ------------------- Вкладка "Заказы" -------------------
    def _setup_orders_tab(self) -> None:
        """Настройка вкладки заказов."""
        # Форма добавления заказа (упрощённая: выбор клиента, добавление товаров с количеством)
        form_frame = ttk.LabelFrame(self.orders_frame, text="Создать заказ", padding=5)
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(form_frame, text="Клиент:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.order_client_var = tk.StringVar()
        self.order_client_combo = ttk.Combobox(form_frame, textvariable=self.order_client_var, width=40)
        self.order_client_combo.grid(row=0, column=1, padx=5, pady=2)
        self._refresh_client_combo()

        ttk.Label(form_frame, text="Товар:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.order_product_var = tk.StringVar()
        self.order_product_combo = ttk.Combobox(form_frame, textvariable=self.order_product_var, width=40)
        self.order_product_combo.grid(row=1, column=1, padx=5, pady=2)
        self._refresh_product_combo()

        ttk.Label(form_frame, text="Количество:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.order_quantity_entry = ttk.Entry(form_frame, width=10)
        self.order_quantity_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        self.order_quantity_entry.insert(0, "1")

        ttk.Label(form_frame, text="Дата заказа (ГГГГ-ММ-ДД):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.order_date_entry = ttk.Entry(form_frame, width=30)
        self.order_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.order_date_entry.grid(row=3, column=1, padx=5, pady=2)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=5)
        ttk.Button(btn_frame, text="Добавить товар в заказ", command=self.add_order_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Оформить заказ", command=self.create_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить корзину", command=self.clear_order_cart).pack(side=tk.LEFT, padx=5)

        # Корзина заказа (список добавленных товаров)
        cart_frame = ttk.LabelFrame(self.orders_frame, text="Корзина заказа", padding=5)
        cart_frame.pack(fill=tk.X, padx=5, pady=5)

        self.order_cart_listbox = tk.Listbox(cart_frame, height=4)
        self.order_cart_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.order_cart = []  # список кортежей (product_id, product_name, quantity)

        # Фильтр заказов по дате
        filter_frame = ttk.Frame(self.orders_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(filter_frame, text="Фильтр по дате (с):").pack(side=tk.LEFT, padx=5)
        self.order_filter_from = ttk.Entry(filter_frame, width=12)
        self.order_filter_from.pack(side=tk.LEFT, padx=5)
        ttk.Label(filter_frame, text="по:").pack(side=tk.LEFT, padx=5)
        self.order_filter_to = ttk.Entry(filter_frame, width=12)
        self.order_filter_to.pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Применить фильтр", command=self.filter_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Сбросить", command=self.refresh_orders_table).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Сортировать по дате", command=lambda: self.sort_orders_by("order_date")).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Сортировать по сумме", command=lambda: self.sort_orders_by("total_price")).pack(side=tk.LEFT, padx=5)

        # Таблица заказов
        table_frame = ttk.LabelFrame(self.orders_frame, text="Список заказов", padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("id", "client_id", "client_name", "order_date", "total_price")
        self.orders_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.orders_tree.heading("id", text="ID")
        self.orders_tree.heading("client_id", text="ID клиента")
        self.orders_tree.heading("client_name", text="Клиент")
        self.orders_tree.heading("order_date", text="Дата заказа")
        self.orders_tree.heading("total_price", text="Общая сумма")
        self.orders_tree.column("id", width=50)
        self.orders_tree.column("client_id", width=80)
        self.orders_tree.column("client_name", width=150)
        self.orders_tree.column("order_date", width=120)
        self.orders_tree.column("total_price", width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.orders_tree.pack(fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(self.orders_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(control_frame, text="Удалить выбранный", command=self.delete_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Обновить список", command=self.refresh_orders_table).pack(side=tk.LEFT, padx=5)

        # Инициализация корзины
        self.order_cart = []

    # ------------------- Вспомогательные методы для Combobox -------------------
    def _refresh_client_combo(self) -> None:
        """Обновляет список клиентов в выпадающем списке."""
        clients = self.db.get_all_clients()
        client_display = [f"{c.id} - {c.name}" for c in clients]
        self.order_client_combo['values'] = client_display

    def _refresh_product_combo(self) -> None:
        """Обновляет список товаров в выпадающем списке."""
        products = self.db.get_all_products()
        product_display = [f"{p.id} - {p.name} ({p.price} руб.)" for p in products]
        self.order_product_combo['values'] = product_display

    # ------------------- CRUD для клиентов -------------------
    def add_client(self) -> None:
        """Добавляет клиента из формы."""
        name = self.client_name_entry.get().strip()
        email = self.client_email_entry.get().strip()
        phone = self.client_phone_entry.get().strip()
        date = self.client_date_entry.get().strip()

        if not all([name, email, phone, date]):
            messagebox.showwarning("Ошибка", "Все поля обязательны для заполнения!")
            return

        if not validate_email(email):
            messagebox.showwarning("Ошибка", "Некорректный email!")
            return
        if not validate_phone(phone):
            messagebox.showwarning("Ошибка", "Некорректный номер телефона!")
            return

        try:
            client = Client(None, name, email, phone, date)
            self.db.add_client(client)
            messagebox.showinfo("Успех", "Клиент добавлен!")
            self.clear_client_form()
            self.refresh_clients_table()
            self._refresh_client_combo()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def delete_client(self) -> None:
        """Удаляет выбранного клиента."""
        selection = self.clients_tree.selection()
        if not selection:
            messagebox.showwarning("Ошибка", "Выберите клиента для удаления!")
            return
        item = self.clients_tree.item(selection[0])
        client_id = int(item['values'][0])
        if messagebox.askyesno("Подтверждение", "Удалить клиента?"):
            try:
                self.db.delete_client(client_id)
                self.refresh_clients_table()
                self._refresh_client_combo()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def clear_client_form(self) -> None:
        """Очищает поля формы клиента."""
        self.client_name_entry.delete(0, tk.END)
        self.client_email_entry.delete(0, tk.END)
        self.client_phone_entry.delete(0, tk.END)
        self.client_date_entry.delete(0, tk.END)
        self.client_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def refresh_clients_table(self) -> None:
        """Обновляет таблицу клиентов."""
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)
        clients = self.db.get_all_clients()
        for c in clients:
            self.clients_tree.insert("", tk.END, values=(
                c.id, c.name, c.email, c.phone, c.registration_date
            ))
        self.client_search_entry.delete(0, tk.END)

    def search_clients(self) -> None:
        """Поиск клиентов по имени."""
        search_text = self.client_search_entry.get().strip()
        if not search_text:
            self.refresh_clients_table()
            return
        # Используем прямой запрос к БД
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)
        # Получаем через менеджер (добавим метод в db.py для поиска)
        # Временно реализуем фильтрацию через получение всех и проверку
        all_clients = self.db.get_all_clients()
        filtered = [c for c in all_clients if search_text.lower() in c.name.lower()]
        for c in filtered:
            self.clients_tree.insert("", tk.END, values=(
                c.id, c.name, c.email, c.phone, c.registration_date
            ))

    # ------------------- CRUD для товаров -------------------
    def add_product(self) -> None:
        """Добавляет товар."""
        name = self.product_name_entry.get().strip()
        price_str = self.product_price_entry.get().strip()
        category = self.product_category_entry.get().strip()

        if not all([name, price_str, category]):
            messagebox.showwarning("Ошибка", "Все поля обязательны!")
            return
        try:
            price = float(price_str)
            if price < 0:
                raise ValueError("Цена не может быть отрицательной")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную цену (число)")
            return

        try:
            product = Product(None, name, price, category)
            self.db.add_product(product)
            messagebox.showinfo("Успех", "Товар добавлен!")
            self.clear_product_form()
            self.refresh_products_table()
            self._refresh_product_combo()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def delete_product(self) -> None:
        """Удаляет выбранный товар."""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Ошибка", "Выберите товар для удаления!")
            return
        item = self.products_tree.item(selection[0])
        product_id = int(item['values'][0])
        if messagebox.askyesno("Подтверждение", "Удалить товар?"):
            try:
                self.db.delete_product(product_id)
                self.refresh_products_table()
                self._refresh_product_combo()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def clear_product_form(self) -> None:
        """Очищает поля формы товара."""
        self.product_name_entry.delete(0, tk.END)
        self.product_price_entry.delete(0, tk.END)
        self.product_category_entry.delete(0, tk.END)

    def refresh_products_table(self) -> None:
        """Обновляет таблицу товаров."""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        products = self.db.get_all_products()
        for p in products:
            self.products_tree.insert("", tk.END, values=(
                p.id, p.name, p.price, p.category
            ))

    # ------------------- Работа с заказами -------------------
    def add_order_item(self) -> None:
        """Добавляет товар в корзину заказа."""
        product_selection = self.order_product_var.get()
        if not product_selection:
            messagebox.showwarning("Ошибка", "Выберите товар!")
            return
        try:
            product_id = int(product_selection.split(" - ")[0])
        except:
            messagebox.showerror("Ошибка", "Неверный формат выбора товара")
            return
        quantity_str = self.order_quantity_entry.get().strip()
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Введите положительное целое количество")
            return

        # Получаем имя товара
        products = self.db.get_all_products()
        product = next((p for p in products if p.id == product_id), None)
        if not product:
            messagebox.showerror("Ошибка", "Товар не найден")
            return

        # Добавляем в корзину
        # Если товар уже есть, увеличиваем количество
        for i, (pid, name, qty) in enumerate(self.order_cart):
            if pid == product_id:
                self.order_cart[i] = (pid, name, qty + quantity)
                self._update_cart_listbox()
                return
        self.order_cart.append((product_id, product.name, quantity))
        self._update_cart_listbox()
        messagebox.showinfo("Успех", f"Товар {product.name} добавлен в корзину")

    def _update_cart_listbox(self) -> None:
        """Обновляет отображение корзины."""
        self.order_cart_listbox.delete(0, tk.END)
        for pid, name, qty in self.order_cart:
            self.order_cart_listbox.insert(tk.END, f"{name} x {qty}")

    def clear_order_cart(self) -> None:
        """Очищает корзину."""
        self.order_cart = []
        self._update_cart_listbox()

    def create_order(self) -> None:
        """Оформляет заказ."""
        client_selection = self.order_client_var.get()
        if not client_selection:
            messagebox.showwarning("Ошибка", "Выберите клиента!")
            return
        try:
            client_id = int(client_selection.split(" - ")[0])
        except:
            messagebox.showerror("Ошибка", "Неверный формат выбора клиента")
            return
        if not self.order_cart:
            messagebox.showwarning("Ошибка", "Корзина пуста!")
            return

        order_date = self.order_date_entry.get().strip()
        if not order_date:
            order_date = datetime.now().strftime("%Y-%m-%d")

        # Собираем список товаров для заказа
        items = [(pid, qty) for pid, name, qty in self.order_cart]

        # Собираем цены товаров
        products = self.db.get_all_products()
        prices = {p.id: p.price for p in products}
        # Проверяем, что все товары есть в базе
        for pid, _ in items:
            if pid not in prices:
                messagebox.showerror("Ошибка", f"Товар с ID {pid} не найден в БД")
                return

        # Создаём заказ
        order = Order(None, client_id, items, order_date)
        order.recalculate_total(prices)

        try:
            self.db.add_order(order, prices)
            messagebox.showinfo("Успех", "Заказ оформлен!")
            self.clear_order_cart()
            self.refresh_orders_table()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def delete_order(self) -> None:
        """Удаляет выбранный заказ."""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Ошибка", "Выберите заказ для удаления!")
            return
        item = self.orders_tree.item(selection[0])
        order_id = int(item['values'][0])
        if messagebox.askyesno("Подтверждение", "Удалить заказ?"):
            try:
                self.db.delete_order(order_id)
                self.refresh_orders_table()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def refresh_orders_table(self) -> None:
        """Обновляет таблицу заказов (без фильтра)."""
        self.order_filter_from.delete(0, tk.END)
        self.order_filter_to.delete(0, tk.END)
        self._display_orders(self.db.get_all_orders())

    def _display_orders(self, orders_data) -> None:
        """Отображает список заказов в таблице."""
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        # orders_data – список словарей, полученных из db.get_all_orders()
        # Для отображения имени клиента нужно получить клиента по id
        clients = {c.id: c.name for c in self.db.get_all_clients()}
        for order in orders_data:
            client_name = clients.get(order['client_id'], "Неизвестно")
            self.orders_tree.insert("", tk.END, values=(
                order['id'],
                order['client_id'],
                client_name,
                order['order_date'],
                f"{order['total_price']:.2f}"
            ))

    def filter_orders(self) -> None:
        """Фильтрует заказы по дате."""
        from_date = self.order_filter_from.get().strip()
        to_date = self.order_filter_to.get().strip()
        if not from_date or not to_date:
            messagebox.showwarning("Ошибка", "Введите обе даты в формате ГГГГ-ММ-ДД")
            return
        try:
            # Проверяем формат дат
            datetime.strptime(from_date, "%Y-%m-%d")
            datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты (должен быть ГГГГ-ММ-ДД)")
            return
        try:
            filtered = self.db.get_orders_by_date_range(from_date, to_date)
            # convert to list of dicts with needed keys
            self._display_orders(filtered)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def sort_orders_by(self, sort_by: str) -> None:
        """Сортирует текущие заказы в таблице по указанному полю."""
        # Получаем текущие данные из таблицы (парсим строки)
        rows = []
        for child in self.orders_tree.get_children():
            values = self.orders_tree.item(child)['values']
            # Преобразуем в словарь для сортировки
            row_dict = {
                'id': values[0],
                'client_id': values[1],
                'order_date': values[3],
                'total_price': float(values[4])
            }
            rows.append(row_dict)
        if not rows:
            return
        try:
            sorted_rows = sort_orders(rows, sort_by=sort_by, reverse=False)
            self._display_orders(sorted_rows)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ------------------- Экспорт/Импорт -------------------
    def export_csv(self) -> None:
        """Экспорт данных (всех таблиц) в CSV."""
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        try:
            # Экспортируем клиентов, товары, заказы в один файл
            clients = [c.to_dict() for c in self.db.get_all_clients()]
            products = [p.to_dict() for p in self.db.get_all_products()]
            orders = self.db.get_all_orders()
            # Преобразуем заказы в плоские словари (без вложенных items)
            orders_flat = []
            for o in orders:
                orders_flat.append({
                    'id': o['id'],
                    'client_id': o['client_id'],
                    'order_date': o['order_date'],
                    'total_price': o['total_price']
                })
            data = {
                'clients': clients,
                'products': products,
                'orders': orders_flat
            }
            # Сохраняем как JSON, т.к. CSV не поддерживает вложенность
            export_to_json(data, filename)
            messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def import_csv(self) -> None:
        """Импорт данных из CSV (ожидается структура как при экспорте)."""
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        try:
            data = import_from_csv(filename)
            # Здесь надо разобрать структуру и добавить в БД (упрощённо)
            messagebox.showinfo("Информация", "Импорт из CSV не реализован полностью (используйте JSON)")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def export_json(self) -> None:
        """Экспорт данных в JSON."""
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not filename:
            return
        try:
            clients = [c.to_dict() for c in self.db.get_all_clients()]
            products = [p.to_dict() for p in self.db.get_all_products()]
            orders = self.db.get_all_orders()
            data = {
                'clients': clients,
                'products': products,
                'orders': orders
            }
            export_to_json(data, filename)
            messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def import_json(self) -> None:
        """Импорт данных из JSON."""
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not filename:
            return
        try:
            data = import_from_json(filename)
            # Проверяем структуру
            if 'clients' in data:
                for c in data['clients']:
                    client = Client(None, c['name'], c['email'], c['phone'], c.get('registration_date', datetime.now().strftime("%Y-%m-%d")))
                    try:
                        self.db.add_client(client)
                    except Exception:
                        pass  # пропускаем дубликаты
            if 'products' in data:
                for p in data['products']:
                    product = Product(None, p['name'], p['price'], p['category'])
                    try:
                        self.db.add_product(product)
                    except Exception:
                        pass
            if 'orders' in data:
                # Сначала нужно заполнить клиентов и товары, потом заказы – упрощаем
                messagebox.showinfo("Информация", "Импорт заказов из JSON требует дополнительной логики (пропущено)")
            self.refresh_all_tables()
            messagebox.showinfo("Успех", "Данные импортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ------------------- Аналитика -------------------
    def show_analytics(self) -> None:
        """Показывает окно с аналитикой."""
        try:
            show_analysis_window(self.db)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть аналитику: {e}")

    # ------------------- Общие методы -------------------
    def refresh_all_tables(self) -> None:
        """Обновляет все таблицы."""
        self.refresh_clients_table()
        self.refresh_products_table()
        self.refresh_orders_table()
        self._refresh_client_combo()
        self._refresh_product_combo()