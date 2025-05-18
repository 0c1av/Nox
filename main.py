import json
import importlib
import re
import time

GREEN = "\033[32m"
BOLD = "\033[1m"
RESET = "\033[0m"

def load_tools():
	from tools import nmap_scan, dirsearch, port_handler
	from tools.ports.ftp import ftp_info, ftp_bf, ftp_login_exploit
	return {
		"nmap_scan": nmap_scan.run,
		"dirsearch": dirsearch.run,
		"port_handler": port_handler.run,
		"ftp_info": ftp_info.run,
		"ftp_bf": ftp_bf.run,
		"ftp_login_exploit": ftp_login_exploit.run
	}

def describe_tools():
	return """
		- nmap_scan(target): Scan a host for open ports
		- dirsearch(url): Discover hidden paths in a web server
		- port_handler(port): Desides what to do with the port
		- ftp_anon(target, port): Try anonymous login on ftp
		- ftp_bf(target, port): Bruteforce ftp login
		"""



def choose_tool(history, main_target, main_ports, tools):
	if not history:
		return {
			"tool": "nmap_scan",
			"params": {"target": main_target}
		}
	if history:
		if not main_ports:
			if any(event["tool"] == "nmap_scan" and event["params"]["target"] == main_target for event in history):
				for event in history:
					if event["tool"] == "nmap_scan" and event["params"]["target"] == main_target:
						main_ports = event["result"]
						ports2handle = main_ports
						break
		if main_ports:
			handled_port = ports2handle[0]
			del ports2handle[0]
			return {
				"tool": "port_handler",
				"params": {"target": main_target, "port": handled_port, "tools": tools}
			}
	else:
		print(f"history: {history}")
		return None

def main():
	tools = load_tools()
	print("Enter target (IP or Domain): ", end="", flush=True)
	main_target = input()
	main_ports = []
	history = []

	while True:
		tool_to_use = choose_tool(history, main_target, main_ports, tools)
		if tool_to_use is None:
			print("[ERROR]Failed to choose tool. Exiting.")
			break

		tool_name = tool_to_use["tool"]
		params = tool_to_use["params"]

		if tool_name not in tools:
			print(f"Unknown tool: {tool_name}")
			break

		print(f"\n{BOLD}[+] Running {tool_name}...{RESET}")
		result = tools[tool_name](**params)
		if result:
			try:
				print(f"{GREEN}[Result]{RESET}")
				print(json.dumps(result, indent=4))
				print()
			except (TypeError, OverflowError):
				print(f"{GREEN}[Result]{RESET} {result}\n")
		else:
			print(f"[Result]{result}\n")

		history.append({"tool": tool_name, "params": params, "result": result})


		#cont = input("Continue? (y/n): ")
		#if cont.lower() != 'y':
		#	break



if __name__ == "__main__":
	print("Launching Nox...")
	main()
