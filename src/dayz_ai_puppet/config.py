"""Configuration loaded from environment variables and .env file."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configurable parameters for the DayZ AI Puppet controller.

    Values are loaded from environment variables or a .env file in the
    project root. See .env.example for documentation of each variable.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Kimi API ──────────────────────────────────────────────────────
    kimi_api_key: str = ""
    kimi_base_url: str = "https://api.moonshot.ai/v1"
    kimi_model: str = "kimi-k2.6"

    # ── AI Controller ─────────────────────────────────────────────────
    tick_rate: float = 2.0  # seconds between decision cycles
    log_level: str = "INFO"

    # ── Screen Capture ────────────────────────────────────────────────
    capture_width: int = 1280
    capture_height: int = 720
    capture_monitor: int = 1  # 1-based; 1 = primary monitor
    capture_quality: int = 85  # JPEG quality 1-100

    # ── Server State Bridge ───────────────────────────────────────────
    server_state_url: str = "http://localhost:8080/ai-state"
    server_state_file: str = ""  # fallback: absolute path to state JSON
    server_state_timeout: float = 5.0

    # ── Memory & Learning ─────────────────────────────────────────────
    memory_path: str = "data/experience_memory.json"
    max_short_term_memory: int = 20

    # ── Reflexes ──────────────────────────────────────────────────────
    reflex_enabled: bool = True
    reflex_melee_range: float = 3.0  # metres
    reflex_low_health_threshold: float = 0.3  # fraction of max health

    # ── Navigation ────────────────────────────────────────────────────
    landmark_db_path: str = "data/landmarks.json"
