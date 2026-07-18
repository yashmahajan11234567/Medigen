import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import cv2

from app.services.paddleocr_engine import PaddleOCREngine
from app.utils.ocr_utils import OCRResult, OCRError


class TestPaddleOCREngine(unittest.TestCase):
    def setUp(self):
        # Clear singleton instance before each test
        PaddleOCREngine._instance = None
        PaddleOCREngine._ocr = None

    def test_singleton(self):
        engine1 = PaddleOCREngine()
        engine2 = PaddleOCREngine()
        self.assertIs(engine1, engine2)

    @patch("app.services.paddleocr_engine.PaddleOCR")
    def test_lazy_initialization(self, mock_paddle_ocr):
        """Ensure PaddleOCR is not instantiated until first use."""
        engine = PaddleOCREngine()
        # Constructor should not have called PaddleOCR yet
        mock_paddle_ocr.assert_not_called()
        # Create a dummy image
        _, img_encoded = cv2.imencode(".png", np.zeros((10, 10, 3), dtype=np.uint8))
        image_bytes = img_encoded.tobytes()
        # Call extract_text
        engine.extract_text(image_bytes)
        # Now PaddleOCR should have been called once
        mock_paddle_ocr.assert_called_once()
        # Second call should not re-initialize
        mock_paddle_ocr.reset_mock()
        engine.extract_text(image_bytes)
        mock_paddle_ocr.assert_not_called()

    @patch("app.services.paddleocr_engine.PaddleOCR")
    def test_successful_ocr(self, mock_paddle_ocr):
        # Mock OCR result: one detection
        mock_instance = MagicMock()
        mock_instance.ocr.return_value = [
            [
                [[[10, 10], [20, 10], [20, 20], [10, 20]], ("hello", 0.95)]
            ]
        ]
        mock_paddle_ocr.return_value = mock_instance

        engine = PaddleOCREngine()
        # Create a dummy valid image (small black image)
        _, img_encoded = cv2.imencode(
            ".png", np.zeros((10, 10, 3), dtype=np.uint8)
        )
        image_bytes = img_encoded.tobytes()

        result = engine.extract_text(image_bytes)

        self.assertIsInstance(result, OCRResult)
        self.assertEqual(result.text, "hello")
        self.assertEqual(result.average_confidence, 0.95)
        self.assertEqual(result.word_details, [("hello", 0.95)])

        # Ensure PaddleOCR was instantiated once
        mock_paddle_ocr.assert_called_once()
        mock_instance.ocr.assert_called_once()

    def test_invalid_image(self):
        engine = PaddleOCREngine()
        with self.assertRaises(OCRError) as ctx:
            engine.extract_text(b"not an image")
        self.assertIn("Invalid image data", str(ctx.exception))

    def test_empty_image(self):
        engine = PaddleOCREngine()
        with self.assertRaises(OCRError) as ctx:
            engine.extract_text(b"")
        self.assertIn("Invalid image data", str(ctx.exception))

    @patch("app.services.paddleocr_engine.PaddleOCR")
    def test_ocr_failure(self, mock_paddle_ocr):
        mock_instance = MagicMock()
        mock_instance.ocr.side_effect = Exception("Model error")
        mock_paddle_ocr.return_value = mock_instance

        engine = PaddleOCREngine()
        _, img_encoded = cv2.imencode(
            ".png", np.zeros((10, 10, 3), dtype=np.uint8)
        )
        image_bytes = img_encoded.tobytes()

        with self.assertRaises(OCRError) as ctx:
            engine.extract_text(image_bytes)
        self.assertIn("OCR processing failed", str(ctx.exception))

    @patch("app.services.paddleocr_engine.PaddleOCR")
    def test_no_text_detected(self, mock_paddle_ocr):
        mock_instance = MagicMock()
        mock_instance.ocr.return_value = [[]]  # empty page
        mock_paddle_ocr.return_value = mock_instance

        engine = PaddleOCREngine()
        _, img_encoded = cv2.imencode(
            ".png", np.zeros((10, 10, 3), dtype=np.uint8)
        )
        image_bytes = img_encoded.tobytes()

        result = engine.extract_text(image_bytes)

        self.assertEqual(result.text, "")
        self.assertIsNone(result.average_confidence)
        self.assertIsNone(result.word_details)


if __name__ == "__main__":
    unittest.main()