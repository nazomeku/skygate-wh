import unittest
from os import path
from flask import Flask
from flask_testing import TestCase
from app import db
from app.models import Product, Transport, Shelf
BASE_DIR = path.abspath(path.dirname(__file__))


class MyTest(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config.update(
            SQLALCHEMY_DATABASE_URI='sqlite:///' + path.join(BASE_DIR, 'test.db')
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        with app.app_context():
            db.create_all()
        return app

    def setUp(self):
        """Call before any test."""
        db.create_all()

        product = Product(name="a", quantity=100)
        product1 = Product(name="b", quantity=100)
        transport = Transport(product_name="a")
        shelf = Shelf(product_id=1)

        db.session.add(product)
        db.session.add(product1)
        db.session.add(transport)
        db.session.add(shelf)
        db.session.commit()

    def tearDown(self):
        """Call after any test."""
        db.session.remove()
        db.drop_all()


class TestModels(MyTest):

    def test_product_model(self):
        """Test count of product in products table."""
        self.assertEqual(Product.query.count(), 2)

    def test_transport_model(self):
        """Test count of transport in transports table"""
        self.assertEqual(Transport.query.count(), 1)

    def test_shelf_model(self):
        """Test count of product_id in shelfs table"""
        self.assertEqual(Shelf.query.count(), 1)


if __name__ == '__main__':
    unittest.main()
