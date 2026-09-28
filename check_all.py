"""Tests every route of the merged app once. Start uvicorn first, then run: python check_all.py"""
import json
import time
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"

# label, method, path, question, text the reply must contain (lowercase), or None
CHECKS = [
    ("GET  /", "GET", "/", None, "online"),
    ("GET  /app (chat page)", "GET", "/app", None, "<html"),
    ("POST /api/reload-docs", "POST", "/api/reload-docs", None, "reloaded"),
    ("POST /api/chat (database)", "POST", "/api/chat",
     "Which department has the highest average salary?", "engineering"),
    ("POST /api/docs-chat (handbook)", "POST", "/api/docs-chat",
     "How many days of casual leave do employees get?", "12"),
    ("POST /api/ask -> should route to sql", "POST", "/api/ask",
     "Which department has the highest average salary?", '"route":"sql"'),
    ("POST /api/ask -> should route to docs", "POST", "/api/ask",
     "How many days of casual leave do employees get?", '"route":"docs"'),
]


def call(method, path, question):
    url = BASE + path
    if question is not None:
        data = json.dumps({"question": question}).encode()
    elif method == "POST":
        data = b""
    else:
        data = None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return None, repr(e)


passed = 0
for label, method, path, question, expect in CHECKS:
    status, body = call(method, path, question)
    ok = status == 200 and expect in body.lower()
    passed += ok
    print(f"\n{'PASS' if ok else 'FAIL'}  {label}   (status {status})")
    print("      " + body.replace("\n", " ")[:220])
    if question is not None:
        time.sleep(4)   # stay under Groq's 30 requests per minute

print(f"\n{passed} of {len(CHECKS)} checks passed")