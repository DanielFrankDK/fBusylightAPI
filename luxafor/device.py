"""Low-level HID communication via the Linux hidraw interface."""

import glob

VENDOR_ID = 0x04D8
PRODUCT_ID = 0xF372
_VID = f'{VENDOR_ID:04X}'.lower()
_PID = f'{PRODUCT_ID:04X}'.lower()

# LED targets
LED_ALL = 0xFF
LED_FRONT = 0x41
LED_BACK = 0x42

LED_TARGETS = {
    "all": LED_ALL,
    "front": LED_FRONT,
    "back": LED_BACK,
    **{str(i): i for i in range(1, 7)},
}

# Wave types
WAVE_TYPES = {
    "short": 1,
    "long": 2,
    "overlapping-short": 3,
    "overlapping-long": 4,
    "type5": 5,
}

# Built-in patterns
PATTERNS = {
    "traffic-light": 1,
    "random1": 2,
    "random2": 3,
    "random3": 4,
    "random4": 5,
    "random5": 6,
    "police": 7,
    "rainbow": 8,
}

# HID command modes
CMD_STATIC = 1
CMD_FADE = 2
CMD_STROBE = 3
CMD_WAVE = 4
CMD_PATTERN = 6


def _find_hidraw() -> str | None:
    for uevent in glob.glob('/sys/class/hidraw/*/device/uevent'):
        try:
            txt = open(uevent).read().lower()
            if _VID in txt and _PID in txt:
                node = uevent.split('/')[4]
                return f'/dev/{node}'
        except OSError:
            pass
    return None


class LuxaforDevice:
    def __init__(self):
        self._fd = None

    def open(self):
        path = _find_hidraw()
        if path is None:
            raise OSError("Luxafor FLAG not found")
        self._fd = open(path, 'wb')

    def close(self):
        if self._fd:
            try:
                self._fd.close()
            except Exception:
                pass
            self._fd = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *_):
        self.close()

    def _send(self, data: list[int]):
        report = bytes(data + [0] * (8 - len(data)))
        self._fd.write(report[:8])
        self._fd.flush()

    def set_color(self, led: int, r: int, g: int, b: int):
        self._send([CMD_STATIC, led, r, g, b])

    def fade(self, led: int, r: int, g: int, b: int, speed: int):
        self._send([CMD_FADE, led, r, g, b, speed])

    def strobe(self, led: int, r: int, g: int, b: int, speed: int, repeat: int):
        self._send([CMD_STROBE, led, r, g, b, speed, 0, repeat])

    def wave(self, wave_type: int, r: int, g: int, b: int, speed: int, repeat: int):
        self._send([CMD_WAVE, wave_type, r, g, b, 0, repeat, speed])

    def pattern(self, pattern_id: int, repeat: int):
        self._send([CMD_PATTERN, pattern_id, repeat])

    def off(self, led: int = LED_ALL):
        self.set_color(led, 0, 0, 0)

    @staticmethod
    def list_devices() -> list[dict]:
        found = []
        for uevent in glob.glob('/sys/class/hidraw/*/device/uevent'):
            try:
                txt = open(uevent).read().lower()
                if _VID in txt and _PID in txt:
                    found.append({'vendor_id': VENDOR_ID, 'product_id': PRODUCT_ID})
            except OSError:
                pass
        return found
