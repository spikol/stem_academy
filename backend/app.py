"""
Micro:bit AI Bridge — Flask backend for PythonAnywhere.

Accepts a prompt from a micro:bit-connected browser/client, forwards it to
the Claude API, and returns a short response for the micro:bit to display.

Configuration is read entirely from environment variables — never hardcode
the API key here. On PythonAnywhere, set these either in the WSGI config
file (see wsgi_pythonanywhere.py) or in a `.env` file that is NOT committed
to git (see .env.example).

Required:
  ANTHROPIC_API_KEY      Your Anthropic API key.

Optional:
  BRIDGE_SHARED_SECRET    If set, callers must send it as the
                           X-Bridge-Key header. Prevents randoms on the
                           internet from burning your API budget.
  ALLOWED_ORIGIN           CORS origin to allow (default: "*").
  CLAUDE_MODEL             Model id (default: claude-haiku-4-5-20251001).
  MAX_TOKENS               Cap on response length (default: 60).
"""
import os
import re
import time

from anthropic import Anthropic, APIStatusError
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()  # no-op if backend/.env doesn't exist (e.g. on PythonAnywhere)

app = Flask(__name__)

ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")
CORS(app, origins=[ALLOWED_ORIGIN] if ALLOWED_ORIGIN != "*" else "*")

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not API_KEY:
    raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set")

client = Anthropic(api_key=API_KEY)

SHARED_SECRET = os.environ.get("BRIDGE_SHARED_SECRET")
MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "60"))
MAX_PROMPT_CHARS = 500

MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.5

LEADING_YES_NO = re.compile(r"^(yes|no)\b[\s,.:\-—]*", re.IGNORECASE)


def parse_verdict(reply):
    """Return (verdict, remaining_text). verdict is True/False/None
    depending on whether the reply starts with Yes/No; remaining_text has
    that leading word stripped off, since the caller already knows the
    verdict from the boolean."""
    match = LEADING_YES_NO.match(reply)
    if not match:
        return None, reply
    verdict = match.group(1).lower() == "yes"
    return verdict, reply[match.end():].strip()


@app.route("/ask-ai", methods=["POST"])
def ask_ai():
    if SHARED_SECRET and request.headers.get("X-Bridge-Key") != SHARED_SECRET:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()

    if not prompt:
        return jsonify({"error": "missing prompt"}), 400
    if len(prompt) > MAX_PROMPT_CHARS:
        prompt = prompt[:MAX_PROMPT_CHARS]

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"{prompt} If this is a yes/no question, start your "
                            "answer with 'Yes' or 'No'. Keep the whole answer "
                            "extremely short (under 60 characters)."
                        ),
                    }
                ],
            )
            reply = "".join(
                block.text for block in message.content if block.type == "text"
            ).strip()
            verdict, reason = parse_verdict(reply)
            return jsonify({"response": reason, "verdict": verdict})
        except APIStatusError as e:
            last_error = e
            if e.status_code == 429 and attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return jsonify({"error": str(e)}), e.status_code
        except Exception as e:
            last_error = e
            break

    return jsonify({"error": str(last_error)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
