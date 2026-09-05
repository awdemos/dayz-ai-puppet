"""Keyboard and mouse input injection via pydirectinput."""

from __future__ import annotations

import logging
import time
from collections import deque

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

DEFAULT_ACTIONS_PER_SECOND = 10
DEFAULT_RATE_WINDOW_SECONDS = 1.0


def _require_pydirectinput():
    if pydirectinput is None:
        raise RuntimeError(
            "pydirectinput is only available on Windows. "
            "Input injection requires a Windows environment with the DayZ client."
        )


class DayZInput:
    """Physical input injector guarded by an explicit enablement toggle and rate limits.

    Input injection is disabled by default. Call :meth:`enable` only after the user
    has explicitly consented (e.g. the UI acknowledges a confirmation prompt). Once
    enabled, callers must still respect the configured action budget; exceeding it
    triggers an automatic emergency stop.
    """

    def __init__(
        self,
        *,
        actions_per_second: int = DEFAULT_ACTIONS_PER_SECOND,
        rate_window_seconds: float = DEFAULT_RATE_WINDOW_SECONDS,
    ) -> None:
        self._enabled: bool = False
        self._actions_per_second: int = actions_per_second
        self._rate_window_seconds: float = rate_window_seconds
        self._action_times: deque[float] = deque()
        self._active_keys: set[str] = set()

    @property
    def enabled(self) -> bool:
        """Whether physical input injection is currently enabled."""
        return self._enabled

    def enable(self) -> None:
        """Enable physical input injection. Call only after explicit user consent."""
        self._enabled = True
        log.info("DayZInput enabled — physical input injection is active")

    def disable(self) -> None:
        """Disable physical input injection and release any active keys."""
        self._enabled = False
        self._action_times.clear()
        self.emergency_stop()
        log.info("DayZInput disabled — physical input injection stopped")

    @staticmethod
    def confirm() -> bool:
        """Confirmation hook for user-acknowledged enablement.

        The real UI should obtain explicit consent before calling :meth:`enable`.
        This helper exists as a clear API contract: only return True once the user
        has confirmed they want to hand over physical keyboard/mouse control.
        """
        return True

    def _require_enabled(self) -> None:
        if not self._enabled:
            raise RuntimeError(
                "Physical input injection is disabled. "
                "Call confirm() and enable() after obtaining explicit user consent."
            )

    def _check_rate_limit(self) -> None:
        """Enforce the actions-per-second budget; trigger emergency stop on violation."""
        now = time.monotonic()
        cutoff = now - self._rate_window_seconds
        while self._action_times and self._action_times[0] < cutoff:
            self._action_times.popleft()

        if len(self._action_times) >= self._actions_per_second:
            log.error(
                "Rate limit exceeded: %d actions in %.2fs; triggering emergency_stop",
                len(self._action_times),
                self._rate_window_seconds,
            )
            self.emergency_stop()
            raise RuntimeError(
                f"Input rate limit exceeded: more than {self._actions_per_second} actions "
                f"in {self._rate_window_seconds}s. Injection has been emergency stopped."
            )

        self._action_times.append(now)

    def _record_action(self) -> None:
        """Record one physical input action after enforcing the rate limit."""
        self._check_rate_limit()

    def move(self, direction: str, duration: float = 0.5) -> None:
        self._require_enabled()
        _require_pydirectinput()
        key = KEY_MAP.get(direction)
        if key is None:
            log.warning("unknown move direction: %s", direction)
            return
        self._hold_key(key, duration)

    def move_axis(self, forward: float, right: float, duration: float = 1.0) -> None:
        self._require_enabled()
        _require_pydirectinput()
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
            self._record_action()
            pydirectinput.keyDown(k)
            self._active_keys.add(k)
        time.sleep(duration)
        for k in keys:
            pydirectinput.keyUp(k)
            self._active_keys.discard(k)
        log.debug("move_axis fwd=%.1f right=%.1f dur=%.1f keys=%s", forward, right, duration, keys)

    def look(self, delta_x: int, delta_y: int) -> None:
        self._require_enabled()
        _require_pydirectinput()
        self._record_action()
        x, y = pydirectinput.position()
        pydirectinput.moveTo(x + delta_x, y + delta_y)
        log.debug("look dx=%d dy=%d", delta_x, delta_y)

    def interact(self) -> None:
        self._require_enabled()
        _require_pydirectinput()
        self._record_action()
        pydirectinput.press("f")
        log.debug("interact (F)")

    def toggle_inventory(self) -> None:
        self._require_enabled()
        _require_pydirectinput()
        self._record_action()
        pydirectinput.press("tab")
        log.debug("toggle inventory (Tab)")

    def shoot(self, duration: float = 0.1) -> None:
        self._require_enabled()
        _require_pydirectinput()
        self._record_action()
        pydirectinput.mouseDown(button="left")
        time.sleep(duration)
        pydirectinput.mouseUp(button="left")
        log.debug("shoot dur=%.2f", duration)

    def crouch(self) -> None:
        self._require_enabled()
        _require_pydirectinput()
        self._record_action()
        pydirectinput.press("c")
        log.debug("crouch (C)")

    def prone(self) -> None:
        self._require_enabled()
        _require_pydirectinput()
        self._record_action()
        pydirectinput.press("z")
        log.debug("prone (Z)")

    def run_start(self) -> None:
        self._require_enabled()
        _require_pydirectinput()
        self._record_action()
        pydirectinput.keyDown("shift")
        self._active_keys.add("shift")
        log.debug("run start (Shift down)")

    def run_stop(self) -> None:
        self._require_enabled()
        _require_pydirectinput()
        self._record_action()
        pydirectinput.keyUp("shift")
        self._active_keys.discard("shift")
        log.debug("run stop (Shift up)")

    def emergency_stop(self) -> None:
        _require_pydirectinput()
        self._enabled = False
        self._action_times.clear()
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
        _require_pydirectinput()
        self._record_action()
        pydirectinput.keyDown(key)
        self._active_keys.add(key)
        time.sleep(duration)
        pydirectinput.keyUp(key)
        self._active_keys.discard(key)
        log.debug("hold_key %s dur=%.2f", key, duration)
