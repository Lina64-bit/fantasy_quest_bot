import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F

from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
    LabeledPrice,
    PreCheckoutQuery
)

from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN
from states import CharacterCreation

from database import (
    init_db,
    create_or_update_player,
    get_player,
    update_scene,
    get_inventory,
    add_item_to_inventory,
    remove_gold,
    save_inventory,
    equip_weapon,
    equip_shield,
    equip_accessory,
    add_luck_bonus,
    add_battle_damage_bonus,
    set_current_hp,
    start_battle,
    update_battle_turn,
    update_enemy_hp,
    update_enemy_potions,
    end_battle,
    add_xp,
    add_gold,
    increase_progress_stage,
    get_achievements,
    get_claimed_achievements,
    add_achievement,
    claim_achievement
)

from image_generator import generate_character_image
from level_system import get_level_from_xp, get_next_level_xp
from stats_system import get_player_stats
from inventory_system import get_inventory_limit, get_inventory_count, has_inventory_space
from merchant import get_available_items, get_item_by_id
from combat_system import get_boss_by_stage, defense_success
from achievements import get_achievement

from notifications import (
    WORLD_NAME,
    notify_level_up,
    notify_achievement,
    notify_weapon_equipped,
    notify_shield_equipped,
    notify_full_inventory,
    notify_critical_hp,
    notify_max_level,
    notify_final_boss_warning
)

from premium_shop import (
    PREMIUM_PRODUCTS,
    get_premium_product
)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def character_confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оставить образ", callback_data="confirm_character")],
        [InlineKeyboardButton(text="Сгенерировать заново", callback_data="regenerate_character")],
        [InlineKeyboardButton(text="Изменить описание", callback_data="change_appearance")]
    ])


def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Инвентарь", callback_data="inventory_menu")],
        [InlineKeyboardButton(text="Характеристики", callback_data="stats_menu")],
        [InlineKeyboardButton(text="Ачивки", callback_data="achievements_menu")],
        [InlineKeyboardButton(text="К торговцу", callback_data="merchant_menu")],
        [InlineKeyboardButton(text="Астральная лавка", callback_data="premium_shop")],
        [InlineKeyboardButton(text="Начать приключение", callback_data="start_adventure")]
    ])


def back_to_inventory_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад в инвентарь", callback_data="inventory_menu")],
        [InlineKeyboardButton(text="В главное меню", callback_data="main_menu")]
    ])


def battle_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Атаковать", callback_data="battle_attack")],
        [InlineKeyboardButton(text="Использовать инвентарь", callback_data="battle_inventory")]
    ])


def roll_dice_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Бросить кубик", callback_data="battle_roll_dice")]
    ])


async def give_achievement(message: Message, telegram_id: int, achievement_id: str):
    current = await get_achievements(telegram_id)

    if achievement_id not in current:
        await add_achievement(telegram_id, achievement_id)
        achievement = get_achievement(achievement_id)

        if achievement:
            await notify_achievement(
                message,
                achievement["title"],
                achievement["description"]
            )


async def check_level_achievements(message: Message, telegram_id: int, old_level: int | None = None):
    player = await get_player(telegram_id)
    new_level = get_level_from_xp(player["xp"])

    if old_level is not None and new_level > old_level:
        await notify_level_up(message, new_level)

        if new_level >= 20:
            await notify_max_level(message)

    if new_level >= 5:
        await give_achievement(message, telegram_id, "level_5")

    if new_level >= 10:
        await give_achievement(message, telegram_id, "level_10")

    if new_level >= 15:
        await give_achievement(message, telegram_id, "level_15")

    if new_level >= 20:
        await give_achievement(message, telegram_id, "level_20")


async def show_main_menu(message: Message, telegram_id: int):
    player = await get_player(telegram_id)

    if not player:
        await message.answer("Профиль не найден.")
        return

    level = get_level_from_xp(player["xp"])
    next_level_xp = get_next_level_xp(level)

    caption = (
        f"{player['character_name']}\n\n"
        f"Уровень: {level}\n"
        f"Опыт: {player['xp']} / {next_level_xp} XP\n"
        f"Золото: {player['gold']}\n"
        f"Здоровье: {player['current_hp']} HP\n\n"
        "Выберите действие:"
    )

    image_path = player.get("image_url")

    if image_path and os.path.exists(image_path):
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=FSInputFile(image_path),
            caption=caption,
            reply_markup=main_menu_keyboard()
        )
    else:
        await message.answer(caption, reply_markup=main_menu_keyboard())


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()

    player = await get_player(message.from_user.id)

    if player:
        await show_main_menu(message, message.from_user.id)
        return

    await message.answer(
        f"Добро пожаловать в мир {WORLD_NAME}!\n\n"
        "Перед началом путешествия создайте своего героя.\n\n"
        "Введите имя персонажа:"
    )

    await state.set_state(CharacterCreation.waiting_for_name)


