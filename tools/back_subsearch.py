import requests
import json
from urllib.parse import urlparse

def run(target, tools, conn, port=None, wordlist_path="wordlists/common_subs.txt"):
    parsed = urlparse(target)
    base_domain = parsed.hostname if parsed.hostname else target

    # Normalize "www.example.com" to "example.com" if desired
    if base_domain.startswith("www."):
        base_domain = base_domain[4:]

    target_res = tools["dbextract_json"](conn, "targets", "id", f"identifier='{base_domain}'")
    if not target_res:
        return {"success": False, "error": f"Target '{base_domain}' not found in database."}
    target_id = target_res[0]['id']

    # Get old results (if you store them)
    old_results = tools["dbextract_json"](conn, "scans", "scan_data", f"target_id = {target_id} and scan_type = 'subdomain_finder'")
    known_subs = []
    for entry in old_results:
        try:
            data = json.loads(entry["scan_data"])
            if "subdomains" in data:
                subs = data["subdomains"]
                if isinstance(subs, list):
                    known_subs.extend(subs)
        except (json.JSONDecodeError, KeyError, TypeError):
            continue

    found = []
    try:
        with open(wordlist_path, "r") as f:
            subdomains = [line.strip() for line in f if line.strip()]

        amount_subs = len(subdomains)
        count = 0

        for sub in subdomains:
            count += 1
            full_domain = f"{sub}.{base_domain}"
            if full_domain in known_subs:
                continue  # skip previously scanned

            for scheme in ["http", "https"]:
                url = f"{scheme}://{full_domain}"
                try:
                    r = requests.get(url, timeout=3)
                    if r.status_code < 400:
                        found.append(full_domain)
                        break  # no need to try https if http works
                except requests.RequestException:
                    continue
            print(f"{count}/{amount_subs}", end='\r')

        return {"success": True, "subdomains": found if found else None}

    except Exception as e:
        return {"success": False, "error": f"Error: {e}"}
