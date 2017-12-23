from . import models, db


# Products table init.
def db_products_init():
    all_products = models.Product.query.all()
    if len(all_products) < 5:
        product1 = models.Product(name="a", quantity=1000)
        product2 = models.Product(name="b", quantity=1000)
        product3 = models.Product(name="c", quantity=1000)
        product4 = models.Product(name="d", quantity=1000)
        product5 = models.Product(name="e", quantity=1000)
        db.session.add(product1)
        db.session.add(product2)
        db.session.add(product3)
        db.session.add(product4)
        db.session.add(product5)
        db.session.commit()

# Transports table init.
def db_transports_init():
    all_transports = models.Transport.query.all()
    if len(all_transports) < 10:
        for _ in range(1, 11):
            transport = models.Transport(product_name=None, product_id=None)
            db.session.add(transport)
        db.session.commit()


# Shelfs table init.
def db_shelf_init():
    all_shelfs = models.Shelf.query.all()
    if len(all_shelfs) < 100:
        for _ in range(1, 101):
            shelf = models.Shelf(product_id=0)
            db.session.add(shelf)
        db.session.commit()
