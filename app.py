"""Local web interface for the two escape-room versions."""
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import model
import v1
import v2
from room import INTRO

ROOT = Path(__file__).resolve().parent
app = FastAPI()
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
sessions = {}


class Turn(BaseModel):
    action: str = Field(min_length=1, max_length=500)


def session(request, version):
    if version not in {"v1", "v2"}:
        raise HTTPException(404, "Unknown game version")
    token = request.cookies.get("escape_session")
    if token not in sessions:
        token = uuid4().hex
        sessions[token] = {}
    games = sessions[token]
    if version not in games:
        games[version] = fresh_game()
    return token, games


def fresh_game():
    return {"history": [], "escaped": False, "state": v2.new_state()}


def view(token, game):
    response = JSONResponse({
        "intro": INTRO,
        "history": game["history"],
        "escaped": game["escaped"],
        "model_ready": model.configured(),
    })
    response.set_cookie("escape_session", token, httponly=True, samesite="strict")
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/")
def index():
    return FileResponse(ROOT / "templates" / "index.html")


@app.get("/api/{version}")
def get_game(request: Request, version: str):
    token, games = session(request, version)
    return view(token, games[version])


@app.post("/api/{version}/restart")
def restart(request: Request, version: str):
    token, games = session(request, version)
    games[version] = fresh_game()
    return view(token, games[version])


@app.post("/api/{version}/turn")
def turn(request: Request, version: str, body: Turn):
    token, games = session(request, version)
    game = games[version]
    action = body.action.strip()
    if not action:
        raise HTTPException(422, "Type an action first.")
    if game["escaped"]:
        return view(token, game)
    if version == "v1":
        if not model.configured():
            raise HTTPException(503, "Set GROQ_API_KEY in .env and restart the server to play V1.")
        result = v1.play(game["history"], action)
        if result is None:
            raise HTTPException(502, "The model did not respond. Check your key and model or retry.")
        narrative, game["escaped"] = result
        status = "ESCAPED" if game["escaped"] else "PLAYING"
        replay = f"{narrative}\nSTATUS: {status}"
    else:
        outcome = v2.apply_action(game["state"], action)
        narrative = v2.narrate(outcome) if model.configured() else outcome
        game["escaped"] = game["state"]["escaped"]
        replay = narrative
    game["history"].extend([
        {"role": "user", "content": action},
        {"role": "assistant", "content": narrative},
    ])
    # V1 sends only its own turn history and status back to the Game Master.
    if version == "v1":
        game["history"][-1]["content"] = replay
    return view(token, game)
