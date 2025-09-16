from flask import Flask, jsonify, render_template_string
from waitress import serve
import socket
import netifaces
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import server.dbextract_json as dbextract
import server.dbconnection as dbconn




params_path = "system/params.json"


def set_running_flag(status):
	try:
		with open(params_path, "r") as f:
			params = json.load(f)
	except (FileNotFoundError, json.JSONDecodeError):
		params = {}

	if status == "Up":
		params["server"] += 1
	elif status == "Down":
		params["server"] -= 1

	with open(params_path, "w") as f:
		json.dump(params, f, indent=2)

def is_already_running():
	try:
		with open(params_path, "r") as f:
			params = json.load(f)
			if params["server"] > 0:
				return True
			else:
				return False
	except (FileNotFoundError, json.JSONDecodeError):
		return False











app = Flask(__name__)





@app.route("/")
def home():

	try:
		with open(params_path, "r") as f:
			params = json.load(f)
			running_status = params.get("running", False)
			current_target = params.get("target", None)
	except (FileNotFoundError, json.JSONDecodeError):
		running_status = "Unknown"
		current_target = "Unknown"
	if running_status == True:
		running_status = "Up"
	elif running_status == False:
		running_status = "Down"
	logging.info(f"Running Status: {running_status}")
	html = f'''<h1>Welcome to Nox's interface</h1>'''
	html += f'''<p>Program's status: {running_status}</p>'''
	if running_status == "Up":
		html += f'''<p>Target: {current_target}</p>'''
	html += '''
	<ul>
		<li><a href="/targets">View Targets Table</a></li>
		<li><a href="/scans">View Scans Table</a></li>
	</ul>
		'''
	return html

@app.route("/targets")
def list_targets():
	db = dbconn.run("open", None)
	cursor = db.cursor(dictionary=True)
	cursor.execute("SELECT id, identifier FROM targets")
	results = cursor.fetchall()
	db.close()

	html = "<h2>Targets</h2><ul>"
	for row in results:
		html += f'<li><a href="/targets/{row["id"]}">{row["identifier"]}</a></li>'
	html += "</ul><a href='/'>← Back</a>"
	return html


@app.route("/targets/<int:target_id>")
def target_detail(target_id):
	db = dbconn.run("open", None)
	cursor = db.cursor(dictionary=True)
	cursor.execute("SELECT * FROM targets WHERE id = %s", (target_id,))
	result = cursor.fetchone()
	db.close()

	if not result:
		return "<h2>Target not found</h2><a href='/targets'>← Back</a>"

	html = f"<h2>Target Details (ID: {target_id})</h2><ul>"
	for key, value in result.items():
		html += f"<li><b>{key}</b>: {value}</li>"
	html += "</ul><a href='/targets'>← Back</a>"
	return html









@app.route("/scans")
def list_scans():
	db = dbconn.run("open", None)
	cursor = db.cursor(dictionary=True)
	cursor.execute("SELECT id, target_id FROM scans")
	results = cursor.fetchall()
	db.close()

	html = "<h2>Scans</h2><ul>"
	for row in results:
		html += f'<li><a href="/scans/{row["id"]}">Scan {row["id"]} (Target ID: {row["target_id"]})</a></li>'
	html += "</ul><a href='/'>← Back</a>"

	return html


@app.route("/scans/<int:scan_id>")
def scan_detail(scan_id):
	db = dbconn.run("open", None)
	cursor = db.cursor(dictionary=True)
	cursor.execute("SELECT * FROM scans WHERE id = %s", (scan_id,))
	result = cursor.fetchone()
	db.close()

	if not result:
		return "<h2>Scan not found</h2><a href='/scans'>← Back</a>"

	html = f"<h2>Scan Details (ID: {scan_id})</h2><ul>"
	for key, value in result.items():
		html += f"<li><b>{key}</b>: {value}</li>"
	html += "</ul><a href='/scans'>← Back</a>"

	return html


















def get_all_host_ips():
	"""Returns all IPv4 addresses of the machine (including Tailscale)."""
	ips = []
	for iface in netifaces.interfaces():
		addrs = netifaces.ifaddresses(iface)
		if netifaces.AF_INET in addrs:
			for link in addrs[netifaces.AF_INET]:
				ip = link.get("addr")
				if ip and not ip.startswith("127."):
					ips.append(ip)
	return ips

def run():
	ip_list = get_all_host_ips()
	print("\n[+] Web interface available at:")
	for ip in ip_list:
		print(f"    → http://{ip}:5000")
	'''
	if is_already_running():
		print("server already running")
		return
	'''


	set_running_flag("Up")
	try:
		serve(app, host="0.0.0.0", port=5000)
	except KeyboardInterrupt:
		pass
	finally:
		set_running_flag("Down")
