import json
import importlib
import re
import time
import socket
import ipaddress
import platform
import subprocess
from threading import Thread
import argparse

GREEN = "\033[32m"
BOLD = "\033[1m"
RESET = "\033[0m"

def load_tools():
	from tools import nmap_scan, dirsearch, port_handler, xss_scan
	from tools.ports.ftp import ftp_info, ftp_bf, ftp_login_exploit
	from tools.ports.ssh import ssh_info, ssh_bf, ssh_login_exploit
	from tools.ports.telnet import telnet_info, telnet_bf, telnet_login_exploit
	from tools.ports.MySQL import sql_info, sql_bf, sql_login_exploit
	from tools.ports.smtp import smtp_info, smtp_bf
	return {
		"nmap_scan": nmap_scan.run,
		"dirsearch": dirsearch.run,
		"port_handler": port_handler.run,
		"xss_scan": xss_scan.run,

		"ftp_info": ftp_info.run,
		"ftp_bf": ftp_bf.run,
		"ftp_login_exploit": ftp_login_exploit.run,

		"ssh_info": ssh_info.run,
		"ssh_bf": ssh_bf.run,
		"ssh_login_exploit": ssh_login_exploit.run,

		"telnet_info": telnet_info.run,
		"telnet_bf": telnet_bf.run,
		"telnet_login_exploit": telnet_login_exploit.run,

		"sql_info": sql_info.run,
		"sql_bf": sql_bf.run,
		"sql_login_exploit": sql_login_exploit.run,

		"smtp_info": smtp_info.run,
		"smtp_bf": smtp_bf.run
	}




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

	target_valid = verify_target(main_target)
	if target_valid == "invalid":
		print("Excitting.")
		return
	elif target_valid != "invalid" and target_valid != "valid":
		main_target = target_valid


	main_ports = []
	history = []

	while True:
		tool_to_use = choose_tool(history, main_target, main_ports, tools)
		if tool_to_use is None:
			print("No tool to use")
			print(f"History: {history}")
			break

		tool_name = tool_to_use["tool"]
		params = tool_to_use["params"]

		if tool_name not in tools:
			print(f"Unknown tool: {tool_name}")
			break

		print(f"\n{BOLD}[+] Running {tool_name}...{RESET}")
		result = tools[tool_name](**params)

		# show ports and those that aren't supported:
		#supported_ports = [80]
		supported_ports = [21, 22, 23, 80, 443, 445, 8080, 8443, 3306, 25, 587, 465]
		if tool_name == "nmap_scan" and result:
			for i in range(len(result)):
				port = result[i]
				if port not in supported_ports:
					result[i] = f"({port})"

		if result:
			try:
				print(f"{GREEN}[Result]{RESET}")
				print(json.dumps(result, indent=4))
				print()
			except (TypeError, OverflowError):
				print(f"{GREEN}[Result]{RESET} {result}\n")
		#after printing open ports, delete from result for testing
		if tool_name == "nmap_scan" and result:
			i = 0
			while i < len(result):
				port = result[i]
				if isinstance(port, str) and "(" in port:
					result.pop(i)
				else:
					i += 1



		history.append({"tool": tool_name, "params": params, "result": result})


		#cont = input("Continue? (y/n): ")
		#if cont.lower() != 'y':
		#	break





#scripts for launch
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






def verify_target(target):
	clean_target = validate_domain(target)
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


if __name__ == "__main__":
	#print("Launching Nox...")
	try:
		main()
	except KeyboardInterrupt:
		print("\nKeyboardInterrupt: excitting.")
