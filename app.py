import os
from flask_migrate import Migrate
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Restaurant, Menu, Order, OrderItem, Comment

# --------------------
# Flask Configuration
# --------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///revstoran.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB image limit
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_PERMANENT'] = False

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

db.init_app(app)
migrate = Migrate(app, db)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --------------------
# Helpers
# --------------------
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def current_user():
    uid = session.get('user_id')
    return User.query.get(uid) if uid else None

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('You must be logged in to continue.', 'warning')
            return redirect(url_for('login', next=request.path))
        return view_func(*args, **kwargs)
    return wrapper

def owner_required(restaurant: Restaurant):
    user = current_user()
    if not user or restaurant.owner_id != user.id:
        abort(403)

# --------------------
# User Management
# --------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        raw_password = request.form.get('password', '')
        if not username or not email or not raw_password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('This username is already taken.', 'danger')
            return redirect(url_for('register'))
        password = generate_password_hash(raw_password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('index'))
        flash('Invalid login credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# --------------------
# Home / Restaurants
# --------------------
@app.route('/')
def index():
    # Tüm restoranları çekiyoruz, filtreleme yok
    restaurants = Restaurant.query.order_by(Restaurant.id.desc()).all()
    return render_template('index.html', restaurants=restaurants, user=current_user())

@app.route('/restaurant/<int:id>')
def restaurant_detail(id):
    restaurant = Restaurant.query.get_or_404(id)
    menu_items = Menu.query.filter_by(restaurant_id=id).all()
    comments = Comment.query.filter_by(restaurant_id=id).order_by(Comment.id.desc()).all()
    return render_template(
        'restaurant_detail.html',
        restaurant=restaurant,
        menu_items=menu_items,
        comments=comments,
        user=current_user()
    )

# --------------------
# Restaurant & Menu Management
# --------------------
@app.route('/add_restaurant', methods=['GET', 'POST'])
@login_required
def add_restaurant():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()

        image = request.files.get('image')
        image_path = None
        if image and image.filename:
            if not allowed_file(image.filename):
                flash('Allowed image extensions: png, jpg, jpeg, gif, webp', 'danger')
                return redirect(url_for('add_restaurant'))
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = f"uploads/{filename}"

        new_restaurant = Restaurant(
            name=name,
            description=description,
            city=city,
            state=state,
            image_path=image_path,
            owner_id=current_user().id
        )
        db.session.add(new_restaurant)
        db.session.commit()
        flash('New restaurant added.', 'success')
        return redirect(url_for('index'))
    return render_template('add_restaurant.html', user=current_user())

@app.route('/edit_restaurant/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    owner_required(restaurant)

    if request.method == 'POST':
        restaurant.name = request.form.get('name', restaurant.name).strip()
        restaurant.description = request.form.get('description', restaurant.description).strip()
        restaurant.city = request.form.get('city', restaurant.city).strip()
        restaurant.state = request.form.get('state', restaurant.state).strip()

        image = request.files.get('image')
        if image and image.filename:
            if not allowed_file(image.filename):
                flash('Allowed image extensions: png, jpg, jpeg, gif, webp', 'danger')
                return redirect(url_for('edit_restaurant', id=id))
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            restaurant.image_path = f"uploads/{filename}"

        db.session.commit()
        flash('Restaurant updated.', 'success')
        return redirect(url_for('restaurant_detail', id=id))

    return render_template('edit_restaurant.html', restaurant=restaurant, user=current_user())

@app.route('/delete_restaurant/<int:id>', methods=['POST'])
@login_required
def delete_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    owner_required(restaurant)
    db.session.delete(restaurant)
    db.session.commit()
    flash('Restaurant deleted.', 'info')
    return redirect(url_for('index'))

@app.route('/add_menu_item/<int:restaurant_id>', methods=['GET', 'POST'])
@login_required
def add_menu_item(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    owner_required(restaurant)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price_str = request.form.get('price', '0').replace(',', '.')
        try:
            price = float(price_str)
        except ValueError:
            flash('Invalid price.', 'danger')
            return redirect(url_for('add_menu_item', restaurant_id=restaurant_id))
        image = request.files.get('image')
        filename = None
        if image and image.filename:
            if not allowed_file(image.filename):
                flash('Allowed image extensions: png, jpg, jpeg, gif, webp', 'danger')
                return redirect(url_for('add_menu_item', restaurant_id=restaurant_id))
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_item = Menu(
            restaurant_id=restaurant_id,
            name=name,
            description=description,
            price=price,
            image_path=f"uploads/{filename}" if filename else None
        )
        db.session.add(new_item)
        db.session.commit()
        flash('New menu item added.', 'success')
        return redirect(url_for('restaurant_detail', id=restaurant_id))
    return render_template('add_menu_item.html', restaurant_id=restaurant_id, user=current_user())

@app.route('/edit_menu_item/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_menu_item(id):
    item = Menu.query.get_or_404(id)
    restaurant = Restaurant.query.get_or_404(item.restaurant_id)
    owner_required(restaurant)
    if request.method == 'POST':
        item.name = request.form.get('name', item.name).strip()
        item.description = request.form.get('description', item.description).strip()
        price_str = request.form.get('price', str(item.price)).replace(',', '.')
        try:
            item.price = float(price_str)
        except ValueError:
            flash('Invalid price.', 'danger')
            return redirect(url_for('edit_menu_item', id=id))
        image = request.files.get('image')
        if image and image.filename:
            if not allowed_file(image.filename):
                flash('Allowed image extensions: png, jpg, jpeg, gif, webp', 'danger')
                return redirect(url_for('edit_menu_item', id=id))
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            item.image_path = f"uploads/{filename}"
        db.session.commit()
        flash('Menu item updated.', 'success')
        return redirect(url_for('restaurant_detail', id=item.restaurant_id))
    return render_template('edit_menu_item.html', item=item, user=current_user())

@app.route('/delete_menu_item/<int:id>', methods=['POST'])
@login_required
def delete_menu_item(id):
    item = Menu.query.get_or_404(id)
    restaurant = Restaurant.query.get_or_404(item.restaurant_id)
    owner_required(restaurant)
    db.session.delete(item)
    db.session.commit()
    flash('Menu item deleted.', 'info')
    return redirect(url_for('restaurant_detail', id=restaurant.id))

# --------------------
# Cart / Order
# --------------------
def _init_cart():
    if 'cart' not in session:
        session['cart'] = {"restaurants": {}}
    elif 'restaurants' not in session['cart']:
        session['cart']['restaurants'] = {}

def _cart_total():
    _init_cart()
    total = 0
    for items in session['cart']['restaurants'].values():
        total += sum(i['price'] * i['quantity'] for i in items)
    return total

@app.route('/cart')
def cart():
    _init_cart()
    restaurant_objs = {rid: Restaurant.query.get(int(rid)) for rid in session['cart']['restaurants']}
    return render_template('cart.html', cart=session['cart'], restaurants=restaurant_objs, total=_cart_total(), user=current_user())

@app.route('/add_to_cart/<int:menu_id>', methods=['POST'])
def add_to_cart(menu_id):
    _init_cart()
    menu_item = Menu.query.get_or_404(menu_id)
    rid = str(menu_item.restaurant_id)
    if rid not in session['cart']['restaurants']:
        session['cart']['restaurants'][rid] = []

    for it in session['cart']['restaurants'][rid]:
        if it['id'] == menu_item.id:
            it['quantity'] += 1
            session.modified = True
            return redirect(url_for('cart'))

    session['cart']['restaurants'][rid].append({
        "id": menu_item.id,
        "name": menu_item.name,
        "price": float(menu_item.price),
        "quantity": 1,
        "restaurant_name": menu_item.restaurant.name
    })
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/update_cart_quantity/<int:menu_id>', methods=['POST'])
def update_cart_quantity(menu_id):
    _init_cart()
    try:
        qty = int(request.form.get('quantity', '1'))
    except ValueError:
        qty = 1
    qty = max(1, min(50, qty))

    for items in session['cart']['restaurants'].values():
        for it in items:
            if it['id'] == menu_id:
                it['quantity'] = qty
                session.modified = True
                break
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:menu_id>', methods=['POST'])
def remove_from_cart(menu_id):
    _init_cart()
    to_remove = []
    for rid, items in session['cart']['restaurants'].items():
        session['cart']['restaurants'][rid] = [i for i in items if i['id'] != menu_id]
        if not session['cart']['restaurants'][rid]:
            to_remove.append(rid)
    for rid in to_remove:
        session['cart']['restaurants'].pop(rid)
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session['cart'] = {"restaurants": {}}
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    _init_cart()
    restaurants = session['cart'].get('restaurants', {})
    if not restaurants:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart'))

    for rid, items in restaurants.items():
        total_price = sum(it['price'] * it['quantity'] for it in items)
        new_order = Order(
            customer_id=session['user_id'],
            restaurant_id=int(rid),
            total_price=total_price,
            status='pending'
        )
        db.session.add(new_order)
        db.session.commit()

        for it in items:
            db.session.add(OrderItem(
                order_id=new_order.id,
                menu_id=it['id'],
                quantity=it['quantity'],
                price=it['price']
            ))
        db.session.commit()

    session['cart'] = {"restaurants": {}}
    session.modified = True
    flash('Order placed successfully!', 'success')
    return redirect(url_for('index'))

# --------------------
# Reviews
# --------------------
@app.route('/add_review/<int:restaurant_id>', methods=['POST'])
@login_required
def add_review(restaurant_id):
    content = (request.form.get('content') or '').strip()
    try:
        rating = int(request.form.get('rating', '5'))
    except ValueError:
        rating = 5
    rating = max(1, min(5, rating))
    if not content:
        flash('Review cannot be empty.', 'danger')
        return redirect(url_for('restaurant_detail', id=restaurant_id))
    new_comment = Comment(
        user_id=session['user_id'],
        restaurant_id=restaurant_id,
        content=content,
        rating=rating
    )
    db.session.add(new_comment)
    db.session.commit()
    flash('Review submitted.', 'success')
    return redirect(url_for('restaurant_detail', id=restaurant_id))

@app.route('/reviews/<int:restaurant_id>')
def reviews(restaurant_id):
    comments = Comment.query.filter_by(restaurant_id=restaurant_id).order_by(Comment.id.desc()).all()
    return render_template('reviews.html', comments=comments, user=current_user())


# --------------------
# My Restaurants
# --------------------
@app.route('/my_restaurants')
def my_restaurants():
    if 'user_id' not in session:
        flash("You must log in first.", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    restaurants = Restaurant.query.filter_by(owner_id=user_id).all()
    return render_template('my_restaurants.html', restaurants=restaurants, user=current_user())

# --------------------
# Payment
# --------------------
@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    _init_cart()
    total = _cart_total()
    if total == 0:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart'))

    if request.method == 'POST':
        flash('Payment successful! Your order has been placed.', 'success')
        
        restaurants = session['cart'].get('restaurants', {})
        for rid, items in restaurants.items():
            total_price = sum(it['price'] * it['quantity'] for it in items)
            new_order = Order(
                customer_id=session['user_id'],
                restaurant_id=int(rid),
                total_price=total_price,
                status='pending'
            )
            db.session.add(new_order)
            db.session.commit()
            for it in items:
                db.session.add(OrderItem(
                    order_id=new_order.id,
                    menu_id=it['id'],
                    quantity=it['quantity'],
                    price=it['price']
                ))
            db.session.commit()

        session['cart'] = {"restaurants": {}}
        session.modified = True
        return redirect(url_for('index'))

    return render_template('payment.html', total=total, user=current_user())

# --------------------
# Run App
# --------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
