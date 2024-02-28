from flask import Flask, redirect, request, render_template, flash, url_for, session
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy


load_dotenv()

# db = get_session()

app = Flask(__name__)
app.config['SECRET_KEY'] = "COVID_KEY"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vaccine.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
from os import path


class Users(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    phone_number = db.Column(db.String(15))



class CentersInfo(db.Model):
    centerId = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(255))
    city = db.Column(db.String(255))
    address = db.Column(db.String(255))
    location = db.Column(db.String(255))
    openingTime = db.Column(db.Time)
    closingTime = db.Column(db.Time)
    poc = db.Column(db.String(255))



class SlotsBooked(db.Model):
    bookingId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'))
    centerId = db.Column(db.Integer, db.ForeignKey('centers_info.centerId'))
    date = db.Column(db.Date)



class AvailableSlots(db.Model):
    slotId = db.Column(db.Integer, primary_key=True)
    centerId = db.Column(db.Integer, db.ForeignKey('centers_info.centerId'))
    available_slots = db.Column(db.Integer)
    date = db.Column(db.Date)


class Admin(db.Model):
    # admin = db.Column(db.Boolean, nullable=False)
    userId = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)



current_date = datetime.now()
formatted_date = current_date.strftime("%d/%m/%Y")
formatted_date = datetime.strptime(formatted_date, '%d/%m/%Y').date()

print("Current date in dd/mm/yyyy format:", formatted_date)



@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        
        user = Users.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                session['email'] = email
                session['userId'] = user.userId
                flash("Logged in successfully")
               
                return redirect(url_for('list_vaccine_centers'))
            else:
                flash("Invalid password")
        else:
            flash("Invalid Credentials. Register.")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        address = request.form['address']
        phone_number = request.form['phone']
        
       
        
        existing_user = Users.query.filter_by(email=email).first()

        if existing_user:
            flash("User with this email already exists. Try logging in.")

            return render_template('login.html')
        
        else:
            hashed_password = generate_password_hash(password)
            new_user = Users(email=email, password=hashed_password, name=name, address=address, phone_number=phone_number)
            db.session.add(new_user)

            db.session.commit()
            

            session['email'] = email
            session['userId'] = new_user.userId

            flash("User successfully created")
            return redirect(url_for('list_vaccine_centers'))
            
    return render_template('register.html')



