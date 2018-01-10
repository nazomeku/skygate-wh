from flask import render_template, flash, request, redirect, url_for
from . import app, db
from .forms import ManageProduct
from .models import Product, Transport, Shelf
from .services import sv_random_fill, sv_sort_shelfs, sv_transfer, sv_update_shelfs, sv_update_product


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/shelfs')
def shelfs():
    """Shelfs page."""
    all_products = Product.query.all()
    all_shelfs = Shelf.query.all()
    return render_template('shelfs.html', all_products=all_products, shelfs=all_shelfs)


@app.route('/edit_shelfs', methods=['GET', 'POST'])
def edit_shelfs():
    """Edit shelfs."""
    all_products = Product.query.all()
    all_shelfs = Shelf.query.all()
    id_list = []
    for i in range(len(all_products)):
        id_list.append(all_products[i].id)
    return render_template('edit_shelfs.html', all_products=all_products, shelfs=all_shelfs, id_list=id_list)


@app.route('/update_shelfs', methods=['POST'])
def update_shelfs():
    """Update shelfs."""
    all_products = Product.query.all()
    all_shelfs = Shelf.query.all()

    # Execute update shelfs function.
    sv_update_shelfs()
    return render_template('shelfs.html', all_products=all_products, shelfs=all_shelfs)


@app.route('/products', methods=['GET', 'POST'])
def products():
    """Show current products / add products to database."""
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
    transport = Transport.query.filter_by(product_id=product_id).all()

    # Suspend transport for product that will be deleted.
    for i in range(len(transport)):
        transport[i].product_name = None

    # Delete product and commit changes.
    db.session.delete(product)
    db.session.commit()
    flash('You have successfully deleted the product.')
    return redirect(url_for('products'))


@app.route('/product/update/<int:product_id>', methods=['POST'])
def update_product(product_id):
    """Update product."""
    product = Product.query.get_or_404(product_id)
    old_quantity = product.quantity
    product.quantity = request.form.get('new_quantity')
    if int(product.quantity) >= int(old_quantity):
        db.session.commit()
        flash('You have successfully updated the product.')
        return redirect(url_for('products'))
    else:
        if int(product.quantity) >= 0:
            sv_update_product(product_id)
            db.session.commit()
            flash('Quantity reduced.')
            return redirect(url_for('products'))
        else:
            flash('Please enter a positive number.')
            return redirect(url_for('edit_product', product_id=product.id))


@app.route('/transports')
def transports():
    """Show current transports."""
    all_transports = Transport.query.all()
    return render_template('transports.html', at=all_transports)


@app.route('/transport/<int:transport_id>')
def edit_transport(transport_id):
    """Edit page for transport."""
    transport = Transport.query.filter_by(id=transport_id).first()
    all_products = Product.query.all()
    return render_template('edit_transport.html', transport=transport, all_products=all_products)


@app.route('/transport/update/<int:transport_id>', methods=['POST'])
def update_transport(transport_id):
    """Update transport."""
    transport = Transport.query.get_or_404(transport_id)
    transport.product_name = request.form.get('new_product')

    # Update database if different product was selected.
    if transport.product_name != None:
        pid = Product.query.filter_by(name=transport.product_name).first()
        transport.product_id = pid.id
        db.session.commit()
    flash('You have successfully updated transport product.')
    return redirect(url_for('transports'))


@app.route('/transport/delete/<int:transport_id>', methods=['POST'])
def suspend_transport(transport_id):
    """Suspend transport."""
    transport = Transport.query.get_or_404(transport_id)
    transport.product_name = None
    transport.product_id = None
    db.session.commit()
    flash('You have successfully suspended transport.')
    return redirect(url_for('transports'))


@app.route('/transfer', methods=['POST'])
def transfer():
    """Transfer products from shelfs to transports."""

    # Execute transfer function.
    sv_transfer()
    return redirect(url_for('shelfs'))


@app.route('/sort_shelfs', methods=['POST'])
def sort_shelfs():
    """Sort shelfs if there is possibility to reduce rotations."""

    # Execute sorting function.
    sv_sort_shelfs()
    return redirect(url_for('shelfs'))


@app.route('/random_fill', methods=['POST'])
def random_fill():
    """Random shelfs fill (with 1-3 per shelf rule)."""

    # Execute random fill function.
    sv_random_fill()
    return redirect(url_for('shelfs'))
