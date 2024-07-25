from flask import session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length
from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.utils import secure_filename
import os

# Create the app
app = Flask(__name__)
# Configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.secret_key = 'f32a9947143fe06beca3efc0b8032226'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["WTF_CSRF_ENABLED"] = False
app.config["UPLOAD_FOLDER"] = 'uploads'
# Ensure the upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(8), nullable=False)
    user_type = db.Column(db.Integer, nullable=False, default=1)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"Product('{self.name}', '{self.price}')"

# class Cart(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     user = db.relationship('User', backref=db.backref('carts', lazy=True))
#     product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
#     products = db.relationship('Product', secondary='cart_product', backref=db.backref('carts', lazy=True))
#     quantity = db.Column(db.Integer, nullable=False, default=1)

#     def __repr__(self):
#         return f"Cart('{self.user.username}')"

# # Order model
# class Order(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     user = db.relationship('User', backref=db.backref('orders', lazy=True))
#     order_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
#     total_amount = db.Column(db.Float, nullable=False)

#     def __repr__(self):
#         return f"Order('{self.id}', '{self.user.username}', '{self.total_amount}')"

# class Billing(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
#     order = db.relationship('Order', backref=db.backref('billings', lazy=True))
#     billing_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
#     amount = db.Column(db.Float, nullable=False)

#     def __repr__(self):
#         return f"Billing('{self.order.id}', '{self.amount}')"

# # Category model
# class Category(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80), nullable=False)
#     is_active = db.Column(db.Boolean, default=True)

#     def __repr__(self):
#         return f'<Category {self.name}>'


# Define RegisterForm
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=30)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    phone = IntegerField('Phone', validators=[DataRequired(), Length(min=10, max=10)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=10)])

# Routes and handle form submission


# Route to render register page and handle form submission
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Retrieve data from the form
        username = form.username.data
        email = form.email.data
        phone = form.phone.data
        password = form.password.data

        # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Username already exists. Please choose a different one.', category='error')
        elif existing_email:
            flash('Email address already registered. Please use a different email.', category='error')
        else:
            # Create a new user instance
            new_user = User(username=username, email=email, phone=phone, password=password)
            

            # Add new user to the database
            db.session.add(new_user)
            db.session.commit()

            # Redirect to login page after successful registration
            flash('Your account has been successfully registered!', category='success')
            return redirect(url_for('login'))
    
    # Render the register page template with form
    return render_template('register.html', form=form)



# Define LoginForm 
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    remember = BooleanField('Remember Me')


# Route to render login page and handle form submission
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # Check if the username exists in the database
        user = User.query.filter_by(username=username).first()
        if user:
            # Check if the password matches
            if password == user.password:
                session['username'] = user.username
                flash('Login successful!', category='success')
                if int(user.user_type) == 2:
                    return redirect(url_for('admin'))
                # Redirect to the home page
                return redirect(url_for('index'))
            else:
                flash('Login unsuccessful. Please check your password.', category='error')
        else:
            flash('Login unsuccessful. User not found.', category='error')

    return render_template('login.html', form=form)



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
    return render_template('single-product.html')



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/admin')
def admin():
    return render_template('admin_dashboard.html', username=session.get('username'))



@app.route('/list_orders')
def list_orders():
    return render_template('list_orders.html')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['product_name']
        description = request.form['description']
        price = request.form['price']
        quantity = request.form['qty']
        file = request.files['product_img']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_url = file_path
        else:
            image_url = None

        new_product = Product(name=name, description=description, price=price, quantity=quantity, image_url=image_url)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('add_product'))
    
    return render_template('add_product.html')


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']
        user_type = request.form['user_type']
        # create a user
        new_user = User(username=username, email=email, phone=mobile, password=password, user_type=user_type)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('create_user'))

    return render_template('create_user.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    # app.run(host="0.0.0.0", port=9080, debug=True)
