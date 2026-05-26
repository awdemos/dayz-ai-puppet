"""Keyboard and mouse input injection via pydirectinput."""

from __future__ import annotations

import logging
import time

try:
    import pydirectinput
except (ImportError, AttributeError):
    pydirectinput = None

log = logging.getLogger(__name__)

KEY_MAP = {
    "forward": "w",
    "backward": "s",
    "left": "a",
    "right": "d",
}

MOVEMENT_KEYS = {"w", "a", "s", "d"}


def _require_pydirectinput():
    if pydirectinput is None:
        raise RuntimeError(
            "pydirectinput is only available on Windows. "
            "Input injection requires a Windows environment with the DayZ client."
        )


class DayZInput:
    def __init__(self) -> None:
        self._active_keys: set[str] = set()

    def move(self, direction: str, duration: float = 0.5) -> None:
        key = KEY_MAP.get(direction)
        if key is None:
            log.warning("unknown move direction: %s", direction)
            return
        self._hold_key(key, duration)

    def move_axis(self, forward: float, right: float, duration: float = 1.0) -> None:
        keys: list[str] = []
        if forward > 0:
            keys.append("w")
        elif forward < 0:
            keys.append("s")
        if right > 0:
            keys.append("d")
        elif right < 0:
            keys.append("a")

        for k in keys:
            pydirectinput.keyDown(k)
            self._active_keys.add(k)
        time.sleep(duration)
        for k in keys:
            pydirectinput.keyUp(k)
            self._active_keys.discard(k)
        log.debug("move_axis fwd=%.1f right=%.1f dur=%.1f keys=%s", forward, right, duration, keys)

    def look(self, delta_x: int, delta_y: int) -> None:
        x, y = pydirectinput.position()
        pydirectinput.moveTo(x + delta_x, y + delta_y)
        log.debug("look dx=%d dy=%d", delta_x, delta_y)

    def interact(self) -> None:
        pydirectinput.press("f")
        log.debug("interact (F)")

    def toggle_inventory(self) -> None:
        pydirectinput.press("tab")
        log.debug("toggle inventory (Tab)")

    def shoot(self, duration: float = 0.1) -> None:
        pydirectinput.mouseDown(button="left")
        time.sleep(duration)
        pydirectinput.mouseUp(button="left")
        log.debug("shoot dur=%.2f", duration)

    def crouch(self) -> None:
        pydirectinput.press("c")
        log.debug("crouch (C)")

    def prone(self) -> None:
        pydirectinput.press("z")
        log.debug("prone (Z)")

    def run_start(self) -> None:
        pydirectinput.keyDown("shift")
        self._active_keys.add("shift")
        log.debug("run start (Shift down)")

    def run_stop(self) -> None:
        pydirectinput.keyUp("shift")
        self._active_keys.discard("shift")
        log.debug("run stop (Shift up)")

    def emergency_stop(self) -> None:
        for key in list(self._active_keys):
            pydirectinput.keyUp(key)
        self._active_keys.clear()
        try:
            pydirectinput.mouseUp(button="left")
            pydirectinput.mouseUp(button="right")
        except Exception:
            pass
        log.debug("emergency stop — all keys released")

    def _hold_key(self, key: str, duration: float) -> None:
        pydirectinput.keyDown(key)
        self._active_keys.add(key)
        time.sleep(duration)
        pydirectinput.keyUp(key)
        self._active_keys.discard(key)
        log.debug("hold_key %s dur=%.2f", key, duration)
