import sqlite3
from datetime import datetime, timedelta

def create_connection(db_file):

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def insert_fresh_slots(conn):

    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_date = tomorrow.strftime("%Y-%m-%d")

    cur = conn.cursor()


    cur.execute("SELECT centerId FROM centers_info")
    rows = cur.fetchall()

    for row in rows:
        center_id = row[0]
        cur.execute("INSERT INTO available_slots (centerId, available_slots, date) VALUES (?, ?, ?)",
                    (center_id, 10, tomorrow_date))
    conn.commit()

def job():

    database = "instance/vaccine.db"
    conn = create_connection(database)
    with conn:
        print("Inserting fresh slots...")
        insert_fresh_slots(conn)
        print("Fresh slots inserted successfully.")

if __name__ == '__main__':
    job()
