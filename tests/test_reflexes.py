from dayz_ai_puppet.agent.actions import ActionType
from dayz_ai_puppet.config import Settings
from dayz_ai_puppet.reflexes.combat import CombatReflexes


def _make_reflexes(**overrides):
    defaults = {"reflex_melee_range": 3.0, "reflex_low_health_threshold": 0.3}
    defaults.update(overrides)
    return CombatReflexes(Settings(**defaults))


def _safe_state(**overrides):
    base = {
        "health": 100, "max_health": 100,
        "nearby_entities": [], "bleeding": False, "recent_damage": 0,
    }
    base.update(overrides)
    return base


class TestCombatReflexes:
    def test_no_trigger_when_safe(self):
        r = _make_reflexes()
        assert r.check(_safe_state()) is None

    def test_under_attack_bleeding(self):
        r = _make_reflexes()
        action = r.check(_safe_state(health=80, bleeding=True))
        assert action is not None
        assert action.type == ActionType.PRONE
        assert "under_attack" in action.thought

    def test_under_attack_recent_damage(self):
        r = _make_reflexes()
        action = r.check(_safe_state(health=90, recent_damage=25))
        assert action is not None
        assert action.type == ActionType.PRONE

    def test_melee_range_infected(self):
        r = _make_reflexes()
        nearby = [{"type": "Infected_Zombie", "distance": 2.5}]
        action = r.check(_safe_state(nearby_entities=nearby))
        assert action is not None
        assert action.type == ActionType.SHOOT

    def test_melee_range_too_far(self):
        r = _make_reflexes()
        nearby = [{"type": "Infected_Zombie", "distance": 5.0}]
        assert r.check(_safe_state(nearby_entities=nearby)) is None

    def test_low_health(self):
        r = _make_reflexes()
        action = r.check(_safe_state(health=20))
        assert action is not None
        assert action.type == ActionType.HEAL

    def test_priority_under_attack_wins(self):
        r = _make_reflexes()
        nearby = [{"type": "Infected", "distance": 2.0}]
        action = r.check(_safe_state(
            health=20, bleeding=True, recent_damage=50, nearby_entities=nearby,
        ))
        assert action.type == ActionType.PRONE

    def test_non_infected_entity_no_melee(self):
        r = _make_reflexes()
        nearby = [{"type": "Player", "distance": 1.0}]
        assert r.check(_safe_state(nearby_entities=nearby)) is None