@dp.message(CharacterCreation.waiting_for_name)
async def get_character_name(message: Message, state: FSMContext):
    character_name = message.text.strip()

    if len(character_name) < 2:
        await message.answer("Имя слишком короткое.")
        return

    await state.update_data(character_name=character_name)
    await message.answer("Опишите внешность персонажа.")
    await state.set_state(CharacterCreation.waiting_for_appearance)


@dp.message(CharacterCreation.waiting_for_appearance)
async def get_character_appearance(message: Message, state: FSMContext):
    appearance = message.text.strip()

    if len(appearance) < 10:
        await message.answer("Описание слишком короткое.")
        return

    await state.update_data(appearance=appearance)
    await generate_and_show_character(message, state)


async def generate_and_show_character(message: Message, state: FSMContext):
    data = await state.get_data()

    character_name = data["character_name"]
    appearance = data["appearance"]

    await message.answer("Создаю образ персонажа...")

    try:
        image_path = await asyncio.to_thread(
            generate_character_image,
            message.from_user.id,
            appearance
        )
    except Exception as error:
        print("ОШИБКА:", error)
        image_path = "default_character.png"

        await message.answer(
            "Связь с художниками Астральной Башни была потеряна...\n\n"
            "Используется запасной портрет из королевского архива."
        )

    await state.update_data(image_path=image_path)

    await bot.send_photo(
        chat_id=message.chat.id,
        photo=FSInputFile(image_path),
        caption=(
            "Ваш герой готов!\n\n"
            f"Имя: {character_name}\n"
            f"Описание: {appearance}"
        ),
        reply_markup=character_confirm_keyboard()
    )


@dp.callback_query(F.data == "confirm_character")
async def confirm_character(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await create_or_update_player(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username or "",
        character_name=data["character_name"],
        appearance_prompt=data["appearance"],
        image_url=data["image_path"]
    )

    player = await get_player(callback.from_user.id)
    level = get_level_from_xp(player["xp"])
    stats = get_player_stats(level, player)

    await set_current_hp(callback.from_user.id, stats["max_hp"])
    await state.clear()

    await show_main_menu(callback.message, callback.from_user.id)
    await callback.answer()


@dp.callback_query(F.data == "regenerate_character")
async def regenerate_character(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await generate_and_show_character(callback.message, state)


@dp.callback_query(F.data == "change_appearance")
async def change_appearance(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новое описание внешности.")
    await state.set_state(CharacterCreation.waiting_for_new_appearance)
    await callback.answer()


@dp.message(CharacterCreation.waiting_for_new_appearance)
async def get_new_appearance(message: Message, state: FSMContext):
    appearance = message.text.strip()
    await state.update_data(appearance=appearance)
    await generate_and_show_character(message, state)


@dp.callback_query(F.data == "inventory_menu")
async def inventory_menu(callback: CallbackQuery):
    player = await get_player(callback.from_user.id)
    level = get_level_from_xp(player["xp"])
    inventory = await get_inventory(callback.from_user.id)
    limit = get_inventory_limit(level)

    if not inventory:
        await callback.message.answer(
            f"Инвентарь пуст.\n\nЗаполнено: 0 / {limit}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="В главное меню", callback_data="main_menu")]
                ]
            )
        )
        await callback.answer()
        return

    grouped_items = {}

    for item_id in inventory:
        grouped_items[item_id] = grouped_items.get(item_id, 0) + 1

    keyboard = []

    for item_id, amount in grouped_items.items():
        item = get_item_by_id(item_id)
        item_name = item["name"] if item else item_id
        button_text = item_name if amount == 1 else f"{item_name} ({amount})"

        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"itemgroup_{item_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(text="В главное меню", callback_data="main_menu")
    ])

    await callback.message.answer(
        f"Инвентарь\n\nЗаполнено: {get_inventory_count(inventory)} / {limit}\n\nВыберите предмет:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("itemgroup_"))
async def inventory_item_menu(callback: CallbackQuery):
    item_id = callback.data.replace("itemgroup_", "")
    inventory = await get_inventory(callback.from_user.id)
    item = get_item_by_id(item_id)

    if not item:
        await callback.message.answer(
            "Неизвестный предмет.",
            reply_markup=back_to_inventory_keyboard()
        )
        await callback.answer()
        return

    amount = inventory.count(item_id)

    text = (
        f"{item['name']}\n\n"
        f"Количество: {amount}\n"
        f"Описание: {item['description']}\n\n"
        "Что сделать с предметом?"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Использовать", callback_data=f"use_item_{item_id}")],
        [InlineKeyboardButton(text="Выбросить", callback_data=f"drop_item_{item_id}")],
        [InlineKeyboardButton(text="Назад", callback_data="inventory_menu")]
    ])

    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data.startswith("use_item_"))
