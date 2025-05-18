import requests
import json
import os

def run(target, wordlist_path="wordlists/common_dirs.txt"):
	found = []
	history_path = "tools/tool_history/dirsearch_history.json"

	#load history
	os.makedirs(os.path.dirname(history_path), exist_ok=True)
	if not os.path.exists(history_path):
		with open(history_path, "w") as f:
			json.dump([], f)
	with open(history_path, "r") as f:
		try:
			history = json.load(f)
		except json.JSONDecodeError:
			history = []

	#check if scan already done
	for entry in history:
		if entry["target"] == target and entry["wordlist"] == wordlist_path and entry["success"] == True:
			#print(f"[+] Succesfull scan already performed, copying results..")
			return entry["found_paths"]
		elif entry["target"] == target and entry["wordlist"] == wordlist_path and entry["success"] == False:
			continue
			#print(f"[+] Scan already performed unsuccesfully, trying again..")

	try:
		with open(wordlist_path, "r") as f:
			words = [line.strip() for line in f if line.strip()]

		for word in words:
			url = f"{target.rstrip('/')}/{word}"
			try:
				response = requests.get(url, timeout=3)
				if response.status_code < 400:
					found.append(f"{url} ({response.status_code})")
			except requests.RequestException:
				continue


		#If old scan unsuccessfull -> modify with successful
		for i, entry in enumerate(history):
			if entry["target"] == target and entry["wordlist"] == wordlist_path and entry["success"] == False:
				del history[i]
				break
		history.append({"target": target, "wordlist": wordlist_path, "found_paths": found, "success": True})
		with open(history_path, "w") as f:
			json.dump(history, f, indent=2)

		return found if found else None

	except Exception as e:

		history.append({"target": target, "wordlist": wordlist_path, "found_paths": found, "success": False})
		with open(history_path, "w") as f:
			json.dump(history, f, indent=2)

		return [f"Error: {e}"]
