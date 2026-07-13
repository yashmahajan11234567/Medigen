from fastapi import APIRouter

from app.api.routes import auth, dashboard, generic_finder, inventory, medical_records, schedule


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(schedule.router, prefix="/schedule", tags=["Schedule"])
api_router.include_router(
    generic_finder.router,
    prefix="/generic",
    tags=["Generic Medicine Finder"],
)
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(
    medical_records.router,
    prefix="/medical-records",
    tags=["Medical Records"],
)
