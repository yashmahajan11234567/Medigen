import time
import threading
import logging
import cv2
import numpy as np
from typing import Optional, List, Tuple
from paddleocr import PaddleOCR

from app.core.config import get_settings
from app.utils.ocr_utils import OCRError, OCRResult, OCREngineInterface


logger = logging.getLogger(__name__)


class PaddleOCREngine(OCREngineInterface):
    """Singleton PaddleOCR engine with eager initialization for production multi-worker deployments."""

    _instance: Optional["PaddleOCREngine"] = None
    _ocr: Optional[PaddleOCR] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "PaddleOCREngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Eagerly initialize on first instantiation (happens at module import or first use)
        # This ensures the model is loaded once per process before handling requests,
        # avoiding latency spikes in multi-worker deployments (gunicorn, uvicorn --workers, etc.)
        if PaddleOCREngine._ocr is None:
            self._initialize_ocr()

    def _initialize_ocr(self) -> None:
        """Initialize the PaddleOCR instance (thread-safe)."""
        with PaddleOCREngine._lock:
            if PaddleOCREngine._ocr is None:
                logger.info("Initializing PaddleOCR model (CPU)...")
                settings = get_settings()
                lang_setting = settings.OCR_LANGUAGES
                if isinstance(lang_setting, list) and lang_setting:
                    lang = lang_setting[0]
                else:
                    lang = str(lang_setting) if lang_setting else "en"
                PaddleOCREngine._ocr = PaddleOCR(
                    use_textline_orientation=settings.OCR_USE_ANGLE_CLS,
                    lang=lang,
                )
                logger.info("PaddleOCR model initialized.")

    @classmethod
    def pre_warm(cls) -> None:
        """Explicitly initialize the OCR engine. Call at application startup to avoid first-request latency."""
        if cls._ocr is None:
            instance = cls()  # Triggers __init__ which calls _initialize_ocr

    def extract_text(self, image_bytes: bytes) -> OCRResult:
        """
        Extract text from image bytes using PaddleOCR.

        Args:
            image_bytes: Raw image file contents.

        Returns:
            OCRResult containing recognized text and metadata.

        Raises:
            OCRError: If the image is invalid or OCR fails.
        """
        start_time = time.time()
        try:
            # Check for empty input
            if len(image_bytes) == 0:
                raise ValueError("Invalid image data")
            # Convert bytes to OpenCV image
            nparr = np.frombuffer(image_bytes, np.uint8)
            try:
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except cv2.error as e:
                raise ValueError("Invalid image data") from e
            if img is None:
                raise ValueError("Invalid image data")

            height, width, channels = img.shape
            logger.debug(f"Image dimensions: {width}x{height}, channels={channels}")

            # Run OCR - _ocr is guaranteed to be initialized by __init__ or pre_warm
            ocr = PaddleOCREngine._ocr
            result = ocr.ocr(img)

            # Process results
            if not result or not result[0]:
                elapsed = time.time() - start_time
                logger.info(
                    f"OCR completed in {elapsed:.2f}s. No text detected. Image size: {width}x{height}"
                )
                return OCRResult(text="", average_confidence=None, word_details=None)

            texts: List[str] = []
            confidences: List[float] = []
            word_details: List[Tuple[str, float]] = []

            for line in result[0]:
                if not isinstance(line, (list, tuple)) or len(line) != 2:
                    continue
                _bbox, text_conf = line
                if not isinstance(text_conf, (list, tuple)) or len(text_conf) != 2:
                    continue
                text, confidence = text_conf
                if not isinstance(text, str):
                    continue
                try:
                    confidence = float(confidence)
                except (ValueError, TypeError):
                    continue
                texts.append(text)
                confidences.append(confidence)
                word_details.append((text, confidence))

            if not texts:
                elapsed = time.time() - start_time
                logger.info(
                    f"OCR completed in {elapsed:.2f}s. No valid text detected. Image size: {width}x{height}"
                )
                return OCRResult(text="", average_confidence=None, word_details=None)

            full_text = " ".join(texts)
            avg_confidence = (
                sum(confidences) / len(confidences) if confidences else None
            )
            avg_confidence_str = (
                f"{avg_confidence:.3f}" if avg_confidence is not None else "N/A"
            )

            elapsed = time.time() - start_time
            logger.info(
                f"OCR completed in {elapsed:.2f}s. "
                f"Text length: {len(full_text)}, "
                f"Avg confidence: {avg_confidence_str}, "
                f"Words detected: {len(word_details)}, "
                f"Image size: {width}x{height}"
            )

            return OCRResult(
                text=full_text,
                average_confidence=avg_confidence,
                word_details=word_details if word_details else None,
            )

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"OCR failed after {elapsed:.2f}s: {e}", exc_info=True
            )
            raise OCRError(f"OCR processing failed: {e}") from e
