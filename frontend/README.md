# Micro:bit AI Bridge — frontend

Single static page implementing Option A from
[`../dev/microbit_ai_bridge_options.md`](../dev/microbit_ai_bridge_options.md):
students connect their micro:bit over USB using the browser's Web Serial
API, and prompts are relayed to your PythonAnywhere backend.

## Before it works

Edit the two constants at the top of the `<script>` block in `index.html`:

```js
const SERVER_URL = "https://your-username.pythonanywhere.com/ask-ai";
const BRIDGE_KEY = "REPLACE-ME"; // must match BRIDGE_SHARED_SECRET on the server
```

Set `BRIDGE_KEY` to `""` if you didn't set `BRIDGE_SHARED_SECRET` on the
backend. Otherwise the two values must match exactly — the key isn't a
real secret once it's sitting in a page anyone in the room can view-source,
it's just there to stop random internet traffic from hitting your billed
endpoint, not to stop your own students.

## Browser support

Web Serial API only — **desktop Chrome or Edge**. Firefox and Safari don't
support it; there's no mobile fallback for the same reason.

## Hosting

Web Serial requires a "secure context": HTTPS, or `localhost` for local
testing. Easiest options:

- **GitHub Pages** — push `frontend/` to a repo, enable Pages on it, done.
  Free HTTPS.
- **Local testing** — `cd frontend && python3 -m http.server 8000`, open
  `http://localhost:8000`. Works because `localhost` counts as secure even
  over plain HTTP.

## What the micro:bit side needs to send

At 9600 baud (see `dev/microbit_ai_bridge.py` for why — longer messages at
the default 115200 baud were seeing occasional dropped characters on this
hardware), the page watches for serial lines matching `Q<index>`, e.g.:

```
Q0
```

`index` is a position into the `QUESTIONS` array defined in `index.html`,
which must exactly match the `QUESTIONS` list in
`dev/microbit_ai_bridge.py` — the device only ever sends the index, never
the question text itself, to keep messages short.

The page writes the reply back over serial as a single line prefixed
`Y:`/`N:`/`?:` (see `verdictMarker` in `index.html`), so your MicroPython
program should read a line at a time.
