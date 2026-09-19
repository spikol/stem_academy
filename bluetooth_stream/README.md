# Micro:bit Bluetooth Stream

Plots a micro:bit's live sensor stream (light level, sound level,
acceleration strength) as stat tiles with sparklines, plus an optional data
table.

## Why there's a Python bridge in the middle

The first version of this connected the browser directly to the micro:bit
using the Web Bluetooth API. On macOS + Chrome that failed at the
"subscribe to notifications" step with `GATT Error: Not supported`, for
every connection attempt, from both this page's code and Chrome's own
`chrome://bluetooth-internals` inspector. Digging into the characteristic's
properties in that inspector showed why: the micro:bit's UART TX
characteristic implements the BLE **Indicate** property, not **Notify**.
Both are valid per the Web Bluetooth spec (`startNotifications()` is
supposed to work with either), but Chrome's macOS implementation has a gap
here — it doesn't successfully subscribe to indicate-only characteristics.

`bridge.py` (using [`bleak`](https://github.com/hbldh/bleak), which talks to
CoreBluetooth directly) subscribes to the same characteristic without going
through that Chromium code path, and relays parsed readings to the browser
over a plain local WebSocket. The micro:bit stays wireless — only the
bridge process and the browser page are on your laptop.

```
micro:bit --BLE (Indicate)--> bridge.py (bleak) --WebSocket--> index.html
```

## Micro:bit side

Flash this MakeCode script:

```
bluetooth.onBluetoothConnected(function () {
    basic.showIcon(IconNames.Yes)
})
bluetooth.startUartService()
basic.showIcon(IconNames.StickFigure)
basic.forever(function () {
    bluetooth.uartWriteString("" + input.lightLevel() + "," + input.soundLevel() + "," + input.acceleration(Dimension.Strength))
    basic.pause(500)
})
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

Flash it, and the board's LED shows a stick figure while advertising, then a
checkmark once something connects.

## Running it

1. Install the bridge's dependencies (once):
   ```bash
   cd bluetooth_stream
   pip install -r requirements.txt
   ```
2. Start the bridge — it scans for a device named `BBC micro:bit*`, connects,
   and starts a WebSocket server:
   ```bash
   python bridge.py
   ```
   Leave this running. It auto-reconnects if the micro:bit drops out.
3. Serve the page (Chrome/Edge/Firefox/Safari all work now — it's plain
   WebSocket, not Web Bluetooth):
   ```bash
   python3 -m http.server 8000
   ```
4. Open `http://localhost:8000`, click **Connect to Bridge**.

## Protocol notes

- The micro:bit sends `light,sound,accel` (three comma-separated integers)
  over UART every 500ms; `bridge.py` regex-matches that out of each BLE
  notification/indication and forwards `{"light":.., "sound":.., "accel":..}`
  as JSON text frames.
- `bridge.py` broadcasts to every connected browser tab, so multiple people
  can watch the same stream.
- History is capped at the last 60 readings per metric (sparklines) / 30
  rows (table) in the browser — this is a live view, not a logger. To
  persist readings, log them on the Python side (`bridge.py`'s
  `handle_notify` is the place to add a CSV writer or similar) or add an
  export button to the page.
