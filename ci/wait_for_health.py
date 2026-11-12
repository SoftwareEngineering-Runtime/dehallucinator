"""Wait until a deployed /health endpoint returns 200 (used by the Jenkins Deploy stage).

Usage: python ci/wait_for_health.py [URL] [TIMEOUT_SECONDS]
Exits 0 once /health answers {"status": "ok"}, or 1 after the timeout.
"""

import json
import sys
import time
import urllib.error
import urllib.request


def wait_for_health(url: str, timeout_s: float, interval_s: float = 2.0) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:  # nosec B310
                if response.status == 200 and json.load(response).get("status") == "ok":
                    return True
        except (urllib.error.URLError, ConnectionError, TimeoutError, ValueError):
            pass
        time.sleep(interval_s)
    return False


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/health"
    seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 120
    ok = wait_for_health(target, seconds)
    print(f"{target}: {'healthy' if ok else 'not healthy after ' + str(seconds) + ' s'}")
    sys.exit(0 if ok else 1)
