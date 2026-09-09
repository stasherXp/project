import unittest
from src.models import Client, Product, Order

class TestModels(unittest.TestCase):
    def test_client_creation(self):
        client = Client(1, "Иван", "ivan@mail.ru", "+79991234567", "2025-01-01")
        self.assertEqual(client.id, 1)
        self.assertEqual(client.name, "Иван")
        self.assertEqual(client.email, "ivan@mail.ru")

    def test_product_creation(self):
        prod = Product(1, "Ноутбук", 50000, "Электроника")
        self.assertEqual(prod.id, 1)
        self.assertEqual(prod.name, "Ноутбук")
        self.assertEqual(prod.price, 50000)

    def test_order_creation(self):
        items = [(2, 1), (3, 2)]  # product_id, quantity
        order = Order(1, client_id=1, items=items, order_date="2025-01-01")
        self.assertEqual(order.id, 1)
        self.assertEqual(order.client_id, 1)
        self.assertEqual(len(order.items), 2)
        # Проверка пересчёта total_price
        prices = {2: 1000, 3: 250}
        order.recalculate_total(prices)
        self.assertEqual(order.total_price, 1000*1 + 250*2)