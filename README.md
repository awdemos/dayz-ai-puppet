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

### What You Need

| Requirement | Why | Where |
|-------------|-----|-------|
| **Python 3.11+** | Runs the AI controller | [python.org](https://python.org) or Windows Store |
| **Windows** | `pydirectinput` only works on Windows for input injection | — |
| **[uv](https://docs.astral.sh/uv/)** (recommended) or pip | Package manager | `pip install uv` |
| **DayZ** (Steam) | The game the AI plays | [Steam Store](https://store.steampowered.com/app/221100/DayZ/) |
| **DayZ server** | Hosts the `@DayZAIPuppet` mod | Local or rented |
| **Kimi API key** | Access to the Kimi 2.6 Vision model | [platform.moonshot.cn](https://platform.moonshot.cn) |

> **No Windows?** You can develop and run tests on Linux/macOS — just can't inject input into a DayZ client without Windows. Set `KIMI_API_KEY` to test the agent's decision-making without a game.

---

### Step 1: Get a Kimi API Key

1. Go to [platform.moonshot.cn](https://platform.moonshot.cn) and create an account
2. Navigate to **API Keys** in the dashboard
3. Click **Create new key** and copy it
4. You'll need this for the `.env` file in Step 3

The free tier includes enough credits for testing. The API uses the OpenAI-compatible format, so the project talks to it via the standard `openai` Python SDK.

---

### Step 2: Install the AI Controller

```bash
# Clone the repo
git clone https://github.com/awdemos/dayz-ai-puppet.git
cd dayz-ai-puppet

# Install dependencies (using uv — recommended)
uv venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS (for dev/testing only)
uv pip install -e ".[dev]"

# Or with plain pip
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Verify the install:

```bash
python -c "import dayz_ai_puppet; print('OK')"
# Should print: OK

python -m dayz_ai_puppet --help
# Should print CLI usage
```

Run the test suite:

```bash
python -m pytest tests/ -v
# All 76 tests should pass
```

---

### Step 3: Configure

```bash
cp .env.example .env
```

Edit `.env` — the only required setting is your API key:

```ini
KIMI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

Everything else has sensible defaults. See the full [configuration table](#configuration) below.

---

### Step 4: Install the DayZ Server Mod

The server mod runs on your DayZ server (not the client machine). It spawns an AI-controlled player and writes its state (health, position, inventory, nearby entities) to a JSON file the Python controller reads.

**Install on the server:**

1. Copy the entire `server-mod/@DayZAIPuppet/` folder to your DayZ server's mod directory:
   - Typically: `C:\Program Files (x86)\Steam\steamapps\common\DayZServer\`
   - The `@DayZAIPuppet` folder should sit alongside other `@ModName` folders

2. Add the mod to your server's startup parameters:
   ```
   -mod=@DayZAIPuppet
   ```
   If you already have mods: `-mod=@OtherMod;@DayZAIPuppet`

3. Start (or restart) the DayZ server

**Configure the AI player** (optional):

Create a config file at the server's profile directory. On a typical DayZ server this is:

```
C:\Users\<username>\AppData\Local\DayZ\profiles\DayZAIPuppet\config.json
```

Or on a dedicated server: `<server-root>\profiles\DayZAIPuppet\config.json`

```json
{
  "spawn_position": [6000, 0, 6000],
  "export_interval_seconds": 2,
  "starter_loadout": ["Rag", "Flashlight", "Battery9V"]
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `spawn_position` | `[6000, 0, 6000]` | X, Y, Z coordinates to spawn the AI player (near the center of Chernarus) |
| `export_interval_seconds` | `2` | How often the mod writes `state.json` |
| `starter_loadout` | `["Rag", "Flashlight", "Battery9V"]` | Items to put in the AI player's inventory on spawn |

The mod writes player state to `$profile:DayZAIPuppet/state.json` continuously. This is how the Python controller knows the AI's health, position, and surroundings.

---

### Step 5: Connect the Controller to the Server State

The Python controller needs to read the state file the server mod produces. Two options:

**Option A: Shared file (simplest — server and controller on same machine)**

Set `SERVER_STATE_FILE` in `.env` to the path where the mod writes `state.json`:

```ini
SERVER_STATE_FILE=C:\Users\you\AppData\Local\DayZ\profiles\DayZAIPuppet\state.json
```

**Option B: File sync / network share (server and controller on different machines)**

Use a network share, SMB mount, or a tool like `rsync`/`syncthing` to make the server's `state.json` accessible to the controller machine, then point `SERVER_STATE_FILE` at it.

---

### Step 6: Run

Start DayZ on the client machine, load into the server where the mod is installed, then run the controller:

```bash
python -m dayz_ai_puppet
```

The controller will start the see-think-act loop:
1. Captures a screenshot of the DayZ window
2. Reads the AI player's state from the server mod
3. Checks hardcoded reflexes (being shot → go prone, infected nearby → attack, low health → heal)
4. Sends the screenshot + state to Kimi 2.6 Vision API for a decision
5. Executes the returned actions (movement, looking, interacting, etc.)
6. Repeats every 2 seconds (configurable via `TICK_RATE`)

Press `Ctrl+C` to stop. The controller handles graceful shutdown — it releases all held keys.

#### CLI Options

```
python -m dayz_ai_puppet [OPTIONS]

--config PATH       Path to .env file (default: .env)
--tick-rate FLOAT   Seconds between decision cycles (default: 2.0)
--log-level LEVEL   DEBUG, INFO, WARNING, ERROR (default: INFO)
--no-reflexes       Disable hardcoded combat reflexes
--monitor INT       Monitor index for screen capture (1=primary)
```

#### Quick Test Without DayZ

To verify the AI controller can talk to the Kimi API without needing DayZ running:

```bash
python -c "
from dayz_ai_puppet.config import Settings
from dayz_ai_puppet.agent.kimi import DayZAgent

s = Settings()  # reads from .env
agent = DayZAgent(s)
# Test with a dummy state — no screenshot
state = {'health': 1.0, 'position': [6000, 0, 6000]}
print('Agent initialized. API key loaded:', bool(s.kimi_api_key))
"
```

---

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'dayz_ai_puppet'` | Make sure you ran `pip install -e ".[dev]"` and activated the venv |
| `RuntimeError: pydirectinput requires Windows` | Input injection only works on Windows. You can test everything else on Linux/macOS |
| `openai.AuthenticationError` | Check your `KIMI_API_KEY` in `.env` is correct |
| `openai.RateLimitError` | You're hitting Kimi API limits. Increase `TICK_RATE` (e.g., 3.0 or 5.0) |
| Controller starts but DayZ doesn't react | Make sure DayZ is the focused window. The controller sends input to whatever window is active |
| No state.json from server mod | Check the mod is loaded: look for `@DayZAIPuppet` in the server's startup log. Verify the config path exists |
| Tests fail on Linux | Some tests mock Windows-only modules — they should still pass. Run `python -m pytest tests/ -v` and check specific failures |

---

## Configuration

All settings are loaded from environment variables or a `.env` file. See `.env.example` for the full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `KIMI_API_KEY` | *(required)* | Moonshot AI API key — get one at [platform.moonshot.cn](https://platform.moonshot.cn) |
| `KIMI_BASE_URL` | `https://api.moonshot.ai/v1` | API endpoint (don't change unless you know what you're doing) |
| `KIMI_MODEL` | `kimi-k2.6` | Model identifier |
| `TICK_RATE` | `2.0` | Seconds between decision cycles — increase if hitting API rate limits |
| `CAPTURE_WIDTH` | `1280` | Screenshot resize width (lower = faster API calls, less detail) |
| `CAPTURE_HEIGHT` | `720` | Screenshot resize height |
| `CAPTURE_MONITOR` | `1` | Monitor index for screen capture (1 = primary monitor) |
| `CAPTURE_QUALITY` | `85` | JPEG quality 1–100 (lower = smaller images, faster uploads) |
| `SERVER_STATE_URL` | `http://localhost:8080/ai-state` | HTTP endpoint for game state (if available) |
| `SERVER_STATE_FILE` | *(empty)* | File path to `state.json` from the server mod (fallback if HTTP unavailable) |
| `SERVER_STATE_TIMEOUT` | `5.0` | HTTP request timeout in seconds |
| `MEMORY_PATH` | `data/experience_memory.json` | Path to store learned experience (deaths, successes) |
| `MAX_SHORT_TERM_MEMORY` | `20` | Number of recent interactions kept in context |
| `REFLEX_ENABLED` | `true` | Enable hardcoded combat reflexes (prone when shot, attack infected, heal when low) |
| `REFLEX_MELEE_RANGE` | `3.0` | Distance in meters to trigger melee reflex on infected |
| `REFLEX_LOW_HEALTH_THRESHOLD` | `0.3` | Health fraction (0–1) below which the heal reflex triggers |
| `LANDMARK_DB_PATH` | `data/landmarks.json` | Path to custom landmark database (built-in Chernarus landmarks used if absent) |
| `LOG_LEVEL` | `INFO` | Logging verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

---

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

## License

MIT
