# STEM Academy — Playful AI with IoT

Workshop materials for **"Why Playful AI with IoT and Generative AI?"** —
a DIKU / Center for Digital Education seminar series by Daniel Spikol on
didactic transposition and AI literacy, using micro:bit, Teachable Machine,
and Claude as hands-on tools. See [ABOUT.md](ABOUT.md) for the background
and motivation behind the workshops.

## Repo layout

| Path | What it is |
|---|---|
| [`seminars/`](seminars/) | Marp slide decks for each session (intro, AI fluency kickoff, didactic transposition) |
| [`org_notes/`](org_notes/) | Planning notes and drafts behind the seminars |
| [`images/`](images/) | Images used across the slide decks |
| [`backend/`](backend/) + [`frontend/`](frontend/) | Micro:bit → Claude AI bridge: a Flask backend that forwards prompts from a micro:bit-connected browser to the Claude API, deployed on PythonAnywhere |
| [`serial_stream/`](serial_stream/) | Live micro:bit sensor dashboard (light, sound, acceleration) over USB — **working** |
| [`bluetooth_stream/`](bluetooth_stream/) | Same dashboard, attempted over Bluetooth — kept for reference; doesn't work on this hardware (see that folder's README for why) |
| [`dev/`](dev/) | Device-side scripts and reference `.hex` files (MicroPython AI bridge, Teachable Machine firmware, Bluetooth config notes) |

## Quickstarts

- **AI bridge** (micro:bit asks Claude a yes/no question over USB): see
  [`backend/README.md`](backend/README.md) and
  [`frontend/README.md`](frontend/README.md).
- **Live sensor dashboard**: see [`serial_stream/README.md`](serial_stream/README.md) —
  flash the MakeCode script there, plug the micro:bit in over USB, serve the
  page, connect.
- **Teachable Machine + micro:bit** (no code in this repo, browser-based):
  see [`seminars/microbit_ai.md`](seminars/microbit_ai.md) for setup steps.

Each subfolder's own README has the full setup/run instructions for that
piece — this file is just the map.
