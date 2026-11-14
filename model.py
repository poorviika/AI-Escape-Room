"""Small Groq chat client with no dependency on an SDK."""
import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv

load_dotenv()


def configured():
    return bool(os.getenv("GROQ_API_KEY", "").strip())


def chat(messages):
    payload = {
        "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        "messages": messages,
        "max_completion_tokens": 512,
        "temperature": 0.2,
    }
    request = Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.environ["GROQ_API_KEY"].strip(),
        },
    )
    try:
        with urlopen(request, timeout=12) as response:
            result = json.load(response)["choices"][0]["message"]["content"]
        return result.strip() or None
    except (URLError, OSError, ValueError, KeyError, IndexError, TypeError, AttributeError):
        return None
