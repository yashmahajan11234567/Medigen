"""OCR Quality Assessment and Error Handling Tests — Phase 10.1.

Covers 7 required scenarios:
  1. Valid medicine strip (happy path with quality diagnostics)
  2. Blurry image (quality check flags blur)
  3. Blank image (empty upload rejected)
  4. Corrupted image (quality check rejects)
  5. Unsupported file type (MIME validation)
  6. Oversized upload (size limit enforcement)
  7. Low-confidence OCR result (below reject threshold)
"""

from unittest.mock import MagicMock, patch

import pytest

from app.core.enums import MedicineType
from app.schemas.generic_finder import (
    CanonicalComposition,
    GenericFinderSearchResponse,
)
from app.utils.ocr_utils import (
    ImageQualityError,
    ImageQualityIssue,
    OCRError,
    OCRResult,
    ScanQualityDiagnostics,
)


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def valid_png_file() -> dict:
    return {"file": ("test.png", b"fake-png-image-bytes", "image/png")}


@pytest.fixture
def mock_ocr_service():
    with patch("app.api.routes.ocr._ocr_service") as mock:
        mock.extract_bytes.return_value = OCRResult(
            text="Paracetamol 500 mg tablet oral",
            average_confidence=0.95,
            quality=ScanQualityDiagnostics(issues=[], is_pass=True),
        )
        yield mock


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


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO 1 — Valid Medicine Strip (happy path + quality diagnostics)
# ══════════════════════════════════════════════════════════════════════════════

class TestValidMedicineStrip:
    ENDPOINT = "/ocr/composition"

    def test_happy_path_with_quality_diagnostics(
        self, client, auth_headers, mock_ocr_service, valid_png_file, generic_finder_response,
    ):
        """Valid image with passing quality diagnostics → 200 + quality_diagnostics in response."""
        with patch("app.api.routes.ocr.GenericFinderService") as mock_gf_cls:
            mock_gf = MagicMock()
            mock_gf_cls.return_value = mock_gf
            mock_gf.scan_by_composition.return_value = generic_finder_response

            resp = client.post(self.ENDPOINT, files=valid_png_file, headers=auth_headers)

        assert resp.status_code == 200
        body = resp.json()
        assert body["ocr_confidence"] == 0.95
        assert body["processing_time_ms"] >= 0
        assert body["quality_diagnostics"] is not None
        assert body["quality_diagnostics"]["is_pass"] is True
        assert body["quality_diagnostics"]["issues"] == []
        assert body["result"]["message"] == "No Exact Generic Substitute Found"

    def test_all_endpoints_return_quality_diagnostics(
        self, client, auth_headers, generic_finder_response,
    ):
        """All three OCR endpoints include quality_diagnostics in successful responses."""
        from app.utils.ocr_utils import ScanQualityDiagnostics
        quality = ScanQualityDiagnostics(issues=[], is_pass=True)

        for endpoint in ("/ocr/composition", "/ocr/pharmacy-bill", "/ocr/document"):
            with patch("app.api.routes.ocr._ocr_service") as mock:
                mock.extract_bytes.return_value = OCRResult(
                    text="Paracetamol 500 mg tablet oral" if endpoint != "/ocr/document" else "Prescription\nPatient: Test",
                    average_confidence=0.9,
                    quality=quality,
                )

                if endpoint == "/ocr/composition":
                    with patch("app.api.routes.ocr.GenericFinderService") as mgf:
                        mgf.return_value.scan_by_composition.return_value = generic_finder_response
                        resp = client.post(endpoint, files={"file": ("t.png", b"x", "image/png")}, headers=auth_headers)
                else:
                    resp = client.post(endpoint, files={"file": ("t.png", b"x", "image/png")}, headers=auth_headers)

            assert resp.status_code == 200, f"{endpoint} failed: {resp.json()}"
            assert resp.json()["quality_diagnostics"] is not None
            assert resp.json()["quality_diagnostics"]["is_pass"] is True


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO 2 — Blurry Image
# ══════════════════════════════════════════════════════════════════════════════

