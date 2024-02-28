from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient('mongodb://localhost:27017/')
db = client["covid_vaccination"]
available_slots = db["available-slots-info"]

def insert_fresh_slots():
    
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_date = tomorrow.strftime("%d/%m/%Y")

    centers = db["centers-info"].find()
    for center in centers:
        center_id = center["centerId"]
        available_slots.insert_one({"centerId": center_id, "available_slots": 10, "date": tomorrow_date})


def job():
    print("Inserting fresh slots...")
    insert_fresh_slots()
    print("Fresh slots inserted successfully.")


job() 
