"""Version 2 decides every state transition with explicit Python rules."""
import re

from model import chat

OBJECTS = ("desk", "bookshelf", "drawer", "painting", "exit door")
DRAWER_CODE = "274"
EXIT_CODE = "3816"
HELP = (
    "Try examining one object, entering a code on a lock, taking the brass key, "
    "using the key on the painting, or checking inventory."
)
FRAMING = {
    "quiet": "The room falls quiet.",
    "lamp": "The lamp flickers.",
    "echo": "A faint echo passes through the library.",
}


def new_state():
    return {
        "available_objects": list(OBJECTS),
        "discovered": [],
        "inventory": [],
        "drawer_open": False,
        "painting_open": False,
        "escaped": False,
    }


def identify(text):
    aliases = {"exit": "exit door", "door": "exit door", "shelf": "bookshelf"}
    matches = re.findall(r"\b(?:desk|bookshelf|shelf|drawer|painting|exit|door)\b", text)
    objects = {aliases.get(match, match) for match in matches}
    return next(iter(objects)) if len(objects) == 1 else None


def discover(state, clue):
    if clue not in state["discovered"]:
        state["discovered"].append(clue)


def examine(state, target):
    if target == "desk":
        discover(state, "desk note")
        return "The desk note says: Read the marked book numbers from left to right."
    if target == "bookshelf":
        discover(state, "marked books")
        return "The marked books show 2, 7, 4 from left to right."
    if target == "drawer" and state["drawer_open"]:
        return "The drawer is open. Its note says: Read the digits behind the painting in reverse."
    if target == "drawer":
        return "The drawer has a three-digit lock."
    if target == "painting" and state["painting_open"]:
        return "The open compartment shows 6, 1, 8, 3."
    if target == "painting":
        return "Behind the frame is a small compartment secured with a key."
    if target == "exit door":
        return "The exit is locked with a four-digit keypad."
    return "Choose one object in the room to examine."


def try_code(state, target, code):
    if target == "drawer":
        if state["drawer_open"]:
            return "The drawer is already open."
        if code != DRAWER_CODE:
            return "The drawer stays locked. The combination is incorrect."
        state["drawer_open"] = True
        discover(state, "drawer note")
        return (
            "The drawer opens. Inside is a brass key and a note: "
            "Read the digits behind the painting in reverse."
        )
    if target == "exit door":
        if not state["painting_open"]:
            return "The exit stays locked. Investigate the library first."
        if code != EXIT_CODE:
            return "The keypad rejects the code. The exit stays locked."
        state["escaped"] = True
        return "The lock clicks. The exit opens and you escape the library!"
    return "Specify one lock: the drawer or the exit door."


def apply_action(state, action):
    if state["escaped"]:
        return "You have already escaped. Restart to play again."
    text = action.lower().strip().rstrip(".!?")
    text = re.sub(r"^(?:please |i want to |i would like to |i )", "", text)
    target = identify(text)
    if text in {"inventory", "check inventory", "show inventory"}:
        items = ", ".join(state["inventory"]) or "empty"
        return f"Inventory: {items}."
    if re.fullmatch(r"(?:take|collect|pick up|grab) (?:the )?(?:brass )?key", text):
        if not state["drawer_open"]:
            return "You haven't found a key to collect."
        if "brass key" in state["inventory"]:
            return "You already have the brass key."
        state["inventory"].append("brass key")
        return "You collect the brass key."
    if re.fullmatch(r"(?:use (?:the )?(?:brass )?key on|unlock) (?:the )?painting(?: with (?:the )?(?:brass )?key)?", text):
        if "brass key" not in state["inventory"]:
            return "You need to collect the brass key first."
        if state["painting_open"]:
            return "The compartment is already open. The digits are 6, 1, 8, 3."
        state["painting_open"] = True
        discover(state, "painting digits")
        return "The brass key opens the compartment. Inside are the digits 6, 1, 8, 3."
    if re.fullmatch(
        r"(?:try|enter|use|submit)(?: (?:the )?code)? [0-9]+ (?:on|in|at|for) "
        r"(?:the )?(?:locked )?(?:drawer|exit(?: door)?|door)", text
    ):
        return try_code(state, target, re.search(r"[0-9]+", text).group())
    if re.fullmatch(r"(?:examine|inspect|look at|check|investigate) .+", text):
        object_name = re.sub(
            r"^(?:examine|inspect|look at|check|investigate) (?:the )?(?:locked )?", "", text
        )
        if object_name in {*OBJECTS, "shelf", "exit", "door"}:
            return examine(state, target)
        return "That object is not in the room. " + HELP
    return "That action is unavailable. " + HELP


def narrate(outcome, call_model=chat):
    label = call_model([
        {"role": "system", "content": (
            "Select a mood for this validated library game outcome. "
            "Return exactly one label: quiet, lamp, or echo."
        )},
        {"role": "user", "content": outcome},
    ])
    framing = FRAMING.get((label or "").strip().lower())
    return f"{framing} {outcome}" if framing else outcome
