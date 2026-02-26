import pytest
from database import db, Product, Customer, Sale
from datetime import datetime

class TestIntegration:
    """Интеграционные тесты"""
    
    def test_complete_sales_workflow(self, client, app):
        """Тест полного цикла работы с продажей"""
        
        # Добавляем товар
        client.post('/products/add', data={
            'name': 'Integration Product',
            'price': 5000,
            'quantity': 10
        })
        
        # Добавляем покупателя
        client.post('/customers/add', data={
            'name': 'Integration Customer',
            'phone': '+7 (999) 888-77-66',
            'email': 'integ@test.ru'
        })
        
        with app.app_context():
            product = Product.query.filter_by(name='Integration Product').first()
            customer = Customer.query.filter_by(name='Integration Customer').first()
            assert product is not None
            assert customer is not None
            initial_quantity = product.quantity
        
        # Оформляем продажу
        response = client.post('/sales/add', data={
            'product_id': product.id,
            'customer_id': customer.id,
            'quantity': 3
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            db.session.expire_all()
            updated_product = db.session.get(Product, product.id)
            assert updated_product.quantity == initial_quantity - 3
            
            sale = Sale.query.filter_by(product_id=product.id).order_by(Sale.id.desc()).first()
            assert sale is not None
            assert sale.quantity == 3
            assert sale.total_price == 5000 * 3
    
    def test_multiple_sales_same_product(self, client, app, test_data):
        """Тест нескольких продаж одного товара"""
        
        with app.app_context():
            product = Product.query.filter_by(name='Ноутбук').first()
            customer = Customer.query.filter_by(name='Иванов Иван').first()
            assert product is not None
            assert customer is not None
            initial_quantity = product.quantity
        
        quantities = [2, 1, 3]
        for qty in quantities:
            response = client.post('/sales/add', data={
                'product_id': product.id,
                'customer_id': customer.id,
                'quantity': qty
            }, follow_redirects=True)
            assert response.status_code == 200
        
        with app.app_context():
            db.session.expire_all()
            updated_product = db.session.get(Product, product.id)
            assert updated_product.quantity == initial_quantity - sum(quantities)
            
            # Проверяем что создалось правильное количество продаж
            sales_count = Sale.query.filter_by(product_id=product.id).count()
            assert sales_count >= len(quantities)
    
    def test_product_appears_after_add(self, client, app):
        """Тест появления товара после добавления"""
        
        # Добавляем товар
        client.post('/products/add', data={
            'name': 'Visible Product',
            'price': 999,
            'quantity': 7
        })
        
        # Проверяем что товар появился в БД
        with app.app_context():
            product = Product.query.filter_by(name='Visible Product').first()
            assert product is not None
            assert product.price == 999
            assert product.quantity == 7
    
    def test_customer_appears_after_add(self, client, app):
        """Тест появления покупателя после добавления"""
        
        # Добавляем покупателя
        client.post('/customers/add', data={
            'name': 'Visible Customer',
            'phone': '+7 (999) 111-22-33',
            'email': 'visible@test.ru'
        })
        
        # Проверяем что покупатель появился в БД
        with app.app_context():
            customer = Customer.query.filter_by(name='Visible Customer').first()
            assert customer is not None
            assert customer.phone == '+7 (999) 111-22-33'
            assert customer.email == 'visible@test.ru'
    
    def test_sale_appears_after_add(self, client, app, test_data):
        """Тест появления продажи после оформления"""
        
        with app.app_context():
            product = Product.query.filter_by(name='Ноутбук').first()
            customer = Customer.query.filter_by(name='Иванов Иван').first()
            initial_sales_count = Sale.query.count()
        
        # Оформляем продажу
        client.post('/sales/add', data={
            'product_id': product.id,
            'customer_id': customer.id,
            'quantity': 1
        })
        
        # Проверяем что продажа появилась
        with app.app_context():
            assert Sale.query.count() == initial_sales_count + 1