import pytest
from database import db, Product, Customer, Sale
from datetime import datetime

class TestModels:
    """Тестирование моделей базы данных"""
    
    def test_create_product(self, app):
        """Тест создания товара"""
        with app.app_context():
            # Очищаем БД перед тестом
            Product.query.delete()
            db.session.commit()
            
            product = Product(name='Тестовый товар', price=1000, quantity=5)
            db.session.add(product)
            db.session.commit()
            
            saved_product = Product.query.first()
            assert saved_product.name == 'Тестовый товар'
            assert saved_product.price == 1000
            assert saved_product.quantity == 5
            assert isinstance(saved_product.created_at, datetime)
    
    def test_create_product_with_defaults(self, app):
        """Тест создания товара со значениями по умолчанию"""
        with app.app_context():
            Product.query.delete()
            db.session.commit()
            
            product = Product(name='Товар', price=500, quantity=0)
            db.session.add(product)
            db.session.commit()
            
            saved = Product.query.first()
            assert saved.name == 'Товар'
            assert saved.price == 500
            assert saved.quantity == 0
    
    def test_create_customer(self, app):
        """Тест создания покупателя"""
        with app.app_context():
            Customer.query.delete()
            db.session.commit()
            
            customer = Customer(
                name='Тестовый Покупатель',
                phone='+7 (999) 111-22-33',
                email='test@test.ru'
            )
            db.session.add(customer)
            db.session.commit()
            
            saved = Customer.query.first()
            assert saved.name == 'Тестовый Покупатель'
            assert saved.phone == '+7 (999) 111-22-33'
            assert saved.email == 'test@test.ru'
            assert isinstance(saved.created_at, datetime)
    
    def test_create_customer_without_phone(self, app):
        """Тест создания покупателя без телефона"""
        with app.app_context():
            Customer.query.delete()
            db.session.commit()
            
            customer = Customer(name='Без Телефона', email='no-phone@test.ru')
            db.session.add(customer)
            db.session.commit()
            
            saved = Customer.query.first()
            assert saved.name == 'Без Телефона'
            assert saved.phone is None
            assert saved.email == 'no-phone@test.ru'
    
    def test_create_sale(self, app, test_data):
        """Тест создания продажи"""
        with app.app_context():
            product = Product.query.first()
            customer = Customer.query.first()
            
            sale = Sale(
                product_id=product.id,
                customer_id=customer.id,
                quantity=3,
                total_price=product.price * 3
            )
            db.session.add(sale)
            db.session.commit()
            
            saved = Sale.query.filter_by(id=sale.id).first()
            assert saved.quantity == 3
            assert saved.total_price == product.price * 3
            assert saved.product_id == product.id
            assert saved.customer_id == customer.id
            assert isinstance(saved.sale_date, datetime)
    
    def test_product_relationships(self, app, test_data):
        """Тест связей товара"""
        with app.app_context():
            product = Product.query.filter_by(name='Ноутбук').first()
            assert product is not None
            assert len(product.sales) > 0
            assert isinstance(product.sales[0], Sale)
    
    def test_customer_relationships(self, app, test_data):
        """Тест связей покупателя"""
        with app.app_context():
            customer = Customer.query.filter_by(name='Иванов Иван').first()
            assert customer is not None
            assert len(customer.sales) > 0
            assert isinstance(customer.sales[0], Sale)
    
    def test_sale_relationships(self, app, test_data):
        """Тест связей продажи"""
        with app.app_context():
            sale = Sale.query.first()
            assert sale is not None
            assert isinstance(sale.product, Product)
            assert isinstance(sale.customer, Customer)
            assert sale.product.name is not None
            assert sale.customer.name is not None
    
    def test_product_str_representation(self):
        """Тест строкового представления товара"""
        product = Product(name='Мышь', price=800, quantity=50)
        assert str(product) == '<Product Мышь>'
    
    def test_customer_str_representation(self):
        """Тест строкового представления покупателя"""
        customer = Customer(name='Иванов Иван')
        assert str(customer) == '<Customer Иванов Иван>'
    
    def test_sale_str_representation(self, app, test_data):
        """Тест строкового представления продажи"""
        with app.app_context():
            sale = Sale.query.first()
            assert sale is not None
            assert str(sale).startswith('<Sale')