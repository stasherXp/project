import unittest
from unittest.mock import MagicMock
import pandas as pd
from src.analysis import get_top_clients, get_orders_dynamics


class TestAnalysis(unittest.TestCase):
    def test_get_top_clients_returns_dataframe(self):
        # Создаём мок базы данных
        mock_db = MagicMock()
        mock_db.get_all_orders.return_value = []
        mock_db.get_all_clients.return_value = []
        result = get_top_clients(mock_db)
        self.assertIsInstance(result, pd.DataFrame)

    def test_get_orders_dynamics_returns_dataframe(self):
        mock_db = MagicMock()
        mock_db.get_all_orders.return_value = []
        result = get_orders_dynamics(mock_db)
        self.assertIsInstance(result, pd.DataFrame)