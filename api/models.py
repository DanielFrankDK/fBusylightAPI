from typing import Literal
from pydantic import BaseModel, Field

LedTarget = Literal["all", "front", "back", "1", "2", "3", "4", "5", "6"]
WaveType = Literal["short", "long", "overlapping-short", "overlapping-long", "type5"]
PatternName = Literal[
    "traffic-light", "random1", "random2", "random3",
    "random4", "random5", "police", "rainbow"
]

Color = Field(ge=0, le=255)
Speed = Field(default=128, ge=0, le=255)
Repeat = Field(default=0, ge=0, le=255)


class ColorRequest(BaseModel):
    led: LedTarget = "all"
    r: int = Color
    g: int = Color
    b: int = Color


class FadeRequest(BaseModel):
    led: LedTarget = "all"
    r: int = Color
    g: int = Color
    b: int = Color
    speed: int = Speed


class StrobeRequest(BaseModel):
    led: LedTarget = "all"
    r: int = Color
    g: int = Color
    b: int = Color
    speed: int = Speed
    repeat: int = Repeat


class WaveRequest(BaseModel):
    type: WaveType = "short"
    r: int = Color
    g: int = Color
    b: int = Color
    speed: int = Speed
    repeat: int = Repeat


class PatternRequest(BaseModel):
    name: PatternName
    repeat: int = Repeat


class OffRequest(BaseModel):
    led: LedTarget = "all"
