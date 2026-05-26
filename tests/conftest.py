from __future__ import annotations

import pytest

from dayz_ai_puppet.config import Settings


@pytest.fixture
def settings():
    return Settings(
        kimi_api_key="test-key",
        tick_rate=0.1,
        capture_width=640,
        capture_height=480,
        capture_monitor=1,
        capture_quality=80,
        server_state_url="http://localhost:9999/state",
        memory_path="/tmp/test_memory.json",
        reflex_melee_range=3.0,
        reflex_low_health_threshold=0.3,
    )


@pytest.fixture
def sample_game_state():
    return {
        "health": 85,
        "blood": 4500,
        "energy": 60,
        "water": 45,
        "stamina": 90,
        "position": [6600, 50, 2600],
        "direction": [1, 0, 0],
        "inventory": ["Rag", "Apple"],
        "hands_item": "Flashlight",
        "nearby_entities": [],
        "bleeding": False,
        "recent_damage": 0,
        "max_health": 100,
        "time_of_day": "14:30",
        "temperature": 36.5,
    }
