"""DayZ screen capture using mss with base64 JPEG output."""

from __future__ import annotations

import base64
import io
import logging

import mss
import mss.tools
from PIL import Image

log = logging.getLogger(__name__)


class DayZVision:
    def __init__(
        self,
        width: int = 1280,
        height: int = 720,
        monitor: int = 1,
        quality: int = 85,
    ) -> None:
        self.width = width
        self.height = height
        self.monitor = monitor
        self.quality = quality

    def capture(self) -> Image.Image:
        with mss.mss() as sct:
            mon = sct.monitors[self.monitor]
            shot = sct.grab(mon)
            img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
        if img.size != (self.width, self.height):
            img = img.resize((self.width, self.height), Image.LANCZOS)
        return img

    def capture_base64(self) -> str:
        img = self.capture()
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=self.quality)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{b64}"
