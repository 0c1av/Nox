import socket
import time

def run(target, port=3306, timeout=5):
	result = {
		"success": False,
		"output": "",
		"version": None,
		"connection_id": None,
		"capabilities": None,
		"charset": None,
		"plugin": None,
		"ssl_supported": False,
		"login_required": True,
		"error": None
	}


	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(timeout)
		sock.connect((target, port))

		data = sock.recv(4096)
		if len(data) < 34:
			result["error"] = "Handshake too short"
			sock.close()
			return {"success": False}


		# Parse protocol version
		proto_ver = data[4]
		version_end = data.find(b'\x00', 5)
		server_version = data[5:version_end].decode('utf-8', errors='ignore')

		# Connection ID
		conn_id = int.from_bytes(data[version_end+1:version_end+5], 'little')

		# Capabilities (split in 2 parts)
		cap_low = int.from_bytes(data[version_end+13:version_end+15], 'little')
		cap_high = int.from_bytes(data[version_end+27:version_end+29], 'little')
		capabilities = (cap_high << 16) | cap_low

		# Character set
		charset = data[version_end+15]

		# Auth plugin name
		plugin_start = data.find(b'\x00', version_end + 30) + 1
		plugin_end = data.find(b'\x00', plugin_start)
		plugin_name = data[plugin_start:plugin_end].decode('utf-8', errors='ignore') if plugin_end != -1 else None

		# SSL Support Detection (SSL = 0x0800 in capabilities)
		ssl_supported = bool(capabilities & 0x0800)

		result.update({
			"success": True,
			"version": server_version,
			"connection_id": conn_id,
			"capabilities": hex(capabilities),
			"charset": charset,
			"plugin": plugin_name,
			"ssl_supported": ssl_supported,
			"output": f"MySQL {server_version}, charset {charset}, plugin {plugin_name}"
		})

		sock.close()

	except socket.timeout:
		result.update({"success": False})
	except ConnectionRefusedError:
		result.update({"success": False})
	except Exception as e:
		result.update({"success": False})

	return result
