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
        else:
            server = smtplib.SMTP(target, port, timeout=timeout)

        banner = server.sock.getsockname()  # won't give real banner, but shows connection success

        code, msg = server.ehlo()
        ehlo_resp = "\n".join(server.esmtp_features.keys())

        result.update({
            "success": True,
            "banner": msg.decode() if isinstance(msg, bytes) else str(msg),
            "ehlo_response": ehlo_resp,
            "starttls_supported": "starttls" in server.esmtp_features,
            "output": f"{msg.decode() if isinstance(msg, bytes) else msg}\n{ehlo_resp}"
        })

        server.quit()

    except (socket.timeout, ConnectionRefusedError) as e:
        pass
        #result["error"] = f"Connection failed: {str(e)}"
    except Exception as e:
        pass
        #result["error"] = str(e)

    return result
