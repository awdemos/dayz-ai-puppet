from unittest.mock import patch

import pytest

from dayz_ai_puppet.input.controller import DayZInput


@patch("dayz_ai_puppet.input.controller.pydirectinput")
class TestDayZInput:
    def test_disabled_by_default(self, mock_di):
        inp = DayZInput()
        assert inp.enabled is False
        with pytest.raises(RuntimeError, match="Physical input injection is disabled"):
            inp.interact()
        mock_di.press.assert_not_called()

    def test_enable_after_confirm(self, mock_di):
        inp = DayZInput()
        assert DayZInput.confirm() is True
        inp.enable()
        assert inp.enabled is True
        inp.interact()
        mock_di.press.assert_called_with("f")

    def test_disable_releases_keys(self, mock_di):
        inp = DayZInput()
        inp.enable()
        inp._active_keys = {"w", "shift"}
        inp.disable()
        assert inp.enabled is False
        assert len(inp._active_keys) == 0
        assert mock_di.keyUp.call_count >= 2

    def test_interact(self, mock_di):
        inp = DayZInput()
        inp.enable()
        inp.interact()
        mock_di.press.assert_called_with("f")

    def test_crouch(self, mock_di):
        inp = DayZInput()
        inp.enable()
        inp.crouch()
        mock_di.press.assert_called_with("c")

    def test_prone(self, mock_di):
        inp = DayZInput()
        inp.enable()
        inp.prone()
        mock_di.press.assert_called_with("z")

    def test_toggle_inventory(self, mock_di):
        inp = DayZInput()
        inp.enable()
        inp.toggle_inventory()
        mock_di.press.assert_called_with("tab")

    def test_shoot(self, mock_di):
        inp = DayZInput()
        inp.enable()
        inp.shoot(duration=0.2)
        mock_di.mouseDown.assert_called_with(button="left")
        mock_di.mouseUp.assert_called_with(button="left")

    def test_run_start_stop(self, mock_di):
        inp = DayZInput()
        inp.enable()
        inp.run_start()
        mock_di.keyDown.assert_called_with("shift")
        assert "shift" in inp._active_keys

        inp.run_stop()
        mock_di.keyUp.assert_called_with("shift")
        assert "shift" not in inp._active_keys

    def test_move_axis_forward(self, mock_di):
        inp = DayZInput()
        inp.enable()
        inp.move_axis(forward=1, right=0, duration=0.01)
        mock_di.keyDown.assert_called_with("w")
        mock_di.keyUp.assert_called_with("w")

    def test_move_axis_diagonal(self, mock_di):
        inp = DayZInput()
        inp.enable()
        inp.move_axis(forward=1, right=1, duration=0.01)
        assert mock_di.keyDown.call_count == 2
        keys_down = {c[0][0] for c in mock_di.keyDown.call_args_list}
        assert keys_down == {"w", "d"}

    def test_emergency_stop(self, mock_di):
        inp = DayZInput()
        inp.enable()
        inp._active_keys = {"w", "shift"}
        inp.emergency_stop()
        assert inp.enabled is False
        assert len(inp._active_keys) == 0
        assert mock_di.keyUp.call_count >= 2

    def test_look(self, mock_di):
        mock_di.position.return_value = (500, 300)
        inp = DayZInput()
        inp.enable()
        inp.look(delta_x=50, delta_y=-25)
        mock_di.moveTo.assert_called_with(550, 275)

    def test_move_unknown_direction(self, mock_di):
        inp = DayZInput()
        inp.enable()
        inp.move("jump")
        mock_di.press.assert_not_called()
        mock_di.keyDown.assert_not_called()

    def test_move_requires_windows(self, mock_di):
        """If pydirectinput is not importable, move raises RuntimeError."""
        with patch("dayz_ai_puppet.input.controller.pydirectinput", None):
            inp = DayZInput()
            inp.enable()
            with pytest.raises(RuntimeError, match="pydirectinput is only available"):
                inp.move("forward", duration=0.01)

    def test_rate_limit_triggers_emergency_stop(self, mock_di):
        inp = DayZInput(actions_per_second=2, rate_window_seconds=1.0)
        inp.enable()
        inp.interact()
        inp.interact()
        assert inp.enabled is True
        with pytest.raises(RuntimeError, match="Input rate limit exceeded"):
            inp.interact()
        assert inp.enabled is False

    def test_rate_limit_window_allows_resumption_after_clear(self, mock_di):
        inp = DayZInput(actions_per_second=2, rate_window_seconds=0.01)
        inp.enable()
        inp.interact()
        inp.interact()
        with pytest.raises(RuntimeError, match="Input rate limit exceeded"):
            inp.interact()
        assert inp.enabled is False
