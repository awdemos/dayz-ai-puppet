"""HTTP and file-based client for DayZ server mod game state."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

log = logging.getLogger(__name__)


@dataclass
class GameState:
    health: float = 100.0
    blood: float = 5000.0
    energy: float = 100.0
    water: float = 100.0
    stamina: float = 100.0
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    direction: tuple[float, float, float] = (1.0, 0.0, 0.0)
    nearby_entities: list[dict[str, Any]] = field(default_factory=list)
    inventory: list[str] = field(default_factory=list)
    hands_item: str = ""
    bleeding: bool = False
    recent_damage: float = 0.0
    max_health: float = 100.0
    time_of_day: str = ""
    temperature: float = 36.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "health": self.health,
            "blood": self.blood,
            "energy": self.energy,
            "water": self.water,
            "stamina": self.stamina,
            "position": list(self.position),
            "direction": list(self.direction),
            "nearby_entities": self.nearby_entities,
            "inventory": self.inventory,
            "hands_item": self.hands_item,
            "bleeding": self.bleeding,
            "recent_damage": self.recent_damage,
            "max_health": self.max_health,
            "time_of_day": self.time_of_day,
            "temperature": self.temperature,
        }


class ServerStateClient:
    def __init__(
        self,
        url: str = "http://localhost:8080/ai-state",
        fallback_file: str = "",
        timeout: float = 5.0,
        max_retries: int = 3,
    ) -> None:
        self.url = url
        self.fallback_file = fallback_file
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.Client(timeout=timeout)

    def get_state(self) -> GameState:
        for attempt in range(self.max_retries):
            try:
                resp = self._client.get(self.url)
                resp.raise_for_status()
                data = resp.json()
                return self._parse_state(data)
            except Exception as exc:
                log.debug("HTTP state fetch attempt %d failed: %s", attempt + 1, exc)
                if attempt < self.max_retries - 1:
                    time.sleep(0.5 * (2 ** attempt))

        if self.fallback_file:
            return self._read_file_state()

        log.warning("all state fetch methods failed, returning defaults")
        return GameState()

    def close(self) -> None:
        self._client.close()

    def _parse_state(self, data: dict[str, Any]) -> GameState:
        pos = data.get("position", [0, 0, 0])
        direction = data.get("direction", [1, 0, 0])
        return GameState(
            health=float(data.get("health", 100)),
            blood=float(data.get("blood", 5000)),
            energy=float(data.get("energy", 100)),
            water=float(data.get("water", 100)),
            stamina=float(data.get("stamina", 100)),
            position=tuple(float(v) for v in pos[:3]),
            direction=tuple(float(v) for v in direction[:3]),
            nearby_entities=data.get("nearby_entities", []),
            inventory=data.get("inventory", []),
            hands_item=data.get("hands_item", ""),
            bleeding=bool(data.get("bleeding", False)),
            recent_damage=float(data.get("recent_damage", 0)),
            max_health=float(data.get("max_health", 100)),
            time_of_day=data.get("time_of_day", ""),
            temperature=float(data.get("temperature", 36.0)),
        )

    def _read_file_state(self) -> GameState:
        path = Path(self.fallback_file)
        if not path.exists():
            log.warning("fallback file not found: %s", path)
            return GameState()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return self._parse_state(data)
        except Exception as exc:
            log.warning("failed to read fallback file: %s", exc)
            return GameState()
