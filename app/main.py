from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import api_router
from app.agents_runner.lifecycle import app_lifecycle
from app.core.debug import setup_debug_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    await app_lifecycle.startup()
    yield
    await app_lifecycle.shutdown()


setup_debug_logging()

app = FastAPI(
    title="FinPilot AI",
    lifespan=lifespan,
)

app.include_router(api_router)
