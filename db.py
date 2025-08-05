import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="jtc353.encs.concordia.ca",           # or "127.0.0.1"
        user="jtc353_1",                # your MySQL username
        password="G7pX2mQ9",    # replace with your actual MySQL password
        database="jtc353_1"  # replace with your database name
    )

conn = get_connection()
print("✅ Connected!")
conn.close()
