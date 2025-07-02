import os
import sys
import time
import json

import system.system as system
import system.load_tools as load_tools

params_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "system", "params.json"))

def set_running_flag(flag: bool):
	try:
		with open(params_path, "r") as f:
			params = json.load(f)
	except (FileNotFoundError, json.JSONDecodeError):
		params = {}

	params["running"] = flag

	with open(params_path, "w") as f:
		json.dump(params, f, indent=2)

def is_already_running():
	try:
		with open(params_path, "r") as f:
			params = json.load(f)
			return params.get("running", False)
	except (FileNotFoundError, json.JSONDecodeError):
		return False




def run(target):
	if is_already_running():
		print("[!] Another instance is already running. Aborting.")
		return
	set_running_flag(True)

	try:
		print("Loading tools...", end="\r")
		start_loading_time = time.time()
		try:
			tools = load_tools.run()
		except Exception as e:
			print(f"[!] Failed to load tools: {e}")
			return
		end_loading_time = time.time()
		loading_time = end_loading_time - start_loading_time
		print(f"loading time: {loading_time:.2f}s")

		system.run(target, tools)
	except KeyboardInterrupt:
		print("\nKeyboardInterrupt: excitting.")

	finally:
		set_running_flag(False)
