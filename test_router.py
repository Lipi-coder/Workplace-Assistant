import json
import time
import urllib.request
import urllib.error

questions = [
    "How long is the probation period?",
    "Who is on the payroll?",
    "How many employees do we have, and how many casual leave days does each get?",
    "Delete all employees from the database.",
    "Can employees carry over unused leave?",
]

for q in questions:
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/ask",
        data=json.dumps({"question": q}).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = json.loads(r.read().decode())
            print(f"\nQ: {q}\n   route={body['route']}\n   answer={body['answer']}")
    except urllib.error.HTTPError as e:
        print(f"\nQ: {q}\n   ERROR {e.code}: {e.read().decode()}")
    time.sleep(5)   # stay under Groq's 30 requests per minute