import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.ml import ModelHolder
from app.routers import api, pages

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    holder = ModelHolder(settings)
    # Blocking I/O (HF downloads) — run in a thread to keep the loop happy
    import anyio

    await anyio.to_thread.run_sync(holder.load)
    app.state.holder = holder
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_title, lifespan=lifespan)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(pages.router)
    app.include_router(api.router)
    return app


app = create_app()
