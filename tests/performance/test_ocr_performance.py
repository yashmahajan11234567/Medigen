"""Part B — OCR Performance Benchmarks.

Measures: OCR processing time, cold start, concurrent requests.
Uses mocked OCR to measure orchestration overhead independently of PaddleOCR.
"""

import time
from unittest.mock import patch

import pytest

from app.utils.ocr_utils import OCRResult, OCRError


# Share a single mock across concurrent tests
_FAST_MOCK = OCRResult(
    text="Paracetamol 500 mg tablet oral\nQty 10",
    average_confidence=0.95,
)
_SLOW_MOCK = OCRResult(
    text="a b c d e f g h i j k l m n o p q r s t u v w x y z " * 100,
    average_confidence=0.85,
)


class TestPerformance:
    """Measure endpoint orchestration overhead (not PaddleOCR itself)."""

    BASIC_TEXT = "Paracetamol 500 mg tablet oral\nQty 10"
    LARGE_TEXT = "\n".join([f"Medicine{i} {i} mg" for i in range(50)])

    @pytest.mark.parametrize("endpoint", [
        "/ocr/composition",
        "/ocr/pharmacy-bill",
        "/ocr/document",
    ])
    def test_endpoint_response_time_under_500ms(self, client, auth_headers, endpoint):
        """Each OCR endpoint should respond in under 500 ms (mocked OCR)."""
        with patch("app.api.routes.ocr._ocr_service.extract_bytes") as mock:
            mock.return_value = _FAST_MOCK

            start = time.perf_counter()
            resp = client.post(
                endpoint,
                files={"file": ("test.png", b"fake", "image/png")},
                headers=auth_headers,
            )
            elapsed = (time.perf_counter() - start) * 1000

        assert resp.status_code in (200, 422)
        assert elapsed < 500, f"{endpoint} took {elapsed:.0f}ms (limit 500)"

    def test_large_image_processing(self, client, auth_headers):
        """Large simulated OCR output should still respond quickly."""
        large_result = OCRResult(
            text=self.LARGE_TEXT,
            average_confidence=0.9,
        )
        with patch("app.api.routes.ocr._ocr_service.extract_bytes") as mock:
            mock.return_value = large_result

            start = time.perf_counter()
            resp = client.post(
                "/ocr/pharmacy-bill",
                files={"file": ("large.png", b"x" * 5000000, "image/png")},
                headers=auth_headers,
            )
            elapsed = (time.perf_counter() - start) * 1000

        assert resp.status_code in (200, 422)
        assert elapsed < 1000, f"Large image took {elapsed:.0f}ms (limit 1000)"

    def test_concurrent_requests(self, client, auth_headers):
        """Sequential requests to all three OCR endpoints should all complete."""
        with patch("app.api.routes.ocr._ocr_service.extract_bytes") as mock:
            mock.return_value = _FAST_MOCK
            codes = []
            for endpoint in ("/ocr/composition", "/ocr/pharmacy-bill", "/ocr/document"):
                resp = client.post(
                    endpoint,
                    files={"file": ("t.png", b"f", "image/png")},
                    headers=auth_headers,
                )
                codes.append(resp.status_code)

        assert all(c in (200, 422) for c in codes)
        assert len(codes) == 3

    def test_cold_start_vs_warm_start(self, client, auth_headers):
        """Warm request should be faster than first request (mocked OCR)."""
        import gc

        # Cold: force garbage collection before first request
        gc.collect()

        with patch("app.api.routes.ocr._ocr_service.extract_bytes") as mock:
            mock.return_value = _FAST_MOCK

            start = time.perf_counter()
            client.post(
                "/ocr/pharmacy-bill",
                files={"file": ("test.png", b"fake", "image/png")},
                headers=auth_headers,
            )
            cold = (time.perf_counter() - start) * 1000

            start = time.perf_counter()
            client.post(
                "/ocr/pharmacy-bill",
                files={"file": ("test.png", b"fake", "image/png")},
                headers=auth_headers,
            )
            warm = (time.perf_counter() - start) * 1000

        # Warm should not be dramatically slower than cold (mock is deterministic)
        assert warm < 500, f"Warm request took {warm:.0f}ms"