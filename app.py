from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import uuid
from products.data import products
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, PointLog


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# ...existing code...
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        disclaimer = request.form.get('disclaimer')
        if not disclaimer:
            flash('請勾選同意會員聲明')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('帳號已存在')
            return render_template('register.html')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('註冊成功，請登入')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            flash('登入成功')
            return redirect(url_for('profile'))
        else:
            flash('帳號或密碼錯誤')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已登出')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    logs = PointLog.query.filter_by(user_id=current_user.id).order_by(PointLog.timestamp.desc()).all()
    return render_template('profile.html', user=current_user, logs=logs)

@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')

# 管理員點數管理
@app.route('/admin/points', methods=['GET', 'POST'], endpoint='admin_points')
@login_required
def admin_points():
    if current_user.username != ADMIN_USERNAME:
        flash('只有管理員可以操作')
        return redirect(url_for('index'))
    users = User.query.all()
    selected_user = None
    search_user = None
    search_logs = []
    search_username = request.args.get('search_username')
    if request.method == 'GET' and search_username:
        search_user = User.query.filter_by(username=search_username).first()
        if search_user:
            search_logs = PointLog.query.filter_by(user_id=search_user.id).order_by(PointLog.timestamp.desc()).all()
        else:
            flash('查無此會員')
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'search':
            username = request.form.get('user_search')
            selected_user = User.query.filter_by(username=username).first()
            if not selected_user:
                flash('查無此會員')
        elif action == 'update':
            user_id = request.form['user_id']
            change = int(request.form['change'])
            reason = request.form['reason']
            selected_user = User.query.get(user_id)
            if selected_user:
                selected_user.points += change
                log = PointLog(user_id=selected_user.id, change=change, reason=reason)
                db.session.add(log)
                db.session.commit()
                flash('點數已更新')
            else:
                flash('找不到會員')
    return render_template('admin_points.html', users=users, selected_user=selected_user, search_user=search_user, search_logs=search_logs, search_username=search_username)

ADMIN_USERNAME = 'pooh13515'
ADMIN_PASSWORD = '9608739'

app.jinja_env.globals.update(enumerate=enumerate)

# 新增：商品資料寫回 data.py 的函式
def save_products():
    with open('products/data.py', 'w', encoding='utf-8') as f:
        f.write('products = ' + repr(products))

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product(product_id):
    product = products[product_id]
    return render_template('product.html', product=product)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            admin_user = User.query.filter_by(username=ADMIN_USERNAME).first()
            if not admin_user:
                admin_user = User(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
                db.session.add(admin_user)
                db.session.commit()
            login_user(admin_user)
            return redirect(url_for('admin'))
        else:
            return render_template('admin_login.html', error='帳號或密碼錯誤')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


@app.route('/admin/upload_logo', methods=['POST'])
@login_required
def upload_logo():
    if current_user.username != ADMIN_USERNAME:
        return redirect(url_for('login'))
    if 'logo' not in request.files:
        flash('沒有選擇檔案')
        return redirect(url_for('admin'))
    file = request.files['logo']
    if file.filename == '':
        flash('沒有選擇檔案')
        return redirect(url_for('admin'))
    if file:
        logo_folder = os.path.join('static', 'images')
        os.makedirs(logo_folder, exist_ok=True)
        logo_path = os.path.join(logo_folder, 'logo.png')
        file.save(logo_path)
        flash('Logo 上傳成功')
    return redirect(url_for('admin'))

@app.route('/admin')
@login_required
def admin():
    if current_user.username != ADMIN_USERNAME:
        return redirect(url_for('login'))
    return render_template('admin.html', products=products)

@app.route('/admin/add', methods=['POST'])
def add_product():
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    category = request.form['category']
    images = []
    for i in range(1, 4):
        image = request.files.get(f'image{i}')
        if image and image.filename:
            image_folder = app.config['UPLOAD_FOLDER']
            os.makedirs(image_folder, exist_ok=True)
            image_filename = f"{uuid.uuid4().hex}_{image.filename}"
            image_path = os.path.join(image_folder, image_filename)
            image.save(image_path)
            images.append(f'static/images/{image_filename}')
    # 新增商品
    products.append({
        'name': name,
        'description': description,
        'price': price,
        'images': images,
        'category': category
    })
    save_products()
    return redirect(url_for('admin'))

@app.route('/admin/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        images = products[product_id]['images'] if 'images' in products[product_id] else []
        for i in range(1, 4):
            image = request.files.get(f'image{i}')
            if image and image.filename:
                image_folder = app.config['UPLOAD_FOLDER']
                os.makedirs(image_folder, exist_ok=True)
                image_filename = f"{uuid.uuid4().hex}_{image.filename}"
                image_path = os.path.join(image_folder, image_filename)
                image.save(image_path)
                if len(images) >= i:
                    if len(images) == i:
                        images.append(f'static/images/{image_filename}')
                    else:
                        images[i-1] = f'static/images/{image_filename}'
                else:
                    images.append(f'static/images/{image_filename}')
        products[product_id]['name'] = name
        products[product_id]['description'] = description
        products[product_id]['price'] = price
        products[product_id]['category'] = category
        products[product_id]['images'] = images
        save_products()
        return redirect(url_for('admin'))
    product = products[product_id]
    return render_template('admin_edit.html', product=product, product_id=product_id)

@app.route('/admin/delete/<int:product_id>')
def delete_product(product_id):
    products.pop(product_id)
    save_products()
    return redirect(url_for('admin'))

@app.route('/category/<category>')
def category_page(category):
    filtered = [p for p in products if p.get('category') == category]
    return render_template('category.html', products=filtered, category=category)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)