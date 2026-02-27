from app import app, db
from database import Product, Customer, Sale, User
import os

def init_db():
    """Полная перезапись базы данных"""
    
    # Путь к файлу базы данных
    db_path = 'trade.db'
    
    # Удаляем старый файл если существует
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Старый файл {db_path} удален")
    
    with app.app_context():
        # Создаем все таблицы заново
        db.create_all()
        print("Таблицы созданы успешно!")
        
        # Добавляем тестовых пользователей
        users = [
            User(username='admin', password='admin123', role='admin'),
            User(username='manager', password='manager123', role='manager'),
            User(username='storekeeper', password='store123', role='storekeeper'),
        ]
        db.session.add_all(users)
        db.session.flush()
        print("Пользователи добавлены")
        
        # Добавляем тестовые товары
        products = [
            Product(name='Ноутбук', price=45000, quantity=10),
            Product(name='Мышь', price=800, quantity=50),
            Product(name='Клавиатура', price=1500, quantity=30),
            Product(name='Монитор', price=12000, quantity=15),
            Product(name='Наушники', price=2500, quantity=25),
        ]
        db.session.add_all(products)
        db.session.flush()
        print("Товары добавлены")
        
        # Добавляем тестовых покупателей
        customers = [
            Customer(name='Иванов Иван', phone='+7 (999) 123-45-67', email='ivan@mail.ru'),
            Customer(name='Петров Петр', phone='+7 (999) 234-56-78', email='petr@mail.ru'),
            Customer(name='Сидорова Анна', phone='+7 (999) 345-67-89', email='anna@mail.ru'),
        ]
        db.session.add_all(customers)
        db.session.flush()
        print("Покупатели добавлены")
        
        # Сохраняем все изменения
        db.session.commit()
        print("Данные сохранены в БД")
        
        # Добавляем тестовые продажи
        sales = [
            Sale(product_id=1, customer_id=1, quantity=1, total_price=45000),
            Sale(product_id=2, customer_id=2, quantity=2, total_price=1600),
            Sale(product_id=3, customer_id=3, quantity=1, total_price=1500),
        ]
        db.session.add_all(sales)
        db.session.commit()
        print("Продажи добавлены")
        
        print("\n" + "="*50)
        print("✅ База данных успешно создана!")
        print("="*50)
        print("\n📋 Тестовые учетные записи:")
        print("   👑 admin / admin123 (Администратор)")
        print("   👔 manager / manager123 (Менеджер)")
        print("   📦 storekeeper / store123 (Кладовщик)")
        print("="*50)

if __name__ == '__main__':
    init_db()w