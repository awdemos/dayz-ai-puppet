# AGENTS.md — dayz-ai-puppet

Agent session entry point for the DayZ AI Puppet controller.

## Start here

1. Read `README.md` for architecture, setup, and the full config table.
2. Review `pyproject.toml` for dependencies and tool configuration.
3. Look at `src/dayz_ai_puppet/` module layout below before editing code.
4. Never commit `.env` files — secrets (`KIMI_API_KEY`) stay local.

## Project layout

```
src/dayz_ai_puppet/
  __main__.py          CLI entry point (signal handling, arg parsing)
  config.py            pydantic-settings environment config
  loop.py              Main see-think-act loop
  agent/
    actions.py         Action dataclasses and JSON parsing
    kimi.py            Kimi 2.6 Vision API client (OpenAI SDK)
    prompts.py         System prompt construction + state formatting
  input/
    controller.py      Keyboard/mouse injection via pydirectinput
  memory/
    experience.py      JSON persistence for deaths/successes
    vector_store.py    Proximity + feature similarity search
  navigation/
    gps.py             Chernarus landmarks, bearing/distance
  reflexes/
    combat.py          Hardcoded combat reflexes (prone/melee/heal)
  server/
    state_client.py    HTTP/file polling for DayZ server state
  vision/
    capture.py         mss screenshot + resize/base64 JPEG
server-mod/@DayZAIPuppet/   DayZ Enforce Script mod (not tested in CI)
```

## Development commands

```bash
# Setup (Python 3.11+, uv recommended)
uv venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
uv pip install -e ".[dev]"

# Run the controller (requires DayZ + Windows for input injection)
python -m dayz_ai_puppet

# Run tests
python -m pytest tests/ -q

# Lint/format
ruff check src tests
ruff format src tests
```

## Key conventions

- `pydantic-settings` loads config from `.env`; copy `.env.example` to `.env` and set `KIMI_API_KEY`.
- pydirectinput only works on Windows; the rest of the Python code can be developed/tested on Linux/macOS.
- Screenshots are resized to `CAPTURE_WIDTH x CAPTURE_HEIGHT` and JPEG-encoded before being sent to the Vision API.
- The server mod writes `state.json` continuously; the controller reads it via `SERVER_STATE_FILE` or `SERVER_STATE_URL`.
- Reflexes run before the LLM call: prone when shot, melee infected within `REFLEX_MELEE_RANGE`, heal below `REFLEX_LOW_HEALTH_THRESHOLD`.

## Gotchas

- `ModuleNotFoundError: No module named 'dayz_ai_puppet'` means the editable install wasn't run (`uv pip install -e ".[dev]"`).
- `RuntimeError: pydirectinput requires Windows` is expected on non-Windows development machines.
- Input injection goes to the currently focused window — DayZ must be focused.
- The project is experimental; integration with a live DayZ server has not been validated.

## Quality gates

Run before committing:

```bash
ruff check src tests
python -m pytest tests/ -q
```
