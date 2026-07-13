# Phase 2 Report

## 1. Summary of Implementation
- Implemented the Home Dashboard backend only.
- Replaced the placeholder `GET /api/v1/dashboard` endpoint with a real authenticated, read-only aggregate response.
- Added a dedicated dashboard repository for database reads, a dashboard service for greeting and aggregation, and dashboard-specific response schemas.
- Kept the module read-only with no OCR, no inventory editing, no schedule creation, and no cross-module business logic changes.

## 2. Architecture Decisions
- Preserved the Phase 1 project structure and added the dashboard implementation inside the existing `repositories`, `services`, `schemas`, and `api/routes` layers.
- Kept repositories database-only with no presentation or greeting logic.
- Kept greeting logic and response aggregation inside `DashboardService`.
- Reused the existing authentication dependency so the dashboard is scoped to the authenticated user and still returns `401` when no valid token is provided.
- Returned empty collections and zero counts for empty dashboard states instead of treating them as errors.
- Translated database access failures into a consistent `500` application error response with code `database_error`.

## 3. Files Created
- `C:\Users\hitoy\Downloads\Medigen\app\repositories\dashboard_repository.py`
- `C:\Users\hitoy\Downloads\Medigen\app\schemas\dashboard.py`
- `C:\Users\hitoy\Downloads\Medigen\app\services\dashboard_service.py`
- `C:\Users\hitoy\Downloads\Medigen\tests\support.py`
- `C:\Users\hitoy\Downloads\Medigen\tests\api\test_dashboard.py`
- `C:\Users\hitoy\Downloads\Medigen\tests\db\test_dashboard_repository.py`
- `C:\Users\hitoy\Downloads\Medigen\tests\unit\test_dashboard_service.py`

## 4. Files Modified
- `C:\Users\hitoy\Downloads\Medigen\app\api\routes\dashboard.py`
- `C:\Users\hitoy\Downloads\Medigen\tests\api\test_placeholder_routes.py`

## 5. Repository Methods Added
- `DashboardRepository.get_user_by_id(user_id)`
- `DashboardRepository.get_unread_notification_count(user_id)`
- `DashboardRepository.get_todays_schedule(user_id, target_date)`
- `DashboardRepository.get_inventory_summary(user_id)`

## 6. Service Methods Added
- `DashboardService.get_dashboard(user_id, current_datetime=None)`
- `DashboardService.get_greeting(current_datetime=None)`

## 7. API Endpoint Implemented
- `GET /api/v1/dashboard`

Response includes:
- Authenticated user summary
- Time-based greeting
- Unread notification count
- Today's schedule sorted by reminder time
- Inventory summary with total medicines and expiring soon count

## 8. Tests Created
- Repository tests for dashboard reads and empty states
- Service tests for greeting boundaries, aggregation, user-not-found handling, empty states, and database error translation
- API tests for authenticated dashboard responses, empty responses, authentication enforcement, and database error responses

## 9. Test Results
- `python -m pytest`
- Result: `22 passed`

Additional verification:
- `GET /openapi.json` returned `200`
- Dashboard route is registered and covered by API tests

## 10. Known Limitations
- The current schedule model only supports date-range filtering and reminder-time ordering, so “today’s schedule” is derived from active schedules whose date range includes the current server date.
- The inventory summary currently reports `total_medicines` and `expiring_soon` because those are the documented dashboard summary fields available from the current schema.
- “Expiring soon” is based on the existing inventory status field rather than recalculating expiry windows dynamically.

## 11. Assumptions
- The dashboard is authenticated because the documented API includes `401 Unauthorized` and the dashboard is user-specific.
- Greeting boundaries were implemented as:
  - Morning: `05:00` to `11:59`
  - Afternoon: `12:00` to `16:59`
  - Evening: `17:00` to `20:59`
  - Night: `21:00` to `04:59`
- Unread notifications are the notifications with status `pending` or `sent`; `read` and `archived` are excluded from the count.
- Inventory summary counts non-deleted inventory records for the authenticated user and uses the existing `expiring_soon` inventory status to populate that summary field.
