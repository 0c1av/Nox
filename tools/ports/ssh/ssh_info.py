import socket

import paramiko

def run(target, port=22):
	result = {
		"success": False,
		"banner": None,
		"version": None,
		"auth_methods": [],
		"host_key_type": None,
		"host_key_bits": None,
		"ciphers": [],
		"macs": [],
		"compression": [],
		"supports_password_auth": False,
		"supports_publickey_auth": False,
		"error": None
	}

	# Grab raw banner
	try:
		with socket.create_connection((target, port), timeout=5) as sock:
			banner = sock.recv(1024).decode(errors='ignore').strip()
			result["banner"] = banner
			if banner.startswith("SSH-"):
				result["version"] = banner.split("-")[1]
			else:
				result["error"] = "No valid SSH banner received"
				return result
	except Exception as e:
		result["error"] = f"Banner grab failed: {e}"
		return result

	# Proceed with Paramiko only if banner was OK
	try:
		sock = socket.create_connection((target, port), timeout=5)
		transport = paramiko.Transport(sock)
		transport.banner_timeout = 15
		time.sleep(0.5)
		transport.start_client(timeout=10)

		host_key = transport.get_remote_server_key()
		result["host_key_type"] = host_key.get_name()
		result["host_key_bits"] = host_key.get_bits()

		try:
			result["auth_methods"] = transport.auth_none("invalid_user")
		except paramiko.ssh_exception.BadAuthenticationType as e:
			result["auth_methods"] = e.allowed_types

		result["supports_password_auth"] = "password" in result["auth_methods"]
		result["supports_publickey_auth"] = "publickey" in result["auth_methods"]

		opts = transport.get_security_options()
		result["ciphers"] = opts.ciphers
		result["macs"] = opts.macs
		result["compression"] = opts.compression

		transport.close()
		sock.close()

		result["success"] = True

	except Exception as e:
		result["error"] = f"Paramiko error: {e}"

	return result
