# DayZ AI Puppet

Embodied AI agent for DayZ — sees through a puppet client, thinks with Kimi 2.6 Vision, acts via input injection.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  DayZ Client    │     │  AI Controller   │     │  Kimi 2.6       │
│  (Windows)      │◄───►│  (Python)        │◄───►│  Vision API     │
│                 │     │                  │     │  (Moonshot AI)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        ▲                        ▲
        │                        │
        ▼                        ▼
┌─────────────────┐     ┌──────────────────┐
│  Screen Capture │     │  DayZ Server Mod │
│  (mss)          │     │  (Enforce Script)│
└─────────────────┘     └──────────────────┘
```

Three components work together:

1. **AI Controller (Python)** — Captures screenshots, sends them to Kimi 2.6 Vision API, parses JSON actions, injects keyboard/mouse input into the DayZ client
2. **DayZ Server Mod (Enforce Script)** — Spawns and tracks an AI player entity on the server, exports game state (health, inventory, position, nearby entities) to a JSON file
3. **Kimi 2.6 Vision API** — Multimodal LLM that receives screenshots + game state text and returns survival decisions as JSON

### Decision Hierarchy

- **Reflexes** (hardcoded, sub-100ms): Prone when shot, melee when infected is close, heal when low health
- **LLM Strategy** (Kimi 2.6, ~2s): All other decisions — movement, looting, navigation, combat tactics
- **Experience Memory** (RAG): Records deaths and successes; injects relevant past lessons into prompts based on geographic proximity

## Project Status

**This is untested, experimental code.** It has not been validated against a running DayZ instance. The project includes unit tests (76 passing) for the Python modules with mocked I/O, but no integration or end-to-end testing has been performed. The DayZ server mod has not been compiled or tested in-game.

Use at your own risk. Expect bugs, missing edge cases, and API incompatibilities.

## Setup

### Prerequisites

- Python 3.11+
- Windows (for pydirectinput input injection — the controller will not inject input on Linux/macOS)
- A DayZ server with the `@DayZAIPuppet` mod installed
- A Kimi API key from [platform.moonshot.cn](https://platform.moonshot.cn)

### Install

```bash
# Clone
git clone https://github.com/awdemos/dayz-ai-puppet.git
cd dayz-ai-puppet

# Create venv and install
uv venv
uv pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env and add your KIMI_API_KEY
```

### Run

```bash
python -m dayz_ai_puppet
```

CLI options:

```
--config PATH       Path to .env file (default: .env)
--tick-rate FLOAT   Seconds between decision cycles (default: 2.0)
--log-level LEVEL   DEBUG, INFO, WARNING, ERROR (default: INFO)
--no-reflexes       Disable hardcoded combat reflexes
--monitor INT       Monitor index for screen capture (1=primary)
```

### DayZ Server Mod

1. Copy `server-mod/@DayZAIPuppet/` into your DayZ server's mod directory
2. Add `@DayZAIPuppet` to your server's `-mod=` launch parameter
3. Optionally create `$profile:DayZAIPuppet/config.json`:

```json
{
  "spawn_position": [6000, 0, 6000],
  "export_interval_seconds": 2,
  "starter_loadout": ["Rag", "Flashlight", "Battery9V"]
}
```

The mod writes player state to `$profile:DayZAIPuppet/state.json` every few seconds. The Python controller reads this file (or polls HTTP if available).

## Module Reference

| Module | Description |
|--------|-------------|
| `config.py` | Environment variable configuration via pydantic-settings |
| `vision/capture.py` | Screen capture with mss, resize, base64 JPEG encoding |
| `input/controller.py` | Keyboard/mouse input injection via pydirectinput |
| `agent/kimi.py` | Kimi 2.6 Vision API client using OpenAI SDK |
| `agent/actions.py` | Action types, JSON parsing, parameter validation |
| `agent/prompts.py` | System prompt construction and game state formatting |
| `memory/experience.py` | Death/success recording with JSON persistence |
| `memory/vector_store.py` | Proximity-based and feature-based similarity search |
| `navigation/gps.py` | Chernarus landmark database, bearing/distance calculations |
| `reflexes/combat.py` | Hardcoded combat reflexes (prone, melee, heal) |
| `server/state_client.py` | HTTP/file game state polling with retry |
| `loop.py` | Main see-think-act loop |
| `__main__.py` | CLI entry point with signal handling |

## Configuration

All settings are loaded from environment variables or a `.env` file. See `.env.example` for the full list.

Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `KIMI_API_KEY` | *(required)* | Moonshot AI API key |
| `KIMI_BASE_URL` | `https://api.moonshot.ai/v1` | API endpoint |
| `KIMI_MODEL` | `kimi-k2.6` | Model identifier |
| `TICK_RATE` | `2.0` | Seconds between decision cycles |
| `CAPTURE_WIDTH` | `1280` | Screenshot resize width |
| `CAPTURE_HEIGHT` | `720` | Screenshot resize height |
| `REFLEX_ENABLED` | `true` | Enable hardcoded combat reflexes |

## License

MIT
