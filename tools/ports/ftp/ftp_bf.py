from ftplib import FTP, error_perm, all_errors

def run(target, port, usernames_path="wordlists/ftp_users.txt", passwords_path="wordlists/ftp_pw.txt"):
	usernames = []
	passwords = []

	try:
		with open(usernames_path, "r") as f:
			usernames = [line.strip() for line in f if line.strip()]
	except FileNotFoundError:
		return {"success": False, "error": "Username file not found"}

	try:
		with open(passwords_path, "r") as f:
			passwords = [line.strip() for line in f if line.strip()]
	except FileNotFoundError:
		return {"success": False, "error": "Password file not found"}

	#debug
	#usernames = ["anonymous", "admin"]
	#passwords = ["pw", "test1", "test2"]

	for username in usernames:
		for password in passwords:
			try:
				ftp = FTP()
				ftp.connect(target, port, timeout=4)
				ftp.login(username, password)
				ftp.quit()
				return {
					"success": True,
					"username": username,
					"password": password,
				}
			except all_errors as e:
				#print(f"Failed login for {username}:{password} - {e}")
				continue

	return {"success": False}
