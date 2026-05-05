# Luxafor FLAG Busylight API

A local REST API and browser control panel for the [Luxafor FLAG](https://luxafor.com/product/flag/) USB presence light. No Luxafor software required — communicates directly over USB HID.

## Requirements

- Python 3.10+
- Linux: `libusb-1.0` (usually pre-installed)
- The Luxafor FLAG plugged in via USB

## Setup

```bash
python3 -m venv ~/.venv/luxafor
~/.venv/luxafor/bin/pip install -r requirements.txt
```

On first run the app will attempt to install udev rules so the device is accessible without root:

```bash
~/.venv/luxafor/bin/python3 main.py
```

If the udev step requires manual intervention:

```bash
sudo cp 99-luxafor.rules /etc/udev/rules.d/
sudo udevadm control --reload && sudo udevadm trigger
sudo usermod -aG plugdev $USER   # log out and back in after this
```

## Running

```bash
~/.venv/luxafor/bin/python3 main.py
```

The API starts at `http://127.0.0.1:8000`.  
Open that URL in a browser for the visual control panel.  
API reference docs are at `http://127.0.0.1:8000/docs`.

## Control Panel

`http://127.0.0.1:8000` — a single-page panel with controls for every command, a live LED color preview, and a status badge that polls the device connection every 3 seconds.

## API Reference

All endpoints return `{"ok": true}` on success or an HTTP error with a `detail` field.

### `GET /status`

Returns device connection state.

```json
{ "connected": true, "devices": 1 }
```

---

### `POST /color`

Set LEDs to a static color instantly.

| Field | Type | Values |
|-------|------|--------|
| `led` | string | `"all"`, `"front"`, `"back"`, `"1"`–`"6"` |
| `r` | int | 0–255 |
| `g` | int | 0–255 |
| `b` | int | 0–255 |

```bash
curl -X POST http://localhost:8000/color \
  -H "Content-Type: application/json" \
  -d '{"led":"all","r":255,"g":0,"b":0}'
```

---

### `POST /fade`

Fade to a color over time.

| Field | Type | Values |
|-------|------|--------|
| `led` | string | `"all"`, `"front"`, `"back"`, `"1"`–`"6"` |
| `r` | int | 0–255 |
| `g` | int | 0–255 |
| `b` | int | 0–255 |
| `speed` | int | 0–255 (default `128`) |

```bash
curl -X POST http://localhost:8000/fade \
  -H "Content-Type: application/json" \
  -d '{"led":"all","r":0,"g":255,"b":0,"speed":100}'
```

---

### `POST /strobe`

Blink LEDs repeatedly.

| Field | Type | Values |
|-------|------|--------|
| `led` | string | `"all"`, `"front"`, `"back"`, `"1"`–`"6"` |
| `r` | int | 0–255 |
| `g` | int | 0–255 |
| `b` | int | 0–255 |
| `speed` | int | 0–255 (default `128`) |
| `repeat` | int | 0–255, `0` = infinite (default `0`) |

```bash
curl -X POST http://localhost:8000/strobe \
  -H "Content-Type: application/json" \
  -d '{"led":"all","r":255,"g":0,"b":0,"speed":64,"repeat":5}'
```

---

### `POST /wave`

Run a wave animation across all LEDs.

| Field | Type | Values |
|-------|------|--------|
| `type` | string | `"short"`, `"long"`, `"overlapping-short"`, `"overlapping-long"`, `"type5"` |
| `r` | int | 0–255 |
| `g` | int | 0–255 |
| `b` | int | 0–255 |
| `speed` | int | 0–255 (default `128`) |
| `repeat` | int | 0–255, `0` = infinite (default `0`) |

```bash
curl -X POST http://localhost:8000/wave \
  -H "Content-Type: application/json" \
  -d '{"type":"long","r":0,"g":100,"b":255,"speed":128,"repeat":3}'
```

---

### `POST /pattern`

Play a built-in pattern.

| Field | Type | Values |
|-------|------|--------|
| `name` | string | `"traffic-light"`, `"random1"`–`"random5"`, `"police"`, `"rainbow"` |
| `repeat` | int | 0–255, `0` = infinite (default `0`) |

```bash
curl -X POST http://localhost:8000/pattern \
  -H "Content-Type: application/json" \
  -d '{"name":"rainbow","repeat":2}'
```

---

### `POST /off`

Turn off LEDs.

| Field | Type | Values |
|-------|------|--------|
| `led` | string | `"all"`, `"front"`, `"back"`, `"1"`–`"6"` (default `"all"`) |

```bash
curl -X POST http://localhost:8000/off \
  -H "Content-Type: application/json" \
  -d '{"led":"all"}'
```

---

## Project Structure

```
├── main.py              # FastAPI app + entry point
├── preflight.py         # Auto-installs udev rules on first run
├── requirements.txt
├── 99-luxafor.rules     # udev rule for non-root USB access
├── luxafor/
│   └── device.py        # USB HID layer (pyusb)
├── api/
│   ├── models.py        # Pydantic request models
│   └── routes.py        # Route handlers
└── static/
    └── index.html       # Browser control panel
```

## USB HID Protocol

The Luxafor FLAG is a USB HID device (VID `0x04D8`, PID `0xF372`). Commands are 8-byte payloads sent via HID `SET_REPORT` control transfers:

| Byte | Field |
|------|-------|
| 0 | Command mode (1=color, 2=fade, 3=strobe, 4=wave, 6=pattern) |
| 1 | LED target |
| 2–4 | R, G, B |
| 5 | Speed |
| 6 | (reserved) |
| 7 | Repeat |
