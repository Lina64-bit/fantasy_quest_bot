MAX_LEVEL = 20


def get_level_from_xp(xp: int) -> int:
    """
    Возвращает уровень игрока по количеству XP.
    """

    required_xp = 5
    level = 1

    while level < MAX_LEVEL:

        if xp < required_xp:
            return level

        required_xp *= 2
        level += 1

    return MAX_LEVEL


def get_next_level_xp(level: int) -> int:
    """
    XP, необходимый для следующего уровня.
    """

    required_xp = 5

    for _ in range(1, level):
        required_xp *= 2

    return required_xp