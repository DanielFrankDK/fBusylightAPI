from fastapi import APIRouter, HTTPException
from .models import ColorRequest, FadeRequest, StrobeRequest, WaveRequest, PatternRequest, OffRequest
from luxafor.device import LuxaforDevice, LED_TARGETS, WAVE_TYPES, PATTERNS

router = APIRouter()


def get_device() -> LuxaforDevice:
    devices = LuxaforDevice.list_devices()
    if not devices:
        raise HTTPException(status_code=503, detail="No Luxafor device found")
    dev = LuxaforDevice()
    dev.open()
    return dev


@router.get("/status")
def status():
    devices = LuxaforDevice.list_devices()
    return {"connected": len(devices) > 0, "devices": len(devices)}


@router.post("/color")
def color(req: ColorRequest):
    with get_device() as dev:
        dev.set_color(LED_TARGETS[req.led], req.r, req.g, req.b)
    return {"ok": True}


@router.post("/fade")
def fade(req: FadeRequest):
    with get_device() as dev:
        dev.fade(LED_TARGETS[req.led], req.r, req.g, req.b, req.speed)
    return {"ok": True}


@router.post("/strobe")
def strobe(req: StrobeRequest):
    with get_device() as dev:
        dev.strobe(LED_TARGETS[req.led], req.r, req.g, req.b, req.speed, req.repeat)
    return {"ok": True}


@router.post("/wave")
def wave(req: WaveRequest):
    with get_device() as dev:
        dev.wave(WAVE_TYPES[req.type], req.r, req.g, req.b, req.speed, req.repeat)
    return {"ok": True}


@router.post("/pattern")
def pattern(req: PatternRequest):
    with get_device() as dev:
        dev.pattern(PATTERNS[req.name], req.repeat)
    return {"ok": True}


@router.post("/off")
def off(req: OffRequest = OffRequest()):
    with get_device() as dev:
        dev.off(LED_TARGETS[req.led])
    return {"ok": True}
