from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Optional, List, Tuple


class OCRError(Exception):
    """Exception raised when OCR processing fails."""
    pass


class ImageQualityError(Exception):
    """Exception raised when image quality checks fail.

    Attributes:
        message: Human-readable description.
        code: Machine-readable error code for the frontend.
        diagnostics: Detailed quality diagnostics, if available.
    """

    def __init__(
        self,
        message: str,
        code: str = "image_quality_error",
        diagnostics: Optional["ScanQualityDiagnostics"] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.diagnostics = diagnostics


class ImageQualityIssue(StrEnum):
    """Types of image quality issues detectable by the preprocessing pipeline."""

    BLURRY = "blurry"
    TOO_DARK = "too_dark"
    OVEREXPOSED = "overexposed"
    LOW_CONTRAST = "low_contrast"
    CORRUPTED = "corrupted"
    EMPTY = "empty"


@dataclass
class ScanQualityDiagnostics:
    """Quality assessment of an uploaded scan/image.

    Fields:
        issues: List of detected quality issues (empty = no issues).
        blur_score: Laplacian variance — lower values mean more blur.
        brightness: Mean pixel brightness (0-255).
        contrast: Standard deviation of pixel values.
        is_pass: True if the image passes all quality checks.
    """

    issues: List[ImageQualityIssue] = field(default_factory=list)
    blur_score: Optional[float] = None
    brightness: Optional[float] = None
    contrast: Optional[float] = None
    is_pass: bool = True


class OCREngineInterface(ABC):
    """Abstract base class for OCR engines."""

    @abstractmethod
    def extract_text(self, image_bytes: bytes) -> "OCRResult":
        """Run OCR on the supplied image bytes.

        Args:
            image_bytes: Raw image file contents.

        Returns:
            Recognized text as a single string.

        Raises:
            OCRError: If the engine fails to process the image.
        """
        pass


@dataclass
class OCRResult:
    """Container for OCR output and metadata.

    Fields:
        text: The recognized text.
        average_confidence: Mean confidence score across all detections (0-1).
        word_details: List of (word, confidence) tuples.
        quality: Quality diagnostics of the source image, if assessed.
    """

    text: str
    average_confidence: Optional[float] = None
    word_details: Optional[List[Tuple[str, float]]] = None
    quality: Optional[ScanQualityDiagnostics] = None