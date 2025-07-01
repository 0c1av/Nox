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
	from tools import nmap_scan, dirsearch, port_handler, xss_scan, open_port_finder, target_tester

	from tools.ports.ftp import ftp_info, ftp_bf, ftp_login_exploit
	from tools.ports.ssh import ssh_info, ssh_bf, ssh_login_exploit
	from tools.ports.telnet import telnet_info, telnet_bf, telnet_login_exploit
	from tools.ports.MySQL import sql_info, sql_bf, sql_login_exploit
	from tools.ports.smtp import smtp_info, smtp_bf

	from server import dbinsert_json, dbconnection, dbextract_json

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
		"smtp_bf": smtp_bf.run,

		"dbinsert_json": dbinsert_json.run,
		"dbconnection": dbconnection.run,
		"dbextract_json": dbextract_json.run,

		"open_port_finder": open_port_finder.run,
		"target_tester": target_tester.run
	}




def choose_tool(history, current_target, main_ports, tools, supported_ports, handled_ports, conn):
	if not history:
		return {
			"tool": "nmap_scan",
			"params": {"target": current_target}
		}
	elif history:
		if not main_ports:
			if any(event["tool"] == "nmap_scan" and event["params"]["target"] == current_target for event in history):
				for event in history:
					if event["tool"] == "nmap_scan" and event["params"]["target"] == current_target:
						main_ports = event["result"].get("ports", [])
						ports2handle = main_ports.copy()
						break
		if main_ports:
			for port in main_ports:
				if port not in handled_ports and port in supported_ports:
					handled_ports.add(port)
					return {
						"tool": "port_handler",
						"params": {"target": current_target, "port": port, "tools": tools, "conn": conn}
					}

	else:
		print(f"history: {history}")
		return None

def main():
	start_loading_time = time.time()
	print("Loading tools...", end="\r")
	try:
		tools = load_tools()
	except Exception as e:
		print(f"[!] Failed to load tools: {e}")
	end_loading_time = time.time()
	loading_time = end_loading_time - start_loading_time
	print(f"loading time: {loading_time:.2f}s")
	conn = tools["dbconnection"]("open", None)
	print("Enter target (IP or Domain): ", end="", flush=True)
	main_target = input()


	target_valid = tools["target_tester"](main_target)
	if target_valid == "invalid":
		print("Excitting.")
		return
	elif target_valid != "invalid" and target_valid != "valid":
		main_target = target_valid


	main_ports = []
	history = []

	target = main_target

	#supported_ports = [80]
	supported_ports = [21, 22, 23, 80, 443, 445, 8080, 8443, 3306, 25, 587, 465]
	handled_ports = set()

	tool_res_sort = {"dirsearch_result", "XSS_result"}

	while True:
		tool_to_use = choose_tool(history, target, main_ports, tools, supported_ports, handled_ports, conn)
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

		if tool_name == "nmap_scan" and result and "ports" in result:
			ports = result["ports"]
			if not ports:
				print("no open ports. Excitting.")
				return
			printports = ports.copy()
			for i in range(len(printports)):
				port = printports[i]
				if port not in supported_ports:
					printports[i] = f"({port})"

		if result:
			try:
				print(f"{GREEN}[Result]{RESET}")
				print(json.dumps(result, indent=4))
				print()
			except (TypeError, OverflowError):
				print(f"{GREEN}[Result]{RESET} {result}\n")
		#after printing open ports, delete from result for testing
		if tool_name == "nmap_scan" and result and "ports" in result:
			i = 0
			ports = result["ports"]
			ports = ports.copy()
			while i < len(ports):
				port = ports[i]
				if isinstance(port, str) and "(" in port:
					ports.pop(i)
				else:
					i += 1

		target = params["target"]
		n = 0
		'''
		res_sort = tool_res_sort.union(tools.keys())
		for t in res_sort:
			for key in result:
				if key == t:
					n += 1
					tools["dbinsert_json"](conn, target, tool_name, result[t])
		print("no tool in res_sort")
		'''
		if n == 0:
			tools["dbinsert_json"](conn, target, tool_name, result)
		history.append({"tool": tool_name, "params": params, "result": result})


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("\nKeyboardInterrupt: excitting.")
