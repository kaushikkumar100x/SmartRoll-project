from flask import Flask, request, redirect, render_template,jsonify

app = Flask(__name__)
app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    print(data)  # check in terminal

    return jsonify({"message": "Signup Success"}), 200

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/')
def home():
    return render_template('index.html')

# SIGNUP PAGE
@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

# SIGNUP FORM SUBMIT
@app.route('/signup', methods=['POST'])
def signup():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    # basic validation
    if not fullname or not email or not password or not role:
        return "All fields are required ❌"

    # check if user already exists
    if email in users:
        return "User already exists ❌"

    # save user
    users[email] = {
        "fullname": fullname,
        "password": password,
        "role": role
    }

    # role-based redirect
    if role == "teacher":
        return redirect('/teacher_dashboard')
    else:
        return redirect('/student_dashboard')


# LOGIN PAGE (optional for future use)
@app.route('/login')
def login_page():
    return render_template('login form.html')


# DASHBOARDS
@app.route('/teacher_dashboard')
def teacher_dashboard():
    return f"Welcome Teacher 🎓"

@app.route('/student_dashboard')
def student_dashboard():
    return f"Welcome Student 🎓"



if __name__ == '__main__':
    app.run(debug=True)