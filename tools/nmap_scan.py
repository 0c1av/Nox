import subprocess
import re

def run(target):
	#debug
	#return [21, 22, 80, 406, 443, 464, 765, 1035, 1098, 1721, 2288, 2909, 3986, 5002, 5500, 5903, 6001, 6101, 10024, 28201, 41511]


	try:
		output = subprocess.check_output(["nmap", "-sV", "-oG", "-", target], text=True)
		result = extract_ports(output)
		return result
	except Exception as e:
		return f"Error: {e}"

def extract_ports(output):
	open_ports = []

	for line in output.splitlines():
		if line.startswith("Host:") and "Ports:" in line:
			match = re.search(r"Ports: (.+)", line)
			if match:
				port_entries = match.group(1).split(", ")
				for entry in port_entries:
					if "/open/" in entry:
						port_match = re.match(r"(\d+)/open", entry)
						if port_match:
							open_ports.append(int(port_match.group(1)))
	return open_ports if open_ports else None
