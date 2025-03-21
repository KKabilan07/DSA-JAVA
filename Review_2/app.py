from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from config.config import Config
from models.member import Member
from models.workout import Workout
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize MongoDB connection
mongo = PyMongo(app)
db = mongo.db

# --------------------- Authentication Routes ---------------------

# Separate Admin Login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Demo check; replace with proper authentication
        if username == 'admin' and password == 'admin':
            session['user'] = {'username': username, 'role': 'admin'}
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials. Please try again.')
    return render_template('admin_login.html')

# Separate Member Login
@app.route('/member_login', methods=['GET', 'POST'])
def member_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.users.find_one({'username': username})
        if user and user.get('password') == password:
            session['user'] = {'username': username, 'role': 'member'}
            return redirect(url_for('member_dashboard'))
        else:
            flash('Invalid member credentials. Please try again.')
    return render_template('member_login.html')

# Signup Route for new members (default role: member)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for('signup'))
        user = {
            'username': username,
            'email': email,
            'password': password,  # NOTE: Hash passwords in production!
            'role': 'member'
        }
        db.users.insert_one(user)
        flash("Signup successful! Please log in as a member.")
        return redirect(url_for('member_login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for('index'))

# --------------------- Dashboard Routes ---------------------

@app.route('/')
def index():
    return render_template('index.html')

# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    # Admin sees all members, etc.
    members = Member.get_all(db)
    return render_template('admin_dashboard.html', members=members)

# Member Dashboard: displays member-specific data
@app.route('/member_dashboard')
def member_dashboard():
    user = session.get('user', {})
    username = user.get('username')
    # Query only records related to this member
    attendance = list(db.attendance.find({'member_username': username}))
    payments = list(db.payments.find({'member_username': username}))
    feedbacks = list(db.feedback.find({'member_username': username}))
    return render_template('member_dashboard.html', user=user,
                           attendance=attendance, payments=payments, feedbacks=feedbacks)

# --------------------- Member-Specific Operations ---------------------

# Check-In Route for members
@app.route('/add_equipment', methods=['GET', 'POST'])
def add_equipment():
    if request.method == 'POST':
        name = request.form['name']
        equipment_type = request.form['type']
        available = request.form.get('available', 'false').lower() == 'true'
        maintenance_date = request.form['maintenance_date']
        # Insert into the equipment collection
        db.equipment.insert_one({
            'name': name,
            'type': equipment_type,
            'available': available,
            'maintenance_date': maintenance_date
        })
        flash("Equipment added successfully!")
        return redirect(url_for('view_equipment'))
    return render_template('add_equipment.html')

@app.route('/member_check_in', methods=['POST'])
def member_check_in():
    user = session.get('user', {})
    username = user.get('username')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Create a new attendance record for check-in
    db.attendance.insert_one({
        'member_username': username,
        'check_in': now,
        'check_out': '',
        'date': datetime.now().strftime('%Y-%m-%d')
    })
    flash("Check-in recorded successfully!")
    return redirect(url_for('member_dashboard'))

# Check-Out Route for members
@app.route('/member_check_out', methods=['POST'])
def member_check_out():
    user = session.get('user', {})
    username = user.get('username')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Update the latest attendance record for this member that has no check-out time
    db.attendance.update_one(
        {'member_username': username, 'check_out': ''},
        {'$set': {'check_out': now}}
    )
    flash("Check-out recorded successfully!")
    return redirect(url_for('member_dashboard'))

# Member Payment History (only for the logged-in member)
@app.route('/member_payment_history')
def member_payment_history():
    user = session.get('user', {})
    username = user.get('username')
    payments = list(db.payments.find({'member_username': username}))
    return render_template('member_payment_history.html', payments=payments)
@app.route('/add_payment', methods=['GET', 'POST'])
def add_payment():
    if request.method == 'POST':
        member_id = request.form['member_id']
        amount = request.form['amount']
        date = request.form['date']
        status = request.form['status']
        db.payments.insert_one({
            'member_id': member_id,
            'amount': amount,
            'date': date,
            'status': status
        })
        flash("Payment added successfully!")
        return redirect(url_for('payment_history'))
    return render_template('add_payment.html')


# Member Feedback (GET to show form, POST to submit feedback)
@app.route('/member_feedback', methods=['GET', 'POST'])
def member_feedback():
    user = session.get('user', {})
    username = user.get('username')
    if request.method == 'POST':
        message = request.form['message']
        db.feedback.insert_one({
            'member_username': username,
            'message': message,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        flash("Feedback submitted successfully!")
        return redirect(url_for('member_dashboard'))
    return render_template('member_feedback.html')

# User Profile (for the logged-in member)
@app.route('/user_profile')
def user_profile():
    user = session.get('user', {})
    # Optionally, query additional user details from db.users if needed
    return render_template('user_profile.html', user=user)

# --------------------- Admin-Specific Operations ---------------------

# Member CRUD: Already have add_member in admin context (see below)

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        # Retrieve data from the form
        name = request.form['name']
        age = request.form['age']
        membership_type = request.form['membership_type']
        contact = request.form['contact']
        
        # Create a new Member instance and save to database
        new_member = Member(name, age, membership_type, contact)
        new_member.save(db)
        flash("Member added successfully!")
        return redirect(url_for('admin_dashboard'))
    
    # If it's a GET request, render the add member form
    return render_template('add_member.html')


@app.route('/view_members')
def view_members():
    members = Member.get_all(db)
    return render_template('view_members.html', members=members)

# Define routes for update_member and delete_member as needed
from models.member import Member  # Already imported above

@app.route('/delete_member', methods=['POST'])
def delete_member():
    member_id = request.form['member_id']
    Member.delete_member(db, member_id)
    flash("Member deleted successfully!")
    return redirect(url_for('view_members'))

@app.route('/update_member/<member_id>', methods=['GET', 'POST'])
def update_member(member_id):
    if request.method == 'POST':
        updated_data = {
            'name': request.form['name'],
            'age': request.form['age'],
            'email': request.form['email'],
            'membership_type': request.form['membership_type'],
            'contact': request.form['contact']
        }
        Member.update_member(db, member_id, updated_data)
        flash("Member updated successfully!")
        return redirect(url_for('view_members'))
    member = db.members.find_one({'_id': ObjectId(member_id)})
    return render_template('update_member.html', member=member)
from bson.objectid import ObjectId

@app.route('/update_profile/<user_id>', methods=['GET', 'POST'])
def update_profile(user_id):
    if request.method == 'POST':
        updated_data = {
            'username': request.form['username'],
            'email': request.form['email']
            # Add other fields as needed
        }
        db.users.update_one({'_id': ObjectId(user_id)}, {'$set': updated_data})
        flash('Profile updated successfully!')
        return redirect(url_for('user_profile'))
    
    user = db.users.find_one({'_id': ObjectId(user_id)})
    return render_template('update_profile.html', user=user)


# --------------------- Other Routes (Equipment, Attendance, Payments, Feedback) ---------------------

@app.route('/view_equipment')
def view_equipment():
    equipments = list(db.equipment.find())
    return render_template('view_equipments.html', equipments=equipments)

@app.route('/attendance_report')
def attendance_report():
    # This can be an admin view of all attendance records
    attendance = list(db.attendance.find())
    return render_template('attendance_report.html', attendance=attendance)

@app.route('/payment_history')
def payment_history():
    # Admin view of all payments
    payments = list(db.payments.find())
    return render_template('payment_history.html', payments=payments)

@app.route('/view_feedback')
def view_feedback():
    feedbacks = list(db.feedback.find())
    return render_template('view_feedback.html', feedbacks=feedbacks)

# --------------------- Main ---------------------
if __name__ == '__main__':
    app.run(debug=True)
