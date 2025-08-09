from flask import Blueprint, render_template, request, redirect, url_for
import os

admin_bp = Blueprint('admin', __name__)

PRODUCTS_FILE = 'products/data.py'
IMAGE_FOLDER = 'static/images'

def load_products():
    from products.data import products
    return products

def save_products(products):
    with open(PRODUCTS_FILE, 'w') as f:
        f.write('products = ' + str(products))

@admin_bp.route('/admin')
def admin_index():
    products = load_products()
    return render_template('admin.html', products=products)

@admin_bp.route('/admin/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image = request.files['image']
        image_path = os.path.join(IMAGE_FOLDER, image.filename)
        image.save(image_path)

        products = load_products()
        products.append({
            'name': name,
            'description': description,
            'price': price,
            'image': image_path
        })
        save_products(products)
        return redirect(url_for('admin.admin_index'))
    return render_template('admin_edit.html')

@admin_bp.route('/admin/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    products = load_products()
    product = products[product_id]

    if request.method == 'POST':
        product['name'] = request.form['name']
        product['description'] = request.form['description']
        product['price'] = request.form['price']
        
        if 'image' in request.files:
            image = request.files['image']
            image_path = os.path.join(IMAGE_FOLDER, image.filename)
            image.save(image_path)
            product['image'] = image_path

        save_products(products)
        return redirect(url_for('admin.admin_index'))

    return render_template('admin_edit.html', product=product, product_id=product_id)

@admin_bp.route('/admin/delete/<int:product_id>')
def delete_product(product_id):
    products = load_products()
    products.pop(product_id)
    save_products(products)
    return redirect(url_for('admin.admin_index'))