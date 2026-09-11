import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from database import get_db_cursor, init_db
import security

load_dotenv()

app = Flask(__name__)

# Enable CORS for frontend clients (React/Vite)
CORS(
    app,
    resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"]}},
    supports_credentials=True
)

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "status": "success",
        "message": "Bright Buy Retail Flask API is running",
        "endpoints": {
            "register": "POST /api/register",
            "login": "POST /api/login",
            "me": "GET /api/me"
        }
    }), 200

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"detail": "Invalid JSON body provided."}), 400

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    phonenum = (data.get("phonenum") or "").strip()

    # Basic validations
    if not email or not re.match(EMAIL_REGEX, email):
        return jsonify({"detail": "A valid email address is required."}), 400

    if not password or len(password) < 6:
        return jsonify({"detail": "Password must be at least 6 characters long."}), 400

    try:
        with get_db_cursor() as cursor:
            # 1. Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            existing_user = cursor.fetchone()
            if existing_user:
                return jsonify({"detail": "An account with this email already exists."}), 400

            # 2. Hash password
            hashed_pwd = security.hash_password(password)

            # 3. Insert user record
            cursor.execute(
                "INSERT INTO users (email, hashed_password, phonenum) VALUES (%s, %s, %s)",
                (email, hashed_pwd, phonenum if phonenum else None)
            )
            user_id = cursor.lastrowid

            # 4. Generate access token
            access_token = security.create_access_token(data={"sub": email, "id": user_id})

        return jsonify({
            "message": "User registered successfully!",
            "user_id": user_id,
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": email,
                "phonenum": phonenum
            }
        }), 201

    except Exception as e:
        app.logger.error(f"Registration error: {e}")
        return jsonify({"detail": f"Database error occurred: {str(e)}"}), 500


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"detail": "Invalid JSON body provided."}), 400

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"detail": "Email and password are required."}), 400

    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT id, email, hashed_password, phonenum FROM users WHERE email = %s",
                (email,)
            )
            user = cursor.fetchone()

        if not user:
            return jsonify({"detail": "Invalid email or password."}), 401

        # Verify password
        if not security.verify_password(password, user["hashed_password"]):
            return jsonify({"detail": "Invalid email or password."}), 401

        # Generate JWT token
        access_token = security.create_access_token(data={"sub": user["email"], "id": user["id"]})

        return jsonify({
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "phonenum": user.get("phonenum")
            }
        }), 200

    except Exception as e:
        app.logger.error(f"Login error: {e}")
        return jsonify({"detail": f"Database error occurred: {str(e)}"}), 500


@app.route("/api/me", methods=["GET"])
def get_current_user():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"detail": "Missing or invalid authorization token."}), 401

    token = auth_header.split(" ")[1]
    payload = security.decode_access_token(token)
    if not payload:
        return jsonify({"detail": "Invalid or expired token."}), 401

    user_email = payload.get("sub")
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT id, email, phonenum, created_at FROM users WHERE email = %s",
                (user_email,)
            )
            user = cursor.fetchone()

        if not user:
            return jsonify({"detail": "User not found."}), 404

        return jsonify({
            "id": user["id"],
            "email": user["email"],
            "phonenum": user.get("phonenum"),
            "created_at": str(user.get("created_at"))
        }), 200

    except Exception as e:
        return jsonify({"detail": f"Database error: {str(e)}"}), 500


if __name__ == "__main__":
    print(" Initializing database tables...")
    init_db()
    port = int(os.getenv("PORT", 8000))
    print(f" Starting Flask server on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
