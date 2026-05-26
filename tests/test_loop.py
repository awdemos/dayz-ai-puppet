from unittest.mock import patch

from dayz_ai_puppet.agent.actions import Action, ActionType
from dayz_ai_puppet.loop import DayZAILoop


def _make_loop():
    with patch("dayz_ai_puppet.loop.DayZVision"), \
         patch("dayz_ai_puppet.loop.DayZInput"), \
         patch("dayz_ai_puppet.loop.DayZAgent"), \
         patch("dayz_ai_puppet.loop.ExperienceMemory"), \
         patch("dayz_ai_puppet.loop.GPSNavigator"), \
         patch("dayz_ai_puppet.loop.ServerStateClient"), \
         patch("dayz_ai_puppet.loop.CombatReflexes"):
        from dayz_ai_puppet.config import Settings
        s = Settings(kimi_api_key="test", tick_rate=0.1, memory_path="/tmp/test_loop.json")
        loop = DayZAILoop(s)
    return loop


class TestDayZAILoop:
    def test_tick_reflex_bypass(self):
        loop = _make_loop()

        loop.vision.capture_base64.return_value = "data:image/jpeg;base64,abc"
        from dayz_ai_puppet.server.state_client import GameState
        loop.server.get_state.return_value = GameState(health=50)
        loop.reflexes.check.return_value = Action(
            type=ActionType.PRONE, thought="reflex:under_attack",
        )

        loop.tick()

        loop.reflexes.check.assert_called_once()
        loop.input_ctrl.prone.assert_called_once()
        loop.agent.decide.assert_not_called()

    def test_tick_agent_decision(self):
        loop = _make_loop()

        loop.vision.capture_base64.return_value = "data:image/jpeg;base64,abc"
        from dayz_ai_puppet.server.state_client import GameState
        loop.server.get_state.return_value = GameState(
            health=100, position=(100, 0, 200),
        )
        loop.reflexes.check.return_value = None
        loop.agent.decide.return_value = [
            Action(type=ActionType.MOVE, params={"forward": 1, "right": 0}),
        ]
        loop.memory.get_relevant_lessons.return_value = []

        loop.tick()

        loop.agent.decide.assert_called_once()
        loop.input_ctrl.move_axis.assert_called()

    def test_tick_death_handling(self):
        loop = _make_loop()

        loop.vision.capture_base64.return_value = "data:image/jpeg;base64,abc"
        from dayz_ai_puppet.server.state_client import GameState
        loop.server.get_state.return_value = GameState(health=0, position=(500, 0, 600))
        loop.reflexes.check.return_value = None
        loop.agent.decide.return_value = [Action(type=ActionType.STOP)]
        loop.memory.get_relevant_lessons.return_value = []

        loop.tick()

        loop.memory.record_death.assert_called_once()

    def test_shutdown(self):
        loop = _make_loop()
        loop.shutdown()
        loop.input_ctrl.emergency_stop.assert_called_once()
        loop.server.close.assert_called_once()
