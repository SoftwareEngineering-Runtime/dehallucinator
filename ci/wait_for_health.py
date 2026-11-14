"""Wait until the deployed API answers /health (used by the Jenkins Deploy stage).

Usage: python ci/wait_for_health.py [PORT] [TIMEOUT_SECONDS]
Only a port is accepted; the URL is always http://127.0.0.1:<port>/health, so the script can
never be pointed at another host. Exits 0 once /health answers {"status": "ok"}, or 1 after
the timeout.
"""

import json
import sys
import time
import urllib.error
import urllib.request


def health_url(port: int) -> str:
    """The only URL this script ever requests."""
    if not 1 <= port <= 65535:
        raise ValueError(f"port must be between 1 and 65535, got {port}")
    return f"http://127.0.0.1:{port}/health"


def wait_for_health(port: int, timeout_s: float, interval_s: float = 2.0) -> bool:
    url = health_url(port)
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:  # nosec B310: fixed local URL
                if response.status == 200 and json.load(response).get("status") == "ok":
                    return True
        except (urllib.error.URLError, ConnectionError, TimeoutError, ValueError):
            pass
        time.sleep(interval_s)
    return False


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 120
    ok = wait_for_health(port, seconds)
    print(f"{health_url(port)}: {'healthy' if ok else 'not healthy after ' + str(seconds) + ' s'}")
    sys.exit(0 if ok else 1)
