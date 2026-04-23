"""Authentication routes: signup, login, logout."""
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from db import query_one, execute
from utils import is_valid_email, is_valid_password, generate_jwt


auth_bp = Blueprint("auth", __name__)


# ---- Page routes ---- #
@auth_bp.route("/login", methods=["GET"])
def login_page():
    if "user" in session:
        return redirect(url_for("index"))
    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET"])
def signup_page():
    return render_template("signup.html")


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    if request.method == "POST":
        return jsonify({"message": "Logged out"}), 200
    return redirect(url_for("auth.login_page"))


# ---- API routes ---- #
@auth_bp.route("/api/signup", methods=["POST"])
def api_signup():
    """Register a new user with hashed password."""
    data = request.get_json(silent=True) or request.form
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "").strip().lower()

    # Input validation
    if not name or len(name) < 2:
        return jsonify({"error": "Name must be at least 2 characters"}), 400
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email address"}), 400
    if not is_valid_password(password):
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if role not in ("teacher", "student"):
        return jsonify({"error": "Role must be 'teacher' or 'student'"}), 400

    # Prevent duplicate email
    if query_one("SELECT id FROM users WHERE email = ?", (email,)):
        return jsonify({"error": "Email is already registered"}), 409

    hashed = generate_password_hash(password)
    user_id = execute(
        "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        (name, email, hashed, role),
    )

    return jsonify({"message": "Account created successfully", "user_id": user_id}), 201


@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    """Authenticate a user and create a session."""
    data = request.get_json(silent=True) or request.form
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not is_valid_email(email) or not password:
        return jsonify({"error": "Email and password required"}), 400

    row = query_one(
        "SELECT id, name, email, password, role FROM users WHERE email = ?",
        (email,),
    )
    if not row or not check_password_hash(row["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    user = {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"]}
    session.clear()
    session["user"] = user
    session.permanent = True

    token = generate_jwt(user)
    return jsonify({"message": "Login successful", "user": user, "token": token, "redirect": "/"}), 200


@auth_bp.route("/api/me", methods=["GET"])
def api_me():
    if "user" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({"user": session["user"]}), 200
