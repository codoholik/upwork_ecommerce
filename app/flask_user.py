from base64 import urlsafe_b64decode
from flask import Flask, render_template, redirect, url_for
from flask import render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length



app = Flask(__name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

@app.route('/login')
def login():
    return render_template('login.html')

# app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         # Handle login logic here (e.g., check credentials)
#         # For demonstration, redirecting to a placeholder route
#         return redirect(url_for('index'))
#     return render_template('login.html', form=form)


@app.route('/register')
def register():
    return render_template('register.html')


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
