# Micro:bit Mood Narrator

Temperature and motion stream live from a micro:bit over Bluetooth as stat
tiles with sparklines (same visual design as
[`../bluetooth_stream/`](../bluetooth_stream/)); Claude narrates the room
in character, and the two physical buttons switch which character is
narrating — **Button A** for a nervous houseplant, **Button B** for a
small monkey.

This started as a retool of [Daniel's webcam/mic "world as data" p5.js sketch](https://editor.p5js.org/spikol/sketches/PZv1AgE79)
onto micro:bit sensors, then got rebuilt a second time onto
`bluetooth_stream`'s dashboard design — it's a single self-contained
`index.html` now (no p5.js library, no separate sketch.js/style.css), same
pattern as the other pages in this repo.

## How it works

- **Temperature** and **Motion** (frame-to-frame change in the
  acceleration vector) are read continuously over Bluetooth and shown as
  sparkline tiles.
- **Persona** is a third tile — not a sensor reading, but the currently
  active character, switched by pressing a button on the micro:bit itself.
- Every ~2 seconds (or immediately when the persona switches), the current
  temperature/motion reading plus the active persona are sent to Claude,
  which responds with one in-character sentence shown in the narration
  panel.
- The Claude-calling code (key storage, budget cap, usage tracking) is
  unchanged from the original webcam sketch — it doesn't care where the
  reading or persona came from.

## Micro:bit side

Flash the same script used in [`../bluetooth_stream/`](../bluetooth_stream/):

```
bluetooth.onBluetoothConnected(function () {
    basic.showIcon(IconNames.Yes)
})
bluetooth.startAccelerometerService()
bluetooth.startTemperatureService()
bluetooth.startButtonService()
basic.showIcon(IconNames.StickFigure)
```

**Before it's discoverable**, set the project to no-pairing mode (Gear icon
→ Project Settings → pairing slider → no pairing; see
[`../seminars/microbit_ai.md`](../seminars/microbit_ai.md) for the full
steps).

## Running it

```bash
cd microbit_p5
python3 -m http.server 8000
```

Open `http://localhost:8000`, click **Connect Micro:bit**, open **Claude
API key & usage** and save an Anthropic API key, then press a button on
the board.

Needs **desktop Chrome or Edge** (or Chrome on Android) — Web Bluetooth
isn't supported elsewhere.

## If Bluetooth fails to connect

Before assuming something's actually broken: quit the browser completely,
forget the micro:bit in your OS's Bluetooth settings, power-cycle the
micro:bit, then retry. That resolved every connection failure hit while
building `bluetooth_stream/` — stale cached connection state, not a
hardware or firmware problem. Full story in
[`../bluetooth_stream/README.md`](../bluetooth_stream/README.md).

## Notes

- Get your API key from [console.anthropic.com](https://console.anthropic.com/settings/keys) —
  use a separate, spend-limited one, not your main key. It's stored in
  this browser's `localStorage`, readable by anyone with devtools access
  to the same browser/machine.
- `TEMP_LEVELS` and `MOTION_LEVELS`, and the two personas' system prompts,
  are all in the `<script>` block in `index.html` — edit `PERSONAS` there
  to add a third button-triggered character (the micro:bit only has two
  buttons, so a third would need a gesture or combo instead of a press).
- Light and sound levels aren't part of the official micro:bit Bluetooth
  Profile (only a custom UART stream can send those, and that proved
  unreliable on this hardware), which is why this version narrates
  temperature and motion rather than light/sound.
