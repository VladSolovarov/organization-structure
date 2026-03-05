from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Вызов сессии когда это требуется и автоматическое закрытие"""
    async with async_session_maker() as session:
        yield session