"""Experience memory for recording deaths, successes, and retrieving lessons."""

from __future__ import annotations

import json
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

log = __import__("logging").getLogger(__name__)


@dataclass
class Lesson:
    timestamp: float
    event_type: str  # "death" | "success" | "loot"
    position: tuple[float, float, float]
    summary: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class DeathRecord(Lesson):
    cause: str = ""
    screenshot_b64: str = ""


class ExperienceMemory:
    def __init__(self, path: str = "data/experience_memory.json") -> None:
        self.path = Path(path)
        self.lessons: list[Lesson] = []
        self.load()

    def record_death(
        self,
        cause: str,
        position: tuple[float, float, float],
        screenshot_b64: str = "",
        lesson_learned: str = "",
    ) -> None:
        record = DeathRecord(
            timestamp=time.time(),
            event_type="death",
            position=position,
            summary=lesson_learned or f"Died: {cause}",
            cause=cause,
            screenshot_b64=screenshot_b64,
        )
        self.lessons.append(record)
        self.save()
        log.info("recorded death: %s at (%.0f,%.0f,%.0f)", cause, *position)

    def record_success(
        self,
        event_type: str,
        position: tuple[float, float, float],
        details: str = "",
    ) -> None:
        lesson = Lesson(
            timestamp=time.time(),
            event_type=event_type,
            position=position,
            summary=details,
        )
        self.lessons.append(lesson)
        self.save()
        log.info("recorded success: %s — %s", event_type, details)

    def get_relevant_lessons(
        self,
        position: tuple[float, float, float],
        limit: int = 5,
        max_distance: float = 500.0,
    ) -> list[Lesson]:
        scored: list[tuple[float, Lesson]] = []
        px, _, pz = position
        for lesson in self.lessons:
            lx, _, lz = lesson.position
            dist = math.sqrt((px - lx) ** 2 + (pz - lz) ** 2)
            if dist <= max_distance:
                scored.append((dist, lesson))
        scored.sort(key=lambda x: x[0])
        return [lesson for _, lesson in scored[:limit]]

    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.lessons = [_deserialize_lesson(d) for d in data]
            log.debug("loaded %d lessons from %s", len(self.lessons), self.path)
        except Exception as exc:
            log.warning("failed to load memory from %s: %s", self.path, exc)
            self.lessons = []

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(lesson) for lesson in self.lessons]
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _deserialize_lesson(data: dict[str, Any]) -> Lesson:
    pos = tuple(data.get("position", (0, 0, 0)))
    event = data.get("event_type", "unknown")
    if event == "death":
        return DeathRecord(
            timestamp=data.get("timestamp", 0),
            event_type=event,
            position=pos,
            summary=data.get("summary", ""),
            context=data.get("context", {}),
            cause=data.get("cause", ""),
            screenshot_b64=data.get("screenshot_b64", ""),
        )
    return Lesson(
        timestamp=data.get("timestamp", 0),
        event_type=event,
        position=pos,
        summary=data.get("summary", ""),
        context=data.get("context", {}),
    )
