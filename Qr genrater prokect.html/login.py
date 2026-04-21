from flask import Flask, request, redirect, render_template

app = Flask(__name__)

# Dummy users (demo data)
users = {
    "test@gmail.com": {
        "password": "123456",
        "role": "student"
    },
    "teacher@gmail.com": {
        "password": "123456",
        "role": "teacher"
    }
}

@app.route('/')
def home():
    return render_template('index.html')

# LOGIN PAGE (IMPORTANT: file name has space)
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login form.html')  # 👈 EXACT FILE NAME

# LOGIN SUBMIT
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    # validation
    if email in users:
        user = users[email]

        if user["password"] == password and user["role"] == role:

            if role == "teacher":
                return redirect('/teacher_dashboard')
            else:
                return redirect('/student_dashboard')

    return "Invalid Email, Password or Role ❌"

# DASHBOARDS
@app.route('/teacher_dashboard')
def teacher_dashboard():
    return "Welcome Teacher 🎓"

@app.route('/student_dashboard')
def student_dashboard():
    return "Welcome Student 🎓"

if __name__ == '__main__':
    app.run(debug=True)