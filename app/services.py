import random
from flask import flash, request, url_for, redirect
from . import db
from .models import Product, Transport, Shelf


total_shifts = -1
current_shelf = 0


def rotate(lst, shift):
    """Rotate list with given shift value."""
    return lst[shift:] + lst[:shift]


def transfer_products(name, new_order, shelf_list_split):
    """Transfer products with queue."""
    global current_shelf
    global total_shifts

    count = 0
    for x in range(10):
        shelf_set = set().union(*shelf_list_split)
        if len(new_order) > 0:
            if new_order[0] in shelf_set:
                count += 1
                for i in new_order:
                    if i in shelf_list_split[x]:
                        shelf_list_split[x].insert(shelf_list_split[x].index(i), name)
                        shelf_list_split[x].remove(i)
                current_shelf += 1
                total_shifts += 1
                new_order = [new_order[0]]*(len(new_order)-shelf_list_split[x].count(name))
    if count == 0:
        total_shifts += 1
        current_shelf += 1


def sv_sort_shelfs():
    """Sort shelfs if there is possibility to reduce rotations."""
    global current_shelf
    global total_shifts
    low = 1000
    total_shifts = -1
    current_shelf = 0
    shift_single = []

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

    # Split list into chunks.
    adjust = lambda x, cut: [x[i:i+cut] for i in range(0, len(x), cut)]

    # Run
    for x in range(10):
        all_shifts = []
        shelf_list_split = adjust(shelf_list, 10)
        for i in range(10):
            transfer_products('t' + str(i), [order_list[i][0]]*5, rotate(shelf_list_split, x))
            shelf_list_split = rotate(shelf_list_split, current_shelf-1)
            all_shifts.append(total_shifts)
            total_shifts -= 1
            current_shelf = 0
        total_shifts = -1
        current_shelf = 0
        shift_single.append(all_shifts[-1])
        if shift_single[x] < low:
            low = shift_single[x]

    # Flash message.
    count = 0
    for x in range(100):
        if all_shelfs[x].product_id == 0:
            count += 1
    if count == 100:
        flash('No products available on shelfs.')
    else:
        flash('Rotations before sort: ' + str(shift_single[0]) + '. Rotations after sort: ' + str(low) + '. Rotation was applied automatically.')

    shelf_list_split = adjust(shelf_list, 10)

    # Execute rotation if it is worth.
    if low < shift_single[0]:
        shelf_list_split = rotate(shelf_list_split, shift_single.index(low))
        one_list_shelf = [x for one_list in shelf_list_split for x in one_list]
        for x in range(100):
            all_shelfs[x].product_id = one_list_shelf[x]
            db.session.commit()


def sv_random_fill():
    """Random shelfs fill (with 1-3 per shelf rule)."""
    all_shelfs = Shelf.query.all()
    all_products = Product.query.all()
    my_rnd = []
    fin_rnd = []
    product_ids = []
    product_qty = []

    # Get all product ids.
    for product in all_products:
        product_ids.append(product.id)
        product_qty.append(product.quantity)

    # Get 3 random values for each shelf.
    for _ in range(10):
        random.shuffle(product_ids)
        my_rnd.append(product_ids[:3])

    # Fill each element in list up to 10 values.
    for i in range(10):
        fin_rnd.append(my_rnd[i]*3+[random.choice(my_rnd[i])])

    # Get merged list.
    one_fin_rnd = [x for one_list in fin_rnd for x in one_list]

    # Assign products to shelfs.
    for x in range(100):
        all_shelfs[x].product_id = one_fin_rnd[x]
    db.session.commit()


def sv_transfer():
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

    # Split list into chunks.
    adjust = lambda x, cut: [x[i:i+cut] for i in range(0, len(x), cut)]
    shelf_list_split = adjust(shelf_list, 10)

    # Execute transfer products.
    for i in range(10):
        transfer_products('t' + str(i), [order_list[i][0]]*5, shelf_list_split)
        shelf_list_split = rotate(shelf_list_split, -1)

    # Count orders.
    one_list_shelf = [x for one_list in shelf_list_split for x in one_list]

    # Flash message.
    count = 0
    for x in range(100):
        if all_shelfs[x].product_id == 0:
            count += 1
    if count == 100:
        flash('No products available on shelfs.')
    else:
        flash('Transfer completed.')

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


def sv_update_shelfs():
    """Update shelfs."""
    all_products = Product.query.all()
    all_shelfs = Shelf.query.all()

    # Create list with product ids on shelfs before editting.
    shelf_list_pre = []
    for shelf in all_shelfs:
        shelf_list_pre.append(shelf.product_id)

    # Update shelfs.
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
        flash('Not enough product (' + str(product_names[0]) + ') in warehouse to assign.')
        # Revert changes to database.
        for x in range(100):
            all_shelfs[x].product_id = shelf_list_pre[x]
            db.session.commit()
        return redirect(url_for('edit_shelfs'))

    flash('You have successfully updated shelfs.')


def sv_update_product(product_id):
    """Update product."""
    product = Product.query.get_or_404(product_id)
    product.quantity = request.form.get('new_quantity')
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
