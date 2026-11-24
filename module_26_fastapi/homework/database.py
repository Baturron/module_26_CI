"""Настройка базы данных и асинхронных сессий для запросов."""

import os
from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

DEFAULT_DATABASE_URL = f"sqlite+aiosqlite:///{Path(__file__).parent / 'recipes.db'}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Создать сессию приложения и закрыть её после обработки запроса."""
    session_factory: async_sessionmaker[AsyncSession] = (
        request.app.state.session_factory
    )
    async with session_factory() as session:
        yield session
