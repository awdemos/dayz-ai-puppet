"""Hardcoded reflex layer for sub-second reactions bypassing the LLM."""

from __future__ import annotations

import logging
from typing import Any

from dayz_ai_puppet.agent.actions import Action, ActionType
from dayz_ai_puppet.config import Settings

log = logging.getLogger(__name__)


class ReflexCondition:
    def __init__(self, name: str, check_fn, action: ActionType, priority: int = 0) -> None:
        self.name = name
        self.check_fn = check_fn
        self.action = action
        self.priority = priority


class CombatReflexes:
    def __init__(self, settings: Settings) -> None:
        self.melee_range = settings.reflex_melee_range
        self.low_health_threshold = settings.reflex_low_health_threshold
        self._conditions = [
            ReflexCondition(
                "under_attack", self._check_under_attack,
                ActionType.PRONE, priority=10,
            ),
            ReflexCondition("melee_range", self._check_melee_range, ActionType.SHOOT, priority=8),
            ReflexCondition("low_health", self._check_low_health, ActionType.HEAL, priority=6),
        ]

    def check(self, game_state: dict[str, Any]) -> Action | None:
        for condition in sorted(self._conditions, key=lambda c: -c.priority):
            if condition.check_fn(game_state):
                log.info("reflex triggered: %s → %s", condition.name, condition.action.value)
                return Action(
                    type=condition.action,
                    thought=f"reflex:{condition.name}",
                )
        return None

    def _check_under_attack(self, state: dict[str, Any]) -> bool:
        recent_damage = state.get("recent_damage", 0)
        is_bleeding = state.get("bleeding", False)
        return recent_damage > 0 or is_bleeding

    def _check_melee_range(self, state: dict[str, Any]) -> bool:
        nearby = state.get("nearby_entities", [])
        for entity in nearby:
            dist = entity.get("distance", float("inf"))
            etype = entity.get("type", "").lower()
            if dist <= self.melee_range and "infected" in etype:
                return True
        return False

    def _check_low_health(self, state: dict[str, Any]) -> bool:
        health = state.get("health", 100)
        max_health = state.get("max_health", 100)
        if max_health <= 0:
            return False
        return (health / max_health) < self.low_health_threshold
