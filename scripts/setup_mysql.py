import os
import time

from dotenv import load_dotenv
import mysql.connector

load_dotenv()

host = os.getenv("MYSQL_HOST", "localhost")
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
database = os.getenv("MYSQL_DB", "counter")
port = int(os.getenv("MYSQL_PORT", "3306"))

for _ in range(30):
    try:
        conn = mysql.connector.connect(host=host,user=user,password=password,port=port)
        break
    except Exception:
        time.sleep(2)
else:
    raise Exception("Unable to connect to MySQL")

cursor = conn.cursor()
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
cursor.execute(f"USE {database}")

# Object Counter Table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS object_counts (
        object_class VARCHAR(255)
        PRIMARY KEY,
        count INT NOT NULL)"""
        )

# API Monitoring Table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS api_request_log (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        request_id VARCHAR(36),
        request_timestamp TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,
        image_name VARCHAR(255),
        endpoint VARCHAR(100),
        threshold FLOAT,
        detected_classes TEXT,
        response_time_ms INT,
        detected_count INT,
        status_code INT,
        success BOOLEAN,
        error_message TEXT)"""
        )

# Prediction Monitoring Table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS prediction_log (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        request_id VARCHAR(36),
        request_timestamp TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,
        image_name VARCHAR(255),
        endpoint VARCHAR(100),
        object_class VARCHAR(255),
        confidence FLOAT)"""
        )

conn.commit()
cursor.close()
conn.close()

print(
    "MySQL initialized successfully. "
    "Created object_counts, "
    "api_request_log and prediction_log tables."
)