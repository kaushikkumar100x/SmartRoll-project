"""SmartRoll - Smart Attendance System
Flask backend with SQLite, role-based auth, dynamic QR attendance,
notes upload, assignments, and statistics.
"""
import os
from flask import Flask, render_template, redirect, url_for, session, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from db import init_db
from routes.auth import auth_bp
from routes.teacher import teacher_bp
from routes.student import student_bp


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize database (creates tables if missing)
    init_db(app.config["DATABASE"])

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)

    # ---- Page routes ---- #
    @app.route("/")
    def index():
        if "user" not in session:
            return redirect(url_for("auth.login_page"))
        role = session["user"]["role"]
        if role == "teacher":
            return redirect(url_for("teacher_dashboard"))
        return redirect(url_for("student_dashboard"))

    @app.route("/teacher")
    def teacher_dashboard():
        if "user" not in session or session["user"]["role"] != "teacher":
            return redirect(url_for("auth.login_page"))
        return render_template("teacher.html", user=session["user"])

    @app.route("/student")
    def student_dashboard():
        if "user" not in session or session["user"]["role"] != "student":
            return redirect(url_for("auth.login_page"))
        return render_template("student.html", user=session["user"])

    # Serve uploaded notes
    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        if "user" not in session:
            return redirect(url_for("auth.login_page"))
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # Health check
    @app.route("/healthz")
    def healthz():
        return {"status": "ok"}, 200

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
