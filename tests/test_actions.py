from dayz_ai_puppet.agent.actions import Action, ActionType, parse_actions


class TestActionType:
    def test_all_values(self):
        expected = {
            "move", "look", "interact", "inventory", "shoot",
            "crouch", "prone", "run", "stop", "heal",
        }
        actual = {t.value for t in ActionType}
        assert actual == expected


class TestAction:
    def test_default_duration(self):
        a = Action(type=ActionType.STOP)
        assert a.duration == 1.0

    def test_custom_duration(self):
        a = Action(type=ActionType.MOVE, params={"forward": 1, "duration": 2.5})
        assert a.duration == 2.5

    def test_is_valid_move(self):
        a = Action(type=ActionType.MOVE, params={"forward": 1, "right": 0})
        assert a.is_valid()

    def test_invalid_move_missing_forward(self):
        a = Action(type=ActionType.MOVE, params={"right": 1})
        assert a.is_valid()

    def test_valid_look(self):
        a = Action(type=ActionType.LOOK, params={"pitch": 10, "yaw": -5})
        assert a.is_valid()

    def test_valid_no_param_action(self):
        no_param_types = (
            ActionType.INTERACT, ActionType.INVENTORY, ActionType.SHOOT,
            ActionType.CROUCH, ActionType.PRONE, ActionType.RUN,
            ActionType.STOP, ActionType.HEAL,
        )
        for atype in no_param_types:
            assert Action(type=atype).is_valid()


class TestParseActions:
    def test_single_action_json_string(self):
        raw = '{"action": "move", "params": {"forward": 1, "right": 0}}'
        result = parse_actions(raw)
        assert len(result) == 1
        assert result[0].type == ActionType.MOVE
        assert result[0].params["forward"] == 1

    def test_actions_wrapper(self):
        raw = '{"actions": [{"action": "look", "params": {"yaw": 50}}, {"action": "stop"}]}'
        result = parse_actions(raw)
        assert len(result) == 2
        assert result[0].type == ActionType.LOOK
        assert result[1].type == ActionType.STOP

    def test_dict_input(self):
        data = {"action": "crouch", "thought": "zombie nearby"}
        result = parse_actions(data)
        assert len(result) == 1
        assert result[0].thought == "zombie nearby"

    def test_unknown_action_skipped(self):
        raw = '{"action": "backflip"}'
        result = parse_actions(raw)
        assert len(result) == 0

    def test_mixed_valid_invalid(self):
        data = [
            {"action": "prone"},
            {"action": "fly"},
            {"action": "shoot"},
        ]
        result = parse_actions(data)
        assert len(result) == 2
        assert result[0].type == ActionType.PRONE
        assert result[1].type == ActionType.SHOOT

    def test_thought_preserved(self):
        raw = '{"action": "run", "thought": "running from zombie"}'
        result = parse_actions(raw)
        assert result[0].thought == "running from zombie"
