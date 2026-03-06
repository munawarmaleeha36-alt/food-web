from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')  # Change this to a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/foodiehub'  # Update with your MySQL credentials
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

# Sample menu data (in a real app, this would come from a database)
menu = [
    {"id": 1, "name": "Pizza", "price": 10.99, "category": "Italian"},
    {"id": 2, "name": "Burger", "price": 8.99, "category": "American"},
    {"id": 3, "name": "Sushi", "price": 15.99, "category": "Japanese"},
    {"id": 4, "name": "Caesar Salad", "price": 8.99, "category": "Fresh Bites"},
    {"id": 5, "name": "Classic Burger", "price": 10.99, "category": "Tasty Meals"},
    {"id": 6, "name": "Carbonara Pasta", "price": 14.99, "category": "Tasty Meals"},
    {"id": 7, "name": "Beef Stew", "price": 16.99, "category": "Comfort Food"},
    {"id": 8, "name": "Chicken Curry", "price": 15.99, "category": "Flavor Feast"}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/categories')
def categories():
    return render_template('categories.html')

@app.route('/deals')
def deals():
    return render_template('deals.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/menu')
def get_menu():
    return jsonify(menu)

@app.route('/api/order', methods=['POST'])
def place_order():
    data = request.get_json()
    # In a real app, process the order and save to database
    return jsonify({"message": "Order placed successfully", "order_id": 123})

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return jsonify({"error": "Please login to add items to cart"}), 401

    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)

    user_id = session['user_id']
    cart_item = CartItem.query.filter_by(user_id=user_id, item_id=item_id).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=user_id, item_id=item_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    cart_count = sum(item.quantity for item in CartItem.query.filter_by(user_id=user_id).all())
    return jsonify({"message": "Item added to cart", "cart_count": cart_count})

@app.route('/api/cart')
def get_cart():
    if 'user_id' not in session:
        return jsonify({"items": [], "total": 0})

    user_id = session['user_id']
    cart_items = []
    total = 0
    cart_db_items = CartItem.query.filter_by(user_id=user_id).all()
    for cart_item in cart_db_items:
        item = next((m for m in menu if m['id'] == cart_item.item_id), None)
        if item:
            cart_items.append({**item, 'quantity': cart_item.quantity})
            total += item['price'] * cart_item.quantity
    return jsonify({"items": cart_items, "total": round(total, 2)})

@app.route('/api/cart/remove/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    if 'user_id' not in session:
        return jsonify({"error": "Please login"}), 401

    user_id = session['user_id']
    cart_item = CartItem.query.filter_by(user_id=user_id, item_id=item_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    return jsonify({"message": "Item removed from cart"})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['logged_in'] = True
            session['user_id'] = user.id
            session['username'] = user.name
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match")

        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error="Email already registered")

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session['logged_in'] = True
        session['user_id'] = user.id
        session['username'] = user.name
        return redirect(url_for('home'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
