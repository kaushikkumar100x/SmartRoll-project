"""Student routes: scan QR / mark attendance, view own attendance."""
import time

from flask import Blueprint, jsonify, request, session

from db import execute, query_all, query_one
from utils import role_required


student_bp = Blueprint("student", __name__)


@student_bp.route("/api/mark_attendance", methods=["POST"])
@role_required("student")
def mark_attendance():
    """Validate a QR token and record attendance for the current student."""
    data = request.get_json(silent=True) or request.form
    raw = (data.get("token") or data.get("qr_data") or "").strip()
    if not raw:
        return jsonify({"error": "QR token is required"}), 400

    # Accept either the raw token or the full payload "SMARTROLL|<token>"
    token = raw.split("|", 1)[1] if raw.startswith("SMARTROLL|") else raw

    sess = query_one(
        "SELECT token, subject, class_name, expires_at FROM qr_sessions WHERE token = ?",
        (token,),
    )
    if not sess:
        return jsonify({"error": "Invalid QR code"}), 400
    if time.time() > sess["expires_at"]:
        return jsonify({"error": "QR code has expired"}), 400

    student_email = session["user"]["email"]

    # Duplicate prevention — one scan per session
    existing = query_one(
        "SELECT id FROM attendance WHERE student_email = ? AND token = ?",
        (student_email, token),
    )
    if existing:
        return jsonify({"error": "Attendance already marked for this session"}), 409

    execute(
        """INSERT INTO attendance (student_email, subject, class_name, token)
           VALUES (?, ?, ?, ?)""",
        (student_email, sess["subject"], sess["class_name"], token),
    )

    return jsonify({
        "message": "Attendance marked successfully",
        "subject": sess["subject"],
        "class_name": sess["class_name"],
    }), 201


@student_bp.route("/api/my_attendance", methods=["GET"])
@role_required("student")
def my_attendance():
    """Return current student's attendance history."""
    rows = query_all(
        """SELECT subject, class_name, timestamp
             FROM attendance
            WHERE student_email = ?
            ORDER BY timestamp DESC""",
        (session["user"]["email"],),
    )
    return jsonify([dict(r) for r in rows])
