import time
import requests

RENDER_URL = "https://specwise-sih26108.onrender.com"
payload = {"text": "5 HP openwell submersible pumpset for agricultural irrigation"}

latencies = []
print("Measuring 5 live public round trips against Render + Firestore...")

for i in range(5):
    t0 = time.perf_counter()
    r = requests.post(f"{RENDER_URL}/api/v1/analyze", json=payload, timeout=20)
    t1 = time.perf_counter()
    elapsed_ms = (t1 - t0) * 1000.0
    latencies.append(elapsed_ms)
    decision = r.json().get("decision")
    print(f"Roundtrip {i+1}: {elapsed_ms:.1f} ms (HTTP {r.status_code}, Decision: {decision})")
    time.sleep(0.5)

print("--- LATENCY SUMMARY ---")
print(f"First request: {latencies[0]:.1f} ms")
print(f"Subsequent requests: {[f'{x:.1f} ms' for x in latencies[1:]]}")
print(f"Min: {min(latencies):.1f} ms")
print(f"Max: {max(latencies):.1f} ms")
print(f"Average: {sum(latencies)/len(latencies):.1f} ms")
