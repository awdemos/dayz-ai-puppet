
from dayz_ai_puppet.memory.experience import DeathRecord, ExperienceMemory


class TestExperienceMemory:
    def test_record_death(self, tmp_path):
        mem = ExperienceMemory(path=str(tmp_path / "mem.json"))
        mem.record_death("zombie", (100, 0, 200), "avoid zombies here")
        assert len(mem.lessons) == 1
        assert isinstance(mem.lessons[0], DeathRecord)
        assert mem.lessons[0].cause == "zombie"

    def test_record_success(self, tmp_path):
        mem = ExperienceMemory(path=str(tmp_path / "mem.json"))
        mem.record_success("loot", (500, 0, 600), "found AKM")
        assert len(mem.lessons) == 1
        assert mem.lessons[0].summary == "found AKM"

    def test_persistence(self, tmp_path):
        path = str(tmp_path / "mem.json")
        mem = ExperienceMemory(path=path)
        mem.record_death("player", (1000, 0, 2000), "KOS at hill")
        mem.record_success("loot", (500, 0, 600), "found medkit")

        mem2 = ExperienceMemory(path=path)
        assert len(mem2.lessons) == 2

    def test_get_relevant_lessons_nearby(self, tmp_path):
        mem = ExperienceMemory(path=str(tmp_path / "mem.json"))
        mem.record_death("zombie", (100, 0, 100), lesson_learned="death at 100,100")
        mem.record_death("fall", (5000, 0, 5000), lesson_learned="death at 5000,5000")

        relevant = mem.get_relevant_lessons((110, 0, 110), limit=1)
        assert len(relevant) == 1
        assert relevant[0].summary == "death at 100,100"

    def test_get_relevant_lessons_max_distance(self, tmp_path):
        mem = ExperienceMemory(path=str(tmp_path / "mem.json"))
        mem.record_death("zombie", (100, 0, 100), "close")
        relevant = mem.get_relevant_lessons((10000, 0, 10000), max_distance=100)
        assert len(relevant) == 0

    def test_empty_memory(self, tmp_path):
        mem = ExperienceMemory(path=str(tmp_path / "nonexistent.json"))
        assert len(mem.lessons) == 0
        assert mem.get_relevant_lessons((0, 0, 0)) == []
