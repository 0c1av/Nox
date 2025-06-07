import subprocess
import re


def run(target):
	#debug
	#return [21, 22, 23, 25, 80, 3306, 406, 443, 464, 765, 1035, 1098, 1721, 2288, 2909, 3986, 5002, 5500, 5903, 6001, 6101, 10024, 28201, 41511]


	supported_ports = [21, 22, 80, 443, 445, 8080, 8443]
	slow_network_logged = False
	output_lines = []

	try:
		process = subprocess.Popen(
			["nmap", "-sV", "-oG", "-", target],
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			text=True
		)

		for line in process.stdout:
			output_lines.append(line)
			if "RTTVAR has grown to over" in line and not slow_network_logged:
				print("slow network")
				slow_network_logged = True
		process.wait()
		output = ''.join(output_lines)
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
