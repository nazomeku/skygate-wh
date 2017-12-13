from flask import render_template
from app import app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/transports')
def transports():
    return render_template('transports.html')
