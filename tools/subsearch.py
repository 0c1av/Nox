import requests
import json
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# ViewDNS API function
def get_subdomains_viewdns(domain):
	try:
		#domain = domain.replace("www.", "")
		url = f"https://api.viewdns.info/subdomains/?domain={domain}&apikey=410fe345c015f8b40b57487f4101e5e97239c0ea&output=json"
		response = requests.get(url, timeout=5)
		data = response.json()

		# Graceful error handling
		subdomains = []
		if "response" in data and "subdomains" in data["response"]:
			subdomains = [entry["name"] for entry in data["response"]["subdomains"]]
			#print(f"[+] ViewDNS found {len(subdomains)} subdomains for {domain}")
		return subdomains

	except Exception as e:
		#print(f"[-] ViewDNS error: {e}")
		return []

# Wordlist-based subdomain scanner
def scan_subdomains_wordlist(base_domain, known_subs, wordlist_path):
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

	except Exception as e:
		pass
		#print(f"[-] Wordlist scanning error: {e}")
	return found


# Combined runner
def run(target, tools, conn, port=None, wordlist_path="wordlists/common_subs.txt"):
	parsed = urlparse(target)
	base_domain = parsed.hostname if parsed.hostname else target
	# Get known subs from DB
	target_res = tools["dbextract_json"](conn, "targets", "id", f"identifier='{base_domain}'")
	if not target_res:
		return {"success": False, "error": f"Target '{base_domain}' not found in database."}
	target_id = target_res[0]['id']

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
	#if base_domain.startswith("www."):
	#	base_domain = base_domain[4:]
	# Step 1: From ViewDNS API
	viewdns_subs = get_subdomains_viewdns(base_domain)

	# Step 2: From wordlist-based scanner
	wordlist_subs = scan_subdomains_wordlist(base_domain, known_subs + viewdns_subs, wordlist_path)

	# Combine, remove duplicates
	all_subs = set(known_subs + viewdns_subs + wordlist_subs)

	return {
		"success": True,
		"subdomains": sorted(all_subs) if all_subs else None
	}
