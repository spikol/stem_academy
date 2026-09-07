# Micro:bit AI Bridge — PythonAnywhere deployment

Flask backend that receives prompts relayed from micro:bit-connected
browsers/clients and forwards them to the Claude API. See
[`../dev/microbit_ai_bridge_options.md`](../dev/microbit_ai_bridge_options.md)
for the overall architecture.

## Before you deploy

The API key you shared earlier in chat is exposed and must be treated as
compromised — **revoke it in the Anthropic console and generate a new one**
before using any of this. Never paste a real key into a file that gets
committed to git; `.env` and this backend's other secret-bearing files are
already gitignored, but double check with `git status` before committing.

## PythonAnywhere-specific notes

- **Outbound internet access is whitelisted on free accounts.** A free
  PythonAnywhere account can only make outbound HTTPS requests to a
  specific list of allowed domains, and `api.anthropic.com` is not on it.
  You need at least a paid ("Hacker" tier or above) account for this
  backend to reach the Claude API at all.
- PythonAnywhere doesn't run `flask run` / `app.run()` directly — it serves
  your app through a WSGI file it generates for you. See
  `wsgi_pythonanywhere.py` in this folder for what to paste into it.
- Free/paid accounts differ in how you set environment variables:
  - **Paid accounts**: Web tab → "Environment variables" section. Set
    `ANTHROPIC_API_KEY`, `BRIDGE_SHARED_SECRET`, etc. there directly —
    nothing touches a file, nothing touches git.
  - **Free/no env-var UI**: set them at the top of the WSGI config file
    PythonAnywhere generates (Web tab → "WSGI configuration file" link),
    as shown in `wsgi_pythonanywhere.py`. That file lives only on the
    PythonAnywhere server, outside this git repo.

## Setup steps

1. On PythonAnywhere, open a Bash console and clone or upload this repo
   (or just the `backend/` folder).
2. Create a virtualenv and install dependencies:
   ```bash
   mkvirtualenv --python=python3.11 bridge-venv
   pip install -r backend/requirements.txt
   ```
3. Go to the **Web** tab → **Add a new web app** → manual configuration →
   pick the same Python version → point the virtualenv path at
   `bridge-venv`.
4. Open the generated WSGI configuration file and set it up per
   `wsgi_pythonanywhere.py` in this folder — set your real
   `ANTHROPIC_API_KEY` and a `BRIDGE_SHARED_SECRET` there (or in the Web
   tab's environment variables section on paid plans), and point
   `sys.path` at wherever you uploaded `backend/`.
5. Set **Source code** / **Working directory** on the Web tab to the
   `backend/` folder.
6. Hit **Reload**.
7. Test:
   ```bash
   curl https://<your_username>.pythonanywhere.com/health
   curl -X POST https://<your_username>.pythonanywhere.com/ask-ai \
     -H "Content-Type: application/json" \
     -H "X-Bridge-Key: <your BRIDGE_SHARED_SECRET>" \
     -d '{"prompt": "Is a thermostat AI?"}'
   ```

## Local development

```bash
cd backend
cp .env.example .env   # fill in your own key, .env is gitignored
pip install -r requirements.txt python-dotenv
python -c "from dotenv import load_dotenv; load_dotenv()" # or use flask's built-in .env loading
python app.py
```

## Endpoint

`POST /ask-ai`
- Headers: `X-Bridge-Key: <BRIDGE_SHARED_SECRET>` (only required if that
  env var is set on the server — recommended for a public classroom URL,
  so random internet traffic can't burn your API budget).
- Body: `{"prompt": "..."}`
- Response: `{"response": "..."}` or `{"error": "..."}`

## Budget/abuse guardrails already in place

- `BRIDGE_SHARED_SECRET` gate on the endpoint (optional but recommended).
- Prompt length capped at 500 characters server-side.
- Response length capped via `MAX_TOKENS` (default 60).
- Basic exponential backoff retry on Claude API `429` responses.

Still set a hard spending limit in the Anthropic console — none of the
above is a substitute for that.
