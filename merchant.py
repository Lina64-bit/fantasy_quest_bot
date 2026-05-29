SHOP_ITEMS = {
    0: [
        {
            "id": "small_heal_potion",
            "name": "Малое зелье лечения",
            "price": 10,
            "description": "+10 HP",
            "type": "heal_potion",
            "heal_amount": 10
        },
        {
            "id": "rusty_sword",
            "name": "Старый ржавый меч",
            "price": 10,
            "description": "+10 HP к урону",
            "type": "weapon",
            "damage_bonus": 10
        },
        {
            "id": "wooden_shield",
            "name": "Старый деревянный щит",
            "price": 15,
            "description": "+5% к шансу защиты",
            "type": "shield",
            "defense_bonus": 5
        },
        {
            "id": "luck_potion",
            "name": "Малое зелье удачи",
            "price": 30,
            "description": "+1 к Благословению Фортуны",
            "type": "luck_potion",
            "luck_bonus": 1
        }
    ],

    5: [
        {
            "id": "iron_sword",
            "name": "Железный меч",
            "price": 15,
            "description": "+20 HP к урону",
            "type": "weapon",
            "damage_bonus": 20
        },
        {
            "id": "iron_shield",
            "name": "Железный щит",
            "price": 20,
            "description": "+15% к шансу защиты",
            "type": "shield",
            "defense_bonus": 15
        },
        {
            "id": "rage_potion",
            "name": "Зелье ярости",
            "price": 40,
            "description": "+10 HP к урону до конца боя",
            "type": "rage_potion",
            "damage_bonus": 10
        },
        {
            "id": "escape_scroll",
            "name": "Свиток побега",
            "price": 25,
            "description": "Позволяет сбежать из боя",
            "type": "escape_scroll"
        }
    ],

    10: [
        {
            "id": "medium_heal_potion",
            "name": "Стандартное зелье здоровья",
            "price": 20,
            "description": "+25 HP",
            "type": "heal_potion",
            "heal_amount": 25
        },
        {
            "id": "large_heal_potion",
            "name": "Большое зелье лечения",
            "price": 45,
            "description": "+50 HP",
            "type": "heal_potion",
            "heal_amount": 50
        },
        {
            "id": "steel_sword",
            "name": "Стальной меч",
            "price": 50,
            "description": "+70 HP к урону",
            "type": "weapon",
            "damage_bonus": 70
        },
        {
            "id": "medium_luck_potion",
            "name": "Стандартное зелье удачи",
            "price": 45,
            "description": "+2 к Благословению Фортуны",
            "type": "luck_potion",
            "luck_bonus": 2
        }
    ],

    15: [
        {
            "id": "fortune_ring",
            "name": "Кольцо Фортуны",
            "price": 120,
            "description": "+1 к Благословению Фортуны",
            "type": "accessory",
            "luck_bonus": 1
        }
    ]
}


SPECIAL_ITEMS = [
    {
        "id": "healing_rune",
        "name": "Руна лечения",
        "price": 0,
        "description": "Полностью восстанавливает здоровье",
        "type": "healing_rune"
    }
]


def get_available_items(player_level: int):
    items = []

    for required_level, level_items in SHOP_ITEMS.items():
        if player_level >= required_level:
            items.extend(level_items)

    return items


def get_item_by_id(item_id: str):
    for level_items in SHOP_ITEMS.values():
        for item in level_items:
            if item["id"] == item_id:
                return item

    for item in SPECIAL_ITEMS:
        if item["id"] == item_id:
            return item

    return None