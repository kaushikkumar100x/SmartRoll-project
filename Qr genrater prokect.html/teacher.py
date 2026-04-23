"""Teacher routes: QR generation, notes upload, assignments, students, stats."""
import base64
import io
import os
import time
import uuid

import qrcode
from flask import Blueprint, current_app, jsonify, request, session
from werkzeug.utils import secure_filename

from config import Config
from db import execute, query_all, query_one
from utils import allowed_file, role_required


teacher_bp = Blueprint("teacher", __name__)


@teacher_bp.route("/api/generate_qr", methods=["POST"])
@role_required("teacher")
def generate_qr():
    """Generate a unique, time-limited QR token for an attendance session."""
    data = request.get_json(silent=True) or {}
    subject = (data.get("subject") or "").strip()
    class_name = (data.get("class_name") or data.get("class") or "").strip()

    if not subject or not class_name:
        return jsonify({"error": "Subject and class are required"}), 400

    token = uuid.uuid4().hex
    now = time.time()
    expires_at = now + current_app.config["QR_EXPIRY_SECONDS"]
    teacher_email = session["user"]["email"]

    execute(
        """INSERT INTO qr_sessions (token, subject, class_name, teacher_email, created_at, expires_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (token, subject, class_name, teacher_email, now, expires_at),
    )

    # Generate QR image in-memory and return as base64 data URL
    payload = f"SMARTROLL|{token}"
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    return jsonify({
        "token": token,
        "subject": subject,
        "class_name": class_name,
        "qr_image": f"data:image/png;base64,{b64}",
        "expires_in": current_app.config["QR_EXPIRY_SECONDS"],
        "expires_at": expires_at,
    }), 200


@teacher_bp.route("/api/upload_notes", methods=["POST"])
@role_required("teacher")
def upload_notes():
    """Upload a PDF file and persist its metadata."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(f.filename, current_app.config["ALLOWED_EXTENSIONS"]):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    original = secure_filename(f.filename)
    unique_name = f"{uuid.uuid4().hex}_{original}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
    f.save(path)

    note_id = execute(
        "INSERT INTO notes (filename, original_name, uploader_email) VALUES (?, ?, ?)",
        (unique_name, original, session["user"]["email"]),
    )
    return jsonify({
        "message": "Notes uploaded successfully",
        "id": note_id,
        "filename": original,
        "url": f"/uploads/{unique_name}",
    }), 201


@teacher_bp.route("/api/notes", methods=["GET"])
@role_required("teacher")
def list_notes():
    rows = query_all(
        "SELECT id, filename, original_name, uploaded_at FROM notes ORDER BY uploaded_at DESC LIMIT 50"
    )
    return jsonify([
        {"id": r["id"], "filename": r["original_name"], "url": f"/uploads/{r['filename']}",
         "uploaded_at": r["uploaded_at"]}
        for r in rows
    ])


@teacher_bp.route("/api/create_assignment", methods=["POST"])
@role_required("teacher")
def create_assignment():
    """Create a new assignment."""
    data = request.get_json(silent=True) or request.form
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    due_date = (data.get("due_date") or "").strip()

    if not title:
        return jsonify({"error": "Title is required"}), 400

    aid = execute(
        """INSERT INTO assignments (title, description, due_date, teacher_email)
           VALUES (?, ?, ?, ?)""",
        (title, description, due_date, session["user"]["email"]),
    )
    return jsonify({
        "message": "Assignment posted successfully",
        "id": aid,
        "title": title,
        "description": description,
        "due_date": due_date,
    }), 201


@teacher_bp.route("/api/assignments", methods=["GET"])
@role_required("teacher")
def list_assignments():
    rows = query_all(
        "SELECT id, title, description, due_date, created_at FROM assignments ORDER BY created_at DESC"
    )
    return jsonify([dict(r) for r in rows])


@teacher_bp.route("/api/students", methods=["GET"])
@role_required("teacher")
def students():
    """Fetch the list of all registered students."""
    rows = query_all(
        "SELECT id, name, email, created_at FROM users WHERE role = 'student' ORDER BY name"
    )
    return jsonify([dict(r) for r in rows])


@teacher_bp.route("/api/attendance_stats", methods=["GET"])
@role_required("teacher")
def attendance_stats():
    """Return subject-wise attendance statistics."""
    total_students = (query_one("SELECT COUNT(*) AS c FROM users WHERE role = 'student'") or {"c": 0})["c"]

    rows = query_all(
        """SELECT subject,
                  COUNT(*) AS total_marks,
                  COUNT(DISTINCT student_email) AS unique_students
             FROM attendance
            GROUP BY subject
            ORDER BY subject"""
    )

    stats = []
    for r in rows:
        unique = r["unique_students"]
        pct = round((unique / total_students) * 100, 1) if total_students else 0.0
        stats.append({
            "subject": r["subject"],
            "marks": r["total_marks"],
            "unique_students": unique,
            "percentage": pct,
        })

    today = query_one(
        """SELECT COUNT(DISTINCT student_email) AS present
             FROM attendance
            WHERE DATE(timestamp) = DATE('now')"""
    )
    present_today = (today or {"present": 0})["present"]
    return jsonify({
        "total_students": total_students,
        "present_today": present_today,
        "absent_today": max(total_students - present_today, 0),
        "subjects": stats,
    })
