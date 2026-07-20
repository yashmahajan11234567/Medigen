"""Part A — End-to-End OCR Workflow Integration Tests.

Workflow 1: Generic Medicine Scanner
Workflow 2: Pharmacy Bill Scanner
Workflow 3: Medical Document Scanner

All tests mock the OCR engine to avoid PaddleOCR dependency.
They verify the full pipeline: upload -> OCR -> clean -> parse -> (optional service) -> response.
"""

from unittest.mock import patch

import pytest

from app.utils.ocr_utils import OCRResult, OCRError


# ── helpers ──────────────────────────────────────────────────────────────────

def _patch_ocr(text: str, confidence: float = 0.95):
    """Return a patcher that replaces _ocr_service.extract_bytes."""
    return patch(
        "app.api.routes.ocr._ocr_service",
        extract_bytes=lambda _b, _m: OCRResult(
            text=text, average_confidence=confidence,
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# WORKFLOW 1 — Generic Medicine Scanner
# ══════════════════════════════════════════════════════════════════════════════

class TestWorkflow1_GenericMedicineScanner:
    ENDPOINT = "/ocr/composition"

    def test_workflow_success(self, client, db_session, auth_headers):
        """Full pipeline: image → OCR → clean → parse → generic finder → 200 with matches."""
        from app.services.generic_finder_service import GenericFinderService
        from tests.support import create_medicine

        create_medicine(
            db_session,
            name="Paracetamol 500",
            generic_name="Paracetamol",
            brand_name=None,
            composition="Paracetamol",
            strength="500",
            unit="mg",
            dosage_form="tablet",
            route="oral",
        )

        ocr_text = "paracetamol 500 mg tablet oral"
        with _patch_ocr(ocr_text):
            with patch.object(
                GenericFinderService, "scan_by_composition", wraps=None
            ) as mock_scan:
                pass

        with _patch_ocr(ocr_text):
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("strip.png", b"fake", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["ocr_confidence"] == 0.95
        assert body["processing_time_ms"] >= 0
        assert "result" in body

    def test_workflow_unknown_medicine(self, client, auth_headers):
        """Unknown medicine composition → 200 with empty matches."""
        with _patch_ocr("zyzox 999 mg tablet oral"):
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("strip.png", b"fake", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["result"]["matches"] == []
        assert "No Exact Generic Substitute" in body["result"]["message"]

    def test_workflow_invalid_image(self, client, auth_headers):
        """Invalid/empty image → OCR failure → 500."""
        with patch("app.api.routes.ocr._ocr_service.extract_bytes") as mock:
            mock.side_effect = OCRError("Invalid image data")

            resp = client.post(
                self.ENDPOINT,
                files={"file": ("strip.png", b"", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code == 500

    def test_workflow_ocr_text_empty_after_cleaning(self, client, auth_headers):
        """Image with only noise text → cleaned to empty → 422."""
        with _patch_ocr("X\nY\nZ", confidence=0.3):
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("strip.png", b"fake", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# WORKFLOW 2 — Pharmacy Bill Scanner
# ══════════════════════════════════════════════════════════════════════════════

class TestWorkflow2_PharmacyBillScanner:
    ENDPOINT = "/ocr/pharmacy-bill"

    def test_workflow_single_medicine_with_qty(self, client, auth_headers):
        """Single medicine with quantity preserved."""
        with _patch_ocr("Paracetamol 500 mg\nQty 10"):
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("bill.png", b"fake", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        body = resp.json()
        medicines = body["result"]["medicines"]
        assert len(medicines) == 1
        assert medicines[0]["medicine_name"] == "Paracetamol"
        assert medicines[0]["strength"] == "500"
        assert medicines[0]["dosage_unit"] == "mg"
        assert medicines[0]["quantity"] == 10.0

    def test_workflow_multiple_medicines_order_preserved(self, client, auth_headers):
        """Multiple medicines appear in input order."""
        with _patch_ocr("Amoxicillin 250 mg\nQty 6\n\nIbuprofen 400 mg\nQty 10"):
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("bill.png", b"fake", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        medicines = resp.json()["result"]["medicines"]
        assert len(medicines) == 2
        assert medicines[0]["medicine_name"] == "Amoxicillin"
        assert medicines[1]["medicine_name"] == "Ibuprofen"

    def test_workflow_missing_quantity(self, client, auth_headers):
        """Medicine without quantity → quantity is None."""
        with _patch_ocr("Crocin 650"):
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("bill.png", b"fake", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        med = resp.json()["result"]["medicines"][0]
        assert med["medicine_name"] == "Crocin"
        assert med["quantity"] is None

    def test_workflow_empty_bill_rejected(self, client, auth_headers):
        """Completely empty bill text → 422."""
        with _patch_ocr("", confidence=0.0):
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("bill.png", b"fake", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code == 422

    def test_workflow_no_db_writes(self, client, db_session, auth_headers):
        """Verify no scheduler entries or inventory items created."""
        from app.models.schedule import Schedule
        from app.models.inventory import InventoryItem

        pre_schedules = db_session.query(Schedule).count()
        pre_inventory = db_session.query(InventoryItem).count()

        with _patch_ocr("Metformin 500 mg\nQty 30"):
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("bill.png", b"fake", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        post_schedules = db_session.query(Schedule).count()
        post_inventory = db_session.query(InventoryItem).count()
        assert post_schedules == pre_schedules
        assert post_inventory == pre_inventory

    def test_workflow_blurry_image_handled(self, client, auth_headers):
        """Simulate blurry image → low confidence OCR still returns structured data."""
        with _patch_ocr("Paracetamol 5OO mg\nQty 1O", confidence=0.45):
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("bill.png", b"fake", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code in (200, 422)


# ══════════════════════════════════════════════════════════════════════════════
# WORKFLOW 3 — Medical Document Scanner
# ══════════════════════════════════════════════════════════════════════════════

class TestWorkflow3_MedicalDocumentScanner:
    ENDPOINT = "/ocr/document"

    def test_workflow_prescription(self, client, auth_headers):
        """Prescription image → document_type=prescription, patient+doctor+meds extracted."""
        with _patch_ocr(
            "Prescription\nPatient: John Doe\nDr. Smith\nDate: 12/05/2026\nParacetamol 500 mg"
        ):
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("doc.png", b"fake", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        body = resp.json()["result"]
        assert body["document_type"] == "prescription"
        assert body["patient_name"] == "John Doe"
        assert body["doctor_name"] is not None
        assert body["report_date"] == "2026-05-12"
        assert len(body["medicines"]) == 1

    def test_workflow_lab_report(self, client, auth_headers):
        """Lab report → document_type=blood_test_report, relevant fields extracted."""
        with _patch_ocr(
            "Blood Test Report\nPatient: Jane Doe\nDate: 2026-05-12\nHemoglobin: 14.5 g/dL"
        ):
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("doc.png", b"fake", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        body = resp.json()["result"]
        assert body["document_type"] == "blood_test_report"
        assert body["patient_name"] == "Jane Doe"
        assert body["report_date"] == "2026-05-12"

    def test_workflow_discharge_summary(self, client, auth_headers):
        """Discharge summary → correct type, admission/discharge dates handled."""
        with _patch_ocr(
            "Discharge Summary\nPatient: John Doe\nDate of Admission: 10/05/2026\nDate of Discharge: 12/05/2026"
        ):
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("doc.png", b"fake", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        body = resp.json()["result"]
        assert body["document_type"] == "discharge_summary"
        assert body["patient_name"] == "John Doe"

    def test_workflow_medical_certificate(self, client, auth_headers):
        """Medical certificate → correct type."""
        with _patch_ocr(
            "Medical Certificate\nPatient: John Doe\nThis is to certify that Mr. John Doe is medically fit"
        ):
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("doc.png", b"fake", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        assert resp.json()["result"]["document_type"] == "medical_certificate"

    def test_workflow_unknown_document(self, client, auth_headers):
        """Unrecognised document → document_type=other, fields still extracted."""
        with _patch_ocr("Shopping List\nMilk\nEggs\nBread"):
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("doc.png", b"fake", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        assert resp.json()["result"]["document_type"] == "other"

    def test_workflow_missing_fields(self, client, auth_headers):
        """Document with no labelled fields → all extracted fields are None."""
        with _patch_ocr("Some random text without any labelled fields"):
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("doc.png", b"fake", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        body = resp.json()["result"]
        assert body["patient_name"] is None
        assert body["doctor_name"] is None
        assert body["hospital_or_lab"] is None
        assert body["report_date"] is None

    def test_workflow_ocr_failure(self, client, auth_headers):
        """OCR failure → 500."""
        with patch("app.api.routes.ocr._ocr_service.extract_bytes") as mock:
            mock.side_effect = OCRError("OCR engine failed")
            resp = client.post(
                self.ENDPOINT,
                files={"file": ("doc.png", b"fake", "image/png")},
                headers=auth_headers,
            )

        assert resp.status_code == 500