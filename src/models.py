"""
Модуль моделей данных: клиент, товар, заказ.
Демонстрирует инкапсуляцию, наследование, полиморфизм.
"""
from datetime import datetime
from typing import List, Tuple, Optional


class Entity:
    """Базовый класс для всех сущностей."""
    def __init__(self, id: Optional[int] = None):
        self._id = id

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, value: int):
        self._id = value

    def to_dict(self) -> dict:
        raise NotImplementedError

    def display_info(self) -> str:
        return f"{self.__class__.__name__} (ID: {self._id})"


class Client(Entity):
    def __init__(self, name: str, email: str, phone: str,
                 registration_date: Optional[str] = None, id: Optional[int] = None):
        super().__init__(id)
        self._name = name
        self._email = email
        self._phone = phone
        self._registration_date = registration_date or datetime.now().isoformat()

    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> str:
        return self._email

    @property
    def phone(self) -> str:
        return self._phone

    @property
    def registration_date(self) -> str:
        return self._registration_date

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "registration_date": self.registration_date
        }

    def display_info(self) -> str:
        return f"Клиент: {self.name} (email: {self.email})"


class Product(Entity):
    def __init__(self, name: str, price: float, category: str, id: Optional[int] = None):
        super().__init__(id)
        self._name = name
        self._price = price
        self._category = category

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return self._price

    @property
    def category(self) -> str:
        return self._category

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category
        }

    def display_info(self) -> str:
        return f"Товар: {self.name} (цена: {self.price} руб.)"


class Order(Entity):
    def __init__(self, client_id: int, products: List[Tuple[int, int]],
                 order_date: Optional[str] = None, id: Optional[int] = None,
                 total_price: Optional[float] = None):
        super().__init__(id)
        self._client_id = client_id
        self._products = products
        self._order_date = order_date or datetime.now().isoformat()
        self._total_price = total_price

    @property
    def client_id(self) -> int:
        return self._client_id

    @property
    def products(self) -> List[Tuple[int, int]]:
        return self._products

    @property
    def order_date(self) -> str:
        return self._order_date

    @property
    def total_price(self) -> float:
        return self._total_price if self._total_price is not None else 0.0

    @total_price.setter
    def total_price(self, value: float):
        self._total_price = value

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "client_id": self.client_id,
            "products": self.products,
            "order_date": self.order_date,
            "total_price": self.total_price
        }

    def display_info(self) -> str:
        return f"Заказ №{self.id} от {self.order_date} на сумму {self.total_price} руб."