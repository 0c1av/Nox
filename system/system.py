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

def run(main_target, tools):

	target_valid = tools["target_tester"](main_target)
	if target_valid == "invalid":
		print("Excitting.")
		return
	elif target_valid != "invalid" and target_valid != "valid":
		main_target = target_valid

	conn = tools["dbconnection"]("open", None)
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
		tools["dbinsert_json"](conn, target, tool_name, result)
		history.append({"tool": tool_name, "params": params, "result": result})
