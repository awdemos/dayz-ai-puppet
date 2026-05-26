from unittest.mock import MagicMock, patch

from dayz_ai_puppet.vision.capture import DayZVision


class TestDayZVision:
    @patch("dayz_ai_puppet.vision.capture.mss")
    @patch("dayz_ai_puppet.vision.capture.Image")
    def test_capture_resizes(self, mock_image, mock_mss):
        mock_img = MagicMock()
        mock_img.size = (1920, 1080)
        mock_img.resize.return_value = mock_img
        mock_image.frombytes.return_value = mock_img
        mock_image.LANCZOS = 1

        mock_sct = MagicMock()
        mock_sct.monitors = [{}, {"top": 0, "left": 0, "width": 1920, "height": 1080}]
        mock_shot = MagicMock()
        mock_shot.size = (1920, 1080)
        mock_shot.bgra = b"\x00" * (1920 * 1080 * 4)
        mock_sct.grab.return_value = mock_shot
        mock_mss.mss.return_value.__enter__ = MagicMock(return_value=mock_sct)
        mock_mss.mss.return_value.__exit__ = MagicMock(return_value=False)

        vision = DayZVision(width=640, height=480)
        vision.capture()
        mock_img.resize.assert_called_once_with((640, 480), 1)

    def test_capture_base64_format(self):
        vision = DayZVision()
        vision.capture = MagicMock()
        mock_img = MagicMock()
        buf = MagicMock()
        buf.getvalue.return_value = b"fake_jpeg_data"

        import io
        real_bytesio = io.BytesIO

        def fake_bytesio():
            bio = real_bytesio()
            bio.getvalue = MagicMock(return_value=b"fake_jpeg_data")
            return bio

        with patch("dayz_ai_puppet.vision.capture.io.BytesIO", side_effect=fake_bytesio):
            vision.capture.return_value = mock_img
            result = vision.capture_base64()
            assert result.startswith("data:image/jpeg;base64,")
