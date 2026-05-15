from flask import Flask, request, jsonify, session, redirect, render_template
from pymongo import MongoClient
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.secret_key = "secretkey123"

# ------------------ MongoDB ------------------
client = MongoClient("mongodb+srv://groceryadmin:<RSPSND08>@grocery.vtdmefo.mongodb.net/?appName=grocery")
db = client["grocery"]

# Collections
users = db["users"]
customer_orders = db["customer_orders"]

# ------------------ PAGES ------------------

# Default page -> Login
@app.route("/")
def login_page():
    return render_template("login.html")


# Optional direct /login URL
@app.route("/login")
def login_route():
    return render_template("login.html")


# Signup page
@app.route("/signup")
def signup_page():
    return render_template("signup.html")


# Home page (only for logged-in users)
@app.route("/home")
def home_page():
    if "user" not in session:
        return redirect("/")
    return render_template("home.html", username=session["user"])


# Bill page (only for logged-in users)
@app.route("/bill")
def bill_page():
    if "user" not in session:
        return redirect("/")
    return render_template("bill.html")


# Customer details page
@app.route("/customer-details")
def customer_details_page():
    if "user" not in session:
        return redirect("/")
    return render_template("customer_details.html")


# Success page
@app.route("/success")
def success_page():
    if "user" not in session:
        return redirect("/")
    return render_template("success.html")


# ------------------ AUTH APIs ------------------

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    # Check if username already exists
    if users.find_one({"username": username}):
        return jsonify({"error": "Username already exists"}), 400

    # Insert new user
    users.insert_one({
        "username": username,
        "email": email,
        "password": password
    })

    return jsonify({"message": "Signup successful"}), 200


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # Find matching user
    user = users.find_one({
        "username": username,
        "password": password
    })

    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    # Save username in session
    session["user"] = username

    return jsonify({
        "message": "Login successful",
        "username": username
    })


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ------------------ PRODUCTS API ------------------

@app.route("/api/all-products")
def get_all_products():
    collections = [
        "bath",
        "biscuits",
        "chocolate",
        "cooldrinks",
        "dals",
        "detergents",
        "flours",
        "masala",
        "oil",
        "packagedfood",
        "rice"
    ]

    all_products = []

    for col in collections:
        if col in db.list_collection_names():
            items = list(db[col].find({}, {"_id": 0}))

            # Add collection name to each product
            for item in items:
                item["collection"] = col

            all_products.extend(items)

    # Sort products alphabetically by name
    all_products.sort(
        key=lambda x: x.get("name", "").lower()
    )

    return jsonify(all_products)


# ------------------ CONFIRM ORDER API ------------------

@app.route("/api/confirm-order", methods=["POST"])
def confirm_order():
    try:
        # Login check
        if "user" not in session:
            return jsonify({"error": "Please login first"}), 401

        data = request.get_json()

        customer_name = data.get("name")
        phone = data.get("phone")
        address = data.get("address")
        bill = data.get("bill", [])
        total = data.get("total", 0)

        # Validation
        if not customer_name or not phone or not address:
            return jsonify({"error": "All fields are required"}), 400

        # Create order document
        order = {
            "username": session["user"],
            "customer_name": customer_name,
            "phone": phone,
            "address": address,
            "bill": bill,
            "total": float(total),
            "order_time": datetime.now()
        }

        # Save to MongoDB
        result = customer_orders.insert_one(order)

        # Confirm inserted successfully
        if result.inserted_id:
            return jsonify({
                "message": "Order confirmed successfully"
            })

        return jsonify({
            "error": "Failed to save order"
        }), 500

    except Exception as e:
        print("Confirm Order Error:", e)
        return jsonify({
            "error": str(e)
        }), 500

# ------------------ RUN SERVER ------------------

if __name__ == "__main__":
    # Access from laptop:
    # http://127.0.0.1:5000/login
    #
    # Access from mobile on same Wi-Fi:
    # http://YOUR_COMPUTER_IP:5000/login
    #
    # After hosting:
    # https://your-domain.com/login
    app.run(debug=True, host="0.0.0.0", port=5000)