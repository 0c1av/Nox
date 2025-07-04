import requests
import json
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

def run(target, tools, conn, port, wordlist_path="wordlists/common_dirs.txt"):
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

	# ------ threaded section begins here ------
	try:
		with open(wordlist_path, "r") as f:
			words = [line.strip() for line in f if line.strip()]

		scheme = "http" if port in [80, 8080] else "https"
		base_url = f"{scheme}://{target.rstrip('/')}"

		found = []
		amount_words = len(words)

		def check_url(word):
			url = f"{base_url}/{word}"
			try:
				resp = requests.get(url, timeout=3)
				if resp.status_code < 400:
					return url
			except requests.RequestException:
				pass
			return None

		with ThreadPoolExecutor(max_workers=10) as executor:
			future_to_word = {executor.submit(check_url, word): word for word in words}
			count = 0
			for future in as_completed(future_to_word):
				count += 1
				result = future.result()
				if result:
					found.append(result)
				print(f"{count}/{amount_words}", end='\r')

		return {"success": True, "paths": found if found else None}

	except Exception as e:
		history.append({"target": target, "wordlist": wordlist_path, "found_paths": found, "success": False})
		with open(history_path, "w") as f:
			json.dump(history, f, indent=2)
		return {"success": False, "Error": f"Error: {e}"}
