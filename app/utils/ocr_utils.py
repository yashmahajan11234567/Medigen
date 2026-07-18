from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Tuple


class OCRError(Exception):
    """Exception raised when OCR processing fails."""
    pass


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
    """Container for OCR output and metadata."""

    text: str
    average_confidence: Optional[float] = None
    word_details: Optional[List[Tuple[str, float]]] = None