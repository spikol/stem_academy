# Micro:bit Serial Stream

Plots a micro:bit's live sensor stream (light level, sound level,
acceleration strength) as stat tiles with sparklines, plus an optional data
table — over a wired USB connection.

## Why USB instead of Bluetooth

See [`../bluetooth_stream/README.md`](../bluetooth_stream/README.md) for
the full story: this board's UART TX characteristic declares BLE
**Indicate** support but rejects the subscription at the firmware level
(confirmed with two independent Bluetooth stacks — Chrome's Web Bluetooth
*and* Python's `bleak`/CoreBluetooth both hit the identical ATT protocol
error). That's a dead end client-side. USB serial sidesteps Bluetooth
entirely and reuses the same Web Serial API pattern already proven working
in [`../frontend/index.html`](../frontend/index.html) for the AI bridge.

## Micro:bit side

Flash this MakeCode script — same sensors as the Bluetooth version, using
`serial.writeString()` instead of `bluetooth.uartWriteString()`:

```
serial.redirectToUSB()
serial.setBaudRate(BaudRate.BaudRate115200)
basic.showIcon(IconNames.StickFigure)
basic.forever(function () {
    serial.writeString("" + input.lightLevel() + "," + input.soundLevel() + "," + input.acceleration(Dimension.Strength) + "\n")
    basic.pause(500)
})
```

**`serial.redirectToUSB()` is required** — on this hardware/firmware build,
MakeCode's default hardware serial pins are P0/P1, not the USB virtual COM
port, so without this call `serial.writeString()` silently goes nowhere the
browser can see (confirmed by testing: the `forever` loop visibly ran, but
zero bytes reached the browser's serial reader until this was added).

No pairing/project settings needed this time — it's a plain wired
connection.

## Running it

Web Serial requires a secure context: HTTPS, or `localhost` for local
testing.

```bash
cd serial_stream
python3 -m http.server 8000
```

1. Plug the micro:bit into your laptop over USB.
2. Open `http://localhost:8000`.
3. Click **Connect Micro:bit** and pick the board's serial port from the
   browser's picker.

## Browser support

Web Serial only — **desktop Chrome or Edge**. Firefox and Safari don't
support it.

## Protocol notes

- The page reads raw bytes off the serial port, buffers them, and parses
  each `\n`-terminated line as `light,sound,accel` (three comma-separated
  integers) — the `\n` in the MakeCode script is required for this to work,
  unlike the Bluetooth version where each BLE packet was already a discrete
  message.
- 115200 baud is MakeCode's default and matches `serial.setBaudRate(...)`
  in the script above. If readings come through garbled, this same
  hardware family has previously needed a lower baud rate for reliability
  (see `../dev/microbit_ai_bridge.py`'s notes) — try 9600 on both sides
  (`BaudRate.BaudRate9600` in the script, `BAUD_RATE` in `index.html`) if
  that happens.
- History is capped at the last 60 readings per metric (sparklines) / 30
  rows (table) — this is a live view, not a logger. For anything that needs
  to persist past a page reload, log on a backend or add an export button.
