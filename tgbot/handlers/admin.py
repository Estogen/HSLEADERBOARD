import logging

from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.filters.admin import AdminFilter
from tgbot.db_api.sqlite import Database
from tgbot.keyboards import inline
from tgbot.misc.states import Adm
from tgbot.services import broadcaster

admin_router = Router()
admin_router.message.filter(AdminFilter())
db = Database(path_to_db="tgbot/db_api/main.db")


def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@admin_router.message(CommandStart())
async def admin_start(message: Message):
    await message.answer("Привет, админ!",
                        reply_markup=inline.admin_menu)

@admin_router.callback_query(F.data == 'select_all_users')
async def admin_select_all_users(clbck: CallbackQuery):
    await clbck.answer()
    text = str(db.select_all_users())
    await clbck.message.answer(text)

@admin_router.callback_query(F.data == 'count_users')
async def admin_select_all_users(clbck: CallbackQuery):
    await clbck.answer()
    text = str(db.count_users())
    await clbck.message.answer(text)


@admin_router.callback_query(F.data == 'mail')
async def mailing(clbck: CallbackQuery, state: FSMContext):
    await clbck.answer()
    await state.set_state(Adm.mailing)
    await clbck.message.edit_text(f'Введите текст для рассылки:',
                                  reply_markup=inline.admin_back)

@admin_router.message(StateFilter(Adm.mailing))
async def show_score(message: Message, state: FSMContext):
    await state.clear()
    user_ids = db.get_all_user_ids()[0]
    await broadcaster.mailing(message, user_ids)

@admin_router.callback_query(F.data == "back_to_admin_menu")
async def go_to_menu(clbck: CallbackQuery, state: FSMContext):
    await state.clear()
    await clbck.message.answer(reply_markup=inline.admin_menu)
