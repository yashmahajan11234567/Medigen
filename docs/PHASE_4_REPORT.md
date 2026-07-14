# Phase 4 Report

## 1. Summary
- Implemented the Inventory backend only.
- Replaced the placeholder Inventory routes with authenticated CRUD, search, filter, detail, list, and summary endpoints.
- Added an Inventory repository, Inventory service, and Inventory integration service so Inventory remains the single stock owner.
- Updated Generic Finder integration to add selected generic medicines through Inventory instead of bypassing it.

## 2. Architecture Decisions
- Preserved the Phase 1 to Phase 3 module structure and added Inventory logic only in:
  - `repositories`
  - `services`
  - `schemas`
  - `api/routes`
- Kept database access in repositories only.
- Kept validation, duplicate prevention, status calculation, expiry handling, and summary generation inside `InventoryService`.
- Kept cross-module inventory writes behind `InventoryIntegrationService`.
- Treated `Finished` as the Inventory-facing alias for `out_of_stock`, so the API matches the documented filter wording without changing the underlying ownership model.
- Added `ointment` to the supported medicine types because the Inventory docs list it explicitly.

## 3. Files Created
- `C:\Users\hitoy\Downloads\Medigen\app\repositories\inventory_repository.py`
- `C:\Users\hitoy\Downloads\Medigen\app\schemas\inventory.py`
- `C:\Users\hitoy\Downloads\Medigen\app\services\inventory_service.py`
- `C:\Users\hitoy\Downloads\Medigen\tests\db\test_inventory_repository.py`
- `C:\Users\hitoy\Downloads\Medigen\tests\unit\test_inventory_service.py`
- `C:\Users\hitoy\Downloads\Medigen\tests\api\test_inventory.py`

## 4. Files Modified
- `C:\Users\hitoy\Downloads\Medigen\app\api\routes\inventory.py`
- `C:\Users\hitoy\Downloads\Medigen\app\services\inventory_integration_service.py`
- `C:\Users\hitoy\Downloads\Medigen\app\services\generic_finder_service.py`
- `C:\Users\hitoy\Downloads\Medigen\app\schemas\generic_finder.py`
- `C:\Users\hitoy\Downloads\Medigen\app\core\enums.py`
- `C:\Users\hitoy\Downloads\Medigen\tests\support.py`
- `C:\Users\hitoy\Downloads\Medigen\tests\api\test_generic_finder.py`
- `C:\Users\hitoy\Downloads\Medigen\tests\api\test_placeholder_routes.py`

## 5. Repository Methods
- `InventoryRepository.add_inventory_item(inventory_item)`
- `InventoryRepository.update_inventory_item(inventory_item)`
- `InventoryRepository.soft_delete_inventory_item(inventory_item)`
- `InventoryRepository.get_inventory_item_by_id(user_id, inventory_id)`
- `InventoryRepository.list_inventory_items(user_id)`
- `InventoryRepository.search_medicines(user_id, query)`
- `InventoryRepository.filter_medicines(user_id, statuses=None, medicine_type=None)`
- `InventoryRepository.get_duplicate_inventory_item(user_id, medicine_id, expiry_date, exclude_inventory_id=None)`
- `InventoryRepository.get_inventory_summary(user_id)`
- `InventoryRepository.get_expiring_medicines(user_id)`

## 6. Service Methods
- `InventoryService.list_inventory(user_id)`
- `InventoryService.get_inventory_item(user_id, inventory_id)`
- `InventoryService.create_inventory_item(user_id, payload)`
- `InventoryService.update_inventory_item(user_id, inventory_id, payload)`
- `InventoryService.delete_inventory_item(user_id, inventory_id)`
- `InventoryService.search_inventory(user_id, query)`
- `InventoryService.filter_inventory(user_id, status=None, medicine_type=None)`
- `InventoryService.get_inventory_summary(user_id)`
- `InventoryService.add_generic_medicine_to_inventory(...)`
- `InventoryService.add_scheduler_medicine_to_inventory(...)`

## 7. Integration Methods
- `InventoryIntegrationService.add_generic_medicine(...)`
- `InventoryIntegrationService.add_scheduler_medicine(...)`

These methods route external module writes through Inventory instead of allowing direct table updates.

## 8. API Endpoints
- `GET /api/v1/inventory`
- `GET /api/v1/inventory/{id}`
- `POST /api/v1/inventory`
- `PUT /api/v1/inventory/{id}`
- `DELETE /api/v1/inventory/{id}`
- `GET /api/v1/inventory/search`
- `GET /api/v1/inventory/filter`
- `GET /api/v1/inventory/summary`

## 9. Validation Rules
- Rejects duplicate inventory entries for the same user, medicine, and expiry date.
- Rejects invalid expiry dates when expiry is earlier than purchase date.
- Rejects negative quantities.
- Requires quantity for tablets and capsules.
- Rejects missing medicine names when a manual create request does not provide `medicine_id`.
- Rejects invalid inventory filter values.
- Rejects unknown medicine IDs.

## 10. Test Coverage
- Repository:
  - list
  - search
  - filter
  - summary
  - duplicate lookup
  - expiring medicines
- Service:
  - create
  - summary
  - finished state
  - expired state
  - duplicate prevention
  - invalid quantity
  - search
  - filters
- API:
  - CRUD
  - search
  - filter
  - summary
  - auth enforcement
  - Generic Finder integration handoff
- Regression:
  - all previous Phase 1, Phase 2, and Phase 3 tests still pass

## 11. Test Results
- `python -m pytest`
- Result: `47 passed`

Additional verification:
- `GET /openapi.json` returned `200`
- Seeded `POST /api/v1/inventory` returned `201`
- Seeded `GET /api/v1/inventory/summary` returned `200`

## 12. Known Limitations
- Inventory images are metadata only and currently store an image path string; no upload pipeline was implemented in this phase.
- Manual Inventory creation can create a new `Medicine` row when no `medicine_id` is supplied, but this is still a backend-only path with no catalog moderation workflow yet.
- Scheduler integration methods are available through `InventoryIntegrationService`, but Scheduler logic itself remains out of scope and unimplemented.
- Status values are recalculated by the service using current date and quantity rules, which means older rows may be synchronized on read rather than only by background jobs.

## 13. Assumptions
- `Finished` maps to `out_of_stock` in the persisted inventory status model.
- `Available Medicines` in the summary includes both `available` and `low_stock` items.
- `Expiring Soon` is defined as an expiry date within the next 30 days, excluding already expired medicines.
- Tablets and capsules are quantity-tracked; syrups, creams, ointments, injections, and drops are primarily availability-tracked with expiry awareness.
- Generic Finder integration defaults quantity-tracked generic additions to quantity `1` when the caller does not provide a quantity, so the integration can succeed without introducing direct Inventory CRUD in Generic Finder.
