from typing import Optional
import logging

from app.core.config import get_settings
from app.services.image_preprocessing import ImagePreprocessor
from app.services.paddleocr_engine import PaddleOCREngine
from app.utils.ocr_utils import ImageQualityError, ImageQualityIssue, OCRError, ScanQualityDiagnostics


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
        Validate, assess quality, optionally preprocess, and run OCR on an image.

        Args:
            image_bytes: Raw image data.
            mime_type: MIME type of the upload (from client).

        Returns:
            OCRResult containing the recognized text and metadata.

        Raises:
            ValueError: If mime type not allowed or size exceeded.
            ImageQualityError: If the image fails quality checks (corrupted, empty).
            OCRError: If preprocessing or OCR fails.
        """
        settings = self.settings

        # --- Step 1: Validate MIME type ---
        allowed_mime_types = set(settings.OCR_ALLOWED_MIME_TYPES.split(","))
        if mime_type not in allowed_mime_types:
            logger.warning(f"Invalid mime type: {mime_type}. Allowed: {allowed_mime_types}")
            raise ValueError(f"Invalid mime type: {mime_type}")

        # --- Step 2: Validate size ---
        max_size_bytes = settings.OCR_MAX_UPLOAD_MB * 1024 * 1024
        if len(image_bytes) > max_size_bytes:
            logger.warning(
                f"Image size {len(image_bytes)} bytes exceeds limit {max_size_bytes} bytes"
            )
            raise ValueError(
                f"Image size too large. Max {settings.OCR_MAX_UPLOAD_MB} MB allowed"
            )

        # --- Step 3: Check for empty upload ---
        if len(image_bytes) == 0:
            logger.warning("Empty image data received")
            raise ValueError("Empty image data received")

        # --- Step 4: Assess image quality (before preprocessing) ---
        quality: Optional[ScanQualityDiagnostics] = None
        if self.preprocessor is not None:
            try:
                logger.debug("Assessing image quality")
                quality = self.preprocessor.assess_quality(image_bytes)
                logger.debug(
                    f"Quality assessment: pass={quality.is_pass}, "
                    f"issues={[i.value for i in quality.issues]}, "
                    f"blur={quality.blur_score}, "
                    f"brightness={quality.brightness}, "
                    f"contrast={quality.contrast}"
                )

                # Hard reject on corrupted or empty images
                for issue in quality.issues:
                    if issue in (ImageQualityIssue.CORRUPTED, ImageQualityIssue.EMPTY):
                        raise ImageQualityError(
                            message=f"Image quality check failed: {issue.value}",
                            code=f"image_{issue.value}",
                            diagnostics=quality,
                        )

            except ImageQualityError:
                raise
            except Exception as e:
                logger.error(f"Quality assessment failed: {e}", exc_info=True)
                raise OCRError(f"Quality assessment failed: {e}") from e

        # --- Step 5: Optional preprocessing ---
        if self.preprocessor is not None:
            try:
                logger.debug("Calling preprocessor")
                processed_bytes = self.preprocessor.preprocess(image_bytes)
                logger.debug("Preprocessing complete")
            except Exception as e:
                logger.error(f"Preprocessing failed: {e}", exc_info=True)
                raise OCRError(f"Preprocessing failed: {e}") from e
        else:
            processed_bytes = image_bytes
            logger.debug("No preprocessor provided, using original image")

        # --- Step 6: Run OCR ---
        try:
            logger.debug("Calling OCR engine")
            result = self.engine.extract_text(processed_bytes)
            # Attach quality diagnostics to the result
            result.quality = quality
            logger.debug("OCR engine completed")

            # --- Step 7: Check for low confidence ---
            if result.average_confidence is not None:
                if result.average_confidence < settings.OCR_LOW_CONFIDENCE_REJECT_THRESHOLD:
                    logger.warning(
                        f"OCR confidence {result.average_confidence:.3f} below reject threshold "
                        f"{settings.OCR_LOW_CONFIDENCE_REJECT_THRESHOLD}"
                    )
                    raise OCRError(
                        f"OCR confidence too low ({result.average_confidence:.1%}). "
                        "Please provide a clearer image."
                    )

            return result
        except OCRError:
            raise
        except Exception as e:
            logger.error(f"OCR engine failed: {e}", exc_info=True)
            raise OCRError(f"OCR processing failed: {e}") from e