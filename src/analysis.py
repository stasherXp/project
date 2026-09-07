import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any


def get_top_5_clients(orders: List[Dict], clients: List[Dict]) -> pd.DataFrame:
    order_counts = {}
    for order in orders:
        cid = order['client_id']
        order_counts[cid] = order_counts.get(cid, 0) + 1
    client_names = {c['id']: c['name'] for c in clients}
    data = [{'client_id': cid, 'name': client_names.get(cid, 'Неизвестно'),
             'orders_count': count} for cid, count in order_counts.items()]
    df = pd.DataFrame(data)
    if df.empty:
        return pd.DataFrame(columns=['client_id', 'name', 'orders_count'])
    return df.sort_values('orders_count', ascending=False).head(5)


def plot_orders_dynamics(orders: List[Dict]) -> plt.Figure:
    if not orders:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, 'Нет данных для отображения', ha='center', va='center')
        return fig
    df = pd.DataFrame(orders)
    df['order_date'] = pd.to_datetime(df['order_date']).dt.date
    daily = df.groupby('order_date').size().reset_index(name='count')
    daily = daily.sort_values('order_date')
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.lineplot(data=daily, x='order_date', y='count', marker='o', ax=ax)
    ax.set_title('Динамика количества заказов по дням')
    ax.set_xlabel('Дата')
    ax.set_ylabel('Число заказов')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig