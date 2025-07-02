import requests
import json
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

def run(target, tools, conn, port=None, wordlist_path="wordlists/common_subs.txt"):
	parsed = urlparse(target)
	base_domain = parsed.hostname if parsed.hostname else target

	# Normalize "www.example.com" to "example.com"
	if base_domain.startswith("www."):
		base_domain = base_domain[4:]

	# Look up target ID in DB
	target_res = tools["dbextract_json"](conn, "targets", "id", f"identifier='{base_domain}'")
	if not target_res:
		return {"success": False, "error": f"Target '{base_domain}' not found in database."}
	target_id = target_res[0]['id']
	print(f"target_id: {target_id}")

	old_results = tools["dbextract_json"](conn, "scans", "scan_data", f"target_id = {target_id} and scan_type = 'port_handler'")
	known_subs = []
	for entry in old_results:
		try:
			data = json.loads(entry["scan_data"])
			if "subsearch_result" in data:
				subs = data["subsearch_result"]
				if isinstance(subs, dict) and subs.get("success") and "subdomains" in subs:
					subdomains = subs["subdomains"]
					if isinstance(subdomains, list):
						known_subs.extend(subdomains)
		except (json.JSONDecodeError, KeyError, TypeError):
			continue

	if known_subs:
		return {"success": True, "subdomains": known_subs}

	found = []
	try:
		with open(wordlist_path, "r") as f:
			subdomains = [line.strip() for line in f if line.strip()]

		subdomains = [sub for sub in subdomains if f"{sub}.{base_domain}" not in known_subs]
		amount_subs = len(subdomains)

		def check_subdomain(sub):
			full_domain = f"{sub}.{base_domain}"
			for scheme in ["http", "https"]:
				url = f"{scheme}://{full_domain}"
				try:
					r = requests.get(url, timeout=3)
					if r.status_code < 400:
						return full_domain
				except requests.RequestException:
					continue
			return None

		with ThreadPoolExecutor(max_workers=10) as executor:
			future_to_sub = {executor.submit(check_subdomain, sub): sub for sub in subdomains}
			count = 0
			for future in as_completed(future_to_sub):
				count += 1
				result = future.result()
				if result:
					found.append(result)
				print(f"{count}/{amount_subs}", end='\r')

		return {"success": True, "subdomains": found if found else None}

	except Exception as e:
		return {"success": False, "error": f"Error: {e}"}
