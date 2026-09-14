"""
Catalog Blueprint (Member 1)
Handles product inventory, categories, search, filtering, and catalog management.
"""

from flask import Blueprint, request, jsonify, render_template
from db import get_db_cursor

catalog_bp = Blueprint("catalog_bp", __name__)

# --- View Route ---
@catalog_bp.route("/catalog", methods=["GET"])
def catalog_view():
    """Renders the catalog management and browsing frontend page."""
    return render_template("catalog.html")

# --- API Endpoints ---
@catalog_bp.route("/categories", methods=["GET"])
def get_categories():
    """Fetches all product categories along with item count."""
    try:
        query = """
            SELECT 
                c.category_id,
                c.name,
                c.slug,
                c.description,
                c.icon,
                COUNT(p.product_id) AS product_count
            FROM CATEGORIES c
            LEFT JOIN PRODUCTS p ON c.category_id = p.category_id
            GROUP BY c.category_id, c.name, c.slug, c.description, c.icon
            ORDER BY c.name ASC;
        """
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query)
            categories = cursor.fetchall()
        return jsonify({"success": True, "data": categories}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@catalog_bp.route("/products", methods=["GET"])
def get_products():
    """
    Fetches products with optional filtering by category_id, search term, and stock status.
    Query params: category_id, search, in_stock, sort
    """
    try:
        category_id = request.args.get("category_id", type=int)
        search = request.args.get("search", type=str)
        in_stock = request.args.get("in_stock", type=bool)
        sort_by = request.args.get("sort", default="name_asc")

        query = """
            SELECT 
                p.product_id,
                p.category_id,
                c.name AS category_name,
                p.name,
                p.sku,
                CAST(p.price AS FLOAT) AS price,
                p.stock_quantity,
                p.description,
                p.image_url,
                p.is_active,
                p.created_at
            FROM PRODUCTS p
            LEFT JOIN CATEGORIES c ON p.category_id = c.category_id
            WHERE 1=1
        """
        params = []

        if category_id:
            query += " AND p.category_id = %s"
            params.append(category_id)
        if search:
            query += " AND (p.name LIKE %s OR p.sku LIKE %s OR p.description LIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        if in_stock:
            query += " AND p.stock_quantity > 0"

        # Sorting logic
        if sort_by == "price_asc":
            query += " ORDER BY p.price ASC"
        elif sort_by == "price_desc":
            query += " ORDER BY p.price DESC"
        elif sort_by == "stock_desc":
            query += " ORDER BY p.stock_quantity DESC"
        else:
            query += " ORDER BY p.product_id DESC"

        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query, tuple(params))
            products = cursor.fetchall()

        return jsonify({"success": True, "count": len(products), "data": products}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@catalog_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Fetches details of a single product."""
    try:
        query = """
            SELECT 
                p.product_id,
                p.category_id,
                c.name AS category_name,
                p.name,
                p.sku,
                CAST(p.price AS FLOAT) AS price,
                p.stock_quantity,
                p.description,
                p.image_url,
                p.is_active,
                p.created_at
            FROM PRODUCTS p
            LEFT JOIN CATEGORIES c ON p.category_id = c.category_id
            WHERE p.product_id = %s;
        """
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query, (product_id,))
            product = cursor.fetchone()

        if not product:
            return jsonify({"success": False, "error": "Product not found"}), 404

        return jsonify({"success": True, "data": product}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@catalog_bp.route("/products", methods=["POST"])
def create_product():
    """Creates a new product in the catalog."""
    try:
        data = request.get_json() or {}
        required = ["name", "sku", "price"]
        for field in required:
            if field not in data or data[field] is None:
                return jsonify({"success": False, "error": f"Missing required field: '{field}'"}), 400

        query = """
            INSERT INTO PRODUCTS (category_id, name, sku, price, stock_quantity, description, image_url, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        params = (
            data.get("category_id"),
            data.get("name"),
            data.get("sku"),
            data.get("price"),
            data.get("stock_quantity", 0),
            data.get("description", ""),
            data.get("image_url", ""),
            data.get("is_active", True)
        )

        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            new_id = cursor.lastrowid

        return jsonify({"success": True, "message": "Product created successfully", "product_id": new_id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@catalog_bp.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """Updates product details."""
    try:
        data = request.get_json() or {}
        query = """
            UPDATE PRODUCTS
            SET category_id = COALESCE(%s, category_id),
                name = COALESCE(%s, name),
                sku = COALESCE(%s, sku),
                price = COALESCE(%s, price),
                stock_quantity = COALESCE(%s, stock_quantity),
                description = COALESCE(%s, description),
                image_url = COALESCE(%s, image_url),
                is_active = COALESCE(%s, is_active)
            WHERE product_id = %s;
        """
        params = (
            data.get("category_id"),
            data.get("name"),
            data.get("sku"),
            data.get("price"),
            data.get("stock_quantity"),
            data.get("description"),
            data.get("image_url"),
            data.get("is_active"),
            product_id
        )

        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, params)

        return jsonify({"success": True, "message": f"Product {product_id} updated successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@catalog_bp.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """Deletes a product from the catalog."""
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM PRODUCTS WHERE product_id = %s;", (product_id,))
        return jsonify({"success": True, "message": f"Product {product_id} deleted successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
