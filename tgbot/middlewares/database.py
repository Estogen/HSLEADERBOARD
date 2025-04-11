from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.exc import SQLAlchemyError

from infrastructure.database.repo.requests import RequestsRepo

import logging

class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_pool) -> None:
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        async with self.session_pool() as session:
            repo = RequestsRepo(session)
            try:
                user = await repo.users.get_or_create_user(
                    event.from_user.id,
                    event.from_user.full_name,
                    event.from_user.language_code,
                    event.from_user.username
                )
                data["session"] = session
                data["repo"] = repo
                data["user"] = user

                result = await handler(event, data)
            except SQLAlchemyError as e:
                # Обработка ошибок базы данных
                logging.error(f"Database error: {e}")
                # Можно добавить отправку сообщения пользователю об ошибке
                return None

        return result
