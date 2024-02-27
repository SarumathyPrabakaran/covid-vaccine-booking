from flask import Flask, redirect, request, render_template, flash, url_for, session
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime

load_dotenv()


app = Flask(__name__)

current_date = datetime.now()
formatted_date = current_date.strftime("%d/%m/%Y")
client = MongoClient(os.environ.get('MONGO_URI'))

db = client["covid_vaccination"]
app.config['SECRET_KEY'] = "COVID_KEY"

users_collection = db["users-info"]


auto_increment_collection = db["auto-increment-id-info"]
admin_collection = db["admin-info"]
centers_collection = db["centers-info"]


current_date = datetime.now()
formatted_date = current_date.strftime("%d/%m/%Y")
print("Current date in dd/mm/yyyy format:", formatted_date)


def get_next_version_id(collection_auto_increment, coll_name, scan=None):
    counter_doc = collection_auto_increment.find_one(
        {"versionId": "versionId", "collName": coll_name}
    )

    if counter_doc is None:
        collection_auto_increment.insert_one(
            {"versionId": "versionId", "collName": coll_name, "seq": 0}
        )
    result = collection_auto_increment.find_one_and_update(
        {"versionId": "versionId", "collName": coll_name},
        {"$inc": {"seq": 1}},
        return_document=True,
    )
    id =  1 if not result else result["seq"]

    if coll_name=="centers-info":
        id = "VC" + str(result)
    return id



@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({"email": email})
        if user:
            hashed_password = user.get('password')
            if check_password_hash(hashed_password, password):
                session['email'] = email
                session['userId'] = user.get('userId')
                
                flash("Logged in successfully")
                return redirect(url_for('profiles'))
            elif user.get('approved')==False:
                flash("Your request is being proccessed.  We'll send you mail once we accept your registration. Thank you.")
            else:
                flash("Invalid password")
                
        else:
            flash("Invalid Credentials")
    return render_template('login.html')




@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        address = request.form['address']
        phone_number = request.form['phone']

        existing_user = users_collection.find_one({"email": email})

        if existing_user:
            flash("User with this email already exists. Try logging in.")
            return render_template('login.html')
        
        else:
            user_id = get_next_version_id(auto_increment_collection, "users-info")
            users_collection.insert_one({"userId": user_id, "email": email, "password": password, "name": name, "address": address,"phone_number" : phone_number })
            session['email'] = email
            session['userId'] = user_id
            flash("User successfully Created")
            
    return render_template('register.html')

@app.route('/adminlogin', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = admin_collection.find_one({"email": email})
        if user:
            hashed_password = user.get('password')
            if check_password_hash(hashed_password, password):
                session['email'] = email
                session['userId'] = user.get('userId')
                session["admin"] = True

                flash("Logged in successfully")
                return redirect(url_for('profiles'))
            elif user.get('approved')==False:
                flash("Your request is being proccessed.  We'll send you mail once we accept your registration. Thank you.")
            else:
                flash("Invalid password")
                
        else:
            flash("Invalid Credentials")
    return render_template('login.html')


@app.route('/list/center', methods=['GET','POST'])
def list_vaccine_centers():
    if not session.get('userId'):
        return redirect(url_for('login'))
    centers = centers_collection.find({})
    return render_template('list_centers.html', centers=centers, admin=session.get('admin'))


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

        center_id = get_next_version_id(auto_increment_collection, "centers-info")
        avail_slots = 10
        centers_collection.insert_one({"centerId":center_id, "state": state, "city": city, "address": address, "location": location, "openingTime": opening_time, "closingTime": closing_time, "poc": poc, "available_slots": avail_slots, "date": formatted_date})

        flash("Center added successfully")
        return redirect(url_for('list_vaccine_centers'))

    return render_template('add_center.html')


@app.route('/remove/center', methods=['POST'])
def remove_vaccine_center():
    if not session.get('admin'):
        return redirect(url_for('login'))
    vid = request.form.get('vid')
    centers_collection.delete_one({"centerId": vid})
    flash("Center removed successfully")
    return redirect(url_for('list_vaccine_centers'))



@app.route('/apply', methods=['POST'])
def apply():
    if not session.get('userId'):
        return redirect(url_for('login'))
    
    vid = request.form.get('vid')
    centers_collection.update_one({"centerId": vid}, {"$inc": {"available_slots": -1}})
    flash("Slot Booked successfully.. You will receive a confirmation mail.")
    return redirect(url_for('list_vaccine_centers'))


@app.route('/logout')
def logout():
    session.clear()
    flash("Signed out",category='success')
    return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5006)
