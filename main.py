"""Асинхронный сервис кулинарной книги на FastAPI."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from . import models
from .database import DATABASE_URL
from .routes import router


def create_app(database_url: str = DATABASE_URL) -> FastAPI:
    """Создать API-приложение с возможностью указать отдельный адрес базы данных."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine = create_async_engine(database_url)
        try:
            app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)
            async with engine.begin() as connection:
                await connection.run_sync(models.Base.metadata.create_all)
            yield
        finally:
            await engine.dispose()

    app = FastAPI(
        title="API кулинарной книги",
        description=(
            "Асинхронный API для создания рецептов, просмотра списка по популярности "
            "и получения подробной информации. Каждый успешный запрос деталей "
            "увеличивает счётчик просмотров рецепта."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(router)

    return app


app = create_app()
