GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"

def run(target, port, tools, conn):
	print(f"[{port}]")

	if port == 21:
		results = {
			"info_result": None,
			"bf_result": None,
			"exploit_result": None
		}
		print(f"  \-> Port_handler running ftp_info for {target}:{port}")
		results["info_result"] = tools["ftp_info"](target, port)

		if results["info_result"]["anon_allowed"] == True:
			username, password = None, None
		else:
			print(f"  \-> Port_handler running ftp_bf for {target}:{port}")
			results["bf_result"] = tools["ftp_bf"](target, port)
			username = results["bf_result"].get("username")
			password = results["bf_result"].get("password")


		if results["bf_result"]["success"] == True or results["info_result"]["anon_allowed"] == True:
			print(f"  \-> Port_handler running ftp_login_exploit for {target}:{port}")
			results["exploit_result"] = tools["ftp_login_exploit"](target, port, username, password)

		return results

	elif port == 22:
		results = {
			"info_result": None,
			"bf_result": None,
			"exploit_result": None
		}
		print(f"  \-> Port_handler running ssh_info for {target}:{port}", end="\r")
		results["info_result"] = tools["ssh_info"](target, port)
		if results["info_result"]["success"] == False:
			print(f"  {RED}\->{RESET} Port_handler running ssh_info for {target}:{port}")
		else:
			print(f"  {GREEN}\->{RESET} Port_handler running ssh_info for {target}:{port}")

		print(f"  \-> Port_handler running ssh_bf for {target}:{port}", end="\r")
		results["bf_result"] = tools["ssh_bf"](target, port)
		if results["bf_result"]["success"] == False:
			print(f"  {GREEN}\->{RESET} Port_handler running ssh_bf for {target}:{port}")
		else:
			print(f"  {RED}\->{RESET} Port_handler running ssh_bf for {target}:{port}")

		if results["bf_result"]["success"] == True:
			username = results["bf_result"].get("username")
			password = results["bf_result"].get("password")

			print(f"  \-> Port_handler running ssh_login_exploit for {target}:{port}", end="\r")
			results["exploit_result"] = tools["ssh_login_exploit"](target, port, username, password)
			if results["exploit_result"]["success"] == False:
				print(f"  {RED}\->{RESET} Port_handler running ssh_login_exploit for {target}:{port}")
			else:
				print(f"  {GREEN}\->{RESET} Port_handler running ssh_login_exploit for {target}:{port}")


		return results

	elif port == 23:
		results = {
			"info_result": None,
			"bf_result": None,
			"exploit_result": None
		}

		print(f"  \-> Port_handler running telnet_info for {target}:{port}", end="\r")
		results["info_result"] = tools["telnet_info"](target, port)
		if results["info_result"]["success"] == False:
			print(f"  {RED}\->{RESET} Port_handler running telnet_info for {target}:{port}")
			if not "error" in results["info_result"] or results["info_result"]["error"] == None:
				del results["info_result"]
				del results["bf_result"]
				del results["exploit_result"]
			else:
				del results["bf_result"]
				del results["exploit_result"]
			return results
		else:
			print(f"  {GREEN}\->{RESET} Port_handler running telnet_info for {target}:{port}")

		if results["info_result"]["login_required"] == True:
			print(f"  \-> Port_handler running telnet_bf for {target}:{port}")
			results["bf_result"] = tools["telnet_bf"](target, port)
			if results["bf_result"]["success"] == False:
				print(f"  {RED}\->{RESET} Port_handler running telnet_bf for {target}:{port}")
			else:
				print(f"  {GREEN}\->{RESET} Port_handler running telnet_bf for {target}:{port}")
			username = results["bf_result"]["username"]
			password = results["bf_result"]["password"]

		else:
			username = None
			password = None

		if results["bf_result"]["success"] == True or results["info_result"]["login_required"] == False:
			print(f"  \-> Port_handler running telnet_login_exploit for {target}:{port}")
			results["exploit_result"] = tools["telnet_login_exploit"](target, port, username, password)
			if results["exploit_result"]["success"] == False:
				print(f"  {RED}\->{RESET} Port_handler running telnet_login_exploit for {target}:{port}")
			else:
				print(f"  {GREEN}\->{RESET} Port_handler running telnet_login_exploit for {target}:{port}")
		return results






	elif port in [25, 587, 465]:
		results = {
			"info_result": None,
			"bf_result": None
		}

		print(f"  \-> Port_handler running smtp_info for {target}:{port}", end="\r")
		results["info_result"] = tools["smtp_info"](target, port)
		if results["info_result"]["success"] == False:
			print(f" {RED} \->{RESET} Port_handler running smtp_info for {target}:{port}")
			if not "error" in results["info_result"] or results["info_result"]["error"] == None:
				del results["info_result"]
				del results["bf_result"]
			else:
				del results["bf_result"]
			return results
		else:
			print(f"  {GREEN}\->{RESET} Port_handler running smtp_info for {target}:{port}")

		print(f"  \-> Port_handler running smtp_bf for {target}:{port}", end="\r")
		results["bf_result"] = tools["smtp_bf"](target, port)
		if results["bf_result"]["success"] == False:
			print(f"  {RED}\->{RESET} Port_handler running smtp_bf for {target}:{port}")
		else:
			print(f"  {GREEN}\->{RESET} Port_handler running smtp_bf for {target}:{port}")
		username = results["bf_result"].get("username", None)
		password = results["bf_result"].get("password", None)

		#exploit with creds

		return results




	elif port == 3306:
		results = {
			"info_result": None,
			"bf_result": None,
			"exploit_result": None
		}
		print(f"  \-> Port_handler running sql_info for {target}:{port}", end="\r")
		results["info_result"] = tools["sql_info"](target, port)
		if results["info_result"]["success"] == False:
			print(f"  {RED}\->{RESET} Port_handler running sql_info for {target}:{port}")
			if not "error" in results["info_result"] or results["info_result"]["error"] == None:
				del results["info_result"]
				del results["bf_result"]
				del results["exploit_result"]
			else:
				del results["bf_result"]
				del results["exploit_result"]
			return results
		else:
			print(f"  {GREEN}\->{RESET} Port_handler running sql_info for {target}:{port}")

		if results["info_result"]["login_required"] == True:
			print(f"  \-> Port_handler running sql_bf for {target}:{port}", end="\r")
			results["bf_result"] = tools["sql_bf"](target, port)
			if results["bf_result"]["success"] == False:
				print(f"  {RED}\->{RESET} Port_handler running sql_bf for {target}:{port}")
			else:
				print(f"  {GREEN}\->{RESET} Port_handler running sql_bf for {target}:{port}")
			username = results["bf_result"].get("username")
			password = results["bf_result"].get("password")



		else:
			username, password = None, None

		if results["bf_result"]["success"] == True or results["info_result"]["login_required"] == False:
			print(f"  \-> Port_handler running sql_login_exploit for {target}:{port}", end="\r")
			results["exploit_result"] = tools["sql_login_exploit"](target, port, username, password)
			if results["exploit_result"]["success"] == False:
				print(f"  {RED}\->{RESET} Port_handler running sql_login_exploit for {target}:{port}")
			else:
				print(f"  {GREEN}\->{RESET} Port_handler running sql_login_exploit for {target}:{port}")
		return results






	elif port in [80, 443, 8080, 8443]:
		results = {
			"dirsearch_result": None,
			"subsearch_result": None,
			"XSS_result": None
		}
		protocol = "https" if port in [443, 8443] else "http"
		url = f"{protocol}://{target}:{port}"
		print(f"  \-> Port_handler running dirsearch for {url}", end="\r")

		results["dirsearch_result"] = tools["dirsearch"](url, tools, conn, port)
		dir_res = results["dirsearch_result"]

		if isinstance(dir_res, dict) and dir_res.get("success") and dir_res.get("paths"):
			print(f"  {GREEN}\->{RESET} Port_handler running dirsearch for {url}")
			'''
			print(f"  \-> Port_handler running xss_scan", end="\r")
			results["XSS_result"] = tools["xss_scan"](dir_res["paths"], tools)
			if results["XSS_result"].get("success"):
				print(f"  {GREEN}\->{RESET} Port_handler running xss_scan")
			else:
				print(f"  {RED}\->{RESET} Port_handler running xss_scan")
			'''
		else:
			print(f"  {RED}\->{RESET} Port_handler running dirsearch for {url}")

		print(f"  \-> Port_handler running subsearch for {url}", end="\r")
		results["subsearch_result"] = tools["subsearch"](url, tools, conn, port)
		sub_res = results["subsearch_result"]
		if sub_res.get("success"):
			print(f"  {GREEN}\->{RESET} Port_handler running subsearch for {url}")
		else:
			print(f"  {RED}\->{RESET} Port_handler running subsearch for {url}")

		return results


	else:
		print(f"  \-> Not handeling port {port} yet")
		return None
