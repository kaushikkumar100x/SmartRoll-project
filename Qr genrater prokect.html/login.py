import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "smartroll_secret_key_123"
DB_NAME = "database.db"

# ================= DATABASE =================
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ================= HOME =================
@app.route('/')
def home():
    return redirect(url_for('login_page'))

# ================= SIGNUP =================
@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('fullname', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', '').strip().lower()

    if not all([name, email, password, role]):
        flash("Please fill all fields ❌", "warning")
        return redirect(url_for('signup_page'))

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db_connection()

        # Check duplicate email
        user = conn.execute(
            'SELECT * FROM users WHERE email = ?',
            (email,)
        ).fetchone()

        if user:
            conn.close()
            flash("Email already exists ❌", "danger")
            return redirect(url_for('signup_page'))

        conn.execute(
            'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
            (name, email, hashed_password, role)
        )
        conn.commit()
        conn.close()

        flash("Signup successful ✅ Please login", "success")
        return redirect(url_for('login_page'))

    except sqlite3.Error as e:
        return f"Database error: {str(e)}"

# ================= LOGIN =================
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', '').strip().lower()

    if not email or not password or not role:
        flash("Please fill all fields ❌", "warning")
        return redirect(url_for('login_page'))

    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE email = ? AND role = ?',
        (email, role)
    ).fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session.clear()
        session['user_email'] = user['email']
        session['user_name'] = user['name']
        session['role'] = user['role']

        if role == "teacher":
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))

    flash("Invalid Email / Password / Role ❌", "danger")
    return redirect(url_for('login_page'))

# ================= DASHBOARDS =================
@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'user_email' not in session or session['role'] != 'teacher':
        return redirect(url_for('login_page'))
    return render_template('teacher.html', name=session['user_name'])

@app.route('/student_dashboard')
def student_dashboard():
    if 'user_email' not in session or session['role'] != 'student':
        return redirect(url_for('login_page'))
    return render_template('student.html', name=session['user_name'])

# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully 👋", "info")
    return redirect(url_for('login_page'))

# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)