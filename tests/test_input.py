from unittest.mock import patch

from dayz_ai_puppet.input.controller import DayZInput


@patch("dayz_ai_puppet.input.controller.pydirectinput")
class TestDayZInput:
    def test_interact(self, mock_di):
        inp = DayZInput()
        inp.interact()
        mock_di.press.assert_called_with("f")

    def test_crouch(self, mock_di):
        inp = DayZInput()
        inp.crouch()
        mock_di.press.assert_called_with("c")

    def test_prone(self, mock_di):
        inp = DayZInput()
        inp.prone()
        mock_di.press.assert_called_with("z")

    def test_toggle_inventory(self, mock_di):
        inp = DayZInput()
        inp.toggle_inventory()
        mock_di.press.assert_called_with("tab")

    def test_shoot(self, mock_di):
        inp = DayZInput()
        inp.shoot(duration=0.2)
        mock_di.mouseDown.assert_called_with(button="left")
        mock_di.mouseUp.assert_called_with(button="left")

    def test_run_start_stop(self, mock_di):
        inp = DayZInput()
        inp.run_start()
        mock_di.keyDown.assert_called_with("shift")
        assert "shift" in inp._active_keys

        inp.run_stop()
        mock_di.keyUp.assert_called_with("shift")
        assert "shift" not in inp._active_keys

    def test_move_axis_forward(self, mock_di):
        inp = DayZInput()
        inp.move_axis(forward=1, right=0, duration=0.01)
        mock_di.keyDown.assert_called_with("w")
        mock_di.keyUp.assert_called_with("w")

    def test_move_axis_diagonal(self, mock_di):
        inp = DayZInput()
        inp.move_axis(forward=1, right=1, duration=0.01)
        assert mock_di.keyDown.call_count == 2
        keys_down = {c[0][0] for c in mock_di.keyDown.call_args_list}
        assert keys_down == {"w", "d"}

    def test_emergency_stop(self, mock_di):
        inp = DayZInput()
        inp._active_keys = {"w", "shift"}
        inp.emergency_stop()
        assert len(inp._active_keys) == 0
        assert mock_di.keyUp.call_count >= 2

    def test_look(self, mock_di):
        mock_di.position.return_value = (500, 300)
        inp = DayZInput()
        inp.look(delta_x=50, delta_y=-25)
        mock_di.moveTo.assert_called_with(550, 275)
