from datetime import date, timedelta
from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload, Session

from app.core.enums import InventoryStatus, MedicineType, FoodTiming, ScheduleStatus
from app.models.schedule import Schedule
from tests.support import create_inventory_item, create_medicine, create_user
from tests.conftest import engine
from app.services.scheduler_service import SchedulerService
from app.schemas.schedule import ScheduleCreateRequest
from app.services.dashboard_service import DashboardService
from app.repositories.dashboard_repository import DashboardRepository

# Get a fresh session
session = Session(bind=engine)

try:
    user = create_user(session, email='debug@example.com')
    medicine = create_medicine(session, name='Debug Med', dosage_form=MedicineType.TABLET)
    create_inventory_item(session, user_id=user.id, medicine_id=medicine.id, status=InventoryStatus.AVAILABLE, quantity=8, expiry_date=date.today() + timedelta(days=5))

    scheduler = SchedulerService(session)
    result = scheduler.create_schedule(user_id=user.id, payload=ScheduleCreateRequest(
        medicine_id=medicine.id,
        dosage_pattern='1-0-0',
        food_timing=FoodTiming.AFTER_FOOD,
        start_date=date.today(),
        duration_days=2,
        quantity=6,
        quantity_unit='tablets',
    ))

    print(f'Created schedule: id={result.id}, start={result.start_date}, end={result.end_date}, status={result.status}')

    # Query using dashboard repository
    repo = DashboardRepository(session)
    target_date = date.today()
    schedules = repo.get_todays_schedule(user.id, target_date)
    print(f'Dashboard repo query result: {len(schedules)} schedules')
    for s in schedules:
        print(f'  id={s.id}, start={s.start_date}, end={s.end_date}, status={s.status}')

    # Try dashboard service
    dashboard = DashboardService(session).get_dashboard(user.id)
    print(f'Dashboard today_schedule: {len(dashboard.today_schedule)}')
    for s in dashboard.today_schedule:
        print(f'  id={s.id}, medicine={s.medicine_name}')

finally:
    session.close()