# THECHEFenglish
 
# TheChef

#### Video Demo: <https://youtu.be/ylv-I55J3W8?si=FyfpImM7WVZlRMdd>

#### Description:
TheChef is a web-based platform designed to connect home chefs with customers, enabling anyone to create and manage their own personal restaurant without the need for a physical location. Inspired by the concept of home-cooked meals and local culinary talent, TheChef aims to make high-quality, homemade food accessible while supporting independent chefs.

The platform is built using **Flask (Python)** for the backend, **SQLite** for the database, and standard web technologies (HTML, CSS, JavaScript) for the frontend. Users can register, log in, and manage their profiles. Each user can create one or multiple restaurant profiles, add menu items with descriptions, prices, and images, and manage orders from customers.

**Key Features:**

1. **User Management:**
   - Registration, login, and secure password hashing.
   - Session management to keep users logged in.
   - Role-based access: restaurant owners have control over their own restaurants and menu items.

2. **Restaurant Management:**
   - Owners can add, edit, and delete restaurants.
   - Each restaurant can have multiple menu items with images, descriptions, and prices.
   - Users can view restaurant details, menu items, and reviews.

3. **Menu and Order System:**
   - Customers can add menu items to a cart, update quantities, and remove items.
   - Orders are tracked with a database, including total price and status.
   - Checkout and payment simulation are included.

4. **Reviews and Ratings:**
   - Users can submit reviews and ratings for restaurants.
   - Reviews are displayed in descending order by submission date.
   - Ratings are validated to remain between 1 and 5 stars.

5. **Search and Filtering:**
   - Restaurants can be searched by name, city, or state.
   - The search is case-insensitive and supports partial matches.

6. **File Uploads:**
   - Users can upload images for restaurants and menu items.
   - Supported image types: PNG, JPG, JPEG, GIF, WEBP.
   - Images are stored securely in the server's `static/uploads` directory.

7. **Cart and Checkout:**
   - Users can manage a multi-restaurant cart.
   - Cart items are stored in the session.
   - Orders are generated per restaurant with corresponding order items.

8. **Security and Access Control:**
   - Login required for actions like adding restaurants, menu items, or submitting reviews.
   - Restaurant ownership is verified before editing or deleting content.
   - Input validation and allowed file extensions are enforced.

**File Structure Overview:**

- `app.py`: Main Flask application file containing routes, helper functions, and configuration.
- `models.py`: Contains database models for users, restaurants, menu items, orders, order items, and comments.
- `templates/`: HTML templates for different pages (index, restaurant details, login, register, cart, etc.).
- `static/uploads/`: Folder for uploaded images.
- `static/css/`, `static/js/`: Optional static assets for styling and interactivity.

**Design Choices:**

- **Flask** was chosen for simplicity and ease of deployment, suitable for small-scale web applications.
- **SQLite** was selected as the database for its lightweight setup and integration with Flask.
- **Session-based cart** simplifies cart management without a separate front-end framework.
- Security considerations include password hashing, session protection, and ownership checks for sensitive operations.
- File uploads are validated to ensure only allowed image types and size limits (5MB) are accepted.

**Goals and Outcomes:**

- **Minimum goal:** Implement a working platform where users can create restaurants and menu items, view them, and simulate orders.
- **Better outcome:** Include reviews, ratings, image uploads, and full CRUD operations for restaurants and menu items.
- **Best outcome:** Full cart management across multiple restaurants, payment simulation, and polished UI/UX for an end-to-end experience.

** Project Structure:**

thechef/
├──  static/
│   ├── cart.css
│   ├── payment.css
│   ├── kayit.css
│   ├── restaurantdetail.css
│   ├── styles.css
│   ├── script.js
│   └── logo.png
│
├──  templates/
│   ├── add_menu_item.html
│   ├── add_resturant.html
│   ├── edit_menu_item.html
│   ├── edit_resturant.html
│   ├── index.html
│   ├── layout.html
│   ├── login.html
│   ├── payment.html
│   ├── register.html
│   ├── restaurant_detail.html
│   └── reviews.html
│
├── app.py
├── README.md
└── requirements.txt


**How to Run the Project:**

Clone the repository

git clone https://github.com/meryem74/THECHEFenglish.git
cd THECHEFenglish

Install dependencies

pip install -r requirements.txt


Set up the database

flask db init
flask db migrate
flask db upgrade


Run the application

python app.py


Open the app in your browser:
 http://127.0.0.1:5000/
TheChef demonstrates the integration of backend logic, database handling, and frontend interaction while solving a practical problem: allowing people to sell homemade meals easily and safely.                                                                                                                                           buna çalışma şeklinide mi ekliycem
