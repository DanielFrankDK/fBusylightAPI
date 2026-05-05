"""Low-level USB communication with the Luxafor FLAG via pyusb/libusb-1.0."""

import usb.core
import usb.util

VENDOR_ID = 0x04D8
PRODUCT_ID = 0xF372

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

# HID SET_REPORT control transfer constants
_HID_SET_REPORT = 0x09
_HID_OUTPUT_REPORT = 0x0200  # report type Output, report ID 0
_HID_INTERFACE = 0


class LuxaforDevice:
    def __init__(self):
        self._dev = None

    def open(self):
        dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
        if dev is None:
            raise OSError("Luxafor FLAG not found")
        if dev.is_kernel_driver_active(_HID_INTERFACE):
            dev.detach_kernel_driver(_HID_INTERFACE)
        dev.set_configuration()
        self._dev = dev

    def close(self):
        if self._dev:
            try:
                usb.util.dispose_resources(self._dev)
            except Exception:
                pass
            self._dev = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *_):
        self.close()

    def _send(self, data: list[int]):
        # 8-byte payload (no report ID prefix for ctrl_transfer)
        report = data + [0] * (8 - len(data))
        self._dev.ctrl_transfer(
            0x21,              # bmRequestType: Host→Device, Class, Interface
            _HID_SET_REPORT,
            _HID_OUTPUT_REPORT,
            _HID_INTERFACE,
            report[:8],
        )

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
        devices = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID, find_all=True)
        return [{"vendor_id": VENDOR_ID, "product_id": PRODUCT_ID} for _ in (devices or [])]
