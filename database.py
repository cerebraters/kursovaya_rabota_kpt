from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    """Модель товара"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Связь с продажами
    sales = db.relationship('Sale', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Customer(db.Model):
    """Модель покупателя"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Связь с продажами
    sales = db.relationship('Sale', backref='customer', lazy=True)
    
    def __repr__(self):
        return f'<Customer {self.name}>'

class Sale(db.Model):
    """Модель продажи"""
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Sale {self.id}>'

def init_db():
    """Инициализация базы данных"""
    from app import app
    with app.app_context():
        db.create_all()
        print("Таблицы созданы")
        
        # Добавляем тестовые данные
        if Product.query.count() == 0:
            # Товары
            products = [
                Product(name='Ноутбук', price=45000, quantity=10),
                Product(name='Мышь', price=800, quantity=50),
                Product(name='Клавиатура', price=1500, quantity=30),
                Product(name='Монитор', price=12000, quantity=15),
                Product(name='Наушники', price=2500, quantity=25),
            ]
            db.session.add_all(products)
            
            # Покупатели
            customers = [
                Customer(name='Иванов Иван', phone='+7 (999) 123-45-67', email='ivan@mail.ru'),
                Customer(name='Петров Петр', phone='+7 (999) 234-56-78', email='petr@mail.ru'),
                Customer(name='Сидорова Анна', phone='+7 (999) 345-67-89', email='anna@mail.ru'),
            ]
            db.session.add_all(customers)
            db.session.commit()
            
            # Продажи
            sales = [
                Sale(product_id=1, customer_id=1, quantity=1, total_price=45000),
                Sale(product_id=2, customer_id=2, quantity=2, total_price=1600),
                Sale(product_id=3, customer_id=3, quantity=1, total_price=1500),
            ]
            db.session.add_all(sales)
            db.session.commit()
            
            print("Тестовые данные добавлены")