class TestBlurryImage:
    ENDPOINT = "/ocr/document"

    def test_blurry_at_quality_check_level(self, client, auth_headers):
        """Quality check detects blur → route returns 200 with blur diagnostics (not a hard reject)."""
        quality = ScanQualityDiagnostics(
            issues=[ImageQualityIssue.BLURRY],
            blur_score=45.0,
            brightness=120.0,
            contrast=50.0,
            is_pass=False,
        )
        with patch("app.api.routes.ocr._ocr_service") as mock:
            mock.extract_bytes.return_value = OCRResult(
                text="Prescription\nPatient: Test\nParacetamol 500 mg",
                average_confidence=0.6,
                quality=quality,
            )
            resp = client.post(self.ENDPOINT, files={"file": ("t.png", b"x", "image/png")}, headers=auth_headers)

        # Blurry alone is NOT a hard reject — it just appears in quality_diagnostics
        assert resp.status_code == 200
        body = resp.json()
        assert body["quality_diagnostics"] is not None
        assert "blurry" in body["quality_diagnostics"]["issues"]
        assert body["quality_diagnostics"]["is_pass"] is False
        assert body["quality_diagnostics"]["blur_score"] == 45.0

    def test_blurry_image_via_service(self):
        """Service-level: assess_quality returns BLURRY — should not raise (only CORRUPTED/EMPTY reject)."""
        from app.services.ocr_service import OCRService
        preprocessor = MagicMock()
        engine = MagicMock()
        engine.extract_text.return_value = OCRResult(text="test", average_confidence=0.9)

        quality = ScanQualityDiagnostics(
            issues=[ImageQualityIssue.BLURRY],
            blur_score=45.0,
            brightness=120.0,
            contrast=50.0,
            is_pass=False,
        )
        preprocessor.assess_quality.return_value = quality
        preprocessor.preprocess.return_value = b"processed"

        service = OCRService(engine=engine, preprocessor=preprocessor)
        result = service.extract_bytes(b"img", "image/png")

        assert result.text == "test"
        assert result.quality is not None
        assert ImageQualityIssue.BLURRY in result.quality.issues


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO 3 — Blank / Empty Image
# ══════════════════════════════════════════════════════════════════════════════

class TestBlankImage:
    ENDPOINT = "/ocr/composition"

    def test_empty_file_bytes_rejected(self, client, auth_headers):
        """Sending empty bytes → 400 (empty data)."""
        with patch("app.api.routes.ocr._ocr_service.extract_bytes") as mock:
            mock.side_effect = ValueError("Empty image data received")
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("test.png", b"", "image/png")},
                headers=auth_headers,
            )
        assert resp.status_code == 400

    def test_empty_bytes_at_service_level(self):
        """Service-level: len(image_bytes)==0 → ValueError."""
        from app.services.ocr_service import OCRService
        engine = MagicMock()
        service = OCRService(engine=engine)
        with pytest.raises(ValueError, match="Empty image data"):
            service.extract_bytes(b"", "image/png")


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO 4 — Corrupted Image
# ══════════════════════════════════════════════════════════════════════════════

class TestCorruptedImage:
    ENDPOINT = "/ocr/composition"

    def test_corrupted_raises_image_quality_error(self, client, auth_headers):
        """Quality check detects CORRUPTED → route returns 422."""
        with patch("app.api.routes.ocr._ocr_service.extract_bytes") as mock:
            mock.side_effect = ImageQualityError(
                message="Image quality check failed: corrupted",
                code="image_corrupted",
                diagnostics=ScanQualityDiagnostics(
                    issues=[ImageQualityIssue.CORRUPTED],
                    is_pass=False,
                ),
            )
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("test.png", b"garbage", "image/png")},
                headers=auth_headers,
            )
        assert resp.status_code == 422
        assert "corrupted" in resp.json()["message"].lower()

    def test_corrupted_at_service_level(self):
        """Service-level: CORRUPTED quality issue → ImageQualityError raised."""
        from app.services.ocr_service import OCRService
        preprocessor = MagicMock()
        engine = MagicMock()
        quality = ScanQualityDiagnostics(
            issues=[ImageQualityIssue.CORRUPTED],
            is_pass=False,
        )
        preprocessor.assess_quality.return_value = quality

        service = OCRService(engine=engine, preprocessor=preprocessor)
        with pytest.raises(ImageQualityError, match="corrupted"):
            service.extract_bytes(b"garbage", "image/png")


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO 5 — Unsupported File Type
# ══════════════════════════════════════════════════════════════════════════════

