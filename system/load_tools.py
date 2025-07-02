def run():
        from tools import nmap_scan, dirsearch, subsearch, port_handler, xss_scan, open_port_finder, target_tester

        from tools.ports.ftp import ftp_info, ftp_bf, ftp_login_exploit
        from tools.ports.ssh import ssh_info, ssh_bf, ssh_login_exploit
        from tools.ports.telnet import telnet_info, telnet_bf, telnet_login_exploit
        from tools.ports.MySQL import sql_info, sql_bf, sql_login_exploit
        from tools.ports.smtp import smtp_info, smtp_bf

        from server import dbinsert_json, dbconnection, dbextract_json

        return {
                "nmap_scan": nmap_scan.run,
                "dirsearch": dirsearch.run,
		"subsearch": subsearch.run,
                "port_handler": port_handler.run,
                "xss_scan": xss_scan.run,

                "ftp_info": ftp_info.run,
                "ftp_bf": ftp_bf.run,
                "ftp_login_exploit": ftp_login_exploit.run,

                "ssh_info": ssh_info.run,
                "ssh_bf": ssh_bf.run,
                "ssh_login_exploit": ssh_login_exploit.run,

                "telnet_info": telnet_info.run,
                "telnet_bf": telnet_bf.run,
                "telnet_login_exploit": telnet_login_exploit.run,

                "sql_info": sql_info.run,
                "sql_bf": sql_bf.run,
                "sql_login_exploit": sql_login_exploit.run,

                "smtp_info": smtp_info.run,
                "smtp_bf": smtp_bf.run,

                "dbinsert_json": dbinsert_json.run,
                "dbconnection": dbconnection.run,
                "dbextract_json": dbextract_json.run,

                "open_port_finder": open_port_finder.run,
                "target_tester": target_tester.run
        }
