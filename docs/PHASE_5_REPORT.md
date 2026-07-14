# Phase 5 Report

## 1. Summary
- Implemented the Medicine Scheduler backend only.
- Replaced the placeholder Scheduler routes with authenticated CRUD, today, bill-based creation, and reminder-completion endpoints.
- Added a dedicated scheduler repository, scheduler service, schedule reminder model, and schedule schemas.
- Kept Scheduler independent from Generic Medicine Finder and routed inventory coordination only through `InventoryIntegrationService`.

## 2. Architecture Decisions
- Preserved the existing layered FastAPI architecture and added Scheduler logic only in:
  - `repositories`
  - `services`
  - `schemas`
  - `api/routes`
  - `models` where schema support was necessary
- Added a dedicated `schedule_reminders` table because reminder completion and per-day reminder generation require schedule-owned reminder instances.
- Kept Dashboard compatibility intact by preserving the existing `schedules` row as the schedule owner and continuing to populate:
  - `start_date`
  - `end_date`
  - `reminder_time`
  - `dosage_amount`
- Kept Inventory ownership intact by using `InventoryIntegrationService` instead of writing Inventory rows directly from Scheduler.

## 3. Files Created
- `C:\Users\hitoy\Downloads\Medigen\app\models\schedule_reminder.py`
- `C:\Users\hitoy\Downloads\Medigen\app\repositories\schedule_repository.py`
- `C:\Users\hitoy\Downloads\Medigen\app\schemas\schedule.py`
- `C:\Users\hitoy\Downloads\Medigen\app\services\scheduler_service.py`
- `C:\Users\hitoy\Downloads\Medigen\alembic\versions\20260713_0002_schedule_backend_expansion.py`
- `C:\Users\hitoy\Downloads\Medigen\tests\db\test_schedule_repository.py`
- `C:\Users\hitoy\Downloads\Medigen\tests\unit\test_scheduler_service.py`
- `C:\Users\hitoy\Downloads\Medigen\tests\api\test_schedule.py`

## 4. Files Modified
- `C:\Users\hitoy\Downloads\Medigen\app\api\routes\schedule.py`
- `C:\Users\hitoy\Downloads\Medigen\app\models\schedule.py`
- `C:\Users\hitoy\Downloads\Medigen\app\models\__init__.py`
- `C:\Users\hitoy\Downloads\Medigen\app\core\enums.py`
- `C:\Users\hitoy\Downloads\Medigen\app\services\inventory_integration_service.py`
- `C:\Users\hitoy\Downloads\Medigen\tests\db\test_schema.py`
- `C:\Users\hitoy\Downloads\Medigen\tests\api\test_placeholder_routes.py`

## 5. Repository Methods
- `ScheduleRepository.create_schedule(schedule, reminders)`
- `ScheduleRepository.update_schedule(schedule, reminders=None)`
- `ScheduleRepository.delete_schedule(schedule)`
- `ScheduleRepository.get_schedule_by_id(user_id, schedule_id)`
- `ScheduleRepository.get_schedules_by_user(user_id)`
- `ScheduleRepository.get_schedules_by_date(user_id, target_date)`
- `ScheduleRepository.get_todays_schedule(user_id, today)`
- `ScheduleRepository.get_active_schedules(user_id)`
- `ScheduleRepository.get_duplicate_active_schedule(user_id, medicine_id, start_date, end_date, exclude_schedule_id=None)`
- `ScheduleRepository.get_reminder_by_id(user_id, reminder_id)`
- `ScheduleRepository.mark_reminder_completed(reminder)`

## 6. Service Methods
- `SchedulerService.list_schedules(user_id)`
- `SchedulerService.get_schedule(user_id, schedule_id)`
- `SchedulerService.create_schedule(user_id, payload)`
- `SchedulerService.update_schedule(user_id, schedule_id, payload)`
- `SchedulerService.delete_schedule(user_id, schedule_id)`
- `SchedulerService.get_todays_schedule(user_id, today=None)`
- `SchedulerService.create_schedule_from_bill(user_id, payload)`
- `SchedulerService.complete_reminder(user_id, payload)`

## 7. Inventory Integration
- Scheduler integrates with Inventory only through:
  - `InventoryIntegrationService.add_scheduler_medicine(...)`
