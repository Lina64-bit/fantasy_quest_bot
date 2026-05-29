import os
import aiosqlite
import json

DB_NAME = os.getenv(
    "DB_PATH",
    "game.db"
)


async def ensure_column(db, table_name: str, column_name: str, column_definition: str):
    cursor = await db.execute(f"PRAGMA table_info({table_name})")
    columns = await cursor.fetchall()
    existing_columns = [column[1] for column in columns]

    if column_name not in existing_columns:
        await db.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        )


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS players (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                character_name TEXT,
                appearance_prompt TEXT,
                image_url TEXT,
                current_scene TEXT DEFAULT 'start',
                xp INTEGER DEFAULT 0,
                gold INTEGER DEFAULT 0,
                inventory TEXT DEFAULT '[]',
                equipped_weapon TEXT DEFAULT '',
                equipped_shield TEXT DEFAULT '',
                equipped_accessory TEXT DEFAULT '',
                luck_bonus INTEGER DEFAULT 0,
                current_hp INTEGER DEFAULT 10,
                progress_stage INTEGER DEFAULT 0,
                in_battle INTEGER DEFAULT 0,
                battle_enemy_name TEXT DEFAULT '',
                battle_enemy_hp INTEGER DEFAULT 0,
                battle_enemy_max_hp INTEGER DEFAULT 0,
                battle_enemy_damage INTEGER DEFAULT 0,
                battle_enemy_defense INTEGER DEFAULT 0,
                battle_enemy_potions INTEGER DEFAULT 0,
                battle_reward_gold INTEGER DEFAULT 0,
                battle_reward_xp INTEGER DEFAULT 0,
                battle_turn TEXT DEFAULT '',
                battle_damage_bonus INTEGER DEFAULT 0,
                achievements TEXT DEFAULT '[]',
                claimed_achievements TEXT DEFAULT '[]'
            )
        """)

        await ensure_column(db, "players", "inventory", "TEXT DEFAULT '[]'")
        await ensure_column(db, "players", "equipped_weapon", "TEXT DEFAULT ''")
        await ensure_column(db, "players", "equipped_shield", "TEXT DEFAULT ''")
        await ensure_column(db, "players", "equipped_accessory", "TEXT DEFAULT ''")
        await ensure_column(db, "players", "luck_bonus", "INTEGER DEFAULT 0")
        await ensure_column(db, "players", "current_hp", "INTEGER DEFAULT 10")
        await ensure_column(db, "players", "progress_stage", "INTEGER DEFAULT 0")
        await ensure_column(db, "players", "in_battle", "INTEGER DEFAULT 0")
        await ensure_column(db, "players", "battle_enemy_name", "TEXT DEFAULT ''")
        await ensure_column(db, "players", "battle_enemy_hp", "INTEGER DEFAULT 0")
        await ensure_column(db, "players", "battle_enemy_max_hp", "INTEGER DEFAULT 0")
        await ensure_column(db, "players", "battle_enemy_damage", "INTEGER DEFAULT 0")
        await ensure_column(db, "players", "battle_enemy_defense", "INTEGER DEFAULT 0")
        await ensure_column(db, "players", "battle_enemy_potions", "INTEGER DEFAULT 0")
        await ensure_column(db, "players", "battle_reward_gold", "INTEGER DEFAULT 0")
        await ensure_column(db, "players", "battle_reward_xp", "INTEGER DEFAULT 0")
        await ensure_column(db, "players", "battle_turn", "TEXT DEFAULT ''")
        await ensure_column(db, "players", "battle_damage_bonus", "INTEGER DEFAULT 0")
        await ensure_column(db, "players", "achievements", "TEXT DEFAULT '[]'")
        await ensure_column(db, "players", "claimed_achievements", "TEXT DEFAULT '[]'")

        await db.commit()


async def create_or_update_player(
    telegram_id: int,
    username: str,
    character_name: str,
    appearance_prompt: str,
    image_url: str = ""
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO players (
                telegram_id,
                username,
                character_name,
                appearance_prompt,
                image_url
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id)
            DO UPDATE SET
                username = excluded.username,
                character_name = excluded.character_name,
                appearance_prompt = excluded.appearance_prompt,
                image_url = excluded.image_url
        """, (
            telegram_id,
            username,
            character_name,
            appearance_prompt,
            image_url
        ))

        await db.commit()


async def get_player(telegram_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            "SELECT * FROM players WHERE telegram_id = ?",
            (telegram_id,)
        )

        player = await cursor.fetchone()

        return dict(player) if player else None


async def update_scene(telegram_id: int, scene_id: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET current_scene = ? WHERE telegram_id = ?",
            (scene_id, telegram_id)
        )
        await db.commit()


async def add_xp(telegram_id: int, amount: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET xp = xp + ? WHERE telegram_id = ?",
            (amount, telegram_id)
        )
        await db.commit()


async def add_gold(telegram_id: int, amount: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET gold = gold + ? WHERE telegram_id = ?",
            (amount, telegram_id)
        )
        await db.commit()


async def remove_gold(telegram_id: int, amount: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET gold = MAX(gold - ?, 0) WHERE telegram_id = ?",
            (amount, telegram_id)
        )
        await db.commit()