class TestUnsupportedFileType:
    def test_mime_type_rejected_at_route(self, client, auth_headers):
        """Unsupported MIME type → 415."""
        for endpoint in ("/ocr/composition", "/ocr/pharmacy-bill", "/ocr/document"):
            resp = client.post(
                endpoint,
                files={"file": ("test.gif", b"fake", "image/gif")},
                headers=auth_headers,
            )
            assert resp.status_code == 415, f"{endpoint} should reject gif"

    def test_mime_type_rejected_at_service(self):
        """Service-level: unsupported MIME → ValueError."""
        from app.services.ocr_service import OCRService
        service = OCRService(engine=MagicMock())
        with pytest.raises(ValueError, match="Invalid mime type"):
            service.extract_bytes(b"data", "image/gif")

    def test_multiple_unsupported_types_rejected(self, client, auth_headers):
        """Multiple unsupported MIME types are all rejected."""
        unsupported = [
            ("test.bmp", b"x", "image/bmp"),
            ("test.tiff", b"x", "image/tiff"),
            ("test.webp", b"x", "image/webp"),
            ("test.svg", b"x", "image/svg+xml"),
        ]
        for filename, data, mime in unsupported:
            resp = client.post(
                "/ocr/composition",
                files={"file": (filename, data, mime)},
                headers=auth_headers,
            )
            assert resp.status_code == 415, f"{mime} should be rejected"


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO 6 — Oversized Upload
# ══════════════════════════════════════════════════════════════════════════════

class TestOversizedUpload:
    ENDPOINT = "/ocr/composition"

    def test_oversized_rejected_at_route(self, client, auth_headers):
        """File exceeding size limit → 413."""
        with patch("app.api.routes.ocr._ocr_service.extract_bytes") as mock:
            mock.side_effect = ValueError("Image size too large. Max 5 MB allowed")
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("test.png", b"x" * 100, "image/png")},
                headers=auth_headers,
            )
        assert resp.status_code == 413
        assert "large" in resp.json()["message"].lower()

    def test_oversized_rejected_at_service(self):
        """Service-level: oversized → ValueError."""
        from app.services.ocr_service import OCRService
        service = OCRService(engine=MagicMock())
        with pytest.raises(ValueError, match="Image size too large"):
            # Default OCR_MAX_UPLOAD_MB is 5, so 6MB of data should fail
            service.extract_bytes(b"x" * (6 * 1024 * 1024), "image/png")

    def test_size_at_limit_passes(self):
        """Service-level: exactly at the limit should pass validation and reach MIME/OCR stage."""
        from app.services.ocr_service import OCRService
        engine = MagicMock()
        engine.extract_text.return_value = OCRResult(text="test", average_confidence=0.9)
        # Default OCR_MAX_UPLOAD_MB is 5 → exactly 5MB should pass
        service = OCRService(engine=engine)
        result = service.extract_bytes(b"x" * (5 * 1024 * 1024), "image/png")
        assert result.text == "test"


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO 7 — Low-Confidence OCR Result
# ══════════════════════════════════════════════════════════════════════════════

