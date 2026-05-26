"""GPS navigation with Chernarus landmark database."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Landmark:
    name: str
    x: float
    z: float
    category: str  # city, military, medical, industrial, coastal


CHERNARUS_LANDMARKS: list[Landmark] = [
    Landmark("Chernogorsk", 6600, 2600, "city"),
    Landmark("Elektrozavodsk", 10400, 2200, "city"),
    Landmark("Berezino", 12200, 3400, "city"),
    Landmark("Svetloyarsk", 13800, 3800, "city"),
    Landmark("Solnichniy", 13200, 4400, "city"),
    Landmark("Kamyshovo", 12000, 3600, "city"),
    Landmark("Krasnostav", 11200, 5800, "city"),
    Landmark("Gorka", 9400, 5600, "city"),
    Landmark("Novy Sobor", 7200, 6000, "city"),
    Landmark("Stary Sobor", 6400, 6200, "city"),
    Landmark("Vybor", 3800, 6600, "city"),
    Landmark("Zelenogorsk", 2800, 5200, "city"),
    Landmark("Bor", 4800, 5400, "city"),
    Landmark("Nadezhdino", 6200, 4800, "city"),
    Landmark("Mogilevka", 8200, 5400, "city"),
    Landmark("Balota", 4800, 2400, "city"),
    Landmark("Komarovo", 3600, 2200, "city"),
    Landmark("Kamenka", 1800, 2200, "city"),
    Landmark("NWAF (Vybor side)", 4600, 7800, "military"),
    Landmark("NWAF (Stary side)", 5800, 7600, "military"),
    Landmark("NWAF South Barracks", 5000, 7200, "military"),
    Landmark("NEAF", 11600, 7400, "military"),
    Landmark("Myshkino", 1800, 6400, "city"),
    Landmark("Pustoshka", 2800, 7000, "city"),
    Landmark("Grishino", 6400, 8400, "city"),
    Landmark("Petrovka", 9600, 8600, "city"),
    Landmark("Tulga", 13200, 3000, "city"),
    Landmark("Prigorodki", 8000, 3200, "city"),
    Landmark("Chapaevsk", 6200, 3400, "city"),
    Landmark("Nizhnoye", 13000, 4800, "city"),
    Landmark("Olsha", 13800, 4400, "city"),
    Landmark("Dubrovka", 10600, 5800, "city"),
    Landmark("Polana", 9800, 6400, "city"),
    Landmark("Orlovets", 11400, 6000, "city"),
    Landmark("Msta", 10800, 5000, "city"),
    Landmark("Staroye", 9800, 4800, "city"),
    Landmark("Dolina", 8600, 5000, "city"),
    Landmark("Shakhovka", 10200, 6200, "city"),
    Landmark("Guglovo", 8200, 6200, "city"),
    Landmark("Pulkovo", 6800, 5800, "city"),
    Landmark("Kabanino", 5400, 6600, "city"),
    Landmark("Lopatino", 2800, 8200, "city"),
    Landmark("Tisy Military Base", 1600, 8600, "military"),
]


class GPSNavigator:
    def __init__(self, landmarks: list[Landmark] | None = None) -> None:
        self.landmarks = landmarks or CHERNARUS_LANDMARKS

    def bearing(
        self,
        from_pos: tuple[float, float, float],
        to_pos: tuple[float, float, float],
    ) -> float:
        fx, _, fz = from_pos
        tx, _, tz = to_pos
        dx = tx - fx
        dz = tz - fz
        angle = math.degrees(math.atan2(dx, dz))
        return angle % 360

    def distance(
        self,
        from_pos: tuple[float, float, float],
        to_pos: tuple[float, float, float],
    ) -> float:
        fx, _, fz = from_pos
        tx, _, tz = to_pos
        return math.sqrt((tx - fx) ** 2 + (tz - fz) ** 2)

    def nearest_landmark(self, position: tuple[float, float, float]) -> Landmark:
        best = self.landmarks[0]
        best_dist = float("inf")
        for lm in self.landmarks:
            d = math.sqrt((position[0] - lm.x) ** 2 + (position[2] - lm.z) ** 2)
            if d < best_dist:
                best_dist = d
                best = lm
        return best

    def direction_to(
        self, from_pos: tuple[float, float, float], landmark_name: str
    ) -> tuple[float, float]:
        target = self._find_landmark(landmark_name)
        if target is None:
            return 0.0, 0.0
        target_pos = (target.x, 0, target.z)
        return self.bearing(from_pos, target_pos), self.distance(from_pos, target_pos)

    def landmarks_within(
        self,
        position: tuple[float, float, float],
        radius: float,
    ) -> list[tuple[Landmark, float]]:
        results: list[tuple[Landmark, float]] = []
        for lm in self.landmarks:
            d = math.sqrt((position[0] - lm.x) ** 2 + (position[2] - lm.z) ** 2)
            if d <= radius:
                results.append((lm, d))
        results.sort(key=lambda x: x[1])
        return results

    def _find_landmark(self, name: str) -> Landmark | None:
        lower = name.lower()
        for lm in self.landmarks:
            if lm.name.lower() == lower:
                return lm
        return None
