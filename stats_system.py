from merchant import get_item_by_id


def get_player_stats(
    level: int,
    player: dict | None = None
):

    stats = {
        "max_hp": 10,
        "damage": 5,
        "defense_chance": 0,
        "luck": 0
    }

    if 6 <= level <= 10:
        stats["max_hp"] = 20
        stats["damage"] = 10
        stats["defense_chance"] = 5

    elif level >= 11:
        stats["max_hp"] = 40
        stats["damage"] = 20
        stats["defense_chance"] = 5

    if player:

        equipped_weapon = player.get("equipped_weapon")
        equipped_shield = player.get("equipped_shield")
        equipped_accessory = player.get("equipped_accessory")

        if equipped_weapon:
            weapon = get_item_by_id(equipped_weapon)

            if weapon:
                stats["damage"] += weapon.get("damage_bonus", 0)

        if equipped_shield:
            shield = get_item_by_id(equipped_shield)

            if shield:
                stats["defense_chance"] += shield.get("defense_bonus", 0)

        if equipped_accessory:
            accessory = get_item_by_id(equipped_accessory)

            if accessory:
                stats["luck"] += accessory.get("luck_bonus", 0)

        stats["luck"] += player.get("luck_bonus", 0)

    return stats