# Micro:bit AI Bridge — device-side code (MicroPython, micro:bit v2)
#
# Button A: cycle through preset questions (index flashes briefly)
# Button B: send the selected question to the AI bridge and scroll the reply
#
# Talks to frontend/index.html over the same USB serial connection used for
# the REPL, at 9600 baud (lower than the micro:bit's 115200 default - far
# more tolerant of cable/port signal noise). Even so, longer messages were
# still seeing occasional dropped characters, so the outgoing request is
# just "Q<index>\n" - the frontend keeps its own copy of QUESTIONS and looks
# the text up locally, keeping the fragile wire format as short as possible.
# The reply comes back as one line prefixed with "Y:" (yes, this is AI -
# smiley), "N:" (no - cross), or "?:" (unclear - question mark) so the right
# face shows before the reason scrolls by.
#
# Flash this with the online editor (python.microbit.org — paste and
# download), or `uflash microbit_ai_bridge.py` from the command line.

from microbit import *

uart.init(baudrate=9600)

QUESTIONS = [
    "Is a thermostat AI?",
    "Is a calculator AI?",
    "Is a search engine AI?",
    "Is ChatGPT AI?",
    "Is a self-driving car AI?",
]

REPLY_TIMEOUT_MS = 15000

selected = 0


def show_selected():
    display.scroll(str(selected + 1), delay=80, wait=True)


def send_request(index):
    # This hardware occasionally drops/corrupts a byte in transit even on
    # a message this short. Send it 3 times - the frontend debounces
    # duplicates, and the odds of all 3 attempts landing corrupted are low.
    payload = ("Q" + str(index) + "\n").encode("utf-8")
    for _ in range(3):
        uart.write(payload)
        sleep(30)


def wait_for_reply(timeout_ms):
    buffer = b""
    start = running_time()
    while running_time() - start < timeout_ms:
        if uart.any():
            chunk = uart.read()
            if chunk:
                buffer += chunk
                if b"\n" in buffer:
                    line = buffer.split(b"\n", 1)[0]
                    try:
                        return line.decode("utf-8").strip()
                    except UnicodeError:
                        return None
        sleep(20)
    return None


VERDICT_FACES = {
    "Y": Image.HAPPY,
    "N": Image.NO,
    "?": Image.CONFUSED,
}


def show_reply(line):
    # str.partition() isn't implemented in this MicroPython build - use
    # find()/slicing instead.
    colon_index = line.find(":")
    if colon_index == -1:
        marker, text = None, line
    else:
        marker, text = line[:colon_index], line[colon_index + 1:]

    face = VERDICT_FACES.get(marker)
    if face:
        display.show(face)
        sleep(1000)
    if text:
        display.scroll(text, delay=80, wait=True)


display.scroll("AI BRIDGE", delay=80, wait=True)
display.show(Image.ARROW_E)

while True:
    if button_a.was_pressed():
        selected = (selected + 1) % len(QUESTIONS)
        show_selected()
        display.show(Image.ARROW_E)

    if button_b.was_pressed():
        # Any lit LED needs a continuous background refresh interrupt for
        # multiplexing, which contends with the UART at the bit level and
        # corrupts serial data - so the display stays fully blank for the
        # whole send+receive round trip, not just during the write() call.
        display.clear()
        send_request(selected)
        reply = wait_for_reply(REPLY_TIMEOUT_MS)
        if reply:
            show_reply(reply)
        else:
            display.show(Image.SAD)
            sleep(1500)

        display.show(Image.ARROW_E)
