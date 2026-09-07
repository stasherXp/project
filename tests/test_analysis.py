import unittest
from src.analysis import get_top_5_clients, plot_orders_dynamics

class TestAnalysis(unittest.TestCase):
    def test_top_clients(self):
        orders = [
            {'client_id': 1, 'order_date': '2025-01-01'},
            {'client_id': 1, 'order_date': '2025-01-02'},
            {'client_id': 2, 'order_date': '2025-01-03'},
        ]
        clients = [{'id': 1, 'name': 'A'}, {'id': 2, 'name': 'B'}]
        df = get_top_5_clients(orders, clients)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]['name'], 'A')
        self.assertEqual(df.iloc[0]['orders_count'], 2)

    def test_dynamics_returns_figure(self):
        orders = [{'order_date': '2025-01-01'}, {'order_date': '2025-01-01'}]
        fig = plot_orders_dynamics(orders)
        self.assertIsNotNone(fig)

if __name__ == '__main__':
    unittest.main()