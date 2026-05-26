"""Main see-think-act loop orchestrating all subsystems."""

from __future__ import annotations

import logging
import time
from typing import Any

from dayz_ai_puppet.agent.actions import ActionType
from dayz_ai_puppet.agent.kimi import DayZAgent
from dayz_ai_puppet.config import Settings
from dayz_ai_puppet.input.controller import DayZInput
from dayz_ai_puppet.memory.experience import ExperienceMemory
from dayz_ai_puppet.navigation.gps import GPSNavigator
from dayz_ai_puppet.reflexes.combat import CombatReflexes
from dayz_ai_puppet.server.state_client import ServerStateClient
from dayz_ai_puppet.vision.capture import DayZVision

log = logging.getLogger(__name__)


class DayZAILoop:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.vision = DayZVision(
            width=settings.capture_width,
            height=settings.capture_height,
            monitor=settings.capture_monitor,
            quality=settings.capture_quality,
        )
        self.input_ctrl = DayZInput()
        self.agent = DayZAgent(settings)
        self.memory = ExperienceMemory(path=settings.memory_path)
        self.navigator = GPSNavigator()
        self.reflexes = CombatReflexes(settings) if settings.reflex_enabled else None
        self.server = ServerStateClient(
            url=settings.server_state_url,
            fallback_file=settings.server_state_file,
            timeout=settings.server_state_timeout,
        )
        self._running = False

    def run(self) -> None:
        self._running = True
        log.info("DayZ AI Puppet loop started (tick=%.1fs)", self.settings.tick_rate)
        while self._running:
            try:
                self.tick()
            except KeyboardInterrupt:
                break
            except Exception:
                log.exception("tick error")
            elapsed = time.monotonic() - self._tick_start
            sleep_time = self.settings.tick_rate - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
        self.shutdown()

    def tick(self) -> None:
        self._tick_start = time.monotonic()

        screenshot_b64 = self.vision.capture_base64()
        game_state_obj = self.server.get_state()
        state_dict = game_state_obj.to_dict()

        if self.reflexes:
            reflex_action = self.reflexes.check(state_dict)
            if reflex_action is not None:
                self._execute_action(reflex_action)
                return

        lessons: list[str] = []
        if game_state_obj.position != (0.0, 0.0, 0.0):
            relevant = self.memory.get_relevant_lessons(game_state_obj.position, limit=3)
            lessons = [lesson.summary for lesson in relevant]

        actions = self.agent.decide(screenshot_b64, state_dict, lessons)

        for action in actions:
            self._execute_action(action)

        if game_state_obj.health <= 0:
            self._handle_death(state_dict, screenshot_b64)

    def shutdown(self) -> None:
        self._running = False
        self.input_ctrl.emergency_stop()
        self.server.close()
        log.info("DayZ AI Puppet stopped")

    def _execute_action(self, action: Any) -> None:
        atype = action.type
        p = action.params

        if atype == ActionType.MOVE:
            self.input_ctrl.move_axis(
                forward=p.get("forward", 0),
                right=p.get("right", 0),
                duration=p.get("duration", 1.0),
            )
        elif atype == ActionType.LOOK:
            self.input_ctrl.look(
                delta_x=int(p.get("yaw", 0)),
                delta_y=int(p.get("pitch", 0)),
            )
        elif atype == ActionType.INTERACT:
            self.input_ctrl.interact()
        elif atype == ActionType.INVENTORY:
            self.input_ctrl.toggle_inventory()
        elif atype == ActionType.SHOOT:
            self.input_ctrl.shoot(duration=p.get("duration", 0.1))
        elif atype == ActionType.CROUCH:
            self.input_ctrl.crouch()
        elif atype == ActionType.PRONE:
            self.input_ctrl.prone()
        elif atype == ActionType.RUN:
            self.input_ctrl.run_start()
        elif atype == ActionType.STOP:
            self.input_ctrl.emergency_stop()
        elif atype == ActionType.HEAL:
            self.input_ctrl.interact()

    def _handle_death(self, state: dict[str, Any], screenshot_b64: str) -> None:
        pos = state.get("position", (0, 0, 0))
        if isinstance(pos, list):
            pos = tuple(pos)
        self.memory.record_death(
            cause="unknown",
            position=pos,
            screenshot_b64=screenshot_b64[:200],
            lesson_learned="Died here — avoid this area or approach differently",
        )
