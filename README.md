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
| [`bluetooth_stream/`](bluetooth_stream/) | Live micro:bit sensor dashboard (acceleration, temperature, buttons) over Bluetooth, using the official micro:bit Bluetooth Profile services — **working** |
| [`microbit_p5/`](microbit_p5/) | Micro:bit → Claude narration: temperature/motion tiles plus a narration panel where Claude improvises in character, with the two physical buttons switching persona live |
| [`dev/`](dev/) | Device-side scripts and reference `.hex` files (MicroPython AI bridge, Teachable Machine firmware, Bluetooth config notes) |

## Quickstarts

- **AI bridge** (micro:bit asks Claude a yes/no question over USB): see
  [`backend/README.md`](backend/README.md) and
  [`frontend/README.md`](frontend/README.md).
- **Live sensor dashboard**: see [`serial_stream/README.md`](serial_stream/README.md)
  (USB) or [`bluetooth_stream/README.md`](bluetooth_stream/README.md)
  (Bluetooth) — flash the matching MakeCode script, serve the page, connect.
- **Micro:bit mood narrator**: see [`microbit_p5/README.md`](microbit_p5/README.md) —
  Bluetooth-connected dashboard plus a Claude narration panel, persona
  switched by the board's buttons.
- **Teachable Machine + micro:bit** (no code in this repo, browser-based):
  see [`seminars/Seminar_3_microbit_ai.md`](seminars/Seminar_3_microbit_ai.md)
  for setup steps.

Each subfolder's own README has the full setup/run instructions for that
piece — this file is just the map.
