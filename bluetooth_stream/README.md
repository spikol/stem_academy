# Micro:bit Bluetooth Stream

Plots acceleration (X/Y/Z), temperature, and button A/B state, streamed
live from a micro:bit over Web Bluetooth, as stat tiles with sparklines
plus an optional data table.

## Why this uses different services than you might expect

The first version of this streamed light/sound/acceleration as a custom
CSV string over a **Nordic UART Service** (`bluetooth.startUartService()` +
`bluetooth.uartWriteString()`). That consistently failed to subscribe to
notifications — `GATT Error: Not supported` — no matter what we tried:
Chrome's Web Bluetooth, Chrome's own `chrome://bluetooth-internals`
inspector, and even Python's `bleak` library (which talks to CoreBluetooth
directly, bypassing Chrome entirely) all hit the same wall.

It turned out to be a **stale Bluetooth connection/bonding state**, not a
hardware or firmware limitation — this board had been reflashed and
reconnected to many times across a long debugging session (Teachable
Machine firmware, several custom UART builds), and macOS/Chrome had cached
something stale. The fix was a full reset: quit Chrome, forget the device
in System Settings → Bluetooth, and power-cycle the micro:bit. Once tested
with that clean state, notifications worked fine.

This version uses the **official micro:bit Bluetooth Profile** services
(Accelerometer, Temperature, Button) instead of a custom UART string.
Those are separate from the generic UART approach, and don't require any
custom device-side parsing — each one has a fixed, documented data format:

- **Accelerometer Service** — `e95d0753-251d-470a-a062-fa1922dfa9a8`,
  Data characteristic `e95dca4b-...` — X/Y/Z as three `int16` (little-endian,
  milli-g).
- **Temperature Service** — `e95d6100-...`, Data characteristic
  `e95d9250-...` — one `int8`, °C.
- **Button Service** — `e95d9882-...`, Button A `e95dda90-...` / Button B
  `e95dda91-...` — one `uint8`: `0` not pressed, `1` pressed, `2` held/long
  press.

Light level and sound level aren't part of the official profile, so they're
not available this way — see [`../serial_stream/`](../serial_stream/) if
you need those (over USB) instead.

## Micro:bit side

Flash this MakeCode script:

```
bluetooth.onBluetoothConnected(function () {
    basic.showIcon(IconNames.Yes)
})
bluetooth.startAccelerometerService()
bluetooth.startTemperatureService()
bluetooth.startButtonService()
basic.showIcon(IconNames.StickFigure)
```

**Before it's discoverable**, set the project to no-pairing mode (same step
as the Teachable Machine bridge — see
[`../seminars/microbit_ai.md`](../seminars/microbit_ai.md)):

1. Gear icon → Project Settings → set the pairing slider to **no pairing**.
2. Edit Settings as Text, and under Bluetooth confirm/add:
   ```json
   "bluetooth": {
       "open": 1,
       "pairing_mode": 0,
       "whitelist": 0,
       "security_level": null
   }
   ```

Flash it, and the board's LED shows a stick figure while advertising, then
a checkmark once something connects.

## Running it

Web Bluetooth requires a secure context: HTTPS, or `localhost` for local
testing.

```bash
cd bluetooth_stream
python3 -m http.server 8000
```

Open `http://localhost:8000`, click **Connect Micro:bit**, and pick the
board (shows as `BBC micro:bit [xxxxx]`).

**If it fails to find a service or fails subscribing to notifications**,
before assuming it's broken again: quit Chrome fully, forget the device in
System Settings → Bluetooth, power-cycle the micro:bit, then retry. That
resolved every failure we hit while building this.

## Browser support

Web Bluetooth only — **desktop Chrome or Edge**, or Chrome on Android.
Firefox and Safari don't support it.

## Protocol notes

- History is capped at the last 60 readings per metric (sparklines) / 30
  rows (table) — this is a live view, not a logger.
- Button state changes are event-driven (notified on press/release), not
  polled — the tile just reflects the last state received.
