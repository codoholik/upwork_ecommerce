import datetime
import random
from flask import session
import traceback
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length
from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, session, jsonify
from werkzeug.utils import secure_filename
from wtforms.validators import DataRequired, Length, Regexp
import os
from flask_migrate import Migrate
from flask_mail import Mail, Message
import os


# Create the app
app = Flask(__name__)
# Configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# secret is imp for  
app.secret_key = 'f32a9947143fe06beca3efc0b8032226'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["WTF_CSRF_ENABLED"] = False
app.config["UPLOAD_FOLDER"] = 'uploads'
# Ensure the upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
# Initialize SQLAlchemy
db = SQLAlchemy(app)
# Initialize Flask-Migrate
migrate = Migrate(app, db)
# keeping user sessions




# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'

mail = Mail(app)




# Models
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(8), nullable=False)
    user_type = db.Column(db.Integer, nullable=False, default=1)

class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"Product('{self.name}', '{self.price}')"



class Cart(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    product_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)

    user = db.relationship('User', backref=db.backref('carts', lazy=True))

    

class Billing(db.Model):
    __tablename__ = 'billing'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)


from enum import Enum
class OrderStatus(Enum):
    PROCESSING = 'Processing'
    COMPLETE = 'Complete'
    CANCEL = 'Cancel'
class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(20), nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    billing_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.Enum(OrderStatus), nullable=False, default=OrderStatus.PROCESSING)


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
    phone = StringField('Phone', validators=[
        DataRequired(), Length(min=10, max=10),
        Regexp('^[0-9]+$', message='Phone number must contain only digits.')
    ])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=10)])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    remember = BooleanField('Remember Me')


class BillingForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired(), Regexp(r'^\+?1?\d{9,15}$', message="Invalid phone number")])
    address = StringField('Address', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired(), Regexp(r'^\d{5}(-\d{4})?$', message="Invalid postal code")])



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

        # phone number validation error 
        if len(phone) != 10:  
            flash('Phone number must be exactly 10 digits.', category='error')
            return render_template('register.html', form=form)


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
                # Store the user id in the session
                session['username'] = user.username
                # Store the user id in the session
                session['user_id'] = user.id
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



@app.route('/logout')
def logout():
    # Clear the session to log out the user
    if 'username' in session:
        session.pop('username')
        session.pop('user_id')
        return redirect(url_for('login'))
    session.pop('user_id', None)
    session.pop('username')
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))



@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.root_path, filename)


@app.route('/shop')
def shop():
    products = Product.query.all()
    for product in products:
        print(product.product_name)
    return render_template('shop.html', products=products)


@app.route('/add_cart/<int:product_id>', methods=['POST'])
def add_cart(product_id):
    if 'user_id' in session:
        user_id = session.get('user_id')
        quantity = int(request.form.get('quantity', 1))

        # Get the product by product_id
        product = Product.query.get_or_404(product_id)

        # Check if the item already exists in the cart
        existing_item = Cart.query.filter_by(user_id=user_id, product_name=product.product_name).first()

        if existing_item:
            # If the item exists, update the quantity
            existing_item.quantity += 1
            existing_item.price += product.price
            flash('Item quantity updated in cart!', 'success')
            db.session.add(existing_item)
        else:
            # If the item does not exist, add it to the cart
            cart_item = Cart(
                user_id=user_id,
                product_name=product.product_name,
                quantity=quantity,
                price=product.price
            )

            db.session.add(cart_item)
            flash('Item added to cart successfully!', 'success')

        # Commit changes to the database
        db.session.commit()
        return redirect(url_for('cart'))
    
    else:
        flash('You must be logged in to add items to cart.', 'warning')
        return redirect(url_for('login'))