class TestLowConfidenceOCR:
    ENDPOINT = "/ocr/composition"

    def test_low_confidence_rejected_at_route(self, client, auth_headers):
        """OCR result with confidence below reject threshold → 422/500."""
        with patch("app.api.routes.ocr._ocr_service.extract_bytes") as mock:
            mock.side_effect = OCRError(
                "OCR confidence too low (10.0%). Please provide a clearer image."
            )
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("test.png", b"fake", "image/png")},
                headers=auth_headers,
            )
        assert resp.status_code in (422, 500)
        assert "confidence too low" in resp.json()["message"].lower()

    def test_low_confidence_rejected_at_service(self):
        """Service-level: confidence below OCR_LOW_CONFIDENCE_REJECT_THRESHOLD → OCRError."""
        from app.services.ocr_service import OCRService
        engine = MagicMock()
        preprocessor = MagicMock()
        preprocessor.assess_quality.return_value = ScanQualityDiagnostics(issues=[], is_pass=True)
        preprocessor.preprocess.return_value = b"processed"
        # Default OCR_LOW_CONFIDENCE_REJECT_THRESHOLD is 0.25, so 0.1 is below
        engine.extract_text.return_value = OCRResult(
            text="noisy text",
            average_confidence=0.1,
            word_details=[("noisy", 0.1)],
        )

        service = OCRService(engine=engine, preprocessor=preprocessor)
        with pytest.raises(OCRError, match="confidence too low"):
            service.extract_bytes(b"img", "image/png")

    def test_confidence_above_threshold_passes(self):
        """Service-level: confidence above reject threshold passes through."""
        from app.services.ocr_service import OCRService
        engine = MagicMock()
        preprocessor = MagicMock()
        preprocessor.assess_quality.return_value = ScanQualityDiagnostics(issues=[], is_pass=True)
        preprocessor.preprocess.return_value = b"processed"
        engine.extract_text.return_value = OCRResult(
            text="valid", average_confidence=0.5, word_details=[("valid", 0.5)],
        )

        service = OCRService(engine=engine, preprocessor=preprocessor)
        result = service.extract_bytes(b"img", "image/png")
        assert result.text == "valid"
        assert result.average_confidence == 0.5

    def test_none_confidence_passes(self):
        """Service-level: None confidence (no detected text) passes (handled by text cleaner later)."""
        from app.services.ocr_service import OCRService
        engine = MagicMock()
        preprocessor = MagicMock()
        preprocessor.assess_quality.return_value = ScanQualityDiagnostics(issues=[], is_pass=True)
        preprocessor.preprocess.return_value = b"processed"
        engine.extract_text.return_value = OCRResult(
            text="", average_confidence=None,
        )

        service = OCRService(engine=engine, preprocessor=preprocessor)
        result = service.extract_bytes(b"img", "image/png")
        assert result.text == ""


# ══════════════════════════════════════════════════════════════════════════════
# Auth Enforcement — all endpoints require authentication
# ══════════════════════════════════════════════════════════════════════════════

class TestAuthEnforcement:
    def test_all_endpoints_require_auth(self, client):
        """All three OCR endpoints return 401 without auth."""
        for endpoint in ("/ocr/composition", "/ocr/pharmacy-bill", "/ocr/document"):
            resp = client.post(endpoint, files={"file": ("t.png", b"x", "image/png")})
            assert resp.status_code == 401, f"{endpoint} should require auth"

    def test_invalid_token_rejected(self, client):
        """Invalid auth token → 401."""
        headers = {"Authorization": "Bearer invalid-token"}
        for endpoint in ("/ocr/composition", "/ocr/pharmacy-bill", "/ocr/document"):
            resp = client.post(
                endpoint,
                files={"file": ("t.png", b"x", "image/png")},
                headers=headers,
            )
            assert resp.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# ImagePreprocessor quality assessment unit tests
# ══════════════════════════════════════════════════════════════════════════════

class TestImagePreprocessorQuality:
    def test_corrupted_image_detected(self):
        """Non-decodable bytes → CORRUPTED quality issue."""
        from app.services.image_preprocessing import ImagePreprocessor
        preprocessor = ImagePreprocessor()
        diagnostics = preprocessor.assess_quality(b"this is not a valid image")
        assert not diagnostics.is_pass
        assert ImageQualityIssue.CORRUPTED in diagnostics.issues

    def test_empty_image_detected(self):
        """Tiny image (e.g. 1x1) may pass decode but fail size check → check behavior."""
        from app.services.image_preprocessing import ImagePreprocessor
        import cv2
        import numpy as np
        # A 5x5 image should NOT be flagged as EMPTY (threshold is 10x10)
        small = np.zeros((5, 5, 3), dtype=np.uint8)
        _, encoded = cv2.imencode(".png", small)
        preprocessor = ImagePreprocessor()
        diagnostics = preprocessor.assess_quality(encoded.tobytes())
        # 5x5 < 10x10 → EMPTY issue
        assert not diagnostics.is_pass
        assert ImageQualityIssue.EMPTY in diagnostics.issues

    def test_quality_check_disabled(self):
        """When OCR_ENABLE_QUALITY_CHECK is False, always pass."""
        from app.services.image_preprocessing import ImagePreprocessor
        with patch("app.services.image_preprocessing.get_settings") as mock_settings:
            settings = MagicMock()
            settings.OCR_ENABLE_QUALITY_CHECK = False
            mock_settings.return_value = settings

            preprocessor = ImagePreprocessor()
            diagnostics = preprocessor.assess_quality(b"garbage")
            assert diagnostics.is_pass
            assert diagnostics.issues == []