from typing import Optional
from sqlalchemy import select, insert
from sqlalchemy.exc import SQLAlchemyError
from infrastructure.database.models import User
from infrastructure.database.repo.base import BaseRepo
import logging

class UserRepo(BaseRepo):
    async def get_or_create_user(
        self, user_id: int, full_name: str, language: str, username: Optional[str] = None
    ):
        try:
            insert_stmt = (
                insert(User)
                .values(user_id=user_id, username=username, full_name=full_name, language=language)
                .on_conflict_do_update(
                    index_elements=[User.user_id],
                    set_=dict(username=username, full_name=full_name, language=language),
                )
                .returning(User)
            )
            result = await self.session.execute(insert_stmt)
            await self.session.commit()
            return result.scalar_one()
        except SQLAlchemyError as e:
            logging.error(f"Error in get_or_create_user: {e}")
            await self.session.rollback()
            return None
