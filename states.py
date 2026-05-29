from aiogram.fsm.state import State, StatesGroup


class CharacterCreation(StatesGroup):
    waiting_for_name = State()
    waiting_for_appearance = State()
    waiting_for_new_appearance = State()