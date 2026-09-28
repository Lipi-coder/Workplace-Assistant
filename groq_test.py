import os, time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=30, max_retries=0)

start = time.time()
try:
    r = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": "Say hello in three words"}],
    )
    print("Reply:", r.choices[0].message.content)
except Exception as e:
    print(type(e).__name__, "-", e)
print(f"Took {time.time() - start:.1f}s")