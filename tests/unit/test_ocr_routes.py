from unittest.mock import MagicMock, patch

import pytest

from app.core.enums import MedicineType
from app.schemas.generic_finder import (
    CanonicalComposition,
    GenericFinderSearchResponse,
)
from app.utils.ocr_utils import OCRResult, OCRError


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_ocr_result():
    """Return a reasonable OCRResult for use across tests."""
    return OCRResult(
        text="Paracetamol 500 mg tablet oral\nQty 10",
        average_confidence=0.95,
        word_details=[("Paracetamol", 0.95)],
    )


@pytest.fixture
def mock_ocr_service(mock_ocr_result):
    with patch("app.api.routes.ocr._ocr_service") as mock:
        mock.extract_bytes.return_value = mock_ocr_result
        yield mock


@pytest.fixture
def valid_png_file() -> dict:
    return {"file": ("test.png", b"fake-png-image-bytes", "image/png")}


@pytest.fixture
def generic_finder_response() -> GenericFinderSearchResponse:
    composition = CanonicalComposition(
        ingredient="paracetamol",
        strength="500",
        unit="mg",
        dosage_form=MedicineType.TABLET,
        route="oral",
    )
    return GenericFinderSearchResponse(
        source_medicine=None,
        normalized_composition=composition,
        matches=[],
        message="No Exact Generic Substitute Found",
    )


# ── /ocr/composition ──────────────────────────────────────────────────────────

