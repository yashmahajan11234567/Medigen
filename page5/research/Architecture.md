# Architecture Notes

MedicalRecord
 ├── Documents
 │    ├── Prescription
 │    ├── Pharmacy Bill
 │    └── Other Document
 ├── Notes
 ├── Linked Schedule IDs
 ├── Linked Inventory IDs
 └── Linked Generic Search IDs

Recommendation:
Store links (IDs), never duplicate data across modules.
