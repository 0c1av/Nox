import subprocess
import socket


def validate_domain(target):
	protocols = ["https://", "http://"]
	for prot in protocols:
		if target.startswith(prot):
			return target.removeprefix(prot)
	return target

def target_check(target):
	timeout = 5
	try:
		result = subprocess.run(
			["ping", "-c", "1", target],
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL
		)
		if result.returncode == 0:
			return True
		else:
			print("[!] Ping failed")
	except Exception:
		print("[!] Ping failed")

	ports_to_scan = [22, 23, 80, 443, 445, 3306, 3389]
	for port in ports_to_scan:
		try:
			with socket.create_connection((target, port), timeout=timeout):
				return True
		except Exception:
			continue
	return False




def run(target):
	clean_target = validate_domain(target)
	print(f"clean_target: {clean_target}")
	if clean_target != target:
		if target_check(clean_target):
			print(f"[!] Target '{target}' includes a protocol prefix.")
			option = input(f"  \-> Use '{clean_target}' instead? (y/n): ")
			if option.lower() == "y":
				return clean_target
			else:
				return "invalid"
		else:
			print(f"[!] Target inaccessible.")
			return "invalid"
	else:
		if target_check(target):
			return "valid"
		else:
			print(f"[!] Target inaccessible.")
			return "invalid"

