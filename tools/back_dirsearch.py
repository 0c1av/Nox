import requests
import json
import os
from urllib.parse import urlparse


def run(target, tools, conn, port, wordlist_path="wordlists/common_dirs.txt"):
	#target = target.replace("http://", "").split(":")[0]  # crude but effective
	parsed = urlparse(target)
	target = parsed.hostname

	target_res = tools["dbextract_json"](conn, "targets", "id", f"identifier='{target}'")
	if not target_res:
		return {"success": False, "error": f"Target '{target}' not found in database."}
	target_id = target_res[0]['id']
	old_results = tools["dbextract_json"](conn, "scans", "scan_data", f"target_id = {target_id} and scan_type = 'port_handler'")
	all_paths = []
	for entry in old_results:
		try:
			data = json.loads(entry["scan_data"])

			if "dirsearch_result" in data:
				dir_res = data["dirsearch_result"]
				if isinstance(dir_res, dict) and dir_res.get("success") and "paths" in dir_res:
					paths = dir_res["paths"]
					if isinstance(paths, list):
						all_paths.extend(paths)
		except (json.JSONDecodeError, KeyError, TypeError):
			continue

	history = all_paths
	if history:
		return {"success": True, "paths": history}
	found = []



	try:
		with open(wordlist_path, "r") as f:
			words = [line.strip() for line in f if line.strip()]

		amount_words = 0
		for word in words:
			amount_words += 1
		count = 0
		for word in words:
			count += 1
			if port in [80, 8080]:
				url = f"http://{target.rstrip('/')}/{word}"
			elif port in [443, 8443]:
				url = f"https://{target.rstrip('/')}/{word}"
			try:
				response = requests.get(url, timeout=3)
				if response.status_code < 400:
					found.append(f"{url}")
				print(f"{count}/{amount_words}", end='\r')
			except requests.RequestException:
				continue

		return {"success": True, "paths": found if found else None}


	except Exception as e:

		history.append({"target": target, "wordlist": wordlist_path, "found_paths": found, "success": False})
		with open(history_path, "w") as f:
			json.dump(history, f, indent=2)

		return {"success": False, "Error": f"Error: {e}"}
