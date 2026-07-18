from typing import Optional
import logging

from app.core.config import get_settings
from app.services.image_preprocessing import ImagePreprocessor
from app.services.paddleocr_engine import PaddleOCREngine
from app.utils.ocr_utils import OCRError


logger = logging.getLogger(__name__)


class OCRService:
    def __init__(
        self,
        engine: PaddleOCREngine,
        preprocessor: Optional[ImagePreprocessor] = None,
    ) -> None:
        self.engine = engine
        self.preprocessor = preprocessor
        self.settings = get_settings()

    def extract_bytes(
        self,
        image_bytes: bytes,
        mime_type: str,
    ) -> "OCRResult":
        """
        Validate, optionally preprocess, and run OCR on an image.

        Args:
            image_bytes: Raw image data.
            mime_type: MIME type of the upload (from client).

        Returns:
            OCRResult containing the recognized text and metadata.

        Raises:
            ValueError: If mime type not allowed or size exceeded.
            OCRError: If preprocessing or OCR fails.
        """
        settings = self.settings
        # Validate mime type
        allowed_mime_types = set(settings.OCR_ALLOWED_MIME_TYPES.split(","))
        if mime_type not in allowed_mime_types:
            logger.warning(f"Invalid mime type: {mime_type}. Allowed: {allowed_mime_types}")
            raise ValueError(f"Invalid mime type: {mime_type}")

        # Validate size
        max_size_bytes = settings.OCR_MAX_UPLOAD_MB * 1024 * 1024
        if len(image_bytes) > max_size_bytes:
            logger.warning(
                f"Image size {len(image_bytes)} bytes exceeds limit {max_size_bytes} bytes"
            )
            raise ValueError(
                f"Image size too large. Max {settings.OCR_MAX_UPLOAD_MB} MB allowed"
            )

        # Optional preprocessing
        if self.preprocessor is not None:
            try:
                logger.debug("Calling preprocessor")
                processed_bytes = self.preprocessor.preprocess(image_bytes, mime_type)
                logger.debug("Preprocessing complete")
            except Exception as e:
                logger.error(f"Preprocessing failed: {e}", exc_info=True)
                raise OCRError(f"Preprocessing failed: {e}") from e
        else:
            processed_bytes = image_bytes
            logger.debug("No preprocessor provided, using original image")

        # Run OCR
        try:
            logger.debug("Calling OCR engine")
            result = self.engine.extract_text(processed_bytes)
            logger.debug("OCR engine completed")
            return result
        except OCRError:
            # Re-raise OCRError as is
            raise
        except Exception as e:
            logger.error(f"OCR engine failed: {e}", exc_info=True)
            raise OCRError(f"OCR processing failed: {e}") from e