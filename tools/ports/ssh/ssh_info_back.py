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
			result["banner"] = sock.recv(1024).decode(errors='ignore').strip()
			if result["banner"].startswith("SSH-"):
				result["version"] = result["banner"].split("-")[1]
		result["success"] = True
	except Exception as e:
		result["error"] = f"Banner grab failed: {e}"
		return result

	# Paramiko client
	try:
		transport = paramiko.Transport((target, port))
		transport.start_client(timeout=5)

		# Host key info
		host_key = transport.get_remote_server_key()
		result["host_key_type"] = host_key.get_name()
		result["host_key_bits"] = host_key.get_bits()

		# Auth methods
		try:
			result["auth_methods"] = transport.auth_none("invalid_user")
		except paramiko.ssh_exception.BadAuthenticationType as e:
			result["auth_methods"] = e.allowed_types

		result["supports_password_auth"] = "password" in result["auth_methods"]
		result["supports_publickey_auth"] = "publickey" in result["auth_methods"]

		# Ciphers / algorithms
		result["ciphers"] = transport.get_security_options().ciphers
		result["macs"] = transport.get_security_options().macs
		result["compression"] = transport.get_security_options().compression

		transport.close()

		result["success"] = True

	except Exception as e:
		result["error"] = f"Paramiko error: {e}"

	return result
