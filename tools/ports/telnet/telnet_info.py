import telnetlib
import socket
import time

def run(target, port=23, timeout=5):
    result = {
        "success": False,
        "output": "",
        "login_required": False,
        "error": None
    }

    try:
        tn = telnetlib.Telnet(target, port, timeout=timeout)

        tn.sock.settimeout(1)  # set socket read timeout shorter than total timeout
        total_data = []
        start_time = time.time()

        while True:
            try:
                chunk = tn.read_eager()
                if chunk:
                    total_data.append(chunk)
                else:
                    # no data available now, break if timeout elapsed
                    if time.time() - start_time > timeout:
                        break
                    time.sleep(0.1)
            except EOFError:
                break
            except socket.timeout:
                # No data currently, break if timeout elapsed
                if time.time() - start_time > timeout:
                    break

        output = b"".join(total_data).decode("utf-8", errors="ignore")
        result["output"] = output.strip()

        if any(keyword in output.lower() for keyword in ["login", "username", "password"]):
            result["login_required"] = True

        result["success"] = True
        tn.close()

    except socket.timeout:
        pass
        #result["error"] = "Connection timed out"
    except ConnectionRefusedError:
        pass
        #result["error"] = "Connection refused"
    except Exception as e:
        pass
        #result["error"] = f"{type(e).__name__}: {str(e)}"

    return result
