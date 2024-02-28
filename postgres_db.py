import psycopg2

from sqlalchemy import Float, column, create_engine, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from sqlalchemy.orm import relationship, backref
# from sqlalchemy.engine.result import ResultProxy

import json
from dotenv import load_dotenv
import os
load_dotenv() 

JSON_MIME_TYPE = 'application/json'

Base = declarative_base()



conn = psycopg2.connect(database=os.getenv('DB_NAME'),
                        user=os.getenv('DB_USER'),
                        password=os.getenv('DB_PASS'),
                        host=os.getenv('DB_HOST'),
                        port=os.getenv('DB_PORT'))

print("Database connected successfully")



cur = conn.cursor()  



def get_session():
    engine = create_engine('postgresql+psycopg2://postgres:test@0.0.0.0:5432/vaccines')
    Base.metadata.bind = engine
    
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session



class Users(Base):
    __tablename__ = 'users'

    userid = Column(Integer, primary_key=True)
    email = Column(String(255))
    password = Column(String(255))
    name = Column(String(255))
    address = Column(String(255))
    phone_number = Column(Integer)

    slots_booked = relationship("SlotsBooked", backref="users")


class CentersInfo(Base):
    __tablename__ = 'centersinfo'

    centerid = Column(Integer, primary_key=True)
    state = Column(String(255))
    city = Column(String(255))
    address = Column(String(255))
    location = Column(String(255))
    openingtime = Column(String(255))
    closingtime = Column(String(255))
    poc = Column(String(255))

    available_slots = relationship("AvailableSlots", backref="center")


class AvailableSlots(Base):
    __tablename__ = 'availableslots'

    slotid = Column(Integer, primary_key=True)
    centerid = Column(Integer, ForeignKey('centersinfo.centerid'))
    available_slots = Column(Integer)
    date = Column(Date)


class SlotsBooked(Base):
    __tablename__ = 'slotsbooked'

    bookingid = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('users.userid'))
    centerid = Column(Integer, ForeignKey('centersinfo.centerid'))
    date = Column(Date)


class Admin(Base):
    __tablename__ = 'admins'

    adminid = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)


conn.commit()