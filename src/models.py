"""
src/models.py

Модуль содержит классы данных для предметной области:
- Entity (базовый класс)
- Client
- Product
- Order

Все классы реализуют инкапсуляцию, наследование и полиморфизм.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Tuple, Optional


class Entity(ABC):
    """
    Абстрактный базовый класс для всех сущностей системы.

    Атрибуты
    ----------
    _id : int
        Уникальный идентификатор сущности.
    _name : str
        Название сущности (имя клиента, название товара и т.д.).
    """

    def __init__(self, entity_id: int, name: str) -> None:
        self._id = entity_id
        self._name = name

    @property
    def id(self) -> int:
        """Возвращает идентификатор сущности."""
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        """Устанавливает идентификатор сущности."""
        self._id = value

    @property
    def name(self) -> str:
        """Возвращает имя сущности."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Устанавливает имя сущности."""
        self._name = value

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Преобразует объект в словарь для сериализации.

        Returns
        -------
        dict
            Словарь с данными сущности.
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id}, name='{self._name}')"


class Client(Entity):
    """
    Класс, представляющий клиента интернет-магазина.

    Атрибуты
    ----------
    _email : str
        Адрес электронной почты клиента.
    _phone : str
        Номер телефона клиента.
    _registration_date : str
        Дата регистрации в формате YYYY-MM-DD.
    """

    def __init__(
        self,
        client_id: int,
        name: str,
        email: str,
        phone: str,
        registration_date: Optional[str] = None
    ) -> None:
        """
        Инициализирует клиента.

        Parameters
        ----------
        client_id : int
            Уникальный идентификатор клиента.
        name : str
            Полное имя клиента.
        email : str
            Электронная почта.
        phone : str
            Номер телефона.
        registration_date : str, optional
            Дата регистрации в формате YYYY-MM-DD. Если не указана,
            устанавливается текущая дата.
        """
        super().__init__(client_id, name)
        self._email = email
        self._phone = phone
        if registration_date is None:
            self._registration_date = datetime.now().strftime("%Y-%m-%d")
        else:
            self._registration_date = registration_date

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        self._email = value

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        self._phone = value

    @property
    def registration_date(self) -> str:
        return self._registration_date

    @registration_date.setter
    def registration_date(self, value: str) -> None:
        self._registration_date = value

    def to_dict(self) -> dict:
        """
        Преобразует клиента в словарь.

        Returns
        -------
        dict
            Словарь с ключами: id, name, email, phone, registration_date.
        """
        return {
            "id": self._id,
            "name": self._name,
            "email": self._email,
            "phone": self._phone,
            "registration_date": self._registration_date,
        }

    def __repr__(self) -> str:
        return (f"Client(id={self._id}, name='{self._name}', "
                f"email='{self._email}', phone='{self._phone}')")


class Product(Entity):
    """
    Класс, представляющий товар в каталоге.

    Атрибуты
    ----------
    _price : float
        Цена товара.
    _category : str
        Категория товара.
    """

    def __init__(self, product_id: int, name: str, price: float, category: str) -> None:
        """
        Инициализирует товар.

        Parameters
        ----------
        product_id : int
            Уникальный идентификатор товара.
        name : str
            Название товара.
        price : float
            Цена товара (положительное число).
        category : str
            Категория товара (например, "Электроника").
        """
        super().__init__(product_id, name)
        self._price = price
        self._category = category

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        if value < 0:
            raise ValueError("Цена не может быть отрицательной.")
        self._price = value

    @property
    def category(self) -> str:
        return self._category

    @category.setter
    def category(self, value: str) -> None:
        self._category = value

    def to_dict(self) -> dict:
        """
        Преобразует товар в словарь.

        Returns
        -------
        dict
            Словарь с ключами: id, name, price, category.
        """
        return {
            "id": self._id,
            "name": self._name,
            "price": self._price,
            "category": self._category,
        }

    def __repr__(self) -> str:
        return (f"Product(id={self._id}, name='{self._name}', "
                f"price={self._price}, category='{self._category}')")


