"""
Модуль GUI на Tkinter.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.models import Client, Product, Order
from src.db import DatabaseManager
from src.utils import (validate_email, validate_phone, export_to_csv, import_from_csv,
                       export_to_json, import_from_json, sort_orders)
from src.analysis import get_top_5_clients, plot_orders_dynamics


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система учёта заказов")
        self.root.geometry("1000x700")
        self.db = DatabaseManager()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tab_clients = ttk.Frame(self.notebook)
        self.tab_products = ttk.Frame(self.notebook)
        self.tab_orders = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_clients, text="Клиенты")
        self.notebook.add(self.tab_products, text="Товары")
        self.notebook.add(self.tab_orders, text="Заказы")

        self._build_clients_tab()
        self._build_products_tab()
        self._build_orders_tab()
        self._build_global_buttons()

    # ---------- Клиенты ----------
    def _build_clients_tab(self):
        frame = self.tab_clients
        add_frame = ttk.LabelFrame(frame, text="Добавить клиента", padding=5)
        add_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(add_frame, text="Имя:").grid(row=0, column=0, sticky=tk.W)
        self.entry_client_name = ttk.Entry(add_frame, width=30)
        self.entry_client_name.grid(row=0, column=1, padx=5)

        ttk.Label(add_frame, text="Email:").grid(row=1, column=0, sticky=tk.W)
        self.entry_client_email = ttk.Entry(add_frame, width=30)
        self.entry_client_email.grid(row=1, column=1, padx=5)

        ttk.Label(add_frame, text="Телефон:").grid(row=2, column=0, sticky=tk.W)
        self.entry_client_phone = ttk.Entry(add_frame, width=30)
        self.entry_client_phone.grid(row=2, column=1, padx=5)

        btn_add_client = ttk.Button(add_frame, text="Добавить", command=self._add_client)
        btn_add_client.grid(row=3, column=0, columnspan=2, pady=5)

        table_frame = ttk.LabelFrame(frame, text="Список клиентов")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        cols = ('ID', 'Имя', 'Email', 'Телефон', 'Дата регистрации')
        self.tree_clients = ttk.Treeview(table_frame, columns=cols, show='headings')
        for col in cols:
            self.tree_clients.heading(col, text=col)
            self.tree_clients.column(col, width=100)
        self.tree_clients.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree_clients.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_clients.configure(yscrollcommand=scroll.set)

        btn_del_client = ttk.Button(frame, text="Удалить выбранного клиента", command=self._delete_client)
        btn_del_client.pack(pady=5)

        self._refresh_clients()

    def _add_client(self):
        name = self.entry_client_name.get().strip()
        email = self.entry_client_email.get().strip()
        phone = self.entry_client_phone.get().strip()
        if not name or not email:
            messagebox.showwarning("Ошибка", "Имя и Email обязательны")
            return
        if not validate_email(email):
            messagebox.showwarning("Ошибка", "Некорректный email")
            return
        if phone and not validate_phone(phone):
            messagebox.showwarning("Ошибка", "Некорректный телефон (должен содержать 11 цифр, начинаться с 7 или 8)")
            return
        client = Client(name, email, phone)
        try:
            self.db.add_client(client)
            self._refresh_clients()
            self.entry_client_name.delete(0, tk.END)
            self.entry_client_email.delete(0, tk.END)
            self.entry_client_phone.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))

    def _delete_client(self):
        selected = self.tree_clients.selection()
        if not selected:
            return
        item = self.tree_clients.item(selected[0])
        client_id = item['values'][0]
        if messagebox.askyesno("Удаление", "Удалить клиента?"):
            self.db.delete_client(client_id)
            self._refresh_clients()

    def _refresh_clients(self):
        for row in self.tree_clients.get_children():
            self.tree_clients.delete(row)
        clients = self.db.get_all_clients()
        for c in clients:
            self.tree_clients.insert('', tk.END, values=(c['id'], c['name'], c['email'], c['phone'], c['registration_date']))

    # ---------- Товары ----------
    def _build_products_tab(self):
        frame = self.tab_products
        add_frame = ttk.LabelFrame(frame, text="Добавить товар", padding=5)
        add_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(add_frame, text="Название:").grid(row=0, column=0, sticky=tk.W)
        self.entry_prod_name = ttk.Entry(add_frame, width=30)
        self.entry_prod_name.grid(row=0, column=1, padx=5)

        ttk.Label(add_frame, text="Цена:").grid(row=1, column=0, sticky=tk.W)
        self.entry_prod_price = ttk.Entry(add_frame, width=30)
        self.entry_prod_price.grid(row=1, column=1, padx=5)

        ttk.Label(add_frame, text="Категория:").grid(row=2, column=0, sticky=tk.W)
        self.entry_prod_category = ttk.Entry(add_frame, width=30)
        self.entry_prod_category.grid(row=2, column=1, padx=5)

        btn_add_prod = ttk.Button(add_frame, text="Добавить", command=self._add_product)
        btn_add_prod.grid(row=3, column=0, columnspan=2, pady=5)

        table_frame = ttk.LabelFrame(frame, text="Список товаров")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        cols = ('ID', 'Название', 'Цена', 'Категория')
        self.tree_products = ttk.Treeview(table_frame, columns=cols, show='headings')
        for col in cols:
            self.tree_products.heading(col, text=col)
            self.tree_products.column(col, width=100)
        self.tree_products.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree_products.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_products.configure(yscrollcommand=scroll.set)

        btn_del_prod = ttk.Button(frame, text="Удалить выбранный товар", command=self._delete_product)
        btn_del_prod.pack(pady=5)

        self._refresh_products()

    def _add_product(self):
        name = self.entry_prod_name.get().strip()
        price_str = self.entry_prod_price.get().strip()
        category = self.entry_prod_category.get().strip()
        if not name or not price_str:
            messagebox.showwarning("Ошибка", "Название и цена обязательны")
            return
        try:
            price = float(price_str)
        except ValueError:
            messagebox.showwarning("Ошибка", "Некорректная цена")
            return
        product = Product(name, price, category)
        self.db.add_product(product)
        self._refresh_products()
        self.entry_prod_name.delete(0, tk.END)
        self.entry_prod_price.delete(0, tk.END)
        self.entry_prod_category.delete(0, tk.END)

    def _delete_product(self):
        selected = self.tree_products.selection()
        if not selected:
            return
        item = self.tree_products.item(selected[0])
        prod_id = item['values'][0]
        if messagebox.askyesno("Удаление", "Удалить товар?"):
            self.db.delete_product(prod_id)
            self._refresh_products()

    def _refresh_products(self):
        for row in self.tree_products.get_children():
            self.tree_products.delete(row)
        products = self.db.get_all_products()
        for p in products:
            self.tree_products.insert('', tk.END, values=(p['id'], p['name'], p['price'], p['category']))

    # ---------- Заказы ----------
    def _build_orders_tab(self):
        frame = self.tab_orders
        add_frame = ttk.LabelFrame(frame, text="Создать заказ", padding=5)
        add_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(add_frame, text="Клиент (ID):").grid(row=0, column=0, sticky=tk.W)
        self.entry_order_client = ttk.Entry(add_frame, width=10)
        self.entry_order_client.grid(row=0, column=1, padx=5)

        ttk.Label(add_frame, text="Товар (ID):").grid(row=1, column=0, sticky=tk.W)
        self.entry_order_product = ttk.Entry(add_frame, width=10)
        self.entry_order_product.grid(row=1, column=1, padx=5)

        ttk.Label(add_frame, text="Количество:").grid(row=2, column=0, sticky=tk.W)
        self.entry_order_qty = ttk.Entry(add_frame, width=10)
        self.entry_order_qty.grid(row=2, column=1, padx=5)

        btn_add_order = ttk.Button(add_frame, text="Добавить позицию", command=self._add_order_item)
        btn_add_order.grid(row=3, column=0, columnspan=2, pady=2)

        self.order_items = []
        self.listbox_items = tk.Listbox(add_frame, height=4, width=50)
        self.listbox_items.grid(row=4, column=0, columnspan=2, pady=5)

        btn_finish_order = ttk.Button(add_frame, text="Завершить заказ", command=self._finish_order)
        btn_finish_order.grid(row=5, column=0, columnspan=2, pady=5)

        # Таблица заказов
        table_frame = ttk.LabelFrame(frame, text="Все заказы")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        cols = ('ID', 'Клиент ID', 'Дата', 'Сумма')
        self.tree_orders = ttk.Treeview(table_frame, columns=cols, show='headings')
        for col in cols:
            self.tree_orders.heading(col, text=col)
            self.tree_orders.column(col, width=100)
        self.tree_orders.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree_orders.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_orders.configure(yscrollcommand=scroll.set)

        btn_del_order = ttk.Button(frame, text="Удалить заказ", command=self._delete_order)
        btn_del_order.pack(pady=5)

        # Фильтр и сортировка
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(filter_frame, text="Сортировать по:").pack(side=tk.LEFT)
        self.sort_var = tk.StringVar(value="date")
        ttk.Radiobutton(filter_frame, text="Дате", variable=self.sort_var, value="date",
                        command=self._refresh_orders).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Сумме", variable=self.sort_var, value="total",
                        command=self._refresh_orders).pack(side=tk.LEFT)
        self.reverse_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_frame, text="По убыванию", variable=self.reverse_var,
                        command=self._refresh_orders).pack(side=tk.LEFT)

        self._refresh_orders()

    def _add_order_item(self):
        try:
            prod_id = int(self.entry_order_product.get().strip())
            qty = int(self.entry_order_qty.get().strip())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректные ID товара и количество")
            return
        self.order_items.append((prod_id, qty))
        self.listbox_items.insert(tk.END, f"Товар {prod_id} x {qty}")
        self.entry_order_product.delete(0, tk.END)
        self.entry_order_qty.delete(0, tk.END)

    def _finish_order(self):
        client_id_str = self.entry_order_client.get().strip()
        if not client_id_str:
            messagebox.showwarning("Ошибка", "Укажите ID клиента")
            return
        try:
            client_id = int(client_id_str)
        except ValueError:
            messagebox.showwarning("Ошибка", "Некорректный ID клиента")
            return
        # Проверяем, существует ли клиент
        clients = self.db.get_all_clients()
        if not any(c['id'] == client_id for c in clients):
            messagebox.showwarning("Ошибка", f"Клиент с ID {client_id} не найден")
            return
        if not self.order_items:
            messagebox.showwarning("Ошибка", "Добавьте хотя бы одну позицию")
            return

        products = self.db.get_all_products()
        prod_dict = {p['id']: p['price'] for p in products}
        total = 0.0
        for pid, qty in self.order_items:
            if pid not in prod_dict:
                messagebox.showwarning("Ошибка", f"Товар с ID {pid} не найден")
                return
            total += prod_dict[pid] * qty

        order = Order(client_id, self.order_items, total_price=total)
        try:
            self.db.add_order(order)
            self.order_items = []
            self.listbox_items.delete(0, tk.END)
            self.entry_order_client.delete(0, tk.END)
            self._refresh_orders()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _delete_order(self):
        selected = self.tree_orders.selection()
        if not selected:
            return
        item = self.tree_orders.item(selected[0])
        order_id = item['values'][0]
        if messagebox.askyesno("Удаление", "Удалить заказ?"):
            self.db.delete_order(order_id)
            self._refresh_orders()

    def _refresh_orders(self):
        for row in self.tree_orders.get_children():
            self.tree_orders.delete(row)
        orders = self.db.get_all_orders()
        sort_by = self.sort_var.get()
        reverse = self.reverse_var.get()
        sorted_orders = sort_orders(orders, by=sort_by, reverse=reverse)
        for o in sorted_orders:
            self.tree_orders.insert('', tk.END, values=(o['id'], o['client_id'], o['order_date'], o['total_price']))

    # ---------- Глобальные кнопки ----------
    def _build_global_buttons(self):
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(btn_frame, text="Экспорт клиентов в CSV", command=self._export_clients_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Импорт клиентов из CSV", command=self._import_clients_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Экспорт заказов в JSON", command=self._export_orders_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Аналитика", command=self._show_analytics).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить всё", command=self._refresh_all).pack(side=tk.LEFT, padx=5)

    def _export_clients_csv(self):
        clients = self.db.get_all_clients()
        if not clients:
            messagebox.showinfo("Нет данных", "Нет клиентов для экспорта")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            try:
                export_to_csv(clients, filename, ['id', 'name', 'email', 'phone', 'registration_date'])
                messagebox.showinfo("Успех", "Экспорт выполнен")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def _import_clients_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            try:
                data = import_from_csv(filename)
                for row in data:
                    client = Client(row['name'], row['email'], row.get('phone', ''))
                    self.db.add_client(client)
                self._refresh_clients()
                messagebox.showinfo("Успех", f"Импортировано {len(data)} клиентов")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def _export_orders_json(self):
        orders = self.db.get_all_orders()
        if not orders:
            messagebox.showinfo("Нет данных", "Нет заказов для экспорта")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                export_to_json(orders, filename)
                messagebox.showinfo("Успех", "Экспорт выполнен")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def _show_analytics(self):
        orders = self.db.get_all_orders()
        clients = self.db.get_all_clients()
        if not orders:
            messagebox.showinfo("Нет данных", "Нет заказов для анализа")
            return

        win = tk.Toplevel(self.root)
        win.title("Аналитика")
        win.geometry("900x600")
        nb = ttk.Notebook(win)
        nb.pack(fill=tk.BOTH, expand=True)

        frame1 = ttk.Frame(nb)
        nb.add(frame1, text="Топ-5 клиентов")
        top_df = get_top_5_clients(orders, clients)
        if not top_df.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(data=top_df, x='name', y='orders_count', ax=ax)
            ax.set_title("Топ-5 клиентов по числу заказов")
            ax.set_xlabel("Клиент")
            ax.set_ylabel("Число заказов")
            plt.xticks(rotation=45)
            canvas = FigureCanvasTkAgg(fig, master=frame1)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            ttk.Label(frame1, text="Недостаточно данных").pack()

        frame2 = ttk.Frame(nb)
        nb.add(frame2, text="Динамика заказов")
        fig2 = plot_orders_dynamics(orders)
        canvas2 = FigureCanvasTkAgg(fig2, master=frame2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _refresh_all(self):
        self._refresh_clients()
        self._refresh_products()
        self._refresh_orders()