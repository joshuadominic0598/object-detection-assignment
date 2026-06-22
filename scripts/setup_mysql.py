import os
import time
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

host = os.getenv("MYSQL_HOST", "localhost")
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
database = os.getenv("MYSQL_DB", "counter")

for _ in range(30):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        break
    except Exception:
        time.sleep(2)
else:
    raise Exception("Unable to connect to MySQL")

cursor = conn.cursor()

cursor.execute(f"""
CREATE DATABASE IF NOT EXISTS {database}
""")

cursor.execute(f"USE {database}")

cursor.execute("""
CREATE TABLE IF NOT EXISTS object_counts (
    object_class VARCHAR(255) PRIMARY KEY,
    count INT NOT NULL
)
""")

conn.commit()

cursor.close()
conn.close()

print("MySQL initialized successfully.")