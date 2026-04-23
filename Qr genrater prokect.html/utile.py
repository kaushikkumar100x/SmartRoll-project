"""Reusable helpers: validation, decorators, JWT."""
import re
import time
from functools import wraps
from typing import Callable

import jwt
from flask import current_app, jsonify, session


EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def is_valid_email(email: str) -> bool:
    return bool(email and EMAIL_RE.match(email))


def is_valid_password(pw: str) -> bool:
    """Min 6 chars."""
    return bool(pw and len(pw) >= 6)


def allowed_file(filename: str, allowed: set[str]) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def login_required(fn: Callable):
    """Require an authenticated session."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return fn(*args, **kwargs)
    return wrapper


def role_required(role: str):
    """Require a specific role (teacher or student)."""
    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if "user" not in session:
                return jsonify({"error": "Authentication required"}), 401
            if session["user"].get("role") != role:
                return jsonify({"error": f"{role.capitalize()} access required"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ---- JWT (optional advanced auth) ---- #
def generate_jwt(user: dict) -> str:
    payload = {
        "email": user["email"],
        "role": user["role"],
        "name": user["name"],
        "iat": int(time.time()),
        "exp": int(time.time()) + current_app.config["JWT_EXPIRY_HOURS"] * 3600,
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")


def decode_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
