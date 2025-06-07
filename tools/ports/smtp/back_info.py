import smtplib
import socket

def run(target, port=25, timeout=15):
	result = {
		"success": False,
		"output": "",
		"banner": None,
		"ehlo_response": None,
		"starttls_supported": False,
		"error": None
	}

	try:
		if port == 465:
			server = smtplib.SMTP_SSL(target, port, timeout=timeout)
			server.ehlo()
		else:
			server = smtplib.SMTP(target, port, timeout=timeout)
			server.ehlo()

			# Only try STARTTLS if it's port 587
			if port == 587:
				code, resp = server.starttls()
				server.ehlo()

		banner = server.sock.recv(1024).decode(errors='ignore').strip()
		ehlo_resp = "\n".join(server.esmtp_features.keys())

		result.update({
			"success": True,
			"banner": banner,
			"ehlo_response": ehlo_resp,
			"starttls_supported": "starttls" in server.esmtp_features,
			"output": f"{banner}\n{ehlo_resp}"
		})

		server.quit()

	except (socket.timeout, ConnectionRefusedError) as e:
		result["error"] = str(e)
	except Exception as e:
		result["error"] = str(e)

	return result