# render added items to cart in cart.html
@app.route('/cart')
def cart():
    print(session)
    if 'user_id' not in session:
        flash('You must be logged in to view the cart.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    total_price = 0

    # Build a list of cart item details to pass to the template
    cart_list = []
    for item in cart_items:
        # item_total = item.quantity * item.price
        total_price += item.price
        # fetch product here
        product  = Product.query.filter_by(product_name=item.product_name).first()
        cart_list.append({
            'id': item.id,
            'product_name': item.product_name,
            'price': product.price,
            'quantity': item.quantity,
            'total': item.price,
            'user_id': user_id
        })

    return render_template('cart.html', cart_items=cart_list, total_price=total_price)



# remove items from the  cart through cart id
@app.route('/remove_cart_item/<int:cart_id>', methods=['POST'])
def remove_cart_item(cart_id):
    if 'user_id' not in session:
        flash('You must be logged in to remove items from cart.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    # Remove the item from the cart for the current user
    cart_item = Cart.query.filter_by(user_id=user_id, id=cart_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart successfully!', 'success')
    else:
        flash('Item not found in cart.', 'error')
    
    return redirect(url_for('cart'))



@app.route('/update_cart', methods=['POST'])
def update_cart():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'You must be logged in to update items in the cart.'})
        
        user_id = session['user_id']
        data = request.get_json()


        new_quantity = data.get('quantity')
        product_name = data.get('product_name')
        user_id = data.get('user_id')
        price = data.get('price')

        if new_quantity is None or not user_id:
            return jsonify({'success': False, 'message': 'Invalid request data.'})

        cart_item = Cart.query.filter_by(user_id=int(user_id), product_name=product_name).first()

        if cart_item:
            cart_item.quantity = int(new_quantity)
            cart_item.price = 0
            cart_item.price = float(price) * int(new_quantity)

            db.session.add(cart_item)
            db.session.commit()


            total_price = Cart.query.filter_by(user_id=int(user_id)).all()
            final_price = 0
            for price in total_price:
                final_price += price.price
            return jsonify({'success': True, 'qty':cart_item.quantity, 'total_price': cart_item.price, 'final_price': final_price})
        else:
            return jsonify({'success': False, 'message': 'Item not found in cart.'})

    except:
        traceback.print_exc()



@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'})

    user_id = session.get('user_id')
    form = request.form

    full_name = form.get('full_name')
    phone = form.get('phone')
    address = form.get('address')
    country = form.get('country')
    city = form.get('city')
    postal_code = form.get('postal_code')
    total_price = form.get('total_price')

    # if billing info already exist:
    exist_bill =  Billing.query.filter_by(
        user_id=user_id,
        full_name=full_name,
        phone=phone,
        address=address,
        country=country,
        city=city,
        postal_code=postal_code
    ).first()

    if exist_bill:
        billing = exist_bill
    else:
        # Save billing info
        billing = Billing(
            user_id=user_id,
            full_name=full_name,
            phone=phone,
            address=address,
            country=country,
            city=city,
            postal_code=postal_code
        )
        db.session.add(billing)
        db.session.commit()

    # store billing ID in session
    session['billing_id'] = billing.id


    # Generate a unique 6-digit order ID
    def generate_order_id():
        order_id = f'{random.randint(100000, 999999)}'
        if not Order.query.filter_by(order_id=order_id).first():
            return order_id

    order_id = generate_order_id()

    # Save order info
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    for item in cart_items:
        order = Order(
            user_id=user_id,
            order_id=order_id,
            billing_id=billing.id,
            product_name=item.product_name,
            quantity=item.quantity,
            price=item.price,
            order_date=datetime.datetime.now()
        )
        db.session.add(order)

    # Clear the cart
    Cart.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    return jsonify({
        'full_name': full_name,
        'order_id': order_id,
        'order_message': 'Your order has been dispatched. We are delivering your order.',
        'address': address,
        'payment_method': 'Cash on Delivery'
    })
    


@app.route('/checkout')
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))  

    user_id = session.get('user_id')
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    # Calculate total price
    total_price = sum(item.price for item in cart_items)

    # fetch existing billing info
    billing_items = Billing.query.filter_by(user_id=user_id).all()


    return render_template('checkout.html', cart_items=cart_items, total_price=total_price, billing_items=billing_items)



@app.route('/')
def index():
    return render_template('index.html', username=session.get('username'))



@app.route('/about')
def about():
    return render_template("about.html")


# contact page 
@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    subject = request.form.get('subject')
    message = request.form.get('message')

    # Create a message object
    msg = Message(
        subject=f"Contact Form Submission: {subject}",
        # admin email address
        recipients=["sachdevagarima25@gmail.com"],
        body=f"""
        Name: {name}
        Email: {email}
        Phone: {phone}
        
        Message:
        {message}
        """
    )

    try:
        # Send the email
        mail.send(msg)
        return jsonify({'status': 'success', 'message': 'Your message has been sent!'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'There was an error sending your message. Please try again later.'})



# ADMIN PANEL

@app.route('/admin')
def admin():
    return render_template('admin_dashboard.html', username=session.get('username'))


# adding a product through admin
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

        new_product = Product(product_name=name, description=description, price=price, quantity=quantity, image_url=image_url)
        
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('add_product'))
    
    return render_template('add_product.html')



# listing of all the products in admin dashboard
@app.route('/products_list')
def products_list():
    products = Product.query.all()
    return render_template('products_list.html', products=products)



# updating any specific any product in admin dashboard
@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    if request.method == 'POST':
        # Retrieve data from the form
        pname = request.form['product_name']
        description = request.form['description']
        price = request.form['price']
        qty = request.form['quantity']
        file = request.files.get('image_url')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_url = file_path
        else:
            image_url = request.form.get('existing_image_url')

         # Find the product by ID
        product = Product.query.filter_by(id=product_id).first()

        # update product details in db
        product.product_name = pname
        product.description = description
        product.price = price
        product.quantity = qty
        product.image_url = image_url

        # commit changes to db
        db.session.add(product)
        db.session.commit()

        # redirect to product list page
        return redirect(url_for('products_list', product_id=product_id))
    
    product = Product.query.filter_by(id=product_id).first()
    return render_template('update_product.html', product=product)