async def use_inventory_item(callback: CallbackQuery):
    item_id = callback.data.replace("use_item_", "")
    inventory = await get_inventory(callback.from_user.id)

    if item_id not in inventory:
        await callback.message.answer(
            "Предмет не найден.",
            reply_markup=back_to_inventory_keyboard()
        )
        await callback.answer()
        return

    item = get_item_by_id(item_id)

    if not item:
        await callback.message.answer(
            "Неизвестный предмет.",
            reply_markup=back_to_inventory_keyboard()
        )
        await callback.answer()
        return

    if item["type"] == "weapon":
        await equip_weapon(callback.from_user.id, item_id)
        await give_achievement(callback.message, callback.from_user.id, "well_armed")

        await notify_weapon_equipped(
            callback.message,
            item["name"],
            item.get("damage_bonus", 0)
        )

    elif item["type"] == "shield":
        await equip_shield(callback.from_user.id, item_id)
        await give_achievement(callback.message, callback.from_user.id, "shield_bearer")

        await notify_shield_equipped(
            callback.message,
            item["name"],
            item.get("defense_bonus", 0)
        )

    elif item["type"] == "accessory":
        await equip_accessory(callback.from_user.id, item_id)

        await callback.message.answer(
            f"Вы надели: {item['name']}.\n\n"
            f"Благословение Фортуны увеличено на +{item.get('luck_bonus', 0)}.\n\n"
            "Предмет остаётся в инвентаре.",
            reply_markup=back_to_inventory_keyboard()
        )

    elif item["type"] == "rage_potion":
        await callback.message.answer(
            "Зелье ярости можно использовать только во время боя.\n\n"
            "Оно временно усиливает ваши атаки до конца текущего сражения.",
            reply_markup=back_to_inventory_keyboard()
        )
         
    elif item["type"] == "luck_potion":
        await add_luck_bonus(callback.from_user.id, item["luck_bonus"])
        await give_achievement(callback.message, callback.from_user.id, "lucky_one")

        inventory.remove(item_id)
        await save_inventory(callback.from_user.id, inventory)

        await callback.message.answer(
            f"Вы выпили: {item['name']}.\n\n"
            f"Благословение Фортуны увеличено на +{item['luck_bonus']}.",
            reply_markup=back_to_inventory_keyboard()
        )

    elif item["type"] == "escape_scroll":
        await callback.message.answer(
        "Свиток побега можно использовать только во время боя.\n\n"
        "Он позволяет мгновенно покинуть сражение.",
        reply_markup=back_to_inventory_keyboard()
        )
        
    elif item["type"] == "heal_potion":
        player = await get_player(callback.from_user.id)
        level = get_level_from_xp(player["xp"])
        stats = get_player_stats(level, player)

        new_hp = min(
            player["current_hp"] + item["heal_amount"],
            stats["max_hp"]
        )

        await set_current_hp(callback.from_user.id, new_hp)

        inventory.remove(item_id)
        await save_inventory(callback.from_user.id, inventory)

        await callback.message.answer(
            f"Вы выпили: {item['name']}.\n\n"
            f"Здоровье восстановлено до {new_hp} / {stats['max_hp']} HP.",
            reply_markup=back_to_inventory_keyboard()
        )

    elif item["type"] == "healing_rune":
        player = await get_player(callback.from_user.id)
        level = get_level_from_xp(player["xp"])
        stats = get_player_stats(level, player)

        await set_current_hp(callback.from_user.id, stats["max_hp"])

        inventory.remove(item_id)
        await save_inventory(callback.from_user.id, inventory)

        await callback.message.answer(
            f"Вы активировали: {item['name']}.\n\n"
            f"Здоровье полностью восстановлено: {stats['max_hp']} HP.",
            reply_markup=back_to_inventory_keyboard()
        )

    await callback.answer()


