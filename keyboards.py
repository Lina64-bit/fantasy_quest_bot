from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_scene_keyboard(scene):
    buttons = []

    for choice in scene["choices"]:
        buttons.append([
            InlineKeyboardButton(
                text=choice["text"],
                callback_data=choice["next"]
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)