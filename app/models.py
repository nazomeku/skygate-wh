from app import db


class Product(db.Model):
    """Create a Product table."""

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    quantity = db.Column(db.Integer, nullable=False)
    transports = db.relationship('Transport', backref='product', lazy='dynamic')
    shelfs = db.relationship('Shelf', backref='product', lazy='dynamic')

class Transport(db.Model):
    """Create a Transport table."""

    __tablename__ = 'transports'

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(50))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))


class Shelf(db.Model):
    """Create a Shelf table."""

    __tablename__ = 'shelfs'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))


class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)
