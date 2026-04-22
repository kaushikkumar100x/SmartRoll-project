import sqlite3
from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = 'smartroll_secret_123' # Required for flashing messages
DB_NAME = 'database.db'

# 1. Database Connection Function
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# 2. Initialize Database (Create table if not exists)
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

# Initialize the DB when the script starts
init_db()

@app.route('/')
def home():
    return redirect(url_for('signup_page'))

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    # Extract data from form
    name = request.form.get('fullname', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', '').strip()

    # 3. Basic Validation
    # if not all([name, email, password, role]):
    #     return "Missing information. Please fill all fields. ❌", "warning"
    # 3. Basic Validation
    if not all([name, email, password, role]):
          flash("Please fill all fields ❌", "warning")
          return redirect(url_for('signup_page'))
    # 4. Password Hashing
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    try:
        conn = get_db_connection()
        
        # 5. Check if User Already Exists
        user_exists = conn.execute('SELECT email FROM users WHERE email = ?', (email,)).fetchone()
        
        # if user_exists:
        #     conn.close()
        #     return "Email already registered. Please try logging in. ❌", 409
        try:
           conn.execute('INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
                 (name, email, hashed_password, role))
           conn.commit()
           conn.close()
        except sqlite3.IntegrityError:
                return "Email already exists ❌"

        # 6. Save User to Database
        conn.execute(
            'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
            (name, email, hashed_password, role)
        )
        conn.commit()
        conn.close()

        # 7. Role-based Redirection
        if role.lower() == "teacher":
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))

    except sqlite3.Error as e:
        return f"Database error: {str(e)}", 500

# Dashboard Routes
@app.route('/teacher_dashboard')
def teacher_dashboard():
    return "<h1>Welcome to the Teacher Dashboard 🎓</h1>"

@app.route('/student_dashboard')
def student_dashboard():
    return "<h1>Welcome to the Student Dashboard 🎓</h1>"

if __name__ == '__main__':
    app.run(debug=True)