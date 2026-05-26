from dayz_ai_puppet.navigation.gps import CHERNARUS_LANDMARKS, GPSNavigator, Landmark


class TestGPSNavigator:
    def setup_method(self):
        self.nav = GPSNavigator()

    def test_bearing_north(self):
        b = self.nav.bearing((0, 0, 0), (0, 0, 100))
        assert 355 < b or b < 5  # ~0 degrees = north

    def test_bearing_east(self):
        b = self.nav.bearing((0, 0, 0), (100, 0, 0))
        assert 85 < b < 95

    def test_bearing_south(self):
        b = self.nav.bearing((0, 0, 0), (0, 0, -100))
        assert 175 < b < 185

    def test_distance(self):
        d = self.nav.distance((0, 0, 0), (3, 0, 4))
        assert abs(d - 5.0) < 0.01

    def test_nearest_landmark(self):
        lm = self.nav.nearest_landmark((6500, 0, 6100))
        assert lm.name == "Stary Sobor"

    def test_direction_to(self):
        bearing, dist = self.nav.direction_to((0, 0, 0), "Chernogorsk")
        assert dist > 0
        assert 0 <= bearing < 360

    def test_direction_to_unknown(self):
        bearing, dist = self.nav.direction_to((0, 0, 0), "NowhereVille")
        assert bearing == 0.0
        assert dist == 0.0

    def test_landmarks_within(self):
        results = self.nav.landmarks_within((6600, 0, 2600), radius=2000)
        names = [lm.name for lm, _ in results]
        assert "Chernogorsk" in names
        for _, d in results:
            assert d <= 2000

    def test_landmarks_within_empty(self):
        results = self.nav.landmarks_within((0, 0, 0), radius=1)
        assert len(results) == 0

    def test_chernarus_landmarks_populated(self):
        assert len(CHERNARUS_LANDMARKS) > 30

    def test_custom_landmarks(self):
        custom = [Landmark("Base", 0, 0, "test")]
        nav = GPSNavigator(landmarks=custom)
        assert nav.nearest_landmark((10, 0, 10)).name == "Base"
