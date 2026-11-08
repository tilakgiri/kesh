import subprocess
import re

def check_internet(host="8.8.8.8"):

    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "1500", host],
            capture_output=True,
            text=True,
            timeout=3
        )

        output = result.stdout

        if result.returncode == 0:

            match = re.search(
                r"time[=<]\s*(\d+)\s*ms",
                output,
                re.IGNORECASE
            )

            latency = float(match.group(1)) if match else 0.5

            return {
                "connected": True,
                "latency": latency,
                "status": "Online"
            }

        return {
            "connected": False,
            "latency": None,
            "status": "Offline"
        }

    except subprocess.TimeoutExpired:
        return {
            "connected": False,
            "latency": None,
            "status": "Timeout"
        }

    except Exception as error:
        return {
            "connected": False,
            "latency": None,
            "status": str(error)
        }
