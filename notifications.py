WORLD_NAME = "Аэларис"


async def notify_level_up(message, new_level: int):
    await message.answer(
        f"✨ Новый уровень!\n\n"
        f"Ваш персонаж достиг {new_level} уровня.\n\n"
        f"Сила {WORLD_NAME} откликается на ваш путь."
    )


async def notify_achievement(message, title: str, description: str):
    await message.answer(
        f"🏆 Получено достижение!\n\n"
        f"«{title}»\n\n"
        f"{description}\n\n"
        "Награду можно забрать в меню ачивок."
    )


async def notify_weapon_equipped(message, item_name: str, damage_bonus: int):
    await message.answer(
        f"⚔️ Экипировано оружие\n\n"
        f"{item_name}\n\n"
        f"Урон увеличен на +{damage_bonus} HP.\n\n"
        "Предмет остаётся в инвентаре."
    )


async def notify_shield_equipped(message, item_name: str, defense_bonus: int):
    await message.answer(
        f"🛡️ Экипирован щит\n\n"
        f"{item_name}\n\n"
        f"Шанс защиты увеличен на +{defense_bonus}%.\n\n"
        "Предмет остаётся в инвентаре."
    )


async def notify_full_inventory(message):
    await message.answer(
        "🎒 Инвентарь переполнен.\n\n"
        "Некуда положить предмет.\n"
        "Освободите место перед покупкой."
    )


async def notify_critical_hp(message):
    await message.answer(
        "🩸 Вы тяжело ранены.\n\n"
        "Каждое движение отдаётся болью."
    )


async def notify_max_level(message):
    await message.answer(
        "🌟 Достигнут максимальный уровень.\n\n"
        "Ваше имя уже стало легендой."
    )


async def notify_final_boss_warning(message):
    await message.answer(
        "☠️ Вы чувствуете нечто...\n\n"
        "Воздух вокруг становится тяжелее.\n"
        "Следующее приключение приведёт вас к сильнейшему противнику."
    )