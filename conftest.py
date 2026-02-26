import pytest
from app import app as flask_app
from database import db, Product, Customer, Sale
from datetime import datetime

@pytest.fixture
def app():
    """Создание тестового приложения"""
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['WTF_CSRF_ENABLED'] = False
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Тестовый клиент"""
    return app.test_client()

@pytest.fixture
def test_data(app):
    """Создание тестовых данных"""
    with app.app_context():
        # Товары
        product1 = Product(name='Ноутбук', price=45000, quantity=10)
        product2 = Product(name='Мышь', price=800, quantity=50)
        db.session.add_all([product1, product2])
        
        # Покупатели
        customer1 = Customer(name='Иванов Иван', phone='1234567890', email='ivan@test.ru')
        customer2 = Customer(name='Петров Петр', phone='0987654321', email='petr@test.ru')
        db.session.add_all([customer1, customer2])
        db.session.commit()
        
        # Продажи
        sale1 = Sale(product_id=product1.id, customer_id=customer1.id, 
                    quantity=2, total_price=90000)
        sale2 = Sale(product_id=product2.id, customer_id=customer2.id, 
                    quantity=5, total_price=4000)
        db.session.add_all([sale1, sale2])
        db.session.commit()
        
        return {
            'products': [product1, product2],
            'customers': [customer1, customer2],
            'sales': [sale1, sale2]
        }