import json
from unittest.mock import MagicMock

from dayz_ai_puppet.server.state_client import GameState, ServerStateClient


class TestGameState:
    def test_defaults(self):
        gs = GameState()
        assert gs.health == 100
        assert gs.position == (0.0, 0.0, 0.0)
        assert gs.inventory == []

    def test_to_dict(self, sample_game_state):
        gs = GameState(
            health=85, blood=4500, energy=60, water=45,
            position=(6600, 50, 2600), direction=(1, 0, 0),
            inventory=["Rag", "Apple"], hands_item="Flashlight",
        )
        d = gs.to_dict()
        assert d["health"] == 85
        assert d["position"] == [6600, 50, 2600]


class TestServerStateClient:
    def test_http_success(self, sample_game_state):
        client = ServerStateClient(url="http://localhost:9999/state")
        mock_resp = MagicMock()
        mock_resp.json.return_value = sample_game_state
        mock_resp.raise_for_status = MagicMock()
        client._client.get = MagicMock(return_value=mock_resp)

        state = client.get_state()
        assert state.health == 85
        assert state.position == (6600.0, 50.0, 2600.0)
        client.close()

    def test_http_retry_then_fallback_file(self, sample_game_state, tmp_path):
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps(sample_game_state))

        client = ServerStateClient(
            url="http://localhost:9999/state",
            fallback_file=str(state_file),
            max_retries=2,
        )
        client._client.get = MagicMock(side_effect=Exception("conn refused"))

        state = client.get_state()
        assert state.health == 85
        client.close()

    def test_no_fallback_returns_defaults(self):
        client = ServerStateClient(max_retries=1)
        client._client.get = MagicMock(side_effect=Exception("fail"))

        state = client.get_state()
        assert state.health == 100
        client.close()

    def test_missing_fallback_file(self):
        client = ServerStateClient(
            fallback_file="/nonexistent/path.json",
            max_retries=1,
        )
        client._client.get = MagicMock(side_effect=Exception("fail"))

        state = client.get_state()
        assert state.health == 100
        client.close()

    def test_parse_state_partial_data(self):
        client = ServerStateClient()
        partial = {"health": 50}
        gs = client._parse_state(partial)
        assert gs.health == 50
        assert gs.blood == 5000.0
        client.close()