@dp.callback_query(F.data.startswith("drop_item_"))
async def drop_inventory_item(callback: CallbackQuery):
    item_id = callback.data.replace("drop_item_", "")
    inventory = await get_inventory(callback.from_user.id)

    if item_id not in inventory:
        await callback.message.answer(
            "Предмет не найден.",
            reply_markup=back_to_inventory_keyboard()
        )
        await callback.answer()
        return

    item = get_item_by_id(item_id)
    inventory.remove(item_id)
    await save_inventory(callback.from_user.id, inventory)

    item_name = item["name"] if item else item_id

    await callback.message.answer(
        f"Вы выбросили предмет: {item_name}.",
        reply_markup=back_to_inventory_keyboard()
    )

    await callback.answer()


@dp.callback_query(F.data == "stats_menu")
async def stats_menu(callback: CallbackQuery):
    player = await get_player(callback.from_user.id)
    level = get_level_from_xp(player["xp"])
    next_level_xp = get_next_level_xp(level)
    stats = get_player_stats(level, player)

    weapon = get_item_by_id(player.get("equipped_weapon"))
    shield = get_item_by_id(player.get("equipped_shield"))
    accessory = get_item_by_id(player.get("equipped_accessory"))

    weapon_name = weapon["name"] if weapon else "нет"
    shield_name = shield["name"] if shield else "нет"
    accessory_name = accessory["name"] if accessory else "нет"

    text = (
        "Характеристики персонажа\n\n"
        f"Имя: {player['character_name']}\n"
        f"Уровень: {level}\n"
        f"Опыт: {player['xp']} / {next_level_xp} XP\n"
        f"Золото: {player['gold']}\n\n"
        f"Здоровье: {player['current_hp']} / {stats['max_hp']} HP\n"
        f"Урон: {stats['damage']} HP\n"
        f"Шанс защиты: {stats['defense_chance']}%\n"
        f"Благословение Фортуны: +{stats['luck']}\n\n"
        f"Оружие: {weapon_name}\n"
        f"Щит: {shield_name}\n"
        f"Аксессуар: {accessory_name}"
    )

    await callback.message.answer(text)
    await callback.answer()


@dp.callback_query(F.data == "achievements_menu")
async def achievements_menu(callback: CallbackQuery):
    achievements = await get_achievements(callback.from_user.id)
    claimed = await get_claimed_achievements(callback.from_user.id)

    if not achievements:
        await callback.message.answer(
            "Ачивок пока нет.\n\n"
            "Побеждайте врагов, покупайте предметы и развивайте персонажа.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="В главное меню", callback_data="main_menu")]
                ]
            )
        )
        await callback.answer()
        return

    keyboard = []

    for achievement_id in achievements:
        achievement = get_achievement(achievement_id)

        if not achievement:
            continue

        status = "получено" if achievement_id in claimed else "награда доступна"

        keyboard.append([
            InlineKeyboardButton(
                text=f"{achievement['title']} — {status}",
                callback_data=f"achievement_{achievement_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(text="В главное меню", callback_data="main_menu")
    ])

    await callback.message.answer(
        "Ваши ачивки:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("achievement_"))
async def achievement_detail(callback: CallbackQuery):
    achievement_id = callback.data.replace("achievement_", "")
    achievement = get_achievement(achievement_id)

    if not achievement:
        await callback.message.answer("Достижение не найдено.")
        await callback.answer()
        return

    claimed = await get_claimed_achievements(callback.from_user.id)

    if achievement_id in claimed:
        text = (
            f"{achievement['title']}\n\n"
            f"{achievement['description']}\n\n"
            "Награда уже получена."
        )
    else:
        old_player = await get_player(callback.from_user.id)
        old_level = get_level_from_xp(old_player["xp"])

        await add_gold(callback.from_user.id, achievement["reward_gold"])
        await add_xp(callback.from_user.id, achievement["reward_xp"])
        await claim_achievement(callback.from_user.id, achievement_id)

        await check_level_achievements(callback.message, callback.from_user.id, old_level)

        text = (
            f"{achievement['title']}\n\n"
            f"{achievement['description']}\n\n"
            "Награда получена:\n"
            f"+{achievement['reward_gold']} золота\n"
            f"+{achievement['reward_xp']} XP"
        )

    await callback.message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Назад к ачивкам", callback_data="achievements_menu")]
            ]
        )
    )

    await callback.answer()


