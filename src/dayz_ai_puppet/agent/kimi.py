"""Kimi 2.6 Vision API client using the OpenAI SDK."""

from __future__ import annotations

import json
import logging
import re
import time
from collections import deque
from typing import Any

from openai import OpenAI

from dayz_ai_puppet.agent.actions import Action, ActionType, parse_actions
from dayz_ai_puppet.agent.prompts import build_system_prompt, format_game_state
from dayz_ai_puppet.config import Settings

log = logging.getLogger(__name__)


class DayZAgent:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(
            api_key=settings.kimi_api_key,
            base_url=settings.kimi_base_url,
        )
        self.model = settings.kimi_model
        self.short_term_memory: deque[dict[str, Any]] = deque(maxlen=settings.max_short_term_memory)

    def decide(
        self,
        screenshot_b64: str,
        game_state: dict[str, Any] | None = None,
        lessons: list[str] | None = None,
    ) -> list[Action]:
        messages = self._build_messages(screenshot_b64, game_state, lessons)

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=512,
                    temperature=0.3,
                )
                text = response.choices[0].message.content or ""
                actions = self._parse_response(text)
                self.short_term_memory.append({"role": "assistant", "content": text})
                return actions
            except Exception as exc:
                log.warning("API call attempt %d failed: %s", attempt + 1, exc)
                if attempt < 2:
                    time.sleep(2 ** attempt)

        log.error("all API attempts failed, returning STOP")
        return [Action(type=ActionType.STOP)]

    def _build_messages(
        self,
        screenshot_b64: str,
        game_state: dict[str, Any] | None,
        lessons: list[str] | None,
    ) -> list[dict[str, Any]]:
        location = ""
        vitals = None
        if game_state:
            pos = game_state.get("position")
            if pos:
                location = f"({pos[0]:.0f}, {pos[1]:.0f}, {pos[2]:.0f})"
            vitals = {
                "health": game_state.get("health", 100),
                "blood": game_state.get("blood", 5000),
                "energy": game_state.get("energy", 100),
                "water": game_state.get("water", 100),
            }

        system_prompt = build_system_prompt(lessons=lessons, location=location, vitals=vitals)

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
        ]

        messages.extend(list(self.short_term_memory))

        state_text = ""
        if game_state:
            state_text = format_game_state(
                health=game_state.get("health", 100),
                blood=game_state.get("blood", 5000),
                energy=game_state.get("energy", 100),
                water=game_state.get("water", 100),
                position=tuple(game_state.get("position", (0, 0, 0))),
                direction=tuple(game_state.get("direction", (1, 0, 0))),
                inventory=game_state.get("inventory", []),
                hands_item=game_state.get("hands_item", ""),
                nearby_entities=game_state.get("nearby_entities", []),
                time_of_day=game_state.get("time_of_day", ""),
                temperature=game_state.get("temperature", 36.0),
            )

        user_content: list[dict[str, Any]] = []
        if state_text:
            user_content.append({"type": "text", "text": state_text})
        user_content.append({
            "type": "image_url",
            "image_url": {"url": screenshot_b64},
        })

        messages.append({"role": "user", "content": user_content})
        return messages

    def _parse_response(self, text: str) -> list[Action]:
        json_match = re.search(r"\{[\s\S]*\}", text)
        if not json_match:
            log.warning("no JSON found in response: %s", text[:200])
            return [Action(type=ActionType.STOP)]

        try:
            data = json.loads(json_match.group())
            return parse_actions(data)
        except json.JSONDecodeError as exc:
            log.warning("JSON parse error: %s — text: %s", exc, text[:200])
            return [Action(type=ActionType.STOP)]
