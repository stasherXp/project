import unittest
from src.models import Client, Product, Order

class TestModels(unittest.TestCase):
    def test_client_creation(self):
        client = Client("Иван", "ivan@mail.ru", "+79991234567")
        self.assertEqual(client.name, "Иван")
        self.assertEqual(client.email, "ivan@mail.ru")
        d = client.to_dict()
        self.assertIn("name", d)

    def test_product_creation(self):
        prod = Product("Ноутбук", 50000, "Электроника")
        self.assertEqual(prod.price, 50000)

    def test_order_creation(self):
        order = Order(client_id=1, products=[(2, 1), (3, 2)], total_price=1500)
        self.assertEqual(order.client_id, 1)
        self.assertEqual(len(order.products), 2)

if __name__ == '__main__':
    unittest.main()