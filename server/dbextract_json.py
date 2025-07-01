import mysql.connector
import json

def run(db_conn, table, column, condition):
	cursor = db_conn.cursor(dictionary=True)

	query = f"SELECT {column} FROM {table} WHERE {condition}"
	try:
		cursor.execute(query)
		results = cursor.fetchall()
		if not results:
			return []

		return results

	except mysql.connector.Error as err:
		print(f"[!] MySQL error: {err}")
	except Exception as e:
		print(f"[!] Unexpected error: {e}")
	return []
