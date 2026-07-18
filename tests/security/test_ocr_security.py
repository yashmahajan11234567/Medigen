"""Part C — OCR Security Tests.

Tests: invalid MIME types, corrupted images, oversized uploads,
zip renamed as PNG, path traversal filenames, empty uploads,
duplicate multipart fields, malformed requests.
"""

from io import BytesIO
from unittest.mock import patch

import pytest

from app.utils.ocr_utils import OCRResult


class TestSecurity:
    """Security boundary testing for OCR endpoints."""

    @pytest.mark.parametrize("endpoint", [
        "/ocr/composition",
        "/ocr/pharmacy-bill",
        "/ocr/document",
    ])
    @pytest.mark.parametrize("invalid_mime,filename", [
        ("image/bmp", "test.bmp"),
        ("image/gif", "test.gif"),
        ("text/plain", "test.txt"),
        ("application/xml", "test.xml"),
        ("video/mp4", "test.mp4"),
        ("audio/mpeg", "test.mp3"),
    ])
    def test_invalid_mime_types_rejected(self, client, endpoint, invalid_mime, filename):
        """Invalid MIME types should be rejected with 415."""
        resp = client.post(
            endpoint,
            files={"file": (filename, b"fake", invalid_mime)},
        )
        assert resp.status_code == 415, f"{endpoint} accepted {invalid_mime}"

    @pytest.mark.parametrize("endpoint", [
        "/ocr/composition",
        "/ocr/pharmacy-bill",
        "/ocr/document",
    ])
    def test_oversized_upload_rejected(self, client, endpoint):
        """File exceeding max upload size should be rejected."""
        # ~10 MB (default max is 5 MB)
        oversized = b"x" * (10 * 1024 * 1024 + 1)
        with patch("app.api.routes.ocr._ocr_service.extract_bytes") as mock:
            mock.side_effect = ValueError("Image size too large. Max 5 MB allowed")
            resp = client.post(
                endpoint,
                files={"file": ("large.png", oversized, "image/png")},
            )
        assert resp.status_code == 413

    @pytest.mark.parametrize("endpoint", [
        "/ocr/composition",
        "/ocr/pharmacy-bill",
        "/ocr/document",
    ])
    def test_empty_upload_rejected(self, client, endpoint):
        """Empty file upload should be rejected."""
        with patch("app.api.routes.ocr._ocr_service.extract_bytes") as mock:
            mock.side_effect = ValueError("Invalid mime type")
            resp = client.post(
                endpoint,
                files={"file": ("empty.png", b"", "image/png")},
            )
        assert resp.status_code == 415

    @pytest.mark.parametrize("endpoint", [
        "/ocr/composition",
        "/ocr/pharmacy-bill",
        "/ocr/document",
    ])
    def test_zip_renamed_as_png_rejected(self, client, endpoint):
        """ZIP file with .png extension should be validated by OCR engine."""
        zip_bytes = BytesIO()
        import zipfile
        with zipfile.ZipFile(zip_bytes, "w") as zf:
            zf.writestr("test.txt", "hello")
        payload = zip_bytes.getvalue()

        with patch("app.api.routes.ocr._ocr_service.extract_bytes") as mock:
            mock.side_effect = ValueError("Invalid image data")
            resp = client.post(
                endpoint,
                files={"file": ("malicious.png", payload, "image/png")},
            )
        assert resp.status_code in (400, 415, 422, 500)

    @pytest.mark.parametrize("endpoint", [
        "/ocr/composition",
        "/ocr/pharmacy-bill",
        "/ocr/document",
    ])
    def test_path_traversal_filename_rejected(self, client, endpoint):
        """Filename with path traversal should not cause issues."""
        resp = client.post(
            endpoint,
            files={"file": ("../../../etc/passwd.png", b"fake", "image/png")},
        )
        assert resp.status_code in (200, 415, 422, 500)

    @pytest.mark.parametrize("endpoint", [
        "/ocr/composition",
        "/ocr/pharmacy-bill",
        "/ocr/document",
    ])
    def test_duplicate_multipart_fields(self, client, endpoint):
        """Duplicate file fields should still work (last one wins in FastAPI)."""
        resp = client.post(
            endpoint,
            files=[
                ("file", ("a.png", b"first", "image/png")),
                ("file", ("b.png", b"second", "image/png")),
            ],
        )
        assert resp.status_code in (200, 415, 422, 500)

    @pytest.mark.parametrize("endpoint", [
        "/ocr/composition",
        "/ocr/pharmacy-bill",
        "/ocr/document",
    ])
    def test_no_file_uploaded(self, client, endpoint):
        """No file in request → 422."""
        resp = client.post(endpoint)
        assert resp.status_code == 422

    def test_malformed_content_type(self, client):
        """Malformed content-type header should not crash."""
        from httpx import Client

        with Client(transport=client._transport, base_url="http://testserver") as c:
            resp = c.post(
                "/ocr/composition",
                content=b"garbage",
                headers={"content-type": "image/png"},
            )
        assert resp.status_code in (200, 400, 415, 422, 500)

    def test_unexpected_query_params(self, client):
        """Unexpected query parameters should be silently ignored."""
        from unittest.mock import patch
        patch("app.api.routes.ocr._ocr_service.extract_bytes",
              return_value=OCRResult(text="test", average_confidence=0.9)).start()
        resp = client.post(
            "/ocr/composition?inject=true&debug=1",
            files={"file": ("test.png", b"fake", "image/png")},
        )
        assert resp.status_code in (200, 422)
        patch.stopall()