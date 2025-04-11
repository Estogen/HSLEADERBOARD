from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import logging

from search import search_top20, search_nickname
from tgbot.keyboards import inline
from tgbot.keyboards.inline import RegionCallback
from tgbot.misc.states import Gen
from tgbot.db_api.sqlite import Database

user_router = Router()
db = Database(path_to_db="tgbot/db_api/main.db")

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def get_region(state: FSMContext):
    state_name = await state.get_state()
    return state_name.split(':')[1] if state_name else 'EU'

@user_router.message(CommandStart())
async def user_start(message: Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    db.add_user(id=user_id, username=username, name=full_name)

    await message.answer(f"Привет, {full_name}! 😊\n\n"
                         "Помогу найти информацию об игроке в рейтинговой таблице\n\n"
                         "Выберите регион поиска:",
                         reply_markup=inline.menu)

@user_router.callback_query(RegionCallback.filter())
async def select_us(clbck: CallbackQuery, state: FSMContext, callback_data: RegionCallback):
    await clbck.answer()
    if callback_data.entitys == '🗽 Америка':
        await state.set_state(Gen.US)
    elif callback_data.entitys == '🇪🇺 Европа':
        await state.set_state(Gen.EU)
    else:
        await state.set_state(Gen.AP)
    await clbck.message.edit_text(f'<b>Регион поиска</b> - {callback_data.entitys}\n\n'
                                  'Введите ник игрока или его часть 👨‍💻\n\n'
                                  'Например:\n'
                                  'nusm ---> Šnusmümriken\n'
                                  'gudd ---> guDDummit\n\n'
                                  '<i>Или нажмите на кнопку ниже</i> ⤵️',
                                  reply_markup=inline.menu2)

@user_router.callback_query(F.data == "top20")
async def show_top20(clbck: CallbackQuery, state: FSMContext):
    region = await get_region(state)
    if not region:
        logging.warning("Region is not set in the state")
        await clbck.message.answer("Что-то пошло не так. Пожалуйста, попробуйте снова.")
        return
    text = search_top20(region)
    await clbck.message.edit_text(f'Топ-20 игроков в {region}\n\n{text}\n\n<i>Введите ник или нажмите на кнопку:</i>',
                                  reply_markup=inline.back)


@user_router.callback_query(F.data == "refresh")
async def show_top20(clbck: CallbackQuery, state: FSMContext):
    region = await get_region(state)
    if not region:
        logging.warning("Region is not set in the state")
        await clbck.message.answer("Что-то пошло не так. Пожалуйста, попробуйте снова.")
        return
    text = search_top20(region)
    await clbck.message.answer(f'Топ-20 игроков в {region}\n\n{text}\n\n<i>Введите ник или нажмите на кнопку:</i>',
                                  reply_markup=inline.back)
@user_router.callback_query(F.data == "back_to_menu")
async def go_to_menu(clbck: CallbackQuery, state: FSMContext):
    await state.clear()
    await clbck.message.edit_text('Выберите регион поиска:',
                                  reply_markup=inline.menu)

@user_router.message(F.text, StateFilter(None))
async def nogen(message: Message):
    await message.answer("Выберите регион поиска:",
                         reply_markup=inline.menu)

@user_router.message(F.text)
async def show_score(message: Message, state: FSMContext):
    region = await get_region(state)
    if not region:
        logging.warning("Region is not set in the state")
        await message.answer("Что-то пошло не так. Пожалуйста, попробуйте снова.")
        return
    text = search_nickname(region, message.text)
    await message.answer(f'{text}\n\n<i>Введите ник или нажмите на кнопку:</i>',
                         reply_markup=inline.menu2)
