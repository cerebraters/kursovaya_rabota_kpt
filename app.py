from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db, Product, Customer, Sale, User
from datetime import datetime
from sqlalchemy import func
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trade.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Включаем проверку внешних ключей для SQLite
@app.before_request
def before_request():
    if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
        db.session.execute(db.text('PRAGMA foreign_keys=ON'))

# Декораторы для проверки ролей
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'admin':
            flash('Доступ запрещен. Требуются права администратора', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def manager_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] not in ['admin', 'manager']:
            flash('Доступ запрещен. Требуются права менеджера или администратора', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Авторизация
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role
            flash(f'Добро пожаловать, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

# Главная страница
@app.route('/')
@login_required
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
                         today_revenue=today_revenue,
                         user_role=session.get('user_role'))

# Управление товарами
@app.route('/products')
@login_required
def products():
    """Список товаров"""
    all_products = Product.query.all()
    return render_template('products.html', products=all_products, user_role=session.get('user_role'))

@app.route('/products/add', methods=['POST'])
@manager_or_admin_required
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

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@manager_or_admin_required
def edit_product(id):
    """Редактирование товара"""
    product = db.session.get(Product, id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = float(request.form['price'])
        product.quantity = int(request.form['quantity'])
        
        db.session.commit()
        flash('Товар успешно обновлен', 'success')
        return redirect(url_for('products'))
    
    return render_template('edit_product.html', product=product, user_role=session.get('user_role'))

@app.route('/products/delete/<int:id>')
@admin_required
def delete_product(id):
    """Удаление товара"""
    product = db.session.get(Product, id)
    
    # Проверяем, есть ли продажи у этого товара
    sales_count = Sale.query.filter_by(product_id=id).count()
    if sales_count > 0:
        flash('Нельзя удалить товар, по которому были продажи', 'danger')
        return redirect(url_for('products'))
    
    if product:
        db.session.delete(product)
        db.session.commit()
        flash('Товар удален', 'success')
    else:
        flash('Товар не найден', 'danger')
    return redirect(url_for('products'))

# Управление покупателями
@app.route('/customers')
@login_required
def customers():
    """Список покупателей"""
    all_customers = Customer.query.all()
    return render_template('customers.html', customers=all_customers, user_role=session.get('user_role'))

@app.route('/customers/add', methods=['POST'])
@manager_or_admin_required
def add_customer():
    """Добавление покупателя"""
    name = request.form['name']
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    
    customer = Customer(name=name, phone=phone, email=email)
    db.session.add(customer)
    db.session.commit()
    
    flash('Покупатель успешно добавлен', 'success')
    return redirect(url_for('customers'))

@app.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
@manager_or_admin_required
def edit_customer(id):
    """Редактирование покупателя"""
    customer = db.session.get(Customer, id)
    
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.phone = request.form.get('phone', '')
        customer.email = request.form.get('email', '')
        
        db.session.commit()
        flash('Покупатель успешно обновлен', 'success')
        return redirect(url_for('customers'))
    
    return render_template('edit_customer.html', customer=customer, user_role=session.get('user_role'))

@app.route('/customers/delete/<int:id>')
@admin_required
def delete_customer(id):
    """Удаление покупателя"""
    customer = db.session.get(Customer, id)
    
    # Проверяем, есть ли продажи у этого покупателя
    sales_count = Sale.query.filter_by(customer_id=id).count()
    if sales_count > 0:
        flash('Нельзя удалить покупателя, у которого были продажи', 'danger')
        return redirect(url_for('customers'))
    
    if customer:
        db.session.delete(customer)
        db.session.commit()
        flash('Покупатель удален', 'success')
    else:
        flash('Покупатель не найден', 'danger')
    return redirect(url_for('customers'))

# Продажи
@app.route('/sales')
@login_required
def sales():
    """Список продаж и форма добавления"""
    all_sales = Sale.query.order_by(Sale.sale_date.desc()).all()
    products = Product.query.filter(Product.quantity > 0).all()
    customers = Customer.query.all()
    return render_template('sales.html', sales=all_sales, products=products, 
                          customers=customers, user_role=session.get('user_role'))

@app.route('/sales/add', methods=['POST'])
@manager_or_admin_required
def add_sale():
    """Добавление продажи"""
    product_id = int(request.form['product_id'])
    customer_id = int(request.form['customer_id'])
    quantity = int(request.form['quantity'])
    
    product = db.session.get(Product, product_id)
    
    if not product:
        flash('Товар не найден', 'danger')
        return redirect(url_for('sales'))
    
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
@login_required
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
    
    return render_template('reports.html', report=report_data, user_role=session.get('user_role'))

# Управление пользователями (только для админа)
@app.route('/users')
@admin_required
def users():
    """Список пользователей"""
    all_users = User.query.all()
    return render_template('users.html', users=all_users, session=session)

@app.route('/users/add', methods=['POST'])
@admin_required
def add_user():
    """Добавление пользователя"""
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    
    # Проверка на существующего пользователя
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash('Пользователь с таким именем уже существует', 'danger')
        return redirect(url_for('users'))
    
    user = User(username=username, password=password, role=role)
    db.session.add(user)
    db.session.commit()
    
    flash('Пользователь успешно добавлен', 'success')
    return redirect(url_for('users'))

@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    """Редактирование пользователя"""
    user = db.session.get(User, id)
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.password = request.form['password']
        user.role = request.form['role']
        
        db.session.commit()
        flash('Пользователь успешно обновлен', 'success')
        return redirect(url_for('users'))
    
    return render_template('edit_user.html', user=user)

@app.route('/users/delete/<int:id>')
@admin_required
def delete_user(id):
    """Удаление пользователя"""
    user = db.session.get(User, id)
    
    # Нельзя удалить самого себя
    if user.id == session.get('user_id'):
        flash('Нельзя удалить свою учетную запись', 'danger')
        return redirect(url_for('users'))
    
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь удален', 'success')
    else:
        flash('Пользователь не найден', 'danger')
    return redirect(url_for('users'))

# Создание таблиц при запуске
def create_tables():
    with app.app_context():
        db.create_all()
        print("Таблицы созданы/проверены")

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)