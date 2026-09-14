"""
Auth & Cart Blueprint (Member 2)
Handles customer profile, Texas city associations, session management, and shopping cart operations.
"""

from flask import Blueprint, request, jsonify, render_template
from db import get_db_cursor

auth_cart_bp = Blueprint("auth_cart_bp", __name__)

# --- View Route ---
@auth_cart_bp.route("/cart", methods=["GET"])
def cart_view():
    """Renders customer auth and shopping cart frontend page."""
    return render_template("auth_cart.html")

# --- API Endpoints ---
@auth_cart_bp.route("/cities", methods=["GET"])
def get_texas_cities():
    """Returns list of Texas cities for customer selection and shipping."""
    try:
        query = """
            SELECT city_id, city_name, city_type, state_code, postal_code_prefix
            FROM TEXAS_CITY
            ORDER BY city_type ASC, city_name ASC;
        """
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query)
            cities = cursor.fetchall()
        return jsonify({"success": True, "data": cities}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@auth_cart_bp.route("/customers", methods=["GET"])
def get_customers():
    """Returns all customers along with their Texas city details."""
    try:
        query = """
            SELECT 
                c.customer_id,
                c.first_name,
                c.last_name,
                c.email,
                c.phone,
                c.address_line,
                c.city_id,
                tc.city_name,
                tc.city_type,
                c.created_at
            FROM CUSTOMERS c
            LEFT JOIN TEXAS_CITY tc ON c.city_id = tc.city_id
            ORDER BY c.customer_id ASC;
        """
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query)
            customers = cursor.fetchall()
        return jsonify({"success": True, "data": customers}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@auth_cart_bp.route("/customers", methods=["POST"])
def create_customer():
    """Registers a new customer associated with a Texas city."""
    try:
        data = request.get_json() or {}
        required = ["first_name", "last_name", "email", "city_id"]
        for field in required:
            if not data.get(field):
                return jsonify({"success": False, "error": f"Missing required field: '{field}'"}), 400

        query = """
            INSERT INTO CUSTOMERS (first_name, last_name, email, phone, address_line, city_id)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        params = (
            data.get("first_name"),
            data.get("last_name"),
            data.get("email"),
            data.get("phone", ""),
            data.get("address_line", ""),
            data.get("city_id")
        )

        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            customer_id = cursor.lastrowid

            # Create default empty cart for customer
            cursor.execute("INSERT INTO CARTS (customer_id, session_token) VALUES (%s, %s)",
                           (customer_id, f"sess_cust_{customer_id}"))

        return jsonify({"success": True, "message": "Customer registered", "customer_id": customer_id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@auth_cart_bp.route("/cart/<int:customer_id>", methods=["GET"])
def get_customer_cart(customer_id):
    """Retrieves current cart items and totals for a given customer."""
    try:
        # Ensure cart exists
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("SELECT cart_id FROM CARTS WHERE customer_id = %s;", (customer_id,))
            cart = cursor.fetchone()
            if not cart:
                cursor.execute("INSERT INTO CARTS (customer_id, session_token) VALUES (%s, %s);",
                               (customer_id, f"sess_cust_{customer_id}"))
                cursor.execute("SELECT cart_id FROM CARTS WHERE customer_id = %s;", (customer_id,))
                cart = cursor.fetchone()

            cart_id = cart["cart_id"]

            items_query = """
                SELECT 
                    ci.cart_item_id,
                    ci.cart_id,
                    ci.product_id,
                    p.name AS product_name,
                    p.sku,
                    CAST(p.price AS FLOAT) AS unit_price,
                    ci.quantity,
                    CAST(p.price * ci.quantity AS FLOAT) AS line_total,
                    p.image_url,
                    p.stock_quantity
                FROM CART_ITEMS ci
                JOIN PRODUCTS p ON ci.product_id = p.product_id
                WHERE ci.cart_id = %s
                ORDER BY ci.added_at DESC;
            """
            cursor.execute(items_query, (cart_id,))
            items = cursor.fetchall()

        subtotal = sum(item["line_total"] for item in items)
        tax = round(subtotal * 0.0825, 2)  # Texas state sales tax 8.25%
        shipping = 10.00 if subtotal > 0 else 0.00
        total = round(subtotal + tax + shipping, 2)

        return jsonify({
            "success": True,
            "cart_id": cart_id,
            "customer_id": customer_id,
            "items": items,
            "summary": {
                "subtotal": round(subtotal, 2),
                "tax": tax,
                "shipping": shipping,
                "total": total,
                "item_count": sum(i["quantity"] for i in items)
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@auth_cart_bp.route("/cart/add", methods=["POST"])
def add_to_cart():
    """Adds a product to customer's cart or increments existing quantity."""
    try:
        data = request.get_json() or {}
        customer_id = data.get("customer_id")
        product_id = data.get("product_id")
        quantity = int(data.get("quantity", 1))

        if not customer_id or not product_id:
            return jsonify({"success": False, "error": "customer_id and product_id are required"}), 400

        with get_db_cursor(commit=True) as cursor:
            # Get cart
            cursor.execute("SELECT cart_id FROM CARTS WHERE customer_id = %s;", (customer_id,))
            cart = cursor.fetchone()
            if not cart:
                cursor.execute("INSERT INTO CARTS (customer_id, session_token) VALUES (%s, %s);",
                               (customer_id, f"sess_cust_{customer_id}"))
                cursor.execute("SELECT cart_id FROM CARTS WHERE customer_id = %s;", (customer_id,))
                cart = cursor.fetchone()

            cart_id = cart["cart_id"]

            upsert_query = """
                INSERT INTO CART_ITEMS (cart_id, product_id, quantity)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity);
            """
            cursor.execute(upsert_query, (cart_id, product_id, quantity))

        return jsonify({"success": True, "message": "Item added to cart"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@auth_cart_bp.route("/cart/update", methods=["POST"])
def update_cart_item():
    """Updates quantity of a cart item."""
    try:
        data = request.get_json() or {}
        cart_item_id = data.get("cart_item_id")
        quantity = int(data.get("quantity", 1))

        with get_db_cursor(commit=True) as cursor:
            if quantity <= 0:
                cursor.execute("DELETE FROM CART_ITEMS WHERE cart_item_id = %s;", (cart_item_id,))
            else:
                cursor.execute("UPDATE CART_ITEMS SET quantity = %s WHERE cart_item_id = %s;", (quantity, cart_item_id))

        return jsonify({"success": True, "message": "Cart item updated"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@auth_cart_bp.route("/cart/clear", methods=["POST"])
def clear_cart():
    """Clears all items in a customer's cart."""
    try:
        data = request.get_json() or {}
        customer_id = data.get("customer_id")
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("SELECT cart_id FROM CARTS WHERE customer_id = %s;", (customer_id,))
            cart = cursor.fetchone()
            if cart:
                cursor.execute("DELETE FROM CART_ITEMS WHERE cart_id = %s;", (cart["cart_id"],))
        return jsonify({"success": True, "message": "Cart cleared"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