class Order(Entity):
    """
    Класс, представляющий заказ клиента.

    Атрибуты
    ----------
    _client_id : int
        Идентификатор клиента, сделавшего заказ.
    _items : List[Tuple[int, int]]
        Список кортежей (product_id, quantity).
    _order_date : str
        Дата оформления заказа в формате YYYY-MM-DD.
    _total_price : float
        Общая стоимость заказа (вычисляется автоматически).
    """

    def __init__(
        self,
        order_id: int,
        client_id: int,
        items: List[Tuple[int, int]],
        order_date: Optional[str] = None,
        total_price: Optional[float] = None
    ) -> None:
        """
        Инициализирует заказ.

        Parameters
        ----------
        order_id : int
            Уникальный идентификатор заказа.
        client_id : int
            Идентификатор клиента.
        items : List[Tuple[int, int]]
            Список товаров в заказе, где каждый элемент – кортеж (product_id, quantity).
        order_date : str, optional
            Дата заказа в формате YYYY-MM-DD. Если не указана, устанавливается сегодня.
        total_price : float, optional
            Если передана, используется как общая стоимость; иначе вычисляется из items и цен товаров.
            (Для корректного вычисления в конструкторе нужен доступ к каталогу товаров,
            поэтому мы делаем этот параметр опциональным и вычисляем отдельно.)
        """
        super().__init__(order_id, f"Order {order_id}")
        self._client_id = client_id
        self._items = items[:]  # копируем, чтобы избежать мутаций извне
        if order_date is None:
            self._order_date = datetime.now().strftime("%Y-%m-%d")
        else:
            self._order_date = order_date

        # Если total_price не передан, вычисляем его позже через отдельный метод.
        # Для простоты пока присваиваем None, а вычисление вынесем в отдельный метод,
        # который будет использовать каталог товаров (но в данной модели мы не храним каталог).
        # Поэтому мы просто сохраняем переданное значение, а если None, то ставим 0.0
        # и предоставляем метод для пересчёта.
        if total_price is None:
            self._total_price = 0.0
        else:
            self._total_price = total_price

    @property
    def client_id(self) -> int:
        return self._client_id

    @client_id.setter
    def client_id(self, value: int) -> None:
        self._client_id = value

    @property
    def items(self) -> List[Tuple[int, int]]:
        return self._items.copy()

    def add_item(self, product_id: int, quantity: int) -> None:
        """Добавляет товар в заказ или увеличивает его количество."""
        for i, (pid, qty) in enumerate(self._items):
            if pid == product_id:
                self._items[i] = (pid, qty + quantity)
                return
        self._items.append((product_id, quantity))

    @property
    def order_date(self) -> str:
        return self._order_date

    @order_date.setter
    def order_date(self, value: str) -> None:
        self._order_date = value

    @property
    def total_price(self) -> float:
        return self._total_price

    def recalculate_total(self, product_prices: dict) -> None:
        """
        Пересчитывает общую стоимость заказа на основе переданного словаря цен товаров.

        Parameters
        ----------
        product_prices : dict
            Словарь вида {product_id: price}
        """
        total = 0.0
        for product_id, quantity in self._items:
            price = product_prices.get(product_id, 0.0)
            total += price * quantity
        self._total_price = total

    def to_dict(self) -> dict:
        """
        Преобразует заказ в словарь.

        Returns
        -------
        dict
            Словарь с ключами: id, client_id, items, order_date, total_price.
        """
        return {
            "id": self._id,
            "client_id": self._client_id,
            "items": self._items,  # список кортежей
            "order_date": self._order_date,
            "total_price": self._total_price,
        }

    def __repr__(self) -> str:
        return (f"Order(id={self._id}, client_id={self._client_id}, "
                f"items={self._items}, total={self._total_price})")