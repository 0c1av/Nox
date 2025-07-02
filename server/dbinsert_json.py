import mysql.connector
import json

def run(db_conn, target_identifier, scan_type, scan_data_json):
	cursor = db_conn.cursor()

	# Check if target exists
	cursor.execute("SELECT id FROM targets WHERE identifier = %s", (target_identifier,))
	result = cursor.fetchone()

	if result:
		target_id = result[0]
	else:
		# Insert new target
		cursor.execute("INSERT INTO targets (identifier) VALUES (%s)", (target_identifier,))
		target_id = cursor.lastrowid
		db_conn.commit()

	# Prepare scan data
	json_str = json.dumps(scan_data_json)

	# Insert or update scan result
	cursor.execute("""
		INSERT INTO scans (target_id, scan_type, scan_data)
		VALUES (%s, %s, %s)
		ON DUPLICATE KEY UPDATE scan_data = VALUES(scan_data)
	""", (target_id, scan_type, json_str))

	db_conn.commit()
	#print(f"[+] Stored {scan_type} scan for {target_identifier}")
