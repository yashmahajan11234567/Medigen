import cv2
import numpy as np
import logging
from typing import Optional, Tuple

from app.core.config import get_settings
from app.utils.ocr_utils import OCRError  # We'll reuse OCRError for consistency, or define our own? Let's define a new one.

logger = logging.getLogger(__name__)


class ImageProcessingError(Exception):
    """Exception raised for errors in the image preprocessing pipeline."""
    pass


class ImagePreprocessor:
    """
    Handles image preprocessing steps for OCR.
    Steps are configurable via settings (or constructor overrides).
    Steps (in order):
      1. Decode image from bytes
      2. Resize (maintaining aspect ratio, max dimension from settings)
      3. Deskew (optional)
      4. Convert to grayscale (optional)
      5. Apply CLAHE (optional)
      6. Apply adaptive threshold (optional)
      7. Denoise (optional)
    Returns processed image as PNG-encoded bytes.
    """

    def __init__(
        self,
        grayscale: Optional[bool] = None,
        binarize: Optional[bool] = None,
        deskew: Optional[bool] = None,
        apply_clahe: Optional[bool] = None,
        denoise: Optional[bool] = None,
        max_dimension: Optional[int] = None,
    ) -> None:
        settings = get_settings()
        # Use provided values or fall back to settings
        self.grayscale = grayscale if grayscale is not None else settings.OCR_PREPROCESS_GRAYSCALE
        self.binarize = binarize if binarize is not None else settings.OCR_PREPROCESS_BINARIZE
        self.deskew = deskew if deskew is not None else settings.OCR_PREPROCESS_DESKEW
        self.apply_clahe = apply_clahe if apply_clahe is not None else settings.OCR_PREPROCESS_APPLY_CLAHE
        self.denoise = denoise if denoise is not None else settings.OCR_PREPROCESS_DENOISE
        self.max_dimension = max_dimension if max_dimension is not None else 1500  # Default max dimension

        # Note: We could add more settings for CLAHE and denoise parameters, but for simplicity we use defaults.
        # In a production system, we might expose these as well.

    def preprocess(self, image_bytes: bytes) -> bytes:
        """
        Apply the preprocessing pipeline to the input image bytes.

        Args:
            image_bytes: Raw image data (e.g., from an uploaded file).

        Returns:
            Processed image as PNG-encoded bytes.

        Raises:
            ImageProcessingError: If any step fails.
        """
        try:
            # Step 0: Validate and decode image
            img = self._decode_image(image_bytes)
            original_height, original_width = img.shape[:2]
            logger.debug(f"Image decoded: {original_width}x{original_height}")

            # Step 1: Resize while maintaining aspect ratio
            img = self._resize_image(img)
            resized_height, resized_width = img.shape[:2]
            if (resized_width, resized_height) != (original_width, original_height):
                logger.debug(
                    f"Image resized from {original_width}x{original_height} to {resized_width}x{resized_height}"
                )

            # Step 2: Deskew (if enabled)
            if self.deskew:
                img = self._deskew_image(img)
                logger.debug("Deskewing applied")

            # Step 3: Convert to grayscale (if enabled)
            if self.grayscale:
                img = self._to_grayscale(img)
                logger.debug("Grayscale conversion applied")

            # Step 4: Apply CLAHE (if enabled)
            if self.apply_clahe:
                img = self._apply_clahe(img)
                logger.debug("CLAHE applied")

            # Step 5: Apply adaptive threshold (if binarize is enabled)
            if self.binarize:
                img = self._apply_adaptive_threshold(img)
                logger.debug("Adaptive threshold applied")

            # Step 6: Denoise (if enabled)
            if self.denoise:
                img = self._denoise_image(img)
                logger.debug("Denoising applied")

            # Encode back to PNG bytes
            success, encoded_img = cv2.imencode('.png', img)
            if not success:
                raise ImageProcessingError("Failed to encode processed image to PNG")
            result_bytes = encoded_img.tobytes()
            logger.debug(f"Image preprocessing complete. Output size: {len(result_bytes)} bytes")
            return result_bytes

        except Exception as e:
            if not isinstance(e, ImageProcessingError):
                logger.error(f"Image preprocessing failed: {e}", exc_info=True)
                raise ImageProcessingError(f"Image preprocessing failed: {e}") from e
            raise

    def _decode_image(self, image_bytes: bytes) -> np.ndarray:
        """Decode image bytes to OpenCV image (BGR format)."""
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Could not decode image")
            return img
        except Exception as e:
            raise ImageProcessingError(f"Invalid image data: {e}") from e

    def _resize_image(self, img: np.ndarray) -> np.ndarray:
        """Resize image while preserving aspect ratio, limiting the max dimension."""
        height, width = img.shape[:2]
        if max(height, width) <= self.max_dimension:
            return img  # No resizing needed

        # Compute scaling factor
        scale = self.max_dimension / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return resized

    def _deskew_image(self, img: np.ndarray) -> np.ndarray:
        """
        Deskew the image by detecting the angle of text and rotating to correct.
        Uses the method of finding the minimum area rectangle of non-zero points.
        """
        # Convert to grayscale if not already (we need a single channel for thresholding)
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        # Threshold to get binary image (invert so text is white)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Find coordinates of non-zero points
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) < 5:  # Need at least 5 points for minAreaRect
            return img  # Too little data, skip deskewing

        # Get the minimum area rectangle
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]  # The angle is the third element

        # The angle needs to be corrected
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Rotate the image to deskew
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        return rotated

    def _to_grayscale(self, img: np.ndarray) -> np.ndarray:
        """Convert BGR image to grayscale."""
        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img  # Already grayscale

    def _apply_clahe(self, img: np.ndarray) -> np.ndarray:
        """Apply Contrast Limited Adaptive Histogram Equalization."""
        if len(img.shape) == 3:
            # If color, convert to LAB and apply CLAHE to L channel
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            limg = cv2.merge((cl, a, b))
            return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        else:
            # Grayscale image
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            return clahe.apply(img)

    def _apply_adaptive_threshold(self, img: np.ndarray) -> np.ndarray:
        """Apply adaptive thresholding to get a binary image."""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        # Use adaptive threshold with Gaussian weights
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        return binary

    def _denoise_image(self, img: np.ndarray) -> np.ndarray:
        """Apply Non-local Means Denoising."""
        if len(img.shape) == 3:
            return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        else:
            return cv2.fastNlMeansDenoising(img, None, 10, 7, 21)