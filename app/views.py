from flask import render_template, flash, request, redirect, url_for
from app import app, db
from .forms import ManageProduct
from .models import Product, Transport, Shelf, Queue


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


@app.route('/update_shelfs', methods=['GET', 'POST'])
def update_shelfs():
    """Update shelfs."""
    all_products = Product.query.all()
    all_shelfs = Shelf.query.all()
    if request.method == 'POST':
        for x in range(100):
            shelf = request.form.get('shelf_{}'.format(x))
            old_shelf = request.form.get('old_shelf_{}'.format(x))
            if shelf != None:
                all_shelfs[x].product_id = shelf
                db.session.commit()
            elif shelf == old_shelf:
                all_shelfs[x].product_id = request.form.get('old_shelf_{}'.format(x))
                db.session.commit()
        # flash('You have successfully updated shelfs.')
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


@app.route('/product/update/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    """Update product."""
    product = Product.query.get_or_404(product_id)
    product.quantity = request.form.get('new_quantity')
    db.session.commit()
    flash('You have successfully updated the product.')
    return redirect(url_for('products'))


@app.route('/transports', methods=['GET', 'POST'])
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


@app.route('/transport/update/<int:transport_id>', methods=['GET', 'POST'])
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


@app.route('/transport/delete/<int:transport_id>', methods=['GET', 'POST'])
def suspend_transport(transport_id):
    """Suspend transport."""
    transport = Transport.query.get_or_404(transport_id)
    transport.product_name = None
    transport.product_id = None
    db.session.commit()
    flash('You have successfully suspended transport.')
    return redirect(url_for('transports'))


@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    """Transfer products from shelfs to transports."""

    # Create list for orders with product ids.
    order_list = []
    all_transports = Transport.query.all()
    for order in all_transports:
        order_list.append([order.product_id]*5)

    # Create list with product ids.
    product_ids = []
    all_products = Product.query.all()
    for product in all_products:
        product_ids.append(product.id)

    # Create list with current products on shelfs.
    shelf_list = []
    all_shelfs = Shelf.query.all()
    for shelf in all_shelfs:
        shelf_list.append(shelf.product_id)

    # Split list into 10 pieces chunks.
    adjust = lambda x, cut: [x[i:i+cut] for i in range(0, len(x), cut)]
    shelf_list = adjust(shelf_list, 10)

    # Execute transfer function.
    transfer_products('t0_id:' + str(order_list[0][0]), order_list[0], shelf_list)
    #transfer_products('t1_id:' + str(order_list[1][0]), order_list[1], shelf_list)
    #transfer_products('t2_id:' + str(order_list[2][0]), order_list[2], shelf_list)

    # Count orders.
    one_list_shelf = [x for one_list in shelf_list for x in one_list]

    # Mark product as taken in shelfs table.
    for x in range(100):
        if one_list_shelf[x] not in [0, None] and one_list_shelf[x] not in product_ids:
            all_shelfs[x].product_id = 0

    # Update product quantity in products table.
    product = Product.query.get(order_list[0][0])
    product.quantity -= one_list_shelf.count('t0_id:' + str(order_list[0][0]))

    db.session.commit()

    return redirect(url_for('shelfs'))


def transfer_products(transport_name, order, shelf_list):
    """Transfer products with queue."""
    # Initialize Queue object.
    q = Queue()

    # Fill queue with current products.
    for i in shelf_list:
        q.enqueue(i)

    # Rotation magic happens here.
    shift = 0
    for _ in range(len(shelf_list)):
        shift -= 1
        current_shelf = q.dequeue()
        for i in order:
            if i in current_shelf:
                current_shelf.insert(current_shelf.index(i), transport_name)
                current_shelf.remove(i)
        order = [order[0]]*(len(order)-current_shelf.count(transport_name))
        if len(order) > 0:
            q.enqueue(current_shelf)
        elif len(order) == 0:
            q.enqueue(current_shelf)
            return print('Transfer complete for ' + transport_name + ' with shift = ' + str(shift) + '.\n' + str(shelf_list))
    return print('Transfer empty or incomplete for ' + transport_name + ' with shift: ' + str(shift) + ').\n' + str(shelf_list))
