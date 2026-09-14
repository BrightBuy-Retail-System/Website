"""
Central Application Entrypoint (Phase 1 & Phase 2)
Registers all 5 member Blueprints, configures connection pool, and serves the dashboard layout.
"""

import os
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv

# Import shared database connection utilities
from db import init_connection_pool, check_db_health

# Import the 5 modular Flask Blueprints (Phase 2 Modular Architecture)
from routes.catalog import catalog_bp
from routes.auth_cart import auth_cart_bp
from routes.orders import orders_bp
from routes.logistics import logistics_bp
from routes.analytics import analytics_bp

# Load environment configuration
load_dotenv()

def create_app():
    """Application factory for Flask app."""
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "texas-database-system-secret-key-2026")

    # Initialize connection pool on startup
    try:
        init_connection_pool()
    except Exception as e:
        print(f"[Warning] Connection pool initialization deferred: {e}")

    # Register the 5 Flask Blueprints with isolated API url_prefixes (Phase 2)
    app.register_blueprint(catalog_bp, url_prefix='/api/catalog')
    app.register_blueprint(auth_cart_bp, url_prefix='/api/auth-cart')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(logistics_bp, url_prefix='/api/logistics')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

    # Frontend Page Routes
    @app.route("/", methods=["GET"])
    def index():
        """Main overview dashboard page."""
        return render_template("dashboard.html")

    @app.route("/catalog", methods=["GET"])
    def catalog_page():
        return render_template("catalog.html")

    @app.route("/cart", methods=["GET"])
    def cart_page():
        return render_template("auth_cart.html")

    @app.route("/orders", methods=["GET"])
    def orders_page():
        return render_template("orders.html")

    @app.route("/logistics", methods=["GET"])
    def logistics_page():
        return render_template("logistics.html")

    @app.route("/analytics", methods=["GET"])
    def analytics_page():
        return render_template("analytics.html")

    # System Health API
    @app.route("/api/health", methods=["GET"])
    def health_check():
        db_health = check_db_health()
        return jsonify({
            "status": "online",
            "database": db_health,
            "blueprints": [
                "catalog_bp (/api/catalog)",
                "auth_cart_bp (/api/auth-cart)",
                "orders_bp (/api/orders)",
                "logistics_bp (/api/logistics)",
                "analytics_bp (/api/analytics)"
            ]
        }), (200 if db_health.get("status") == "healthy" else 500)

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({"success": False, "error": "Endpoint or resource not found"}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({"success": False, "error": "Internal server error"}), 500

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
    print(f"\n=======================================================")
    print(f" LoneStar Texas Commerce System (Flask + MySQL)")
    print(f" Running at: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
