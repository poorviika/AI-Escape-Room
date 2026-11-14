"""Version 1 delegates narration and game progress to the model."""
from model import chat
from room import WORLD


def play(history, action, call_model=chat):
    messages = [
        {"role": "system", "content": "You are the Game Master.\n" + WORLD},
        *history,
        {"role": "user", "content": action},
    ]
    answer = call_model(messages)
    if not answer:
        return None
    narrative, marker, status = answer.rpartition("\nSTATUS:")
    if marker and status.strip() in {"PLAYING", "ESCAPED"} and narrative.strip():
        return narrative.strip(), status.strip() == "ESCAPED"
    return answer, False
