import pytest
from database import db, Product, Customer, Sale
from datetime import datetime, timedelta

class TestRoutes:
    """Тестирование маршрутов приложения"""
    
    def test_index_page(self, client):
        """Тест загрузки главной страницы"""
        response = client.get('/')
        assert response.status_code == 200
        # Проверяем наличие любого текста на странице
        assert response.data is not None
    
    def test_products_page(self, client):
        """Тест просмотра списка товаров"""
        response = client.get('/products')
        assert response.status_code == 200
        assert response.data is not None
    
    def test_add_product(self, client, app):
        """Тест добавления нового товара"""
        response = client.post('/products/add', data={
            'name': 'Monitor',
            'price': 12000,
            'quantity': 15
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            product = Product.query.filter_by(name='Monitor').first()
            assert product is not None
            assert product.price == 12000
            assert product.quantity == 15
    
    def test_add_customer(self, client, app):
        """Тест добавления нового покупателя"""
        response = client.post('/customers/add', data={
            'name': 'New Customer',
            'phone': '+7 (999) 999-99-99',
            'email': 'new@test.ru'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            customer = Customer.query.filter_by(name='New Customer').first()
            assert customer is not None
            assert customer.phone == '+7 (999) 999-99-99'
            assert customer.email == 'new@test.ru'
    
    def test_add_sale_success(self, client, app, test_data):
        """Тест успешного оформления продажи"""
        with app.app_context():
            # Получаем свежие объекты
            product = Product.query.filter_by(name='Ноутбук').first()
            customer = Customer.query.filter_by(name='Иванов Иван').first()
            assert product is not None
            assert customer is not None
            initial_quantity = product.quantity
        
        response = client.post('/sales/add', data={
            'product_id': product.id,
            'customer_id': customer.id,
            'quantity': 2
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            db.session.expire_all()
            updated_product = Product.query.get(product.id)
            assert updated_product.quantity == initial_quantity - 2
    
    def test_add_sale_insufficient_stock(self, client, app, test_data):
        """Тест продажи с недостаточным количеством товара"""
        with app.app_context():
            product = Product.query.filter_by(name='Ноутбук').first()
            customer = Customer.query.filter_by(name='Иванов Иван').first()
            assert product is not None
            assert customer is not None
            initial_quantity = product.quantity
        
        response = client.post('/sales/add', data={
            'product_id': product.id,
            'customer_id': customer.id,
            'quantity': 100
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            db.session.expire_all()
            updated_product = Product.query.get(product.id)
            assert updated_product.quantity == initial_quantity  # Количество не изменилось
    
    def test_sales_page(self, client):
        """Тест страницы продаж"""
        response = client.get('/sales')
        assert response.status_code == 200
        assert response.data is not None
    
    def test_customers_page(self, client):
        """Тест страницы покупателей"""
        response = client.get('/customers')
        assert response.status_code == 200
        assert response.data is not None
    
    def test_reports_page(self, client):
        """Тест страницы отчетов"""
        response = client.get('/reports')
        assert response.status_code == 200
        assert response.data is not None
    
    def test_delete_product_without_sales(self, client, app):
        """Тест удаления товара без продаж"""
        with app.app_context():
            # Создаём временный товар
            product = Product(name='Temp Product', price=100, quantity=5)
            db.session.add(product)
            db.session.commit()
            product_id = product.id
        
        response = client.get(f'/products/delete/{product_id}', follow_redirects=True)
        assert response.status_code == 200
        
        with app.app_context():
            product = Product.query.get(product_id)
            assert product is None