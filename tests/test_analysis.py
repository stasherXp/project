import unittest
from unittest.mock import MagicMock
from src.analysis import get_top_clients, get_orders_dynamics


class TestAnalysis(unittest.TestCase):
    def test_get_top_clients_returns_list(self):
        mock_db = MagicMock()
        mock_db.get_all_orders.return_value = []
        mock_db.get_all_clients.return_value = []
        self.assertIsInstance(get_top_clients(mock_db), list)

    def test_get_orders_dynamics_returns_list(self):
        mock_db = MagicMock()
        mock_db.get_all_orders.return_value = []
        self.assertIsInstance(get_orders_dynamics(mock_db), list)