- When a schedule is created, Scheduler passes medicine, quantity, unit, and expiry metadata to Inventory through the integration service.
- If Inventory integration fails, the newly created schedule is soft-deleted and the API returns an integration failure error instead of leaving the modules out of sync.

## 8. API Endpoints
- `GET /api/v1/schedule`
- `GET /api/v1/schedule/{id}`
- `POST /api/v1/schedule`
- `PUT /api/v1/schedule/{id}`
- `DELETE /api/v1/schedule/{id}`
- `GET /api/v1/schedule/today`
- `POST /api/v1/schedule/from-bill`
- `POST /api/v1/schedule/complete`

## 9. Reminder Algorithm
- Dosage input is accepted in fixed `Morning-Afternoon-Night` form such as:
  - `1-0-1`
  - `0-1-0`
  - `0-0-1`
- The algorithm:
  1. Parses the dosage pattern into morning, afternoon, and night counts.
  2. Resolves the effective schedule date range from `start_date` plus `end_date` or `duration_days`.
  3. Generates one reminder per active period per day across the resolved date range.
  4. Uses user-supplied period times when provided.
  5. Falls back to deterministic defaults when not provided:
     - Morning: `08:00`
     - Afternoon: `14:00`
     - Night: `20:00`
- `schedule.reminder_time` stores the earliest reminder time for compatibility with existing Dashboard reads.

## 10. Validation Rules
- Rejects invalid dosage patterns that are not `x-y-z`.
- Rejects `0-0-0` because it creates no reminders.
- Rejects end dates earlier than start dates.
- Rejects purchase/expiry combinations where expiry is earlier than purchase.
- Rejects scheduling medicines whose expiry date is earlier than the schedule start date.
- Rejects negative or invalid duration values.
- Rejects unknown medicines.
- Rejects duplicate overlapping active schedules for the same user and medicine.
- Rejects invalid reminder completion IDs.

## 11. Test Coverage
- Repository:
  - create
  - fetch by id
  - today lookup
  - by-date lookup
  - active schedules
  - reminder completion
- Service:
  - schedule creation
  - reminder generation
  - duplicate active schedule rejection
  - today schedule generation
  - bill-based workflow
  - reminder completion
  - expired medicine rejection
- API:
  - CRUD
  - today endpoint
  - from-bill endpoint
  - complete endpoint
  - auth enforcement
  - invalid dosage handling
- Regression:
  - all previous Phase 1 to Phase 4 tests still pass

## 12. Test Results
- `python -m pytest`
- Result: `56 passed`

Additional verification:
- `GET /openapi.json` returned `200`
- Seeded scheduler flow returned:
  - `schedule_create=201`
  - `schedule_today=200`
  - `schedule_complete=200`
- Alembic verification:
  - `python -m alembic upgrade head` succeeded on the current local DB
  - `python -m alembic upgrade head` also succeeded on a clean temp SQLite database

## 13. Known Limitations
- OCR, bill parsing from images, and notification delivery are intentionally not implemented in this phase.
- Scheduler accepts structured pharmacy bill data only; it does not extract that data from files or images.
- Reminder generation currently supports the documented morning/afternoon/night dosage model and daily recurrence; more complex recurrence rules remain out of scope.
- Updating a schedule regenerates its reminder set, so reminder IDs are not stable across schedule edits.

## 14. Assumptions
- A schedule with no explicit `end_date` and no `duration_days` defaults to a single-day schedule on `start_date`.
- Duplicate active schedules are defined as overlapping date ranges for the same user and medicine while the existing schedule remains active.
- Bill-based scheduling matches medicines through the existing medicine repository using exact brand/name lookup already established in the codebase.
- Default reminder times are acceptable when the request omits explicit times for morning, afternoon, and night.

## 15. Proof That Scheduler Remains Independent From Generic Medicine Finder
- Scheduler code imports:
  - `MedicineRepository`
  - `ScheduleRepository`
  - `InventoryIntegrationService`
  - Scheduler-specific schemas and models
- Scheduler code does **not** import:
  - `GenericFinderService`
  - `ExactMatchingEngine`
  - `CompositionNormalizationService`
  - Generic Finder routes, repositories, or schemas
- No Scheduler endpoint calls any Generic Finder endpoint or service.
- Inventory coordination is routed only through `InventoryIntegrationService`, matching the documented module boundary.
