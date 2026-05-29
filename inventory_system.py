def get_inventory_limit(level: int) -> int:
    return level * 5


def get_inventory_count(inventory: list) -> int:
    return len(inventory)


def has_inventory_space(inventory: list, level: int) -> bool:
    return get_inventory_count(inventory) < get_inventory_limit(level)