async def get_inventory(telegram_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT inventory FROM players WHERE telegram_id = ?",
            (telegram_id,)
        )

        result = await cursor.fetchone()

        if not result:
            return []

        return json.loads(result[0])


async def save_inventory(telegram_id: int, inventory: list):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET inventory = ? WHERE telegram_id = ?",
            (
                json.dumps(inventory, ensure_ascii=False),
                telegram_id
            )
        )
        await db.commit()


async def add_item_to_inventory(telegram_id: int, item_id: str):
    inventory = await get_inventory(telegram_id)
    inventory.append(item_id)
    await save_inventory(telegram_id, inventory)


async def equip_weapon(telegram_id: int, item_id: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET equipped_weapon = ? WHERE telegram_id = ?",
            (item_id, telegram_id)
        )
        await db.commit()


async def equip_shield(telegram_id: int, item_id: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET equipped_shield = ? WHERE telegram_id = ?",
            (item_id, telegram_id)
        )
        await db.commit()


async def equip_accessory(telegram_id: int, item_id: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET equipped_accessory = ? WHERE telegram_id = ?",
            (item_id, telegram_id)
        )
        await db.commit()


async def add_luck_bonus(telegram_id: int, amount: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET luck_bonus = luck_bonus + ? WHERE telegram_id = ?",
            (amount, telegram_id)
        )
        await db.commit()


async def set_current_hp(telegram_id: int, hp: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET current_hp = ? WHERE telegram_id = ?",
            (hp, telegram_id)
        )
        await db.commit()


async def increase_progress_stage(telegram_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET progress_stage = progress_stage + 1 WHERE telegram_id = ?",
            (telegram_id,)
        )
        await db.commit()


async def add_battle_damage_bonus(telegram_id: int, amount: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET battle_damage_bonus = battle_damage_bonus + ? WHERE telegram_id = ?",
            (amount, telegram_id)
        )
        await db.commit()


async def start_battle(
    telegram_id: int,
    enemy_name: str,
    enemy_hp: int,
    enemy_damage: int,
    enemy_defense: int,
    enemy_potions: int,
    reward_gold: int,
    reward_xp: int
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE players
            SET
                in_battle = 1,
                battle_enemy_name = ?,
                battle_enemy_hp = ?,
                battle_enemy_max_hp = ?,
                battle_enemy_damage = ?,
                battle_enemy_defense = ?,
                battle_enemy_potions = ?,
                battle_reward_gold = ?,
                battle_reward_xp = ?,
                battle_turn = '',
                battle_damage_bonus = 0
            WHERE telegram_id = ?
        """, (
            enemy_name,
            enemy_hp,
            enemy_hp,
            enemy_damage,
            enemy_defense,
            enemy_potions,
            reward_gold,
            reward_xp,
            telegram_id
        ))

        await db.commit()


async def update_battle_turn(telegram_id: int, turn: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET battle_turn = ? WHERE telegram_id = ?",
            (turn, telegram_id)
        )
        await db.commit()


async def update_enemy_hp(telegram_id: int, hp: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET battle_enemy_hp = ? WHERE telegram_id = ?",
            (hp, telegram_id)
        )
        await db.commit()


async def update_enemy_potions(telegram_id: int, amount: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET battle_enemy_potions = ? WHERE telegram_id = ?",
            (amount, telegram_id)
        )
        await db.commit()


async def end_battle(telegram_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE players
            SET
                in_battle = 0,
                battle_enemy_name = '',
                battle_enemy_hp = 0,
                battle_enemy_max_hp = 0,
                battle_enemy_damage = 0,
                battle_enemy_defense = 0,
                battle_enemy_potions = 0,
                battle_reward_gold = 0,
                battle_reward_xp = 0,
                battle_turn = '',
                battle_damage_bonus = 0
            WHERE telegram_id = ?
        """, (telegram_id,))

        await db.commit()


async def get_achievements(telegram_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT achievements FROM players WHERE telegram_id = ?",
            (telegram_id,)
        )
        result = await cursor.fetchone()

        if not result:
            return []

        return json.loads(result[0])


async def get_claimed_achievements(telegram_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT claimed_achievements FROM players WHERE telegram_id = ?",
            (telegram_id,)
        )
        result = await cursor.fetchone()

        if not result:
            return []

        return json.loads(result[0])


async def add_achievement(telegram_id: int, achievement_id: str):
    achievements = await get_achievements(telegram_id)

    if achievement_id not in achievements:
        achievements.append(achievement_id)

        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute(
                "UPDATE players SET achievements = ? WHERE telegram_id = ?",
                (
                    json.dumps(achievements, ensure_ascii=False),
                    telegram_id
                )
            )
            await db.commit()


async def claim_achievement(telegram_id: int, achievement_id: str):
    claimed = await get_claimed_achievements(telegram_id)

    if achievement_id not in claimed:
        claimed.append(achievement_id)

        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute(
                "UPDATE players SET claimed_achievements = ? WHERE telegram_id = ?",
                (
                    json.dumps(claimed, ensure_ascii=False),
                    telegram_id
                )
            )
            await db.commit()