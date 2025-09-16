import mysql.connector
import time

def run(action, conn=None):
    if action == "open":
        for i in range(10):  # Retry up to 10 times
            try:
                conn = mysql.connector.connect(
                    host="nox-db",
                    user="pentool_user",
                    password="10tartesframboises!",
                    database="pentool"
                )
                return conn
            except mysql.connector.Error:
                print("Waiting for DB to be ready...")
                time.sleep(1)
        raise Exception("Cannot connect to DB after 10 attempts")

    elif action == "close":
        if conn is not None:
            conn.close()
