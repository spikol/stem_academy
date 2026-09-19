"""
Micro:bit BLE bridge.

Chrome's Web Bluetooth on macOS fails to subscribe to this micro:bit's UART
TX characteristic because it only implements the BLE "Indicate" property,
not "Notify" — confirmed via chrome://bluetooth-internals, which shows the
same NotSupportedError even from Chrome's own inspector. bleak talks to
CoreBluetooth directly (no Chromium property gate in the way) and
subscribes to either Notify or Indicate transparently, so it works around
that gap entirely.

This script connects to the micro:bit over Bluetooth, parses each UART line
as "<light>,<sound>,<accel>", and relays it as JSON to any browser tab
connected to its local WebSocket server. index.html connects to that
WebSocket instead of using Web Bluetooth directly.

Usage:
    pip install -r requirements.txt
    python bridge.py
"""
import asyncio
import json
import re

from bleak import BleakClient, BleakScanner
import websockets

UART_TX = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
DEVICE_NAME_PREFIX = "BBC micro:bit"

WS_HOST = "localhost"
WS_PORT = 8765

SCAN_TIMEOUT_S = 15.0
RECONNECT_DELAY_S = 5.0

READING_RE = re.compile(rb"(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)")

connected_clients = set()


async def broadcast(message):
    if not connected_clients:
        return
    dead = set()
    for ws in connected_clients:
        try:
            await ws.send(message)
        except websockets.ConnectionClosed:
            dead.add(ws)
    connected_clients.difference_update(dead)


async def ws_handler(websocket):
    connected_clients.add(websocket)
    print(f"Browser connected ({len(connected_clients)} total)")
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.discard(websocket)
        print(f"Browser disconnected ({len(connected_clients)} total)")


async def find_device():
    print(f"Scanning for a device named '{DEVICE_NAME_PREFIX}*'...")
    device = await BleakScanner.find_device_by_filter(
        lambda d, adv: d.name is not None and d.name.startswith(DEVICE_NAME_PREFIX),
        timeout=SCAN_TIMEOUT_S,
    )
    if device is None:
        raise RuntimeError(
            f"No device found matching '{DEVICE_NAME_PREFIX}*' — is the "
            "micro:bit powered on and running the UART-streaming script?"
        )
    return device


def make_notify_handler(loop):
    def handle_notify(_, data: bytearray):
        match = READING_RE.search(bytes(data))
        if not match:
            return
        light, sound, accel = (int(x) for x in match.groups())
        payload = json.dumps({"light": light, "sound": sound, "accel": accel})
        asyncio.run_coroutine_threadsafe(broadcast(payload), loop)

    return handle_notify


async def run_bridge():
    device = await find_device()
    print(f"Found {device.name} ({device.address}), connecting...")

    loop = asyncio.get_running_loop()

    async with BleakClient(device) as client:
        print("Connected. Subscribing to UART TX...")
        await client.start_notify(UART_TX, make_notify_handler(loop))
        print("Streaming — leave this running and open index.html in a browser.")
        while client.is_connected:
            await asyncio.sleep(1)
    print("Micro:bit disconnected.")


async def main():
    await websockets.serve(ws_handler, WS_HOST, WS_PORT)
    print(f"WebSocket server listening on ws://{WS_HOST}:{WS_PORT}")

    while True:
        try:
            await run_bridge()
        except Exception as e:
            print(f"Bridge error: {e}")
        print(f"Retrying in {RECONNECT_DELAY_S:.0f}s...")
        await asyncio.sleep(RECONNECT_DELAY_S)


if __name__ == "__main__":
    asyncio.run(main())
