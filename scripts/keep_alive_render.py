#!/usr/bin/env python3
"""
Render Backend Keep-Alive Service
Pings the Render backend health endpoint every 14 minutes to prevent free-tier spinning down after 15 minutes of inactivity.
"""

import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime

# Default to environment variable or standard Render URL
RENDER_URL = os.environ.get("RENDER_BACKEND_URL", "http://127.0.0.1:8000")
PING_INTERVAL_SECONDS = 14 * 60  # 14 minutes (840 seconds)

def ping_backend(url: str) -> bool:
    health_url = url.rstrip("/") + "/api/v1/health"
    try:
        req = urllib.request.Request(
            health_url,
            headers={"User-Agent": "SpecWise-Render-KeepAlive/1.0"}
        )
        with urllib.request.urlopen(req, timeout=45) as response:
            status = response.getcode()
            body = response.read().decode("utf-8")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] SUCCESS: Pinged {health_url} -> Status {status} | {body.strip()}")
            return True
    except urllib.error.URLError as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] NOTICE: Wake-up request to {health_url} -> {e}")
        return False
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] ERROR: {e}")
        return False

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else RENDER_URL
    print(f"=== SpecWise Render Keep-Alive Service ===")
    print(f"Target URL: {target}")
    print(f"Interval: Every 14 minutes ({PING_INTERVAL_SECONDS} seconds)")
    print(f"Press Ctrl+C to stop.\n")

    # Initial immediate ping
    ping_backend(target)

    while True:
        try:
            time.sleep(PING_INTERVAL_SECONDS)
            ping_backend(target)
        except KeyboardInterrupt:
            print("\nKeep-alive service stopped.")
            sys.exit(0)

if __name__ == "__main__":
    main()
