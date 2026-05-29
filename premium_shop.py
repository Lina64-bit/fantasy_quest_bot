PREMIUM_PRODUCTS = {
    "stars_gold_100": {
        "title": "100 золота",
        "description": "Мешочек золота из Астральной лавки.",
        "stars": 25,
        "gold": 100,
        "xp": 0
    },
    "stars_gold_500": {
        "title": "500 золота",
        "description": "Большой сундук золота из Астральной лавки.",
        "stars": 100,
        "gold": 500,
        "xp": 0
    },
    "stars_xp_50": {
        "title": "50 XP",
        "description": "Свиток опыта для ускорения развития героя.",
        "stars": 20,
        "gold": 0,
        "xp": 50
    },
    "stars_xp_200": {
        "title": "200 XP",
        "description": "Древний фолиант опыта.",
        "stars": 60,
        "gold": 0,
        "xp": 200
    }
}


def get_premium_product(product_id: str):
    return PREMIUM_PRODUCTS.get(product_id)