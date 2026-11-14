# The Locked Library

An AI escape room. Explore five objects, collect a key, and solve the clues to open the exit. The same room is playable through two architectures.

## Run locally

Requires Python 3.10 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app:app
```

Add your [Groq API key](https://console.groq.com/keys) to `.env` before starting the server, using a free-tier project. The default model is `openai/gpt-oss-20b`. You can change `GROQ_MODEL` to an available chat model. Restart the server after changing configuration. Keep `.env` local.

Open **http://127.0.0.1:8000**. Select **Version 1** for the LLM Game Master or **Version 2** for validated rules. Version 2 can run offline with its built-in narrator. Use **Restart** to clear the selected version's progress.

## Versions

| Version | Code | How it works |
|---|---|---|
| 1 | `v1.py`, `room.py` | The Game Master reads the transcript and decides the story and escape status. |
| 2 | `v2.py` | Python validates actions and owns the state. Groq can select an atmospheric sentence from three safe options. |

### Version 1 architecture

![Version 1 architecture](docs/architecture-v1.png)

### Version 2 architecture

![Version 2 architecture](docs/architecture-v2.png)

## Demonstrate and verify

Try `examine the desk`, then investigate the other objects. V2 accepts one action at a time using verbs such as **examine**, **try**, **take**, and **use**. The following route contains spoilers.

<details>
<summary>Full playthrough</summary>

1. Examine the desk.
2. Examine the bookshelf.
3. Try 274 on the drawer.
4. Take the brass key.
5. Use the brass key on the painting.
6. Enter 3816 at the exit.

</details>

```bash
python -m unittest discover -s tests -v
```

See the [test results](docs/tests.md), [project report](docs/report.pdf), and [demonstration](docs/demo.md). Both versions share the browser chat and use separate in-memory sessions. Restarting the process clears progress. V2 supports common command phrases and may reject paraphrases outside that grammar.

## Publish for class

The accompanying Git bundle preserves the development commits. Keep it outside the repository itself.

```bash
git clone ai-escape-room.bundle ai-escape-room
cd ai-escape-room
git remote set-url origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Create the empty GitHub repository first. Confirm the instructor can open it and submit the repository link in Teams.