@dp.callback_query(F.data == "merchant_menu")
async def merchant_menu(callback: CallbackQuery):
    player = await get_player(callback.from_user.id)
    level = get_level_from_xp(player["xp"])
    inventory = await get_inventory(callback.from_user.id)
    limit = get_inventory_limit(level)
    items = get_available_items(level)

    keyboard = []

    for item in items:
        keyboard.append([
            InlineKeyboardButton(
                text=(
                    f"{item['name']} | "
                    f"{item['price']} золота | "
                    f"{item['description']}"
                ),
                callback_data=f"buy_{item['id']}"
            )
        ])

    if level >= 10:
        keyboard.append([
            InlineKeyboardButton(
                text="А где стальной щит?",
                callback_data="steel_shield_joke"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(text="Уйти", callback_data="main_menu")
    ])

    text = (
        "Торговец\n\n"
        f"Ваше золото: {player['gold']}\n"
        f"Инвентарь: {get_inventory_count(inventory)} / {limit}\n\n"
        "Доступные товары:"
    )

    await callback.message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

    await callback.answer()


@dp.callback_query(F.data == "steel_shield_joke")
async def steel_shield_joke(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Вернуться к товарам", callback_data="merchant_menu")]
        ]
    )

    await callback.message.answer(
        "А ты что, видел много стальных щитов тут?\n\n"
        "Такого у нас не водится.\n\n"
        "Не всё в этом мире подчиняется Святой Логике.",
        reply_markup=keyboard
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("buy_"))
async def buy_item(callback: CallbackQuery):
    item_id = callback.data.replace("buy_", "")
    player = await get_player(callback.from_user.id)
    inventory = await get_inventory(callback.from_user.id)
    level = get_level_from_xp(player["xp"])
    items = get_available_items(level)

    item = next((item for item in items if item["id"] == item_id), None)

    if not item:
        await callback.message.answer(
            "Торговец смотрит на тебя с недоумением.\n\n"
            "— У меня такого товара нет."
        )
        await callback.answer()
        return

    if player["gold"] < item["price"]:
        await callback.message.answer(
            "Торговец качает головой.\n\n"
            "— Боюсь, у тебя недостаточно золота для этой покупки."
        )
        await callback.answer()
        return

    if not has_inventory_space(inventory, level):
        await notify_full_inventory(callback.message)
        await callback.answer()
        return

    await remove_gold(callback.from_user.id, item["price"])
    await add_item_to_inventory(callback.from_user.id, item["id"])

    await give_achievement(callback.message, callback.from_user.id, "first_purchase")

    await callback.message.answer(
        f"Торговец довольно улыбается.\n\n"
        f"— Отличный выбор.\n\n"
        f"Теперь предмет «{item['name']}» принадлежит тебе."
    )

    await callback.answer()


@dp.callback_query(F.data == "start_adventure")
async def start_adventure(callback: CallbackQuery):
    player = await get_player(callback.from_user.id)

    boss = get_boss_by_stage(player["progress_stage"])

    if boss is None:
        await callback.message.answer(
            "На данный момент все противники побеждены.\n\n"
            "Вы прошли доступную цепочку испытаний."
        )
        await callback.answer()
        return

    if get_boss_by_stage(player["progress_stage"] + 1) is None:
        await notify_final_boss_warning(callback.message)

    level = get_level_from_xp(player["xp"])
    stats = get_player_stats(level, player)

    if player["current_hp"] <= 0:
        await set_current_hp(callback.from_user.id, stats["max_hp"])

    await start_battle(
        telegram_id=callback.from_user.id,
        enemy_name=boss["name"],
        enemy_hp=boss["max_hp"],
        enemy_damage=boss["damage"],
        enemy_defense=boss["defense_chance"],
        enemy_potions=boss["heal_potions"],
        reward_gold=boss["reward_gold"],
        reward_xp=boss["reward_xp"]
    )

    await update_scene(callback.from_user.id, "battle")

    await callback.message.answer(
        f"{boss['intro']}\n\n"
        "Перед началом боя нужно определить, кто ходит первым.\n"
        "Бросьте кубик.",
        reply_markup=roll_dice_keyboard()
    )

    await callback.answer()


