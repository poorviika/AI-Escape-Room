import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv

load_dotenv()


def configured():
    return bool(os.getenv("GROQ_API_KEY", "").strip())


def chat(messages):
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        return None

    payload = {
        "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        "messages": messages,
        "max_completion_tokens": 2048,
        "temperature": 0.2,
    }
    request = Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "TheLockedLibrary/1.0",
            "Authorization": f"Bearer {key}",
        },
    )

    try:
        with urlopen(request, timeout=12) as response:
            content = json.load(response)["choices"][0]["message"]["content"]
        return content.strip() or None if isinstance(content, str) else None
    except HTTPError as error:
        print(f"Groq request failed: HTTP {error.code}")
        return None
    except (URLError, OSError, ValueError, KeyError, IndexError, TypeError):
        return None