"""System prompt construction and game state formatting."""

from __future__ import annotations

from typing import Any

SURVIVAL_SYSTEM_PROMPT = """\
You are a DayZ survival AI controlling a player character in real-time.
You receive a screenshot from the game and text describing your current state.
You must output a single JSON action to survive.

## Output Format

Output ONLY a JSON object:
{
  "thought": "brief reasoning for your decision",
  "action": "<action_type>",
  "params": { ... }
}

## Available Actions

| Action     | Parameters                                  | Description                    |
|------------|---------------------------------------------|--------------------------------|
| move       | forward: float, right: float, duration: sec | Walk (-1 to 1 each axis)      |
| look       | pitch: float, yaw: float                    | Relative mouse look            |
| interact   | {}                                          | Press F (doors, items)         |
| inventory  | {}                                          | Toggle inventory (Tab)         |
| shoot      | {}                                          | Fire weapon / melee attack     |
| crouch     | {}                                          | Toggle crouch                  |
| prone      | {}                                          | Toggle prone                   |
| run        | {}                                          | Start sprinting (hold Shift)   |
| stop       | {}                                          | Release all movement keys      |
| heal       | {}                                          | Use bandage / medkit in hands  |

## Survival Priorities (highest first)

1. Immediate threats: under attack → prone + assess
2. Health: bleeding, low blood → bandage/heal
3. Hunger/thirst: find food and water
4. Avoid infected (zombies) — evade unless cornered
5. Avoid hostile players unless armed with firearm
6. Loot buildings for better gear
7. Stay warm (temperature management)

## Decision Rules

- If you see an infected within 20m and you are unarmed → move away stealthily
- If you see a building within 30m and have not looted it → approach and enter
- If you are hungry/thirsty and see items → pick them up
- If you see a player with a weapon raised → find cover immediately
- Never sprint in open areas near cities
- Check corners when entering buildings
"""


def build_system_prompt(
    lessons: list[str] | None = None,
    location: str = "",
    vitals: dict[str, Any] | None = None,
) -> str:
    parts = [SURVIVAL_SYSTEM_PROMPT]

    if lessons:
        lesson_text = "\n".join(f"- {lesson}" for lesson in lessons)
        parts.append(f"\n## Past Lessons From This Area\n{lesson_text}")

    if location:
        parts.append(f"\n## Current Location\n{location}")

    return "\n".join(parts)


def format_game_state(
    health: float,
    blood: float,
    energy: float,
    water: float,
    position: tuple[float, float, float] | None = None,
    direction: tuple[float, float, float] | None = None,
    inventory: list[str] | None = None,
    hands_item: str = "",
    nearby_entities: list[dict[str, Any]] | None = None,
    time_of_day: str = "",
    temperature: float = 36.0,
) -> str:
    lines = [
        f"Health: {health:.0f}% | Blood: {blood:.0f} | "
        f"Hunger: {energy:.0f}% | Thirst: {water:.0f}% | "
        f"Temp: {temperature:.1f}C",
    ]

    if inventory:
        lines.append(f"Inventory: {', '.join(inventory)}")

    if hands_item:
        lines.append(f"In Hands: {hands_item}")

    if position:
        lines.append(f"Position: ({position[0]:.1f}, {position[1]:.1f}, {position[2]:.1f})")

    if direction:
        lines.append(f"Facing: ({direction[0]:.2f}, {direction[1]:.2f}, {direction[2]:.2f})")

    if nearby_entities:
        entities_str = "; ".join(
            f"{e.get('type', 'unknown')} "
            f"({e.get('distance', '?')}m {e.get('direction', '')})"
            for e in nearby_entities
        )
        lines.append(f"Nearby: {entities_str}")

    if time_of_day:
        lines.append(f"Time: {time_of_day}")

    return "\n".join(lines)
