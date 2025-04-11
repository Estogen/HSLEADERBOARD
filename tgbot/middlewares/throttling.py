from aiogram import BaseMiddleware, types
from aiogram.dispatcher.event.bases import CancelHandler
from cachetools import TTLCache
from typing import Dict, Any, Callable, Awaitable


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, throttle_time: int):
        super().__init__()
        self.cache = TTLCache(maxsize=10_000, ttl=throttle_time)

    async def __call__(
            self,
            handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
            event: types.Message,
            data: Dict[str, Any],
    ) -> Any:
        if event.from_user.id in self.cache:
            await event.answer("Подождите немного перед следующим действием.")
            raise CancelHandler()

        self.cache[event.from_user.id] = True
        return await handler(event, data)