# delete a product through admin dashboard
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        print('delete try block')
        product = session.query(Product).filter_by(id=product_id).first()
        print(product.id)
        if product:
            db.session.delete(product)
            db.session.commit()
        return redirect(url_for('products_list'))
    except:
        traceback.print_exc()
        # rollback if any error occurs
        db.session.rollback()
        return redirect(url_for('products_list'))
    



# render all orders in admin dashboard
from sqlalchemy import func
@app.route('/list_orders')
def list_orders():
    # query to perform order_date by grouping order id
    order_summary = (
        db.session.query(
            Order.billing_id,
            Order.order_id,
            Order.order_date,
            func.sum(Order.quantity).label('total_quantity'),
            func.sum(Order.price).label('total_amount'),
            Order.status
        )
        .group_by(Order.order_id)
        .order_by(Order.order_date.desc())
        .all()
    )

    # data  rendering
    order_data = []
    for billing_id, order_id, order_date, total_quantity, total_amount, status in order_summary:
        # billing info
        billing = Billing.query.filter_by(id=billing_id).first()
        # fullname fetch from billing
        full_name = billing.full_name if billing else 'Unknown'
        # Convert Enum to string
        status = status.name

        order_data.append({
            'username': full_name,
            'order_id': order_id,
            'order_date': order_date.strftime('%Y-%m-%d'), 
            'total_quantity': total_quantity,
            'total_amount': total_amount,
            'status': status
        })

    return render_template('list_orders.html', order_items=order_data, username=session.get('username'))



# fetch view details of order modal productname, qty, price
@app.route('/order_details/<int:order_id>')
def order_details(order_id):
    order = Order.query.filter_by(order_id=order_id).first()
    billing = Billing.query.filter_by(id=order.billing_id).first()
    order_items = Order.query.filter_by(order_id=order_id).all()
    total_amount = sum(item.price for item in order_items)

    return jsonify({
        'order_id': order.order_id,
        'order_date': order.order_date.strftime('%Y-%m-%d'),
        'full_name': billing.full_name,
        'items': [
            {
                'product_name': item.product_name,
                'quantity': item.quantity,
                'price': item.price
            } for item in order_items
        ],
        'total_amount': total_amount
    })



# updating order status through admin(processing, complete, cancel)
@app.route('/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    new_status = request.form.get('status')
    orders = Order.query.filter_by(order_id=order_id).all()
    if len(orders) > 0:

        for order in orders:
            order.status = OrderStatus[new_status.upper()]
            db.session.add(order)
            db.session.commit()
        
        return jsonify({'success': True})

    else:
        return jsonify({'error': 'Order not found'})


# edit/update order through  admin
@app.route('/update_order/<int:order_id>', methods=['POST'])
def update_order(order_id):
    if request.method == 'POST':
        try:
            # Retrieve data from JSON request
            full_name = request.json.get('full_name')
            order_date = request.json.get('order_date')
            items = request.json.get('items', [])
            orderid = request.json.get('order_id')
            # Find the order by ID
            orders = Order.query.filter_by(order_id=orderid).all()
            # Update Billing Full Name
            billing = Billing.query.filter_by(id=orders[0].billing_id).first()
            billing.full_name = full_name
            db.session.add(billing)
            db.session.commit()

            for order in orders:
                # Update Order Date
                order.order_date = datetime.datetime.strptime(order_date, '%Y-%m-%d')
                # Update Product Details
                for item in items:
                    product_name = item.get('product_name')
                    quantity = item.get('quantity')
                    price = item.get('price')
                    # Update order with the corresponding product details
                    if order.product_name == product_name:
                        order.quantity = quantity
                        order.price = price
                        db.session.add(order)
                        db.session.commit()
                        break

            return jsonify({'success': True})
        except:
            traceback.print_exc()
            db.session.rollback()
            return jsonify({'success': False})





# creating a user(admin, general) through admin
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

    return render_template('create_user.html', username=session.get('username'))



# listing if all users in admin
@app.route('/users_list')
def users_list():
    users = User.query.all()
    return render_template('users_list.html', users=users, username=session.get('username'))


@app.route('/user_profile/<int:user_id>', methods=['GET', 'POST'])
def user_profile(user_id):
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        user_type = int(request.form['user_type'])
        user = User.query.filter_by(id=user_id).first()
        user.username = username
        user.email = email
        user.phone = phone
        user.user_type = user_type
        db.session.add(user)
        db.session.commit()
        session['username'] = username
        return redirect(url_for('user_profile', user_id=user_id))
    
    user = User.query.filter_by(id=user_id).first()
    return render_template('user_profile.html', user=user)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # app.run(debug=True)

    app.run(host="0.0.0.0", port=4000, debug=True)
