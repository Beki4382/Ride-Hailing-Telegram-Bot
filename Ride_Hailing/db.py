import sqlite3

conn = sqlite3.connect('Ride_Healing/users.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        username TEXT,
        state TEXT,
        fullname TEXT,
        phone TEXT,
        role TEXT,
        history TEXT,
        registration_date TEXT,
        rating INTEGER,
        completed_rides TEXT
    )
''')

conn.commit()
conn.close()
