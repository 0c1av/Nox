def run(target, port, tools):

	if port == 21:
		results = {
			"info_result": None,
			"bf_result": None,
			"exploit_result": None
		}
		print(f"  \-> Port_handler running ftp_info for {target}:{port}")
		#get info
		results["info_result"] = tools["ftp_info"](target, port)

		if results["info_result"]["anon_allowed"] == True:
			print(f"  \-> Port_handler running ftp_exploit for {target}:{port}")
			username, password = None, None
			#exploit ftp if anon
			results["exploit_result"] = tools["ftp_login_exploit"](target, port, username, password)

		#bruteforce ftp
		print(f"  \-> Port_handler running ftp_bf for {target}:{port}")
		results["bf_result"] = tools["ftp_bf"](target, port)

		if results["bf_result"]["success"] == True:
			username, password = results["bf_result"]["username"], results["bf_result"]["password"]
			#exploit ftp if creds
			results["exploit_result"] = tools["ftp_login_exploit"](target, port, username, password)

		return results

	elif port == 22:
		results = {
			"info_result": None
		}
		print(f"  \-> Port_handler running ssh_info for {target}:{port}")
		results["info_result"] = tools["ssh_info"](target, port)
		return results

	elif port in [80, 443, 8080, 8443]:
                protocol = "https" if port in [443, 8443] else "http"
                url = f"{protocol}://{target}:{port}"
                print(f"  \-> Port_handler running dirsearch for {url}")
                result = tools["dirsearch"](url)
                return result

	else:
		print(f"  \-> Not handeling port {port} yet")
		return None
