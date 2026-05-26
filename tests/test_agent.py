from unittest.mock import MagicMock, patch

from dayz_ai_puppet.agent.actions import ActionType
from dayz_ai_puppet.agent.kimi import DayZAgent


def _make_agent():
    with patch("dayz_ai_puppet.agent.kimi.OpenAI"):
        from dayz_ai_puppet.config import Settings
        s = Settings(kimi_api_key="test-key")
        return DayZAgent(s)


class TestDayZAgentBuildMessages:
    def test_basic_messages(self):
        agent = _make_agent()
        msgs = agent._build_messages("data:image/jpeg;base64,abc123", None, None)
        assert msgs[0]["role"] == "system"
        assert msgs[-1]["role"] == "user"
        user_content = msgs[-1]["content"]
        assert any(c["type"] == "image_url" for c in user_content)

    def test_with_game_state(self, sample_game_state):
        agent = _make_agent()
        msgs = agent._build_messages("data:image/jpeg;base64,abc", sample_game_state, None)
        user_content = msgs[-1]["content"]
        text_parts = [c for c in user_content if c["type"] == "text"]
        assert len(text_parts) == 1
        assert "85" in text_parts[0]["text"]

    def test_with_lessons(self):
        agent = _make_agent()
        msgs = agent._build_messages("data:image/jpeg;base64,abc", None, ["Avoid zombies"])
        system = msgs[0]["content"]
        assert "Avoid zombies" in system


class TestDayZAgentParseResponse:
    def test_valid_json(self):
        agent = _make_agent()
        text = '{"action": "move", "params": {"forward": 1}}'
        actions = agent._parse_response(text)
        assert len(actions) == 1
        assert actions[0].type == ActionType.MOVE

    def test_json_in_text(self):
        agent = _make_agent()
        text = 'I think we should go forward. {"action": "run", "thought": "fleeing"}'
        actions = agent._parse_response(text)
        assert len(actions) == 1
        assert actions[0].type == ActionType.RUN

    def test_no_json_returns_stop(self):
        agent = _make_agent()
        actions = agent._parse_response("just plain text no json")
        assert len(actions) == 1
        assert actions[0].type == ActionType.STOP


class TestDayZAgentDecide:
    def test_successful_call(self):
        agent = _make_agent()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"action": "stop"}'
        agent.client.chat.completions.create.return_value = mock_response

        actions = agent.decide("data:image/jpeg;base64,abc")
        assert len(actions) == 1
        assert actions[0].type == ActionType.STOP

    def test_retry_on_failure(self):
        agent = _make_agent()
        agent.client.chat.completions.create.side_effect = Exception("timeout")
        actions = agent.decide("data:image/jpeg;base64,abc")
        assert len(actions) == 1
        assert actions[0].type == ActionType.STOP
        assert agent.client.chat.completions.create.call_count == 3

    def test_short_term_memory_populated(self):
        agent = _make_agent()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"action": "crouch"}'
        agent.client.chat.completions.create.return_value = mock_response

        agent.decide("data:image/jpeg;base64,abc")
        assert len(agent.short_term_memory) == 1
