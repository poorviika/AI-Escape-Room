const log = document.querySelector("#log");
const status = document.querySelector("#status");
const action = document.querySelector("#action");
const form = document.querySelector("form");
const buttons = [...document.querySelectorAll("button")];
let version = "v2";
let escaped = false;

function message(role, text) {
  const article = document.createElement("article");
  article.className = role;
  const name = document.createElement("strong");
  name.textContent = role === "user" ? "You" : "Game Master";
  const body = document.createElement("p");
  body.textContent = text;
  article.append(name, body);
  log.append(article);
}

function render(game) {
  escaped = game.escaped;
  log.replaceChildren();
  message("assistant", game.intro);
  for (const turn of game.history) {
    message(turn.role, turn.content.replace(/\nSTATUS: (PLAYING|ESCAPED)$/, ""));
  }
  if (escaped) status.textContent = "Escaped! Restart to play again.";
  else if (game.model_ready) status.textContent = "Model configured";
  else if (version === "v2") status.textContent = "Offline mode · Python narration";
  else status.textContent = "Version 1 needs a Groq API key. See the README.";
  log.scrollTop = log.scrollHeight;
}

async function update(path = "", body = null) {
  buttons.forEach(button => { button.disabled = true; });
  action.disabled = true;
  status.textContent = "Loading…";
  try {
    const options = body === null ? {} : {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(body),
    };
    const response = await fetch("/api/" + version + path, options);
    const result = await response.json();
    if (!response.ok) throw new Error(typeof result.detail === "string" ? result.detail : "Request failed.");
    render(result);
    return true;
  } catch (error) {
    status.textContent = error.message;
    return false;
  } finally {
    buttons.forEach(button => {
      button.disabled = false;
      if (button.dataset.version) {
        button.setAttribute("aria-pressed", button.dataset.version === version);
      }
    });
    action.disabled = escaped;
    form.querySelector("button").disabled = escaped;
  }
}

for (const button of document.querySelectorAll("[data-version]")) {
  button.addEventListener("click", () => {
    version = button.dataset.version;
    escaped = false;
    log.replaceChildren();
    action.value = "";
    update();
  });
}
document.querySelector("#restart").addEventListener("click", () => update("/restart", {}));
form.addEventListener("submit", async event => {
  event.preventDefault();
  if (await update("/turn", {action: action.value.trim()})) action.value = "";
  action.focus();
});
update();