class TestOCRComposition:
    ENDPOINT = "/ocr/composition"

    def test_success(self, client, auth_headers, mock_ocr_service, valid_png_file, generic_finder_response):
        """Happy path: valid image → OCR → parse → generic finder → 200."""
        with patch("app.api.routes.ocr.GenericFinderService") as mock_gf_cls:
            mock_gf = MagicMock()
            mock_gf_cls.return_value = mock_gf
            mock_gf.scan_by_composition.return_value = generic_finder_response

            resp = client.post(self.ENDPOINT, files=valid_png_file, headers=auth_headers)

        assert resp.status_code == 200
        body = resp.json()
        assert body["ocr_confidence"] == 0.95
        assert body["processing_time_ms"] >= 0
        assert body["quality_diagnostics"] is None
        assert body["result"]["message"] == "No Exact Generic Substitute Found"
        assert body["result"]["normalized_composition"]["ingredient"] == "paracetamol"
        mock_ocr_service.extract_bytes.assert_called_once()

    def test_ocr_failure_returns_500(self, client, auth_headers, mock_ocr_service, valid_png_file):
        """OCR engine failure → 500."""
        mock_ocr_service.extract_bytes.side_effect = OCRError("OCR engine crashed")

        resp = client.post(self.ENDPOINT, files=valid_png_file, headers=auth_headers)

        assert resp.status_code == 500
        assert "OCR processing failed" in resp.json()["message"]

    def test_ocr_invalid_mime_type_returns_415(self, client, auth_headers):
        """Unsupported MIME type → 415."""
        resp = client.post(
            self.ENDPOINT,
            files={"file": ("test.bmp", b"fake", "image/bmp")},
            headers=auth_headers,
        )
        assert resp.status_code == 415

    def test_ocr_file_too_large_returns_413(self, client, auth_headers, mock_ocr_service):
        """File size exceeds limit → 413."""
        mock_ocr_service.extract_bytes.side_effect = ValueError(
            "Image size too large. Max 5 MB allowed"
        )
        resp = client.post(
            self.ENDPOINT,
            files={"file": ("test.png", b"x" * 100, "image/png")},
            headers=auth_headers,
        )
        assert resp.status_code == 413

    def test_ocr_generic_value_error_returns_400(self, client, auth_headers, mock_ocr_service):
        """Generic ValueError from OCR → 400."""
        mock_ocr_service.extract_bytes.side_effect = ValueError("Something went wrong")

        resp = client.post(
            self.ENDPOINT,
            files={"file": ("test.png", b"fake", "image/png")},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_parser_failure_returns_422(self, client, auth_headers, mock_ocr_service):
        """Composition parser cannot parse → 422."""
        mock_ocr_service.extract_bytes.return_value = OCRResult(
            text="@@@ invalid @@@",
            average_confidence=0.5,
        )
        resp = client.post(
            self.ENDPOINT,
            files={"file": ("test.png", b"fake", "image/png")},
            headers=auth_headers,
        )
        assert resp.status_code == 422
        assert "Could not parse medicine composition" in resp.json()["message"]

    def test_empty_ocr_text_returns_422(self, client, auth_headers, mock_ocr_service):
        """OCR returns empty/whitespace-only text → 422."""
        mock_ocr_service.extract_bytes.return_value = OCRResult(
            text="   \n  \t  ",
            average_confidence=0.0,
        )
        resp = client.post(
            self.ENDPOINT,
            files={"file": ("test.png", b"fake", "image/png")},
            headers=auth_headers,
        )
        assert resp.status_code == 422
        assert "No text could be extracted" in resp.json()["message"]

    def test_unauthorized_without_auth(self, client, mock_ocr_service, valid_png_file):
        """No auth token → 401."""
        resp = client.post(self.ENDPOINT, files=valid_png_file)
        assert resp.status_code == 401
        assert "Authentication" in resp.json()["message"]


# ── /ocr/pharmacy-bill ────────────────────────────────────────────────────────

class TestOCRPharmacyBill:
    ENDPOINT = "/ocr/pharmacy-bill"

    def test_success(self, client, auth_headers, mock_ocr_service):
        """Happy path: valid image → OCR → parse bill → 200."""
        mock_ocr_service.extract_bytes.return_value = OCRResult(
            text="Paracetamol 500 mg\nQty 10",
            average_confidence=0.92,
        )
        resp = client.post(
            self.ENDPOINT,
            files={"file": ("test.png", b"fake", "image/png")},
            headers=auth_headers,
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["ocr_confidence"] == 0.92
        assert body["quality_diagnostics"] is None
        assert body["processing_time_ms"] >= 0
        assert len(body["result"]["medicines"]) == 1
        assert body["result"]["medicines"][0]["medicine_name"] == "Paracetamol"
        assert body["result"]["medicines"][0]["quantity"] == 10.0

    def test_parser_failure_returns_422(self, client, auth_headers, mock_ocr_service):
        """Bill parser cannot parse → 422."""
        mock_ocr_service.extract_bytes.return_value = OCRResult(
            text="Qty 10\nSomething",
            average_confidence=0.6,
        )
        resp = client.post(
            self.ENDPOINT,
            files={"file": ("test.png", b"fake", "image/png")},
            headers=auth_headers,
        )
        assert resp.status_code == 422
        assert "Could not parse medicine entries" in resp.json()["message"]

    def test_ocr_failure_returns_500(self, client, auth_headers, mock_ocr_service):
        """OCR engine failure → 500."""
        mock_ocr_service.extract_bytes.side_effect = OCRError("Engine timeout")

        resp = client.post(
            self.ENDPOINT,
            files={"file": ("test.png", b"fake", "image/png")},
            headers=auth_headers,
        )
        assert resp.status_code == 500

    def test_missing_file_returns_422(self, client, auth_headers):
        """No file uploaded → 422 (FastAPI validation)."""
        resp = client.post(self.ENDPOINT, headers=auth_headers)
        assert resp.status_code == 422


# ── /ocr/document ─────────────────────────────────────────────────────────────

class TestOCRDocument:
    ENDPOINT = "/ocr/document"

    def test_success(self, client, auth_headers, mock_ocr_service):
        """Happy path: valid image → OCR → parse document → 200."""
        mock_ocr_service.extract_bytes.return_value = OCRResult(
            text=(
                "Prescription\n"
                "Patient: John Doe\n"
                "Dr. Smith\n"
                "Date: 12/05/2026\n"
                "Paracetamol 500 mg"
            ),
            average_confidence=0.88,
        )
        resp = client.post(
            self.ENDPOINT,
            files={"file": ("test.png", b"fake", "image/png")},
            headers=auth_headers,
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["ocr_confidence"] == 0.88
        assert body["quality_diagnostics"] is None
        assert body["processing_time_ms"] >= 0
        assert body["result"]["document_type"] == "prescription"
        assert body["result"]["patient_name"] == "John Doe"
        assert len(body["result"]["medicines"]) == 1
        assert body["result"]["medicines"][0]["medicine_name"] == "Paracetamol"

    def test_unknown_document_type(self, client, auth_headers, mock_ocr_service):
        """Document with no matching keywords → document_type == other."""
        mock_ocr_service.extract_bytes.return_value = OCRResult(
            text="Shopping list\nMilk\nEggs",
            average_confidence=0.7,
        )
        resp = client.post(
            self.ENDPOINT,
            files={"file": ("test.png", b"fake", "image/png")},
            headers=auth_headers,
        )

        assert resp.status_code == 200
        assert resp.json()["result"]["document_type"] == "other"

    def test_empty_ocr_text_returns_422(self, client, auth_headers, mock_ocr_service):
        """OCR returns only short/noise lines → 422 (cleaned to empty)."""
        mock_ocr_service.extract_bytes.return_value = OCRResult(
            text="X\nY",
            average_confidence=0.4,
        )
        resp = client.post(
            self.ENDPOINT,
            files={"file": ("test.png", b"fake", "image/png")},
            headers=auth_headers,
        )
        assert resp.status_code == 422
        assert "No text could be extracted" in resp.json()["message"]

    def test_ocr_failure_returns_500(self, client, auth_headers, mock_ocr_service):
        """OCR engine failure → 500."""
        mock_ocr_service.extract_bytes.side_effect = OCRError("No text found")

        resp = client.post(
            self.ENDPOINT,
            files={"file": ("test.png", b"fake", "image/png")},
            headers=auth_headers,
        )
        assert resp.status_code == 500

    def test_unsupported_mime_type_returns_415(self, client, auth_headers):
        """Unsupported file type → 415."""
        resp = client.post(
            self.ENDPOINT,
            files={"file": ("test.gif", b"fake", "image/gif")},
            headers=auth_headers,
        )
        assert resp.status_code == 415


# ── text_cleaner ──────────────────────────────────────────────────────────────

class TestTextCleaner:
    def test_clean_basic(self):
        from app.services.text_cleaner import TextCleaner

        cleaner = TextCleaner()
        result = cleaner.clean("  Hello   World  \n  \n  \n  Foo  ")
        assert result == "Hello World\n\nFoo"

    def test_clean_removes_short_lines(self):
        from app.services.text_cleaner import TextCleaner

        cleaner = TextCleaner()
        result = cleaner.clean("Hello\nA\nWorld\nBC")
        assert "Hello" in result
        assert "World" in result
        assert "\nA\n" not in result
        assert "\nBC" not in result

    def test_clean_empty(self):
        from app.services.text_cleaner import TextCleaner

        cleaner = TextCleaner()
        assert cleaner.clean("") == ""
        assert cleaner.clean("   \n  \t  ") == ""