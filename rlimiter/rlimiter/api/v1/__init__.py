from fastapi import APIRouter

from .rquotas import router as quotas_router

router = APIRouter(prefix="/v1")
router.include_router(quotas_router, tags=["quotas"])
