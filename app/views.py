import random
from flask import render_template, flash, request, redirect, url_for
from . import app, db
from .forms import ManageProduct
from .models import Product, Transport, Shelf


total_shifts = -1
current_shelf = 0


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

    # Create list with product ids on shelfs before editting.
    shelf_list_pre = []
    for shelf in all_shelfs:
        shelf_list_pre.append(shelf.product_id)

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

    # Create list with product ids on shelfs after editting.
    shelf_list = []
    for shelf in all_shelfs:
        shelf_list.append(shelf.product_id)

    # Split list into 10 pieces chunks.
    adjust = lambda x, cut: [x[i:i+cut] for i in range(0, len(x), cut)]
    shelf_list_split = adjust(shelf_list, 10)

    # Check the diversity of products on the shelf.
    for i in range(10):
        if len(set([x for x in shelf_list_split[i] if x not in [0, None]])) > 3:
            flash('Too much different products on shelf ' + str(i) + ' (1-3 per shelf allowed).')
            # Revert changes to database.
            for x in range(100):
                all_shelfs[x].product_id = shelf_list_pre[x]
                db.session.commit()
            return redirect(url_for('edit_shelfs'))

    # Check if there is enough product quantity in warehouse to assign.
    product_ids = []
    product_quantity_count = []
    product_names = []
    for product in all_products:
        product_ids.append(product.id)
        product_quantity_count.append(product.quantity)
        product_names.append(product.name)

    if shelf_list.count(product_ids[0]) > product_quantity_count[0]:
        flash('There is not enough product (' + str(product_names[0]) + ') in warehouse to assign.')
        # Revert changes to database.
        for x in range(100):
            all_shelfs[x].product_id = shelf_list_pre[x]
            db.session.commit()
        return redirect(url_for('edit_shelfs'))

    flash('You have successfully updated shelfs.')
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
            all_shelfs = Shelf.query.all()

            # Create list with current products on shelfs.
            shelf_list = []
            for shelf in all_shelfs:
                shelf_list.append(shelf.product_id)

            # Count quantity of product id on shelfs.
            quantity_count = shelf_list.count(product_id)

            # Check if quantity on shelfs is greater then quantity of product in warehouse.
            if quantity_count > int(product.quantity):
                diff = quantity_count - int(product.quantity)
                for _ in range(diff):
                    finder = shelf_list.index(product_id)
                    shelf_list.insert(finder, 0)
                    shelf_list.remove(product_id)

                # Reduce quantity of products on shelfs.
                for x in range(100):
                    all_shelfs[x].product_id = shelf_list[x]

            db.session.commit()
            flash('You have successfully updated the product.')
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
    global current_shelf
    global total_shifts

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
    shelf_list_split = adjust(shelf_list, 10)
    # print(shelf_list_split)

    # Execute transfer products.
    for i in range(10):
        transfer_products('t' + str(i), [order_list[i][0]]*5, shelf_list_split)
        shelf_list_split = rotate(shelf_list_split, current_shelf-1)
        current_shelf = 0
        total_shifts -= 1

    # Back to initial values.
    total_shifts = -1
    current_shelf = 0

    # Count orders.
    one_list_shelf = [x for one_list in shelf_list_split for x in one_list]

    # Mark product as taken in shelfs table.
    for x in range(100):
        if one_list_shelf[x] not in [0, None] and one_list_shelf[x] not in product_ids:
            all_shelfs[x].product_id = 0

    # Update product quantity in products table.
    for x in range(10):
        if order_list[x][0] in product_ids:
            product = Product.query.get(order_list[x][0])
            product.quantity -= one_list_shelf.count('t{}'.format(x))
        else:
            print('Transport suspended or product id not present in database.')
        if product.quantity <= 0:
            product.quantity = 0
        db.session.commit()

    return redirect(url_for('shelfs'))


@app.route('/sort_shelfs', methods=['POST'])
def sort_shelfs():
    """Sort shelfs if there is possibility to reduce rotations."""
    global current_shelf
    global total_shifts

    all_products = Product.query.all()

    # Create list for orders with product ids.
    order_list = []
    all_transports = Transport.query.all()
    for order in all_transports:
        order_list.append([order.product_id]*5)

    # Create list with current products on shelfs.
    shelf_list = []
    all_shelfs = Shelf.query.all()
    for shelf in all_shelfs:
        shelf_list.append(shelf.product_id)

    # Split list into 10 pieces chunks.
    adjust = lambda x, cut: [x[i:i+cut] for i in range(0, len(x), cut)]

    shift_check = []
    # Simulate run with every rotation of shelf.
    for x in range(10):
        shelf_list_split = adjust(shelf_list, 10)
        for i in range(10):
            transfer_products('t' + str(i), [order_list[i][0]]*5, rotate(shelf_list_split, x))
            shelf_list_split = rotate(shelf_list_split, current_shelf-1)
            shift_check.append(total_shifts)
            current_shelf = 0
            total_shifts -= 1
        total_shifts = -1
        current_shelf = 0

    # Append shifts from all stages. Get last value.
    shift_check_split = adjust(shift_check, 10)
    shift_check_single = []
    for i in shift_check_split:
        shift_check_single.append(i[-1])

    # Find the lowest shift value.
    low = shift_check_single[0]
    for i in shift_check_single:
        if i < low:
            low = i

    flash('Rotations before sort: ' + str(shift_check_single[0]) + '. Rotations after sort: ' + str(low) + '. Rotation was applied automatically.')

    shelf_list_split = adjust(shelf_list, 10)

    # Execute rotation if it is worth.
    if low < shift_check_single[0]:
        shelf_list_split = rotate(shelf_list_split, shift_check_single.index(low))
        #print(shelf_list_split)
        one_list_shelf = [x for one_list in shelf_list_split for x in one_list]
        for x in range(100):
            all_shelfs[x].product_id = one_list_shelf[x]
            db.session.commit()

    return render_template('shelfs.html', all_products=all_products, shelfs=all_shelfs)


@app.route('/random_fill', methods=['POST'])
def random_fill():
    """Random shelfs fill (1-3 per shelf rule ignored)."""
    all_shelfs = Shelf.query.all()
    all_products = Product.query.all()
    my_rnd = []
    fin_rnd = []
    product_ids = []

    for product in all_products:
        product_ids.append(product.id)

    for _ in range(10):
        random.shuffle(product_ids)
        my_rnd.append(product_ids[:3])

    for i in range(10):
        fin_rnd.append(my_rnd[i]*3+[random.choice(my_rnd[i])])

    one_fin_rnd = [x for one_list in fin_rnd for x in one_list]

    for x in range(100):
        all_shelfs[x].product_id = one_fin_rnd[x]
    db.session.commit()
    return redirect(url_for('shelfs'))


def rotate(lst, shift):
    """Rotate list with given shift value."""
    return lst[shift:] + lst[:shift]


def transfer_products(name, new_order, shelf_list_split):
    """Transfer products with queue."""
    global current_shelf
    global total_shifts

    for x in range(10):
        if len(new_order) > 0:
            #print(new_order)
            for i in new_order:
                if i in shelf_list_split[x]:
                    shelf_list_split[x].insert(shelf_list_split[x].index(i), name)
                    shelf_list_split[x].remove(i)
                    #print(shelf_list_split[x])
            current_shelf += 1
            total_shifts += 1
            new_order = [new_order[0]]*(len(new_order)-shelf_list_split[x].count(name))
            #print(new_order)
        else:
            #return print('transport completed, currently on shelf number: ' + str(current_shelf) + ' total shifts: ' + str(total_shifts))
            #return total_shifts
            pass
