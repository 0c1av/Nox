import mysql.connector
import json

def run(db_conn, target_identifier, scan_type, scan_data_json, level):
    cursor = db_conn.cursor()

    # Check if target exists
    cursor.execute("SELECT id FROM targets WHERE identifier = %s", (target_identifier,))
    result = cursor.fetchone()

    if result:
        target_id = result[0]
    else:
        # Insert new target
        cursor.execute("INSERT INTO targets (identifier, level) VALUES (%s, %s)", (target_identifier, level))
        target_id = cursor.lastrowid
        db_conn.commit()

    # Prepare scan data JSON string
    json_str = json.dumps(scan_data_json, sort_keys=True)  # sort_keys for consistent comparison

    # Check if the same scan already exists
    cursor.execute("""
        SELECT id FROM scans
        WHERE target_id = %s AND scan_type = %s AND scan_data = %s
    """, (target_id, scan_type, json_str))
    existing = cursor.fetchone()

    # Only insert if not already there
    if not existing:
        cursor.execute("""
            INSERT INTO scans (target_id, scan_type, scan_data)
            VALUES (%s, %s, %s)
        """, (target_id, scan_type, json_str))
        db_conn.commit()
