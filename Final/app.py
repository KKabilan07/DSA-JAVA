from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

app.config['MONGO_URI'] = 'mongodb://localhost:27017/fitnesssdb'
mongo = PyMongo(app)
from functools import wraps

def login_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if role == 'admin' and 'admin' not in session:
                flash("Admin login required", "danger")
                return redirect(url_for('admin_login'))
            elif role == 'member' and 'member_id' not in session:
                flash("Member login required", "danger")
                return redirect(url_for('member_login'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')

# Admin routes
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        admin = mongo.db.admins.find_one({'email': email, 'password': password})
        if admin:
            session['admin'] = email
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/admin_emergency_contact')
def admin_emergency_contact():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    contacts = list(mongo.db.emergency_contacts.find())
    return render_template('admin_emergency_contact.html', contacts=contacts)

# Member routes
@app.route('/member_login', methods=['GET', 'POST'])
def member_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        member = mongo.db.members.find_one({'email': email, 'password': password})
        if member:
            session['member_id'] = str(member['_id'])
            session['member_name'] = member.get('name', 'Member')
            return redirect(url_for('member_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('member_login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name, email, phone, password = [request.form.get(k) for k in ['name', 'email', 'phone', 'password']]
        if mongo.db.members.find_one({'email': email}):
            flash("Email already registered", "danger")
        else:
            mongo.db.members.insert_one({'name': name, 'email': email, 'phone': phone, 'password': password})
            flash("Signup successful!", "success")
            return redirect(url_for('member_login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for('index'))

@app.route('/member_dashboard')
def member_dashboard():
    if 'member_id' not in session:
        return redirect(url_for('member_login'))
    return render_template('member_dashboard.html', member_name=session['member_name'])

@app.route('/member_profile')
def member_profile():
    member = mongo.db.members.find_one({'_id': ObjectId(session['member_id'])})
    return render_template('member_profile.html', member=member)

@app.route('/member_workout')
def member_workout():
    workouts = mongo.db.workouts.find_one({'member_id': session['member_id']})
    return render_template('member_workout.html', workout=workouts)

@app.route('/member_diet')
def member_diet():
    diet = mongo.db.diets.find_one({'member_id': session['member_id']})
    return render_template('member_diet.html', diet=diet)

@app.route('/member_payment')
def member_payment():
    return render_template('member_payment.html')

@app.route('/member_payment_history')
def member_payment_history():
    payments = mongo.db.payments.find({'member_id': session['member_id']})
    return render_template('member_payment_history.html', payments=payments)

@app.route('/member_emergency_contact')
def member_emergency_contact():
    contact = mongo.db.emergency_contacts.find_one({'member_id': session['member_id']})
    return render_template('member_emergency_contact.html', contact=contact)

@app.route('/member_feedback', methods=['GET', 'POST'])
def member_feedback():
    if request.method == 'POST':
        feedback = request.form.get('feedback')
        mongo.db.feedback.insert_one({
            'member_id': session['member_id'],
            'feedback': feedback,
            'timestamp': datetime.now()
        })
        flash("Feedback submitted", "success")
        return redirect(url_for('member_dashboard'))
    return render_template('member_feedback.html')

# Admin functionalities
@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        data = {k: request.form[k] for k in ['name', 'email', 'phone', 'password']}
        mongo.db.members.insert_one(data)
        flash("Member added", "success")
        return redirect(url_for('admin_dashboard'))
    return render_template('add_member.html')

@app.route('/update_member', methods=['GET', 'POST'])
def update_member():
    members = list(mongo.db.members.find())
    if request.method == 'POST':
        member_id = request.form.get('member_id')
        updated = {
            'name': request.form['name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'password': request.form['password']
        }
        mongo.db.members.update_one({'_id': ObjectId(member_id)}, {'$set': updated})
        flash("Member updated", "success")
        return redirect(url_for('admin_dashboard'))
    return render_template('update_member.html', members=members)


from bson.objectid import ObjectId

@app.route('/delete_member', methods=['GET', 'POST'])
@login_required(role='admin')
def delete_member():
    members = list(mongo.db.members.find())
    if request.method == 'POST':
        member_id = request.form.get('member_id')
        if member_id:
            mongo.db.members.delete_one({'_id': ObjectId(member_id)})
            flash('Member deleted successfully!')
            return redirect(url_for('delete_member'))
        else:
            flash('Please select a member to delete.')
    return render_template('delete_member.html', members=members)


from bson.objectid import ObjectId

@app.route('/search_member', methods=['GET', 'POST'])
@login_required(role='admin')
def search_member():
    members = []
    keyword = request.args.get('query', '').strip()

    if keyword:
        query = {
            '$or': [
                {'name': {'$regex': keyword, '$options': 'i'}},
                {'email': {'$regex': keyword, '$options': 'i'}}
            ]
        }

        # Try matching ObjectId if keyword is 24-hex chars
        if len(keyword) == 24:
            try:
                query['$or'].append({'_id': ObjectId(keyword)})
            except Exception:
                pass  # Not a valid ObjectId

        members = list(mongo.db.members.find(query))

    return render_template('search_member.html', members=members, query=keyword)


@app.route('/assign_workout', methods=['GET', 'POST'])
@login_required(role='admin')
def assign_workout():
    members = list(mongo.db.members.find())
    if request.method == 'POST':
        member_email = request.form['member_email']
        schedule = request.form.get('schedule', {})  # or parse as needed
        notes = request.form.get('notes', '')

        mongo.db.workouts.update_one(
            {'member_email': member_email},
            {'$set': {'schedule': schedule, 'notes': notes}},
            upsert=True
        )
        flash("Workout plan assigned successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('assign_workout.html', members=members)


@app.route('/assign_diet', methods=['GET', 'POST'])
@login_required(role='admin')  # ✅ Add this
def assign_diet():
    members = list(mongo.db.members.find())
    if request.method == 'POST':
        member_email = request.form['member_email']
        plan = request.form.get('plan', '')

        mongo.db.diets.update_one(
            {'member_email': member_email},
            {'$set': {'plan': plan}},
            upsert=True
        )
        flash("Diet plan assigned successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('assign_diet.html', members=members)

@app.route('/add_payment', methods=['GET', 'POST'])
def add_payment():
    if 'admin' not in session:
        flash("Unauthorized access. Please login as admin.", "danger")
        return redirect(url_for('admin_login'))

    members = list(mongo.db.members.find())

    if request.method == 'POST':
        mongo.db.payments.insert_one({
            'member_id': request.form['member_id'],
            'amount': float(request.form['amount']),
            'payment_date': request.form['payment_date'],
            'membership_type': request.form['membership_type']
        })
        flash("Payment recorded", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('add_payment.html', members=members)



@app.route('/manage_equipment', methods=['GET', 'POST'])
def manage_equipment():
    if 'admin' not in session:
        flash("Admin login required", "danger")
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        equipment = {
            'name': request.form['name'],
            'quantity': int(request.form['quantity']),
            'condition': request.form['condition'],
            'added_date': datetime.now()
        }
        mongo.db.equipment.insert_one(equipment)
        flash("Equipment added successfully", "success")
        return redirect(url_for('manage_equipment'))

    equipment_list = list(mongo.db.equipment.find())
    return render_template('manage_equipment.html', equipment=equipment_list)


from flask import render_template, request, redirect, url_for, flash, session
from bson.objectid import ObjectId

@app.route('/schedule_equipment', methods=['GET', 'POST'])
def schedule_equipment():
    if 'admin' not in session:
        flash("Unauthorized access. Please login as admin.", "danger")
        return redirect(url_for('admin_login'))

    equipment_list = list(mongo.db.equipment.find())

    if request.method == 'POST':
        equipment_id = request.form.get('equipment_id')
        time_slot = request.form.get('time_slot')

        if equipment_id and time_slot:
            mongo.db.equipment_schedule.insert_one({
                'equipment_id': equipment_id,
                'time_slot': time_slot
            })
            flash("Equipment scheduled successfully!", "success")
            return redirect(url_for('manage_equipment'))
        else:
            flash("Please select equipment and time slot", "danger")

    return render_template('schedule_equipment.html', equipment_list=equipment_list)


@app.route('/view_feedback')
def view_feedback():
    feedbacks = list(mongo.db.feedback.find())
    return render_template('view_feedback.html', feedbacks=feedbacks)

@app.route('/view_attendance')
def view_attendance():
    records = list(mongo.db.attendance.find())
    return render_template('view_attendance.html', records=records)

@app.route('/attendance_report')
def attendance_report():
    report = list(mongo.db.attendance.find())
    return render_template('attendance_report.html', report=report)
@app.errorhandler(KeyError)
def handle_key_error(e):
    flash("Session expired or invalid access. Please log in again.", "danger")
    return redirect(url_for('member_login'))
app.route('/check-in', methods=['GET', 'POST'])
def check_in():
    if 'member_id' not in session:
        flash("Please log in to check in.")
        return redirect(url_for('login'))

    member_id = session['member_id']

    if request.method == 'POST':
        # Record the check-in time
        checkin_data = {
            'member_id': member_id,
            'timestamp': datetime.now()
        }
        mongo.db.checkins.insert_one(checkin_data)
        flash("Check-in successful!")
        return redirect(url_for('member_dashboard'))

    return render_template('check_in.html')
@app.route('/check-in', methods=['GET', 'POST'])
def check_in():
    # Your logic here
    return render_template('check_in.html')
@app.route('/check-out', methods=['GET', 'POST'], endpoint='check_out')
def member_check_out():
    if 'member_id' not in session:
        flash("Please log in to check out.")
        return redirect(url_for('member_login'))

    member_id = session['member_id']

    if request.method == 'POST':
        checkout_data = {
            'member_id': member_id,
            'timestamp': datetime.now()
        }
        mongo.db.checkouts.insert_one(checkout_data)
        flash("Checked out successfully!")
        return redirect(url_for('member_dashboard'))

    return render_template('check_out.html')
@app.route('/admin_checkin_records')
def admin_checkin_records():
    if 'admin' not in session:
        flash("Please log in as admin to view check-ins.", "danger")
        return redirect(url_for('admin_login'))

    checkins = list(mongo.db.checkins.find())
    members = {str(m['_id']): m['name'] for m in mongo.db.members.find()}
    return render_template('admin_checkin_records.html', checkins=checkins, members=members)

@app.route('/admin_checkout_records')
def admin_checkout_records():
    if 'admin' not in session:
        flash("Please log in as admin to view check-outs.", "danger")
        return redirect(url_for('admin_login'))

    checkouts = list(mongo.db.checkouts.find())
    members = {str(m['_id']): m['name'] for m in mongo.db.members.find()}
    return render_template('admin_checkout_records.html', checkouts=checkouts, members=members)


if __name__ == '__main__':
    app.run(debug=True)