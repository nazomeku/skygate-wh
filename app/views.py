from flask import render_template, flash, request, redirect, url_for
from app import app, db
from .forms import ManageProduct
from .models import Product


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/products', methods=['GET', 'POST'])
def products():
    """Show current products and add products to database."""
    form = ManageProduct()
    if form.validate_on_submit():
        product = Product(name=form.name.data, quantity=form.quantity.data)
        db.session.add(product)
        db.session.commit()
        flash('You have successfully added the product.')
    all_products = Product.query.all()
    return render_template('products.html', form=form, products=all_products)


@app.route('/product/<int:product_id>')
def edit_product(product_id):
    """Edit page for product management."""
    product = Product.query.filter_by(id=product_id).first()
    return render_template('edit_product.html', product=product)


@app.route('/product/delete/<int:product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    """Delete product."""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('You have successfully deleted the product.')
    return redirect(url_for('products'))


@app.route('/product/update/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    """Update product."""
    product = Product.query.get_or_404(product_id)
    newname = request.form.get('newname')
    oldname = request.form.get('oldname')
    newquantity = request.form.get('newquantity')
    oldquantity = request.form.get('oldquantity')
    product = Product.query.filter_by(name=oldname).first()
    product = Product.query.filter_by(quantity=oldquantity).first()
    product.name = newname
    product.quantity = newquantity
    db.session.commit()
    flash('You have successfully updated the product.')
    return redirect(url_for('products'))


@app.route('/transports')
def transports():
    """Transport page."""
    return render_template('transports.html')
