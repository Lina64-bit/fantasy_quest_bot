ACHIEVEMENTS = {
    "first_boss": {
        "title": "Первый шаг героя",
        "description": "Победить первого босса.",
        "reward_gold": 20,
        "reward_xp": 5
    },
    "final_boss": {
        "title": "Покоритель Бездны",
        "description": "Победить последнего доступного босса.",
        "reward_gold": 150,
        "reward_xp": 50
    },
    "first_purchase": {
        "title": "Первый торг",
        "description": "Совершить первую покупку у торговца.",
        "reward_gold": 10,
        "reward_xp": 3
    },
    "level_5": {
        "title": "Опытный путник",
        "description": "Достигнуть 5 уровня.",
        "reward_gold": 30,
        "reward_xp": 10
    },
    "level_10": {
        "title": "Закалённый герой",
        "description": "Достигнуть 10 уровня.",
        "reward_gold": 60,
        "reward_xp": 20
    },
    "level_15": {
        "title": "Легенда дорог",
        "description": "Достигнуть 15 уровня.",
        "reward_gold": 100,
        "reward_xp": 35
    },
    "level_20": {
        "title": "Герой Элариона",
        "description": "Достигнуть 20 уровня.",
        "reward_gold": 200,
        "reward_xp": 80
    },
    "lucky_one": {
        "title": "Любимец Фортуны",
        "description": "Получить бонус удачи от зелья.",
        "reward_gold": 25,
        "reward_xp": 8
    },
    "well_armed": {
        "title": "Вооружён и опасен",
        "description": "Экипировать первое оружие.",
        "reward_gold": 20,
        "reward_xp": 5
    },
    "shield_bearer": {
        "title": "Под защитой",
        "description": "Экипировать первый щит.",
        "reward_gold": 20,
        "reward_xp": 5
    }
}


def get_achievement(achievement_id: str):
    return ACHIEVEMENTS.get(achievement_id)