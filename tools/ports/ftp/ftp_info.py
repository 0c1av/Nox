from ftplib import FTP, all_errors

def run(target, port):
    result = {
        "banner": None,
        "anon_allowed": False,
        "writable": False,
        "ftps_supported": False,
        "features": [],
        "directory_traversal_possible": False,
        "commands": []
    }

    try:
        ftp = FTP()
        ftp.connect(target, port, timeout=5)
        result["banner"] = ftp.getwelcome()

        # Check anonymous login
        try:
            ftp.login()
            result["anon_allowed"] = True
        except all_errors:
            pass

        # Check writable by uploading a small file (if logged in)
        try:
            ftp.storbinary('STOR test.txt', open('/dev/null', 'rb'))
            result["writable"] = True
            ftp.delete('test.txt')
        except all_errors:
            result["writable"] = False

        # Check FTPS support (AUTH TLS)
        try:
            resp = ftp.sendcmd('AUTH TLS')
            if '234' in resp:
                result["ftps_supported"] = True
        except all_errors:
            pass

        # List supported features (FEAT)
        try:
            features = ftp.sendcmd('FEAT')
            result["features"] = features.splitlines()
        except all_errors:
            pass

        # List commands (HELP)
        try:
            help_resp = ftp.sendcmd('HELP')
            result["commands"] = help_resp.splitlines()
        except all_errors:
            pass

        # Check directory traversal (non-destructive)
        try:
            # Just attempt a safe stat or cwd to parent directory
            ftp.cwd('..')
            result["directory_traversal_possible"] = True
        except all_errors:
            result["directory_traversal_possible"] = False

        ftp.quit()
    except all_errors as e:
        result["error"] = str(e)

    return result