@app.route('/adminlogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

       
        admin = Admin.query.filter_by(email = email).first()

        if admin:
            if admin.password == password:
                session['email'] = email
                session['userId'] = admin.userId
                session['admin'] = True

                
                
                flash("Logged in successfully")
                return redirect(url_for('list_vaccine_centers'))
            else:
                
                flash("Invalid password")
        else:
            
            flash("Invalid Credentials.")

    return render_template('admin_login.html')

@app.route('/list/center', methods=['GET'])
def list_vaccine_centers():
    if not session.get('userId'):
        return redirect(url_for('login'))
    

    centers = CentersInfo.query.all()

    available_slots_data = AvailableSlots.query.filter_by(date = current_date).all()
    available_slots_dict = {slot.centerid: slot.available_slots for slot in available_slots_data}

    

    freeze = False
    current_time = datetime.now().time()
    if current_time >= datetime.strptime("14:00", "%H:%M").time():
        freeze = True

    return render_template('list_centers.html', centers=centers, available_slots=available_slots_dict, admin=session.get('admin'), freeze=freeze, date=formatted_date, day="Today")


@app.route('/add/center', methods=['GET','POST'])
def add_vaccine_center():
    if not session.get('admin'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        state = request.form.get('state')
        city = request.form.get('city')
        address = request.form['address']
        location = request.form['location']
        opening_time = request.form['opening_time']
        closing_time = request.form['closing_time']
        poc = request.form['poc']


        center = CentersInfo(state=state, city=city, address=address, location=location,
                             openingTime=opening_time, closingTime=closing_time, poc=poc)
        
        db.session.add(center)
        db.session.commit()


        center_id = center.centerid

        avail_slots = 10
        available_slots = AvailableSlots(centerid=center_id, available_slots=avail_slots, date=current_date)
        db.session.add(available_slots)
        db.session.commit()

        

        flash("Center added successfully")
        return redirect(url_for('list_vaccine_centers'))

    return render_template('add_center.html')



@app.route('/remove/center', methods=['POST'])
def remove_vaccine_center():
    if not session.get('admin'):
        return redirect(url_for('login'))
    vid = request.form.get('vid')
    
    
    center = CentersInfo.query.filter_by(centerid = vid).first()
    if center:
        db.session.delete(center)
        db.session.commit()
        
        flash("Center removed successfully")
    else:
        
        flash("Center not found")
    
    return redirect(url_for('list_vaccine_centers'))



@app.route('/apply', methods=['POST'])
def apply():
    if not session.get('userId'):
        return redirect(url_for('login'))
    
    slots_info = SlotsBooked.query.filter_by(userid = session.get('userId'), date = current_date).first()
    if slots_info:
        
        flash("You have already booked a slot.")
        return redirect(url_for('list_vaccine_centers'))
    
    vid = request.form.get('vid')
    
    available_slots = AvailableSlots.query.filter_by(centerid = vid, date = current_date).first()
    if available_slots:
        available_slots.available_slots -= 1
        db.session.add(SlotsBooked(userid=session.get('userId'), centerid=vid, date=current_date))
        db.session.commit()
        
        flash("Slot booked successfully. You will receive a confirmation email.")
    else:
        
        flash("No available slots at this center.")
    
    return redirect(url_for('list_vaccine_centers'))




@app.route('/book/tomorrow', methods=['GET', 'POST'])
def apply_tomorrow():
    if not session.get('userId'):
        return redirect(url_for('login'))
    
    next_day = datetime.now() + timedelta(days=1)
    next_day_date = next_day.strftime("%d/%m/%Y")
    next_day_date = datetime.strptime(next_day_date, '%d/%m/%Y').date()
    
    if request.method == 'POST':
        vid = request.form.get('vid')
        center = CentersInfo.query.filter_by(centerid = vid).first()
        
        if center:
            slots_info = SlotsBooked.query.filter_by(userid = session.get('userId'), date = next_day_date).first()
            if slots_info:
                
                flash("You have already booked a slot for tomorrow.")
                return redirect(url_for('list_vaccine_centers'))
            
            available_slots = AvailableSlots.query.filter_by(centerid = vid, date = next_day_date).first()
            if available_slots:
                available_slots.available_slots -= 1
                db.session.add(SlotsBooked(userid=session.get('userId'), centerid=vid, date=next_day_date))
                db.session.commit()
                
                flash("Slot booked successfully for tomorrow. You will receive a confirmation email.")
            else:
                
                flash("No available slots at this center for tomorrow.")
        else:
            
            flash("Invalid center ID")
    
        return redirect(url_for('list_vaccine_centers'))




    
    centers = CentersInfo.query.all()
    
    next_day = datetime.now() + timedelta(days=1)
    next_day_date = next_day.strftime("%d/%m/%Y")

    available_slots_data = AvailableSlots.query.filter_by(date = next_day_date).all()
    available_slots_dict = {slot.centerid: slot.available_slots for slot in available_slots_data}
    

    return render_template('list_centers.html', centers=centers, available_slots=available_slots_dict, admin=session.get('admin'), date=next_day_date, day="Tomorrow")

   

@app.route('/logout')
def logout():
    session.clear()
    flash("Signed out",category='success')
    return redirect(url_for('login'))




if __name__ == '__main__':
    with app.app_context():
        if not path.exists('vaccine.db'):
            db.create_all()
        admin1 = Admin(email='admin1@gmail.com', password='admin')
        db.session.add(admin1)
        db.session.commit()
        app.run(debug=True, host='0.0.0.0', port=5006)
