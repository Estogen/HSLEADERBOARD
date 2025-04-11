from aiogram.fsm.state import StatesGroup, State


class Gen(StatesGroup):
    US = State()
    EU = State()
    AP = State()

class Adm(StatesGroup):
    mailing = State()