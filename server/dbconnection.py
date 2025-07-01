import mysql.connector

def run(action, conn):
	if action == "open":
		conn = mysql.connector.connect(
			host="100.80.79.60",
			user="pentool_user",
			password="10tartesframboises!",
			database="pentool"
		)
		return conn

	elif action == "close":
		conn.close()
