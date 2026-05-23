from fastapi import APIRouter
from app.modules.reporting.v1.routers import router as reporting_router


router = APIRouter()

router.include_router(
    reporting_router,
    prefix="/reporting",
    tags=["reporting"]
)