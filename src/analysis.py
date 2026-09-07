"""
src/analysis.py

Модуль для анализа данных и построения графиков.
Использует pandas, matplotlib, seaborn.
Реализует функции:
- get_top_clients() – топ-5 клиентов по числу заказов.
- get_orders_dynamics() – динамика заказов по датам.
- plot_top_clients() – столбчатая диаграмма.
- plot_orders_dynamics() – линейный график.
- show_analysis_window() – окно tkinter с графиками.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional
from src.db import DatabaseManager


def get_top_clients(db: DatabaseManager, top_n: int = 5) -> pd.DataFrame:
    """
    Возвращает топ-N клиентов по количеству заказов.

    Parameters
    ----------
    db : DatabaseManager
        Экземпляр менеджера БД.
    top_n : int, optional
        Количество клиентов в топе (по умолчанию 5).

    Returns
    -------
    pd.DataFrame
        Колонки: client_id, name, orders_count.
    """
    orders = db.get_all_orders()
    if not orders:
        return pd.DataFrame(columns=["client_id", "name", "orders_count"])

    df_orders = pd.DataFrame(orders)
    orders_count = df_orders.groupby("client_id").size().reset_index(name="orders_count")

    clients = db.get_all_clients()
    df_clients = pd.DataFrame([c.to_dict() for c in clients])

    merged = pd.merge(orders_count, df_clients, left_on="client_id", right_on="id", how="inner")
    merged = merged[["client_id", "name", "orders_count"]]
    merged = merged.sort_values("orders_count", ascending=False).head(top_n)
    return merged


def get_orders_dynamics(db: DatabaseManager) -> pd.DataFrame:
    """
    Возвращает DataFrame с количеством заказов по дням.

    Returns
    -------
    pd.DataFrame
        Колонки: order_date, orders_count (отсортировано по дате).
    """
    orders = db.get_all_orders()
    if not orders:
        return pd.DataFrame(columns=["order_date", "orders_count"])

    df_orders = pd.DataFrame(orders)
    df_orders["order_date_dt"] = pd.to_datetime(df_orders["order_date"])
    dynamics = df_orders.groupby(df_orders["order_date_dt"].dt.date).size().reset_index(name="orders_count")
    dynamics.columns = ["order_date", "orders_count"]
    dynamics = dynamics.sort_values("order_date")
    return dynamics


def plot_top_clients(db: DatabaseManager, top_n: int = 5, ax: Optional[plt.Axes] = None) -> plt.Axes:
    """Строит столбчатую диаграмму топ-N клиентов."""
    data = get_top_clients(db, top_n)
    if data.empty:
        if ax is None:
            fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "Нет данных", ha="center", va="center", transform=ax.transAxes)
        return ax

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))

    sns.barplot(data=data, x="name", y="orders_count", palette="viridis", ax=ax)
    ax.set_title(f"Топ-{top_n} клиентов по числу заказов")
    ax.set_xlabel("Клиент")
    ax.set_ylabel("Количество заказов")
    for container in ax.containers:
        ax.bar_label(container, fmt="%d")
    return ax


def plot_orders_dynamics(db: DatabaseManager, ax: Optional[plt.Axes] = None) -> plt.Axes:
    """Строит линейный график динамики заказов по датам."""
    data = get_orders_dynamics(db)
    if data.empty:
        if ax is None:
            fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "Нет данных", ha="center", va="center", transform=ax.transAxes)
        return ax

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(data["order_date"], data["orders_count"], marker="o", linestyle="-", color="b")
    ax.set_title("Динамика количества заказов по датам")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Количество заказов")
    ax.grid(True)
    if len(data) > 10:
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    return ax


def show_analysis_window(db: DatabaseManager) -> None:
    """
    Создаёт отдельное окно tkinter с двумя графиками.
    """
    import tkinter as tk
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure

    window = tk.Toplevel()
    window.title("Аналитика")
    window.geometry("1000x600")

    fig = Figure(figsize=(10, 5))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    plot_top_clients(db, ax=ax1)
    plot_orders_dynamics(db, ax=ax2)

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)