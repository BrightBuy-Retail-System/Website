"""
Logistics Blueprint (Member 4)
Handles shipping logistics, Texas delivery route optimization, warehouse hubs, and tracking.
"""

from flask import Blueprint, request, jsonify, render_template
from db import get_db_cursor

logistics_bp = Blueprint("logistics_bp", __name__)

# --- View Route ---
@logistics_bp.route("/logistics", methods=["GET"])
def logistics_view():
    """Renders the logistics and supply chain frontend view."""
    return render_template("logistics.html")

# --- API Endpoints ---
@logistics_bp.route("/warehouses", methods=["GET"])
def get_warehouses():
    """Fetches all Texas warehouse facilities."""
    try:
        query = """
            SELECT 
                w.warehouse_id,
                w.name,
                w.city_id,
                tc.city_name,
                w.address,
                w.capacity_sqft,
                w.is_active
            FROM WAREHOUSES w
            JOIN TEXAS_CITY tc ON w.city_id = tc.city_id
            ORDER BY w.warehouse_id ASC;
        """
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query)
            warehouses = cursor.fetchall()
        return jsonify({"success": True, "data": warehouses}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@logistics_bp.route("/routes", methods=["GET"])
def get_delivery_routes():
    """Fetches delivery routes connecting Texas cities with mileage and transit time."""
    try:
        query = """
            SELECT 
                r.route_id,
                r.origin_city_id,
                c1.city_name AS origin_city,
                c1.city_type AS origin_type,
                r.destination_city_id,
                c2.city_name AS destination_city,
                c2.city_type AS destination_type,
                CAST(r.distance_miles AS FLOAT) AS distance_miles,
                CAST(r.estimated_hours AS FLOAT) AS estimated_hours,
                r.is_major_corridor
            FROM DELIVERY_ROUTES r
            JOIN TEXAS_CITY c1 ON r.origin_city_id = c1.city_id
            JOIN TEXAS_CITY c2 ON r.destination_city_id = c2.city_id
            ORDER BY r.is_major_corridor DESC, r.distance_miles ASC;
        """
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query)
            routes = cursor.fetchall()
        return jsonify({"success": True, "count": len(routes), "data": routes}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@logistics_bp.route("/shipments", methods=["GET"])
def get_shipments():
    """Fetches active and historical shipments across Texas destinations."""
    try:
        status_filter = request.args.get("status")
        query = """
            SELECT 
                s.shipment_id,
                s.order_id,
                o.order_number,
                s.carrier,
                s.tracking_number,
                s.origin_warehouse_id,
                w.name AS origin_warehouse,
                s.destination_city_id,
                tc.city_name AS destination_city,
                tc.city_type AS destination_type,
                s.shipment_status,
                s.shipped_at,
                s.delivered_at,
                s.estimated_delivery
            FROM SHIPMENTS s
            JOIN ORDERS o ON s.order_id = o.order_id
            LEFT JOIN WAREHOUSES w ON s.origin_warehouse_id = w.warehouse_id
            JOIN TEXAS_CITY tc ON s.destination_city_id = tc.city_id
            WHERE 1=1
        """
        params = []
        if status_filter:
            query += " AND s.shipment_status = %s"
            params.append(status_filter)

        query += " ORDER BY s.shipment_id DESC;"

        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query, tuple(params))
            shipments = cursor.fetchall()

        return jsonify({"success": True, "count": len(shipments), "data": shipments}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@logistics_bp.route("/shipments/<int:shipment_id>/status", methods=["PUT"])
def update_shipment_status(shipment_id):
    """Updates shipment tracking status and delivery timestamp."""
    try:
        data = request.get_json() or {}
        status = data.get("shipment_status")
        valid_statuses = ['Label Created', 'In Transit', 'Out for Delivery', 'Delivered', 'Delayed']

        if status not in valid_statuses:
            return jsonify({"success": False, "error": f"Invalid status: {status}"}), 400

        with get_db_cursor(commit=True) as cursor:
            if status == "Delivered":
                cursor.execute("""
                    UPDATE SHIPMENTS 
                    SET shipment_status = %s, delivered_at = CURRENT_TIMESTAMP
                    WHERE shipment_id = %s;
                """, (status, shipment_id))
            elif status == "In Transit":
                cursor.execute("""
                    UPDATE SHIPMENTS 
                    SET shipment_status = %s, shipped_at = COALESCE(shipped_at, CURRENT_TIMESTAMP)
                    WHERE shipment_id = %s;
                """, (status, shipment_id))
            else:
                cursor.execute("""
                    UPDATE SHIPMENTS 
                    SET shipment_status = %s
                    WHERE shipment_id = %s;
                """, (status, shipment_id))

        return jsonify({"success": True, "message": f"Shipment updated to {status}"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@logistics_bp.route("/routes", methods=["POST"])
def add_delivery_route():
    """Adds a new transit corridor between two Texas cities."""
    try:
        data = request.get_json() or {}
        origin_city_id = data.get("origin_city_id")
        destination_city_id = data.get("destination_city_id")
        distance_miles = data.get("distance_miles")
        estimated_hours = data.get("estimated_hours")

        if not (origin_city_id and destination_city_id and distance_miles and estimated_hours):
            return jsonify({"success": False, "error": "All route parameters required"}), 400

        query = """
            INSERT INTO DELIVERY_ROUTES (origin_city_id, destination_city_id, distance_miles, estimated_hours, is_major_corridor)
            VALUES (%s, %s, %s, %s, %s);
        """
        params = (
            origin_city_id,
            destination_city_id,
            distance_miles,
            estimated_hours,
            data.get("is_major_corridor", True)
        )

        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            route_id = cursor.lastrowid

        return jsonify({"success": True, "message": "Delivery route added", "route_id": route_id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
