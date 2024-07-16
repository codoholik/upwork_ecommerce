from base64 import urlsafe_b64decode
from flask import Flask, render_template, redirect, url_for
from flask import render_template, flash, request


app = Flask(__name__)



@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/checkout')
def checkout():
    return render_template('checkout.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/shop')
def shop():
    return render_template('shop.html')


@app.route('/single_product')
def single_product():
    return render_template('single_product.html')


@app.route('/')
def index():
    return render_template('index.html')





if __name__ == '__main__':
    app.run(debug=True)
