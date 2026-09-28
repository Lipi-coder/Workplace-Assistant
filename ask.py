import json
import sys
import time
import urllib.request
import urllib.error

route = sys.argv[1] if len(sys.argv) > 1 else "chat"
question = sys.argv[2] if len(sys.argv) > 2 else "How many employees are there in total?"

url = f"http://127.0.0.1:8000/api/{route}"
data = json.dumps({"question": question}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

start = time.time()
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        print("Status:", r.status)
        print(r.read().decode())
except urllib.error.HTTPError as e:
    print("Status:", e.code)
    print(e.read().decode())
except Exception as e:
    print("Failed:", repr(e))
print(f"Took {time.time() - start:.1f}s")