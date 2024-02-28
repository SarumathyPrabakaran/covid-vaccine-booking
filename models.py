from main import db
from os import path


class Users(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    phone_number = db.Column(db.String(15))

class SlotsBooked(db.Model):
    bookingId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'))
    centerId = db.Column(db.Integer, db.ForeignKey('centersInfo.centerId'))
    date = db.Column(db.Date)

class CentersInfo(db.Model):
    centerId = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(255))
    city = db.Column(db.String(255))
    address = db.Column(db.String(255))
    location = db.Column(db.String(255))
    openingTime = db.Column(db.Time)
    closingTime = db.Column(db.Time)
    poc = db.Column(db.String(255))

class AvailableSlots(db.Model):
    slotId = db.Column(db.Integer, primary_key=True)
    centerId = db.Column(db.Integer, db.ForeignKey('centersInfo.centerId'))
    available_slots = db.Column(db.Integer)
    date = db.Column(db.Date)


if not path.exists('vaccine.db'):
    db.create_all()