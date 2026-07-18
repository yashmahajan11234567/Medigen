import re


class TextCleaner:
    """Clean OCR output before passing to parsers.

    Responsibilities:
      - Strip leading/trailing whitespace
      - Normalise newlines (collapse 3+ consecutive newlines to 2)
      - Remove lines that are likely OCR noise (shorter than 3 chars)
      - Collapse multiple spaces within a line

    This service does NOT infer or modify content.
    """

    MIN_LINE_LENGTH = 2

    def clean(self, raw_text: str) -> str:
        """Clean OCR-extracted text.

        Args:
            raw_text: Raw output from OCRService.

        Returns:
            Cleaned text suitable for parser consumption.
        """
        if not raw_text or not raw_text.strip():
            return ""

        text = raw_text.strip()

        # Collapse 3+ consecutive blank lines to 2 (preserves paragraph breaks)
        text = re.sub(r"(\n\s*){3,}", "\n\n", text)

        lines = text.split("\n")
        cleaned_lines: list[str] = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                cleaned_lines.append("")
                continue
            # Remove very short OCR-noise lines (single chars, stray punctuation)
            if len(stripped) <= self.MIN_LINE_LENGTH:
                continue
            # Collapse internal whitespace
            normalised = re.sub(r"\s+", " ", stripped)
            cleaned_lines.append(normalised)

        # Remove leading/trailing blank lines
        while cleaned_lines and cleaned_lines[0] == "":
            cleaned_lines.pop(0)
        while cleaned_lines and cleaned_lines[-1] == "":
            cleaned_lines.pop()

        return "\n".join(cleaned_lines)