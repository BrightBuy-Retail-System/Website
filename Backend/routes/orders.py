"""
Orders Blueprint (Member 3)
Handles order creation, checkout processing, order line items, and status tracking.
"""

import uuid
from flask import Blueprint, request, jsonify, render_template
from db import get_db_cursor

orders_bp = Blueprint("orders_bp", __name__)

# --- View Route ---
@orders_bp.route("/orders", methods=["GET"])
def orders_view():
    """Renders orders management frontend view."""
    return render_template("orders.html")

# --- API Endpoints ---
@orders_bp.route("/", methods=["GET"])
def get_orders():
    """Fetches all orders with customer details and destination Texas city."""
    try:
        status_filter = request.args.get("status")
        city_id = request.args.get("city_id", type=int)

        query = """
            SELECT 
                o.order_id,
                o.order_number,
                o.customer_id,
                CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
                c.email AS customer_email,
                o.shipping_city_id,
                tc.city_name AS shipping_city,
                tc.city_type,
                o.shipping_address,
                o.order_status,
                o.payment_status,
                CAST(o.subtotal AS FLOAT) AS subtotal,
                CAST(o.tax AS FLOAT) AS tax,
                CAST(o.shipping_cost AS FLOAT) AS shipping_cost,
                CAST(o.total_amount AS FLOAT) AS total_amount,
                o.order_date
            FROM ORDERS o
            JOIN CUSTOMERS c ON o.customer_id = c.customer_id
            JOIN TEXAS_CITY tc ON o.shipping_city_id = tc.city_id
            WHERE 1=1
        """
        params = []
        if status_filter:
            query += " AND o.order_status = %s"
            params.append(status_filter)
        if city_id:
            query += " AND o.shipping_city_id = %s"
            params.append(city_id)

        query += " ORDER BY o.order_id DESC;"

        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query, tuple(params))
            orders = cursor.fetchall()

        return jsonify({"success": True, "count": len(orders), "data": orders}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@orders_bp.route("/<int:order_id>", methods=["GET"])
def get_order_details(order_id):
    """Fetches order details along with individual order items and tracking."""
    try:
        order_query = """
            SELECT 
                o.order_id,
                o.order_number,
                o.customer_id,
                CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
                c.email AS customer_email,
                c.phone AS customer_phone,
                o.shipping_city_id,
                tc.city_name AS shipping_city,
                o.shipping_address,
                o.order_status,
                o.payment_status,
                CAST(o.subtotal AS FLOAT) AS subtotal,
                CAST(o.tax AS FLOAT) AS tax,
                CAST(o.shipping_cost AS FLOAT) AS shipping_cost,
                CAST(o.total_amount AS FLOAT) AS total_amount,
                o.order_date
            FROM ORDERS o
            JOIN CUSTOMERS c ON o.customer_id = c.customer_id
            JOIN TEXAS_CITY tc ON o.shipping_city_id = tc.city_id
            WHERE o.order_id = %s;
        """
        items_query = """
            SELECT 
                oi.order_item_id,
                oi.product_id,
                p.name AS product_name,
                p.sku,
                oi.quantity,
                CAST(oi.unit_price AS FLOAT) AS unit_price,
                CAST(oi.line_total AS FLOAT) AS line_total,
                p.image_url
            FROM ORDER_ITEMS oi
            JOIN PRODUCTS p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s;
        """
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(order_query, (order_id,))
            order = cursor.fetchone()
            if not order:
                return jsonify({"success": False, "error": "Order not found"}), 404

            cursor.execute(items_query, (order_id,))
            items = cursor.fetchall()

            order["items"] = items

        return jsonify({"success": True, "data": order}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@orders_bp.route("/checkout", methods=["POST"])
def checkout_cart():
    """
    Transforms customer's cart items into a placed order.
    Deducts inventory stock and generates an order number.
    """
    try:
        data = request.get_json() or {}
        customer_id = data.get("customer_id")
        shipping_city_id = data.get("shipping_city_id")
        shipping_address = data.get("shipping_address")

        if not customer_id or not shipping_city_id or not shipping_address:
            return jsonify({"success": False, "error": "customer_id, shipping_city_id, and shipping_address are required"}), 400

        with get_db_cursor(commit=True) as cursor:
            # 1. Fetch Cart
            cursor.execute("SELECT cart_id FROM CARTS WHERE customer_id = %s;", (customer_id,))
            cart = cursor.fetchone()
            if not cart:
                return jsonify({"success": False, "error": "No cart found for customer"}), 400

            cart_id = cart["cart_id"]

            # 2. Fetch Cart Items
            cart_items_query = """
                SELECT ci.product_id, ci.quantity, p.price, p.stock_quantity, p.name
                FROM CART_ITEMS ci
                JOIN PRODUCTS p ON ci.product_id = p.product_id
                WHERE ci.cart_id = %s;
            """
            cursor.execute(cart_items_query, (cart_id,))
            cart_items = cursor.fetchall()

            if not cart_items:
                return jsonify({"success": False, "error": "Cart is empty"}), 400

            # 3. Calculate totals & check stock
            subtotal = sum(float(item["price"]) * item["quantity"] for item in cart_items)
            tax = round(subtotal * 0.0825, 2)
            shipping_cost = 12.00
            total_amount = round(subtotal + tax + shipping_cost, 2)
            order_number = f"TX-ORD-{uuid.uuid4().hex[:8].upper()}"

            # 4. Insert Order
            insert_order_sql = """
                INSERT INTO ORDERS (order_number, customer_id, shipping_city_id, shipping_address, order_status, payment_status, subtotal, tax, shipping_cost, total_amount)
                VALUES (%s, %s, %s, %s, 'Processing', 'Paid', %s, %s, %s, %s);
            """
            cursor.execute(insert_order_sql, (order_number, customer_id, shipping_city_id, shipping_address, subtotal, tax, shipping_cost, total_amount))
            order_id = cursor.lastrowid

            # 5. Insert Order Items & deduct stock
            for item in cart_items:
                line_total = float(item["price"]) * item["quantity"]
                cursor.execute("""
                    INSERT INTO ORDER_ITEMS (order_id, product_id, quantity, unit_price, line_total)
                    VALUES (%s, %s, %s, %s, %s);
                """, (order_id, item["product_id"], item["quantity"], item["price"], line_total))

                cursor.execute("""
                    UPDATE PRODUCTS 
                    SET stock_quantity = GREATEST(0, stock_quantity - %s)
                    WHERE product_id = %s;
                """, (item["quantity"], item["product_id"]))

            # 6. Clear Cart
            cursor.execute("DELETE FROM CART_ITEMS WHERE cart_id = %s;", (cart_id,))

            # 7. Create corresponding Shipment record
            tracking_number = f"TX-TRK-{uuid.uuid4().hex[:8].upper()}"
            cursor.execute("""
                INSERT INTO SHIPMENTS (order_id, carrier, tracking_number, origin_warehouse_id, destination_city_id, shipment_status)
                VALUES (%s, 'Texas Express Logistics', %s, 1, %s, 'Label Created');
            """, (order_id, tracking_number, shipping_city_id))

        return jsonify({
            "success": True,
            "message": "Order created successfully",
            "order_id": order_id,
            "order_number": order_number,
            "total_amount": total_amount
        }), 201

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@orders_bp.route("/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    """Updates order fulfillment status."""
    try:
        data = request.get_json() or {}
        new_status = data.get("order_status")
        valid_statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']

        if new_status not in valid_statuses:
            return jsonify({"success": False, "error": f"Invalid status. Must be one of: {valid_statuses}"}), 400

        with get_db_cursor(commit=True) as cursor:
            cursor.execute("UPDATE ORDERS SET order_status = %s WHERE order_id = %s;", (new_status, order_id))

        return jsonify({"success": True, "message": f"Order status updated to {new_status}"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
