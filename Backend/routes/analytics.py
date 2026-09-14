"""
Analytics Blueprint (Member 5)
Handles business intelligence, Texas regional sales breakdown, top-performing products, and KPI metrics.
"""

from flask import Blueprint, jsonify, render_template
from db import get_db_cursor

analytics_bp = Blueprint("analytics_bp", __name__)

# --- View Route ---
@analytics_bp.route("/analytics", methods=["GET"])
def analytics_view():
    """Renders the business intelligence & analytics dashboard view."""
    return render_template("analytics.html")

# --- API Endpoints ---
@analytics_bp.route("/summary", methods=["GET"])
def get_kpi_summary():
    """Returns high-level business intelligence metrics."""
    try:
        with get_db_cursor(commit=False) as cursor:
            # Total Revenue & Total Orders
            cursor.execute("""
                SELECT 
                    COUNT(order_id) AS total_orders,
                    COALESCE(SUM(total_amount), 0.00) AS total_revenue,
                    COALESCE(AVG(total_amount), 0.00) AS avg_order_value
                FROM ORDERS;
            """)
            orders_stat = cursor.fetchone()

            # Active Customers
            cursor.execute("SELECT COUNT(*) AS total_customers FROM CUSTOMERS;")
            cust_stat = cursor.fetchone()

            # Total Catalog Items
            cursor.execute("SELECT COUNT(*) AS total_products, COALESCE(SUM(stock_quantity), 0) AS total_inventory FROM PRODUCTS;")
            prod_stat = cursor.fetchone()

            # Texas Cities Covered
            cursor.execute("SELECT COUNT(*) AS total_cities FROM TEXAS_CITY;")
            city_stat = cursor.fetchone()

            # Active Shipments
            cursor.execute("SELECT COUNT(*) AS active_shipments FROM SHIPMENTS WHERE shipment_status IN ('Label Created', 'In Transit', 'Out for Delivery');")
            ship_stat = cursor.fetchone()

        return jsonify({
            "success": True,
            "data": {
                "total_revenue": float(orders_stat["total_revenue"]),
                "total_orders": orders_stat["total_orders"],
                "avg_order_value": round(float(orders_stat["avg_order_value"]), 2),
                "total_customers": cust_stat["total_customers"],
                "total_products": prod_stat["total_products"],
                "total_inventory": int(prod_stat["total_inventory"]),
                "total_cities": city_stat["total_cities"],
                "active_shipments": ship_stat["active_shipments"]
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@analytics_bp.route("/by-city", methods=["GET"])
def get_sales_by_city():
    """Returns sales breakdown and metrics grouped by Texas city."""
    try:
        query = """
            SELECT 
                city_id,
                city_name,
                city_type,
                total_orders,
                CAST(gross_revenue AS FLOAT) AS gross_revenue,
                CAST(avg_order_value AS FLOAT) AS avg_order_value
            FROM v_sales_by_city
            ORDER BY gross_revenue DESC, total_orders DESC;
        """
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query)
            city_sales = cursor.fetchall()

        return jsonify({"success": True, "count": len(city_sales), "data": city_sales}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@analytics_bp.route("/top-products", methods=["GET"])
def get_top_products():
    """Returns highest grossing and most popular products."""
    try:
        query = """
            SELECT 
                product_id,
                product_name,
                sku,
                category_name,
                CAST(price AS FLOAT) AS price,
                stock_quantity,
                units_sold,
                CAST(total_revenue AS FLOAT) AS total_revenue
            FROM v_top_products
            ORDER BY total_revenue DESC, units_sold DESC
            LIMIT 10;
        """
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query)
            top_products = cursor.fetchall()

        return jsonify({"success": True, "data": top_products}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@analytics_bp.route("/categories", methods=["GET"])
def get_category_performance():
    """Returns revenue contribution and volume per product category."""
    try:
        query = """
            SELECT 
                category_id,
                category_name,
                product_count,
                total_units_sold,
                CAST(total_revenue AS FLOAT) AS total_revenue
            FROM v_category_performance
            ORDER BY total_revenue DESC;
        """
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query)
            cat_perf = cursor.fetchall()

        return jsonify({"success": True, "data": cat_perf}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
