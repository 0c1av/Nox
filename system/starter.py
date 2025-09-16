import threading
import os
import sys
import time
import json
import logging

import system.system as system
import system.load_tools as load_tools

import server.flask_api as flask_api


#params_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "system", "params.json"))

params_path = "system/params.json"
def set_running_flag(flag: bool, target):
	try:
		with open(params_path, "r") as f:
			params = json.load(f)
	except (FileNotFoundError, json.JSONDecodeError):
		params = {}

	params["running"] = flag
	params["target"] = target
	print(f"Running: {params['running']}, Target: {params['target']}")

	with open(params_path, "w") as f:
		json.dump(params, f, indent=2)

def is_already_running():
	try:
		with open(params_path, "r") as f:
			params = json.load(f)
			return params.get("running", False)
	except (FileNotFoundError, json.JSONDecodeError):
		return False



def run(target, level = 1):
	if is_already_running():
		print("[!] Another instance is already running. Aborting.")
		return "abort"
	'''
	flask_thread = threading.Thread(target=flask_api.run, daemon=True)
	flask_thread.start()
	'''

	set_running_flag(True, target)


	try:
		print("Loading tools", end="\r")
		start_loading_time = time.time()
		try:
			tools = load_tools.run()
		except Exception as e:
			print(f"[!] Failed to load tools: {e}")
			return
		end_loading_time = time.time()
		loading_time = end_loading_time - start_loading_time
		print(f"Loading tools ({loading_time:.2f}s)")

		system.run(target, tools, level)
	except KeyboardInterrupt:
		print("\nKeyboardInterrupt: excitting.")

	finally:
		set_running_flag(False, target)
