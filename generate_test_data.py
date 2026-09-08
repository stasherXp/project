import json
import random
from datetime import datetime, timedelta

# ------------------- НАСТРОЙКИ (меняйте здесь) -------------------
NUM_CLIENTS = 30      # Сколько клиентов сгенерировать
NUM_PRODUCTS = 40     # Сколько товаров
NUM_ORDERS = 20       # Сколько заказов
OUTPUT_FILE = "big_data.json"   # Имя выходного файла
# ----------------------------------------------------------------

# ------------------- Данные для генерации -------------------
first_names = [
    "Александр", "Дмитрий", "Максим", "Сергей", "Андрей", "Алексей", "Иван", "Евгений",
    "Владимир", "Николай", "Михаил", "Павел", "Артём", "Роман", "Олег", "Глеб", "Виталий",
    "Анна", "Мария", "Екатерина", "Ольга", "Татьяна", "Светлана", "Наталья", "Елена",
    "Ирина", "Полина", "Людмила", "Ксения", "Надежда", "Юлия"
]
last_names = [
    "Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попов", "Лебедев", "Козлов",
    "Новиков", "Морозов", "Фёдоров", "Егоров", "Волков", "Зайцев", "Павлов", "Романов",
    "Семёнов", "Голубев", "Тихонов", "Михайлов", "Никитин", "Крылов", "Григорьев", "Осипов",
    "Филиппов", "Сорокин", "Макаров", "Беляев", "Шевцов", "Карпов"
]
categories = ["Электроника", "Бытовая техника", "Компьютеры", "Телефоны", "Аксессуары", "Одежда", "Обувь", "Спорт"]
product_names = [
    "Смартфон", "Ноутбук", "Планшет", "Наушники", "Колонка", "Телевизор", "Холодильник",
    "Стиральная машина", "Пылесос", "Кофемашина", "Микроволновка", "Духовка", "Посудомоечная машина",
    "Видеокарта", "Процессор", "Материнская плата", "Оперативная память", "Жёсткий диск", "SSD",
    "Блок питания", "Корпус", "Клавиатура", "Мышь", "Монитор", "Кресло", "Стол", "Принтер",
    "Сканер", "МФУ", "Роутер", "Web-камера", "Микрофон", "Джойстик", "Видеорегистратор", "GPS-навигатор",
    "Электронная книга", "Умные часы", "Фитнес-браслет", "Электрическая зубная щётка", "Робот-пылесос"
]

# ------------------- Генерация клиентов -------------------
def generate_client(client_id):
    name = random.choice(first_names) + " " + random.choice(last_names)
    email = name.split()[0].lower() + "." + name.split()[1].lower() + str(random.randint(1, 999)) + "@mail.ru"
    phone = f"+7 {random.randint(900, 999)} {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"
    reg_date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
    return {
        "id": client_id,
        "name": name,
        "email": email,
        "phone": phone,
        "registration_date": reg_date
    }

clients = [generate_client(i) for i in range(1, NUM_CLIENTS + 1)]

# ------------------- Генерация товаров -------------------
def generate_product(product_id):
    name = random.choice(product_names) + " " + random.choice(["Pro", "Max", "Lite", "Plus", "Ultra", "Mini", ""])
    price = round(random.uniform(500, 150000), 2)
    category = random.choice(categories)
    return {
        "id": product_id,
        "name": name.strip(),
        "price": price,
        "category": category
    }

products = [generate_product(i) for i in range(1, NUM_PRODUCTS + 1)]

# ------------------- Генерация заказов -------------------
def generate_order(order_id):
    client_id = random.randint(1, NUM_CLIENTS)
    order_date = (datetime.now() - timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d")
    # выбираем от 1 до 5 разных товаров
    max_items = min(5, NUM_PRODUCTS)  # чтобы не было ошибки, если товаров мало
    num_items = random.randint(1, max(1, max_items))
    selected_products = random.sample(products, num_items)
    items = []
    total = 0
    for p in selected_products:
        qty = random.randint(1, 5)
        items.append({
            "product_id": p["id"],
            "product_name": p["name"],
            "quantity": qty,
            "price": p["price"]
        })
        total += p["price"] * qty
    total = round(total, 2)
    return {
        "id": order_id,
        "client_id": client_id,
        "order_date": order_date,
        "total_price": total,
        "items": items
    }

orders = [generate_order(i) for i in range(1, NUM_ORDERS + 1)]

# ------------------- Собираем всё в один словарь -------------------
data = {
    "clients": clients,
    "products": products,
    "orders": orders
}

# ------------------- Сохраняем в JSON -------------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Файл {OUTPUT_FILE} создан.")
print(f"Клиентов: {len(clients)}, товаров: {len(products)}, заказов: {len(orders)}.")