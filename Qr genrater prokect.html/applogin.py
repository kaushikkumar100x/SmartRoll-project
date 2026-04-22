import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'smartroll_secure_key_123' # Change this for production
DB_NAME = 'database.db'

# 1. Database Connection Function
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# 2. Login Required Decorator (Protecting Routes)
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_email' not in session:
                flash("Please log in first.", "danger")
                return redirect(url_for('login_page'))
            
            if role and session.get('role') != role:
                flash("Unauthorized access.", "danger")
                return redirect(url_for('home'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def home():
    return render_template('login form.html')

@app.route('/login', methods=['GET'])
def login_page():
    # If already logged in, redirect to respective dashboard
    if 'user_email' in session:
        return redirect(url_for(f"{session['role']}_dashboard"))
    return render_template('login form.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', '').strip().lower()


    # Basic Validation
    if not email or not password or not role:
        return "Please fill all fields ❌", "warning"

    try:
        conn = get_db_connection()
        # Fetch user by email AND role
        user = conn.execute('SELECT * FROM users WHERE email = ? AND role = ?', 
                            (email, role)).fetchone()
        conn.close()

        # 3. Secure Password Verification
        if user and check_password_hash(user['password'], password):
            if user['role'] != role:
                flash("Role mismatch. Please select the correct role.", "danger")
                return redirect(url_for('login_page'))
            # Create Session
            session.clear() # Clear any old session data
            session['user_email'] = user['email']
            session['user_name'] = user['name']
            session['role'] = user['role']
            session.permanent = True # Optional: Make session permanent (lasts until browser close)
            
            # Role-based Redirection
            if role == "teacher":
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        
        return "Invalid Email, Password, or Role ❌", "danger"

    except sqlite3.Error as e:
        return f"Database error: {str(e)}", 500

# 4. Protected Dashboards
@app.route('/teacher_dashboard')
@login_required(role='teacher')
def teacher_dashboard():
    return f"<h1>Welcome Teacher, {session['user_name']} 🎓</h1><a href='/logout'>Logout</a>"

@app.route('/student_dashboard')
@login_required(role='student')
def student_dashboard():
    return f"<h1>Welcome Student, {session['user_name']} 🎓</h1><a href='/logout'>Logout</a>"

# 5. Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True)