@dp.callback_query(F.data == "battle_roll_dice")
async def battle_roll_dice(callback: CallbackQuery):
    player = await get_player(callback.from_user.id)
    level = get_level_from_xp(player["xp"])
    stats = get_player_stats(level, player)

    dice_message = await callback.message.answer_dice(emoji="🎲")
    dice_value = dice_message.dice.value
    total = dice_value + stats["luck"]

    if total < 4:
        await update_battle_turn(callback.from_user.id, "enemy")

        await callback.message.answer(
            f"Выпало: {dice_value}\n"
            f"Благословение Фортуны: +{stats['luck']}\n"
            f"Итого: {total}\n\n"
            "Первым ходит противник!"
        )

        await enemy_turn(callback.message, callback.from_user.id)

    else:
        await update_battle_turn(callback.from_user.id, "player")

        await callback.message.answer(
            f"Выпало: {dice_value}\n"
            f"Благословение Фортуны: +{stats['luck']}\n"
            f"Итого: {total}\n\n"
            "Первым ходите вы.",
            reply_markup=battle_keyboard()
        )

    await callback.answer()


async def enemy_turn(message: Message, telegram_id: int):
    player = await get_player(telegram_id)

    if not player or not player["in_battle"]:
        return

    enemy_hp = player["battle_enemy_hp"]
    enemy_max_hp = player["battle_enemy_max_hp"]
    enemy_potions = player["battle_enemy_potions"]

    if enemy_hp <= 10 and enemy_potions > 0:
        enemy_hp = min(enemy_hp + 10, enemy_max_hp)
        enemy_potions -= 1

        await update_enemy_hp(telegram_id, enemy_hp)
        await update_enemy_potions(telegram_id, enemy_potions)
        await update_battle_turn(telegram_id, "player")

        await message.answer(
            f"{player['battle_enemy_name']} выпивает малое зелье лечения.\n\n"
            f"HP врага: {enemy_hp} / {enemy_max_hp}\n\n"
            "Теперь ваш ход.",
            reply_markup=battle_keyboard()
        )
        return

    level = get_level_from_xp(player["xp"])
    stats = get_player_stats(level, player)

    if defense_success(stats["defense_chance"]):
        await update_battle_turn(telegram_id, "player")

        await message.answer(
            "Противник атакует, но ваша защита срабатывает!\n\n"
            "Теперь ваш ход.",
            reply_markup=battle_keyboard()
        )
        return

    new_hp = max(player["current_hp"] - player["battle_enemy_damage"], 0)

    await set_current_hp(telegram_id, new_hp)

    if new_hp <= 0:
        await player_defeat(message, telegram_id)
        return

    if new_hp <= stats["max_hp"] * 0.25:
        await notify_critical_hp(message)

    await update_battle_turn(telegram_id, "player")

    await message.answer(
        f"{player['battle_enemy_name']} атакует вас.\n\n"
        f"Вы получаете {player['battle_enemy_damage']} урона.\n"
        f"Ваше HP: {new_hp} / {stats['max_hp']}\n\n"
        "Теперь ваш ход.",
        reply_markup=battle_keyboard()
    )


@dp.callback_query(F.data == "battle_attack")
async def battle_attack(callback: CallbackQuery):
    player = await get_player(callback.from_user.id)

    if not player or not player["in_battle"]:
        await callback.message.answer("Сейчас вы не в бою.")
        await callback.answer()
        return

    if player["battle_turn"] != "player":
        await callback.message.answer("Сейчас не ваш ход.")
        await callback.answer()
        return

    level = get_level_from_xp(player["xp"])
    stats = get_player_stats(level, player)

    total_damage = stats["damage"] + player["battle_damage_bonus"]

    if defense_success(player["battle_enemy_defense"]):
        await update_battle_turn(callback.from_user.id, "enemy")

        await callback.message.answer(
            f"{player['battle_enemy_name']} уклоняется от вашей атаки!\n\n"
            "Ход переходит к противнику."
        )

        await enemy_turn(callback.message, callback.from_user.id)
        await callback.answer()
        return

    enemy_hp = max(player["battle_enemy_hp"] - total_damage, 0)

    await update_enemy_hp(callback.from_user.id, enemy_hp)

    if enemy_hp <= 0:
        await player_victory(callback.message, callback.from_user.id)
        await callback.answer()
        return

    await update_battle_turn(callback.from_user.id, "enemy")

    await callback.message.answer(
        f"Вы атакуете противника.\n\n"
        f"Нанесено урона: {total_damage} HP\n"
        f"HP врага: {enemy_hp} / {player['battle_enemy_max_hp']}\n\n"
        "Ход переходит к противнику."
    )

    await enemy_turn(callback.message, callback.from_user.id)
    await callback.answer()


