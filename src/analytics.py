"""
src/analysis.py
Анализ данных без pandas.
Если matplotlib установлен — использует его, иначе рисует графики на tkinter.Canvas.
"""

import tkinter as tk

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False


def get_top_clients(db, top_n: int = 5):
    orders = db.get_all_orders()
    counts = {}
    for o in orders:
        counts[o["client_id"]] = counts.get(o["client_id"], 0) + 1
    clients = {c.id: c.name for c in db.get_all_clients()}
    result = [
        {"client_id": cid, "name": clients.get(cid, "Неизвестно"), "orders_count": cnt}
        for cid, cnt in counts.items()
    ]
    result.sort(key=lambda x: x["orders_count"], reverse=True)
    return result[:top_n]


def get_orders_dynamics(db):
    orders = db.get_all_orders()
    counts = {}
    for o in orders:
        d = o["order_date"]
        counts[d] = counts.get(d, 0) + 1
    return [{"order_date": d, "orders_count": counts[d]} for d in sorted(counts.keys())]


def show_analysis_window(db) -> None:
    window = tk.Toplevel()
    window.title("Аналитика")
    window.geometry("1000x600")
    if HAS_MPL:
        _show_mpl(db, window)
    else:
        _show_canvas(db, window)


def _show_mpl(db, window):
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure

    fig = Figure(figsize=(10, 5))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    data = get_top_clients(db)
    if data:
        names = [d["name"] for d in data]
        vals = [d["orders_count"] for d in data]
        ax1.bar(names, vals, color="#4a90d9")
        ax1.set_title("Топ-5 клиентов по числу заказов")
        ax1.tick_params(axis="x", rotation=30)
    else:
        ax1.text(0.5, 0.5, "Нет данных", ha="center", va="center")

    dyn = get_orders_dynamics(db)
    if dyn:
        dates = [d["order_date"] for d in dyn]
        vals = [d["orders_count"] for d in dyn]
        ax2.plot(dates, vals, marker="o", color="blue")
        ax2.set_title("Динамика заказов по датам")
        ax2.tick_params(axis="x", rotation=45)
        ax2.grid(True)
    else:
        ax2.text(0.5, 0.5, "Нет данных", ha="center", va="center")

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def _show_canvas(db, window):
    """Графики на чистом tkinter.Canvas — без matplotlib."""
    tk.Label(window, text="Топ-5 клиентов по числу заказов",
             font=("Arial", 11, "bold")).pack(pady=5)
    c1 = tk.Canvas(window, width=900, height=200, bg="white")
    c1.pack(pady=5)

    data = get_top_clients(db)
    if not data:
        c1.create_text(450, 100, text="Нет данных", fill="gray", font=("Arial", 12))
    else:
        max_val = max(d["orders_count"] for d in data)
        bar_w, gap = 60, 40
        total = len(data) * bar_w + (len(data) - 1) * gap
        x = (900 - total) // 2
        base_y = 180
        for d in data:
            h = int((d["orders_count"] / max_val) * 140) if max_val else 0
            c1.create_rectangle(x, base_y - h, x + bar_w, base_y,
                                fill="#4a90d9", outline="black")
            c1.create_text(x + bar_w // 2, base_y - h - 10,
                           text=str(d["orders_count"]), font=("Arial", 10))
            c1.create_text(x + bar_w // 2, base_y + 12, text=d["name"], font=("Arial", 9))
            x += bar_w + gap

    tk.Label(window, text="Динамика количества заказов по датам",
             font=("Arial", 11, "bold")).pack(pady=5)
    c2 = tk.Canvas(window, width=900, height=250, bg="white")
    c2.pack(pady=5)

    dyn = get_orders_dynamics(db)
    if not dyn:
        c2.create_text(450, 125, text="Нет данных", fill="gray", font=("Arial", 12))
    else:
        ml, mr, mt, mb = 50, 30, 20, 40
        w, h = 900 - ml - mr, 250 - mt - mb
        max_v = max(d["orders_count"] for d in dyn) or 1
        c2.create_line(ml, 250 - mb, 900 - mr, 250 - mb, fill="black")
        c2.create_line(ml, mt, ml, 250 - mb, fill="black")
        n = len(dyn)
        step = w / (n - 1) if n > 1 else 0
        pts = []
        for i, d in enumerate(dyn):
            x = ml + i * step
            y = 250 - mb - (d["orders_count"] / max_v) * h
            pts.extend([x, y])
            c2.create_oval(x - 3, y - 3, x + 3, y + 3, fill="blue")
            c2.create_text(x, y - 12, text=str(d["orders_count"]), font=("Arial", 9))
            c2.create_text(x, 250 - mb + 12, text=d["order_date"], font=("Arial", 8))
        if len(pts) >= 4:
            c2.create_line(pts, fill="blue", width=2)