from flask import Flask, render_template, request, redirect, url_for, flash
from database import db, Product, Customer, Sale, init_db
from datetime import datetime, timedelta
from sqlalchemy import func

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trade.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Главная страница
@app.route('/')
def index():
    """Отображение главной страницы с краткой статистикой"""
    total_products = Product.query.count()
    total_customers = Customer.query.count()
    total_sales = Sale.query.count()
    
    # Выручка за сегодня
    today = datetime.now().date()
    today_sales = Sale.query.filter(
        func.date(Sale.sale_date) == today
    ).all()
    today_revenue = sum(sale.total_price for sale in today_sales)
    
    return render_template('index.html', 
                         total_products=total_products,
                         total_customers=total_customers,
                         total_sales=total_sales,
                         today_revenue=today_revenue)

# Управление товарами
@app.route('/products')
def products():
    """Список товаров"""
    all_products = Product.query.all()
    return render_template('products.html', products=all_products)

@app.route('/products/add', methods=['POST'])
def add_product():
    """Добавление товара"""
    name = request.form['name']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])
    
    product = Product(name=name, price=price, quantity=quantity)
    db.session.add(product)
    db.session.commit()
    
    flash('Товар успешно добавлен', 'success')
    return redirect(url_for('products'))

@app.route('/products/delete/<int:id>')
def delete_product(id):
    """Удаление товара"""
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    
    flash('Товар удален', 'success')
    return redirect(url_for('products'))

# Управление покупателями
@app.route('/customers')
def customers():
    """Список покупателей"""
    all_customers = Customer.query.all()
    return render_template('customers.html', customers=all_customers)

@app.route('/customers/add', methods=['POST'])
def add_customer():
    """Добавление покупателя"""
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    
    customer = Customer(name=name, phone=phone, email=email)
    db.session.add(customer)
    db.session.commit()
    
    flash('Покупатель успешно добавлен', 'success')
    return redirect(url_for('customers'))

# Продажи
@app.route('/sales')
def sales():
    """Список продаж и форма добавления"""
    all_sales = Sale.query.order_by(Sale.sale_date.desc()).all()
    products = Product.query.filter(Product.quantity > 0).all()
    customers = Customer.query.all()
    return render_template('sales.html', sales=all_sales, products=products, customers=customers)

@app.route('/sales/add', methods=['POST'])
def add_sale():
    """Добавление продажи"""
    product_id = int(request.form['product_id'])
    customer_id = int(request.form['customer_id'])
    quantity = int(request.form['quantity'])
    
    product = Product.query.get(product_id)
    
    # Проверка наличия товара
    if product.quantity < quantity:
        flash(f'Недостаточно товара! В наличии: {product.quantity}', 'danger')
        return redirect(url_for('sales'))
    
    # Расчет стоимости
    total_price = product.price * quantity
    
    # Уменьшаем количество товара
    product.quantity -= quantity
    
    # Создаем запись о продаже
    sale = Sale(
        product_id=product_id,
        customer_id=customer_id,
        quantity=quantity,
        total_price=total_price
    )
    
    db.session.add(sale)
    db.session.commit()
    
    flash('Продажа успешно оформлена', 'success')
    return redirect(url_for('sales'))

# Отчеты
@app.route('/reports', methods=['GET', 'POST'])
def reports():
    """Формирование отчетов за период"""
    report_data = None
    
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        end_date = end_date.replace(hour=23, minute=59, second=59)
        
        # Получаем продажи за период
        sales_period = Sale.query.filter(
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date
        ).order_by(Sale.sale_date).all()
        
        # Статистика
        total_sales = len(sales_period)
        total_revenue = sum(sale.total_price for sale in sales_period)
        
        # Топ товаров
        product_stats = {}
        for sale in sales_period:
            product_name = sale.product.name
            if product_name in product_stats:
                product_stats[product_name]['quantity'] += sale.quantity
                product_stats[product_name]['revenue'] += sale.total_price
            else:
                product_stats[product_name] = {
                    'quantity': sale.quantity,
                    'revenue': sale.total_price
                }
        
        report_data = {
            'start_date': start_date.strftime('%d.%m.%Y'),
            'end_date': request.form['end_date'],
            'sales': sales_period,
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'product_stats': product_stats
        }
    
    return render_template('reports.html', report=report_data)

if __name__ == '__main__':
    app.run(debug=True)