@dp.callback_query(F.data == "battle_inventory")
async def battle_inventory(callback: CallbackQuery):

    inventory = await get_inventory(callback.from_user.id)

    usable_items = []

    for item_id in inventory:

        item = get_item_by_id(item_id)

        if item and item["type"] in [
            "heal_potion",
            "rage_potion",
            "escape_scroll"
        ]:
            usable_items.append(item_id)

    if not usable_items:

        await callback.message.answer(
            "В бою можно использовать только:\n"
            "• зелья лечения\n"
            "• зелья ярости\n"
            "• свитки побега\n\n"
            "Подходящих предметов нет.",
            reply_markup=battle_keyboard()
        )

        await callback.answer()
        return

    grouped = {}

    for item_id in usable_items:
        grouped[item_id] = grouped.get(item_id, 0) + 1

    keyboard = []

    for item_id, amount in grouped.items():

        item = get_item_by_id(item_id)

        keyboard.append([
            InlineKeyboardButton(
                text=f"{item['name']} ({amount})",
                callback_data=f"battle_use_item_{item_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="Назад",
            callback_data="battle_back"
        )
    ])

    await callback.message.answer(
        "Выберите предмет для использования:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard
        )
    )

    await callback.answer()


@dp.callback_query(F.data == "battle_back")
async def battle_back(callback: CallbackQuery):
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=battle_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "premium_shop")
async def premium_shop(callback: CallbackQuery):
    keyboard = []

    for product_id, product in PREMIUM_PRODUCTS.items():
        keyboard.append([
            InlineKeyboardButton(
                text=f"{product['title']} — ⭐ {product['stars']}",
                callback_data=f"premium_buy_{product_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="В главное меню",
            callback_data="main_menu"
        )
    ])

    await callback.message.answer(
        "Астральная лавка\n\n"
        "Здесь можно приобрести дополнительные ресурсы за Telegram Stars.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("premium_buy_"))
async def premium_buy(callback: CallbackQuery):
    product_id = callback.data.replace("premium_buy_", "")
    product = get_premium_product(product_id)

    if not product:
        await callback.message.answer("Товар не найден.")
        await callback.answer()
        return

    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=product["title"],
        description=product["description"],
        payload=product_id,
        provider_token="",
        currency="XTR",
        prices=[
            LabeledPrice(
                label=product["title"],
                amount=product["stars"]
            )
        ]
    )

    await callback.answer()


@dp.pre_checkout_query()
async def pre_checkout_query(pre_checkout: PreCheckoutQuery):
    await pre_checkout.answer(ok=True)


@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    payment = message.successful_payment
    product_id = payment.invoice_payload

    product = get_premium_product(product_id)

    if not product:
        await message.answer(
            "Оплата прошла, но товар не найден. Напишите администратору."
        )
        return

    if product["gold"] > 0:
        await add_gold(message.from_user.id, product["gold"])

    if product["xp"] > 0:
        old_player = await get_player(message.from_user.id)
        old_level = get_level_from_xp(old_player["xp"])

        await add_xp(message.from_user.id, product["xp"])

        await check_level_achievements(
            message,
            message.from_user.id,
            old_level
        )

    await message.answer(
        "⭐ Покупка успешно завершена!\n\n"
        f"Получено: {product['title']}"
    )

    await show_main_menu(message, message.from_user.id)

@dp.callback_query(F.data.startswith("battle_use_item_"))
async def battle_use_item(callback: CallbackQuery):
    item_id = callback.data.replace("battle_use_item_", "")
    player = await get_player(callback.from_user.id)
    inventory = await get_inventory(callback.from_user.id)

    if item_id not in inventory:
        await callback.message.answer(
            "Такого предмета нет в инвентаре.",
            reply_markup=battle_keyboard()
        )
        await callback.answer()
        return

    item = get_item_by_id(item_id)

    if not item:
        await callback.message.answer(
            "Этот предмет нельзя использовать в бою.",
            reply_markup=battle_keyboard()
        )
        await callback.answer()
        return

    if item["type"] == "heal_potion":
        level = get_level_from_xp(player["xp"])
        stats = get_player_stats(level, player)

        new_hp = min(
            player["current_hp"] + item["heal_amount"],
            stats["max_hp"]
        )

        await set_current_hp(callback.from_user.id, new_hp)

        inventory.remove(item_id)
        await save_inventory(callback.from_user.id, inventory)

        await update_battle_turn(callback.from_user.id, "enemy")

        await callback.message.answer(
            f"Вы использовали: {item['name']}.\n\n"
            f"Ваше HP: {new_hp} / {stats['max_hp']}\n\n"
            "Ход переходит к противнику."
        )

        await enemy_turn(callback.message, callback.from_user.id)
        await callback.answer()
        return

    if item["type"] == "rage_potion":
        await add_battle_damage_bonus(callback.from_user.id, item["damage_bonus"])

        inventory.remove(item_id)
        await save_inventory(callback.from_user.id, inventory)

        await update_battle_turn(callback.from_user.id, "enemy")

        await callback.message.answer(
            f"Вы выпили: {item['name']}.\n\n"
            f"Урон увеличен на +{item['damage_bonus']} HP до конца боя.\n\n"
            "Ход переходит к противнику."
        )

        await enemy_turn(callback.message, callback.from_user.id)
        await callback.answer()
        return

    if item["type"] == "escape_scroll":
        inventory.remove(item_id)
        await save_inventory(callback.from_user.id, inventory)

        await end_battle(callback.from_user.id)

        await callback.message.answer(
            "Вы разворачиваете свиток побега.\n\n"
            "Мир вокруг искажается, и через мгновение вы оказываетесь в безопасности."
        )

        await show_main_menu(callback.message, callback.from_user.id)

        await callback.answer()
        return


async def player_victory(message: Message, telegram_id: int):
    player = await get_player(telegram_id)

    reward_gold = player["battle_reward_gold"]
    reward_xp = player["battle_reward_xp"]
    remaining_potions = player["battle_enemy_potions"]
    old_level = get_level_from_xp(player["xp"])

    await add_gold(telegram_id, reward_gold)
    await add_xp(telegram_id, reward_xp)

    updated_player = await get_player(telegram_id)

    if player["progress_stage"] == 0:
        await give_achievement(message, telegram_id, "first_boss")

    if get_boss_by_stage(player["progress_stage"] + 1) is None:
        await give_achievement(message, telegram_id, "final_boss")

    await check_level_achievements(message, telegram_id, old_level)

    inventory = await get_inventory(telegram_id)
    level = get_level_from_xp(updated_player["xp"])

    added_potions = 0

    for _ in range(remaining_potions):
        if has_inventory_space(inventory, level):
            inventory.append("small_heal_potion")
            added_potions += 1

    boss = get_boss_by_stage(player["progress_stage"])
    boss_drops = boss.get("drops", []) if boss else []

    received_items = []

    for item_id in boss_drops:
        if has_inventory_space(inventory, level):
            inventory.append(item_id)
            item = get_item_by_id(item_id)
            received_items.append(item["name"] if item else item_id)

    await save_inventory(telegram_id, inventory)

    await increase_progress_stage(telegram_id)
    await end_battle(telegram_id)

    drops_text = ""

    if received_items:
        drops_text = "\nПолучены предметы:\n" + "\n".join(received_items)

    await message.answer(
        f"Победа!\n\n"
        f"Вы победили врага: {player['battle_enemy_name']}.\n\n"
        f"Награда:\n"
        f"+{reward_gold} золота\n"
        f"+{reward_xp} XP\n"
        f"Получено зелий лечения: {added_potions}"
        f"{drops_text}"
    )

    await show_main_menu(message, telegram_id)


async def player_defeat(message: Message, telegram_id: int):
    player = await get_player(telegram_id)
    level = get_level_from_xp(player["xp"])
    stats = get_player_stats(level, player)

    restored_hp = max(stats["max_hp"] // 2, 1)
    lost_gold = int(player["gold"] * 0.15)

    await set_current_hp(telegram_id, restored_hp)
    await remove_gold(telegram_id, lost_gold)
    await end_battle(telegram_id)

    await message.answer(
        "Вы теряете сознание...\n\n"
        "Когда тьма отступает, вы видите перед собой старого мага.\n\n"
        "— Ну и потрепало же тебя, путник. "
        "Я подлечил тебя по доброте сердечной... "
        "но доброта нынче тоже требует оплаты.\n\n"
        f"Восстановлено HP: {restored_hp} / {stats['max_hp']}\n"
        f"Плата мага: {lost_gold} золота."
    )

    await show_main_menu(message, telegram_id)


@dp.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    await show_main_menu(callback.message, callback.from_user.id)
    await callback.answer()


async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()
    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())