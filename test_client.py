import urllib.request
import json
import ssl

print("Connecting to Intelligent SQL Query Agent...")

url = 'http://127.0.0.1:8000/api/chat'
data = json.dumps({"question": "How many employees are there in total?"}).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

try:
    # Use unverified context for local dev
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    with urllib.request.urlopen(req, context=ctx) as response:
        result = json.loads(response.read().decode())
        print("\\n=== Response ===")
        print(result["answer"])
        print("\\n=== Query Executed ===")
        print(result.get("query_executed", "None"))
except Exception as e:
    print(f"Error connecting to agent: {e}")
