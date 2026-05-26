"""Action types and parameter validation for the AI controller."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ActionType(Enum):
    MOVE = "move"
    LOOK = "look"
    INTERACT = "interact"
    INVENTORY = "inventory"
    SHOOT = "shoot"
    CROUCH = "crouch"
    PRONE = "prone"
    RUN = "run"
    STOP = "stop"
    HEAL = "heal"


@dataclass
class Action:
    type: ActionType
    params: dict[str, Any] = field(default_factory=dict)
    thought: str = ""

    @property
    def duration(self) -> float:
        return self.params.get("duration", 1.0)

    def is_valid(self) -> bool:
        return _validate_action(self)


def parse_actions(raw: str | dict[str, Any]) -> list[Action]:
    """Parse an LLM response into a list of Actions.

    Accepts either a JSON string or a pre-parsed dict. The LLM is
    expected to return either a single action object or a list of them.
    """
    if isinstance(raw, str):
        data = json.loads(raw)
    else:
        data = raw

    if isinstance(data, list):
        items = data
    elif "actions" in data and isinstance(data["actions"], list):
        items = data["actions"]
    else:
        items = [data]

    results: list[Action] = []
    for item in items:
        action = _parse_single(item)
        if action is not None:
            results.append(action)
    return results


def _parse_single(data: dict[str, Any]) -> Action | None:
    action_name = data.get("action", "")
    try:
        action_type = ActionType(action_name.lower())
    except ValueError:
        return None

    return Action(
        type=action_type,
        params=data.get("params", {}),
        thought=data.get("thought", ""),
    )


def _validate_action(action: Action) -> bool:
    t = action.type
    p = action.params

    if t == ActionType.MOVE:
        return isinstance(p.get("forward", 0), (int, float)) and isinstance(
            p.get("right", 0), (int, float)
        )

    if t == ActionType.LOOK:
        return isinstance(p.get("pitch", 0), (int, float)) or isinstance(
            p.get("yaw", 0), (int, float)
        )

    return True
