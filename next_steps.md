# Next steps — Micro:bit AI Bridge

Not ready to deploy yet. Notes to pick back up later.

## Before deploying

- [ ] Swap `SERVER_URL` in `frontend/index.html` from the local
      `http://127.0.0.1:5050/ask-ai` to the real PythonAnywhere URL (the
      commented-out line right above it).
- [ ] Confirm PythonAnywhere plan — the free tier can't reach
      `api.anthropic.com` (outbound domains are whitelisted). Need at
      least the paid "Hacker" tier. See `backend/README.md`.
- [ ] Rotate `BRIDGE_SHARED_SECRET` before a real class uses this — the
      current one has been visible in this session's logs.
- [ ] Set a hard spending limit on the Anthropic account (classroom-scale
      usage guardrail, on top of the app-level prompt/token caps already
      in place).

## Open to reconsider later

- The device/frontend protocol only sends a question index (`Q<n>`), not
  free text, and sends each request 3x with a debounce on the receiving
  end — a workaround for occasional byte corruption on this hardware's
  USB serial at both 115200 and 9600 baud (root cause never fully
  isolated: ruled out browser/JS, ruled out looping-animation interrupt
  contention, ruled out any lit LED during transmission; settled on lower
  baud + redundant sends + tolerant parsing as the practical fix). Worth
  retrying with a different USB cable/port sometime to see if the
  underlying cause was just a marginal cable.
- Only 5 preset questions are wired up (`QUESTIONS` list, duplicated in
  both `dev/microbit_ai_bridge.py` and `frontend/index.html` — must stay
  in sync if either changes).
- No MicroPython code exists yet to run this from the actual card-deck
  workshop flow beyond button A/B cycling — revisit once the activity
  format for using this bridge with the class is decided.
