import random


BOSSES = [
    {
        "name": "Подворотный гоблин",
        "max_hp": 10,
        "damage": 2,
        "defense_chance": 0,
        "heal_potions": 0,
        "reward_gold": 35,
        "reward_xp": 5,
        "drops": [],
        "intro": (
            "Вы сворачиваете в узкий переулок между старыми домами.\n\n"
            "Из темноты доносится мерзкое хихиканье.\n\n"
            "Маленький гоблин с ржавым ножом преграждает вам путь.\n\n"
            "— Кошелёк или жизнь, путник!"
        )
    },
    {
        "name": "Охранник-паладин",
        "max_hp": 25,
        "damage": 10,
        "defense_chance": 25,
        "heal_potions": 3,
        "reward_gold": 20,
        "reward_xp": 15,
        "drops": ["escape_scroll"],
        "intro": (
            "У массивных ворот вас встречает закованный в броню паладин.\n\n"
            "Его меч вспыхивает золотым светом.\n\n"
            "— Никто не пройдёт дальше без дозволения Ордена."
        )
    },
    {
        "name": "Коридорный эльф",
        "max_hp": 20,
        "damage": 5,
        "defense_chance": 30,
        "heal_potions": 5,
        "reward_gold": 15,
        "reward_xp": 15,
        "drops": [],
        "intro": (
            "В длинном каменном коридоре слышится лёгкий звон тетивы.\n\n"
            "Из теней бесшумно выходит эльфийский страж.\n\n"
            "— Люди слишком шумны для этих мест."
        )
    },
    {
        "name": "Пепельный рыцарь",
        "max_hp": 40,
        "damage": 15,
        "defense_chance": 20,
        "heal_potions": 2,
        "reward_gold": 50,
        "reward_xp": 25,
        "drops": ["rage_potion"],
        "intro": (
            "На старом поле битвы поднимается силуэт в почерневших доспехах.\n\n"
            "Из щелей брони просачивается пепельное свечение.\n\n"
            "Рыцарь медленно поднимает огромный меч."
        )
    },
    {
        "name": "Болотная ведьма",
        "max_hp": 35,
        "damage": 20,
        "defense_chance": 10,
        "heal_potions": 6,
        "reward_gold": 70,
        "reward_xp": 30,
        "drops": ["fortune_ring"],
        "intro": (
            "Туман сгущается над болотом.\n\n"
            "Старая женщина с фонарём смотрит прямо на вас пустыми глазами.\n\n"
            "— Ещё один путник заблудился..."
        )
    },
    {
        "name": "Каменный страж руин",
        "max_hp": 70,
        "damage": 18,
        "defense_chance": 40,
        "heal_potions": 0,
        "reward_gold": 100,
        "reward_xp": 45,
        "drops": ["healing_rune"],
        "intro": (
            "Древние руны вспыхивают синим светом.\n\n"
            "Каменный гигант приходит в движение, сотрясая землю тяжёлыми шагами."
        )
    },
    {
        "name": "Лорд Чёрного Леса",
        "max_hp": 90,
        "damage": 30,
        "defense_chance": 25,
        "heal_potions": 4,
        "reward_gold": 150,
        "reward_xp": 70,
        "drops": ["large_heal_potion"],
        "intro": (
            "Лес затихает.\n\n"
            "Даже ветер перестаёт шевелить листья.\n\n"
            "Из темноты выходит высокий силуэт с рогатой короной."
        )
    },
    {
        "name": "Хранитель Бездны",
        "max_hp": 130,
        "damage": 45,
        "defense_chance": 35,
        "heal_potions": 8,
        "reward_gold": 250,
        "reward_xp": 120,
        "drops": ["large_heal_potion", "rage_potion"],
        "intro": (
            "Воздух становится тяжёлым.\n\n"
            "Реальность вокруг начинает дрожать.\n\n"
            "Из разлома в пространстве появляется существо, чью форму невозможно удержать взглядом."
        )
    }
]


def defense_success(chance: int) -> bool:
    return random.randint(1, 100) <= chance


def get_boss_by_stage(stage: int):
    if stage < len(BOSSES):
        return BOSSES[stage].copy()

    return None