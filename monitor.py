import json
import time
import os
import sys
import system.starter as starter
import server.dbextract_json as extract
import server.dbconnection as connector

conn = connector.run("open", None)




def get_subs(target):
	target_id = extract.run(conn, "targets", "id", f"identifier='{target}'")
	if target_id:
		target_id = target_id[0]['id']
	else:
		return []
	scan_data = extract.run(conn, "scans", "scan_data", f"target_id = {target_id} and scan_type = 'port_handler'")
	if scan_data:
		scan_data_json = json.loads(scan_data[0]['scan_data'])
	else:
		return []
	sub_result = scan_data_json.get("subsearch_result")
	if not sub_result or not sub_result.get("success"):
		return []
	subdomains = scan_data_json['subsearch_result']['subdomains']
	return subdomains


def main():
	print("Enter main target (IP or Domain): ", end="", flush=True)
	target = input()
	starter.run(target)
	subdomains = get_subs(target)
	#print(f"subdomains: {subdomains}")
	for sd in subdomains:
		print("\n-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
		time.sleep(5)
		print(f"handling: {sd}\n")
		level = 2
		starter.run(sd, 2)
if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		pass
