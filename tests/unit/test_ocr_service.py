import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import cv2

from app.services.ocr_service import OCRService
from app.utils.ocr_utils import OCRResult, OCRError


class TestOCRService(unittest.TestCase):
    def setUp(self):
        self.mock_preprocessor = MagicMock()
        self.mock_engine = MagicMock()
        self.service = OCRService(engine=self.mock_engine, preprocessor=self.mock_preprocessor)

    def test_without_preprocessor_skips_preprocessing(self):
        # Arrange
        image_bytes = b"fake image data"
        mime_type = "image/png"
        expected_result = OCRResult(text="test", average_confidence=0.9, word_details=[("test", 0.9)])
        self.mock_engine.extract_text.return_value = expected_result

        # Create a service with no preprocessor
        service_no_prep = OCRService(engine=self.mock_engine, preprocessor=None)

        # Act
        result = service_no_prep.extract_bytes(image_bytes, mime_type)

        # Assert
        self.mock_preprocessor.preprocess.assert_not_called()
        self.mock_engine.extract_text.assert_called_once_with(image_bytes)
        self.assertEqual(result, expected_result)

    def test_with_preprocessor_calls_preprocessor_then_engine(self):
        # Arrange
        image_bytes = b"original image"
        mime_type = "image/png"
        processed_bytes = b"processed image"
        expected_result = OCRResult(text="processed", average_confidence=0.8, word_details=[("processed", 0.8)])
        self.mock_preprocessor.preprocess.return_value = processed_bytes
        self.mock_engine.extract_text.return_value = expected_result

        # Act
        result = self.service.extract_bytes(image_bytes, mime_type)

        # Assert
        self.mock_preprocessor.preprocess.assert_called_once_with(image_bytes, mime_type)
        self.mock_engine.extract_text.assert_called_once_with(processed_bytes)
        self.assertEqual(result, expected_result)

    def test_valid_mime_type_and_size_passes_through(self):
        # Arrange
        image_bytes = b"fake image data"
        mime_type = "image/png"
        expected_result = OCRResult(text="test", average_confidence=0.9, word_details=[("test", 0.9)])
        self.mock_preprocessor.preprocess.return_value = image_bytes  # preprocessor acts as pass-through
        self.mock_engine.extract_text.return_value = expected_result

        # Act
        result = self.service.extract_bytes(image_bytes, mime_type)

        # Assert
        self.mock_preprocessor.preprocess.assert_called_once_with(image_bytes, mime_type)
        self.mock_engine.extract_text.assert_called_once_with(image_bytes)
        self.assertEqual(result, expected_result)

    def test_invalid_mime_type_raises_value_error(self):
        # Arrange
        image_bytes = b"fake image data"
        mime_type = "image/bmp"
        self.mock_preprocessor.preprocess.return_value = image_bytes
        self.mock_engine.extract_text.return_value = OCRResult(text="test", average_confidence=0.9, word_details=[("test", 0.9)])

        # Act & Assert
        self.assertRaises(ValueError, self.service.extract_bytes, image_bytes, mime_type)

    def test_size_exceeded_raises_value_error(self):
        # Arrange
        image_bytes = b"x" * (10 * 1024 * 1024 + 1)  # 10 MB + 1 byte
        mime_type = "image/png"
        self.mock_preprocessor.preprocess.return_value = image_bytes
        self.mock_engine.extract_text.return_value = OCRResult(text="test", average_confidence=0.9, word_details=[("test", 0.9)])

        # Act & Assert
        self.assertRaises(ValueError, self.service.extract_bytes, image_bytes, mime_type)

    def test_preprocessing_failure_wraps_in_ocerror(self):
        # Arrange
        image_bytes = b"fake image data"
        mime_type = "image/png"
        self.mock_preprocessor.preprocess.side_effect = Exception("Preprocess failed")
        self.mock_engine.extract_text.return_value = OCRResult(text="test", average_confidence=0.9, word_details=[("test", 0.9)])

        # Act & Assert
        self.assertRaises(OCRError, self.service.extract_bytes, image_bytes, mime_type)

    def test_engine_failure_wraps_in_ocerror(self):
        # Arrange
        image_bytes = b"fake image data"
        mime_type = "image/png"
        self.mock_preprocessor.preprocess.return_value = image_bytes
        self.mock_engine.extract_text.side_effect = Exception("OCR failed")
        self.mock_engine.extract_text.return_value = OCRResult(text="test", average_confidence=0.9, word_details=[("test", 0.9)])

        # Act & Assert
        self.assertRaises(OCRError, self.service.extract_bytes, image_bytes, mime_type)


if __name__ == '__main__':
    unittest.main()