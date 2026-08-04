"""
Official Strategy Rules & Constants for Kaggle Kaggriculture Competition.
Fully compliant with official specs in overview.md and AGENTS.md.
"""

COMMODITIES = {
    'WHEAT': {
        'type': 'One-time',
        'seed_cost': 10,
        'base_price': 25,
        'first_yield_days': 2,
        'max_yield_days': 4,
        'max_yield': 6,
        'action_cost': 1
    },
    'CARROT': {
        'type': 'One-time',
        'seed_cost': 20,
        'base_price': 35,
        'first_yield_days': 2,
        'max_yield_days': 3,
        'max_yield': 4,
        'action_cost': 1
    },
    'TOMATO': {
        'type': 'Ongoing',
        'seed_cost': 50,
        'base_price': 60,
        'first_yield_days': 7,
        'max_yield': 4,
        'action_cost': 1
    },
    'STRAWBERRY': {
        'type': 'Ongoing',
        'seed_cost': 100,
        'base_price': 120,
        'first_yield_days': 10,
        'max_yield': 4,
        'action_cost': 1
    },
    'MELON': {
        'type': 'One-time',
        'seed_cost': 80,
        'base_price': 250,
        'first_yield_days': 10,
        'max_yield_days': 12,
        'max_yield': 6,
        'action_cost': 1
    },
    'EGG': {
        'type': 'AnimalProduct',
        'animal_cost': 300,
        'base_price': 50,
        'first_yield_days': 4,
        'max_yield': 4
    },
    'MILK': {
        'type': 'AnimalProduct',
        'animal_cost': 400,
        'base_price': 160,
        'first_yield_days': 8,
        'max_yield': 6
    },
    'WOOL': {
        'type': 'AnimalProduct',
        'animal_cost': 500,
        'base_price': 200,
        'first_yield_days': 6,
        'max_yield': 6
    },
    'FERTILIZER': {
        'type': 'Consumable',
        'buy_cost': 100,
        'base_price': 100
    }
}

LAND_QUADRANT_COSTS = [1000, 2000, 4000]

QUADRANT_BOUNDS = {
    "NW": {"min_x": 0, "max_x": 4, "min_y": 0, "max_y": 4},
    "NE": {"min_x": 5, "max_x": 9, "min_y": 0, "max_y": 4},
    "SW": {"min_x": 0, "max_x": 4, "min_y": 5, "max_y": 9},
    "SE": {"min_x": 5, "max_x": 9, "min_y": 5, "max_y": 9}
}

def get_base_price(item):
    if item in COMMODITIES:
        return COMMODITIES[item].get('base_price', 25)
    return 25

def get_next_land_cost(unlocked_quadrants_count):
    if unlocked_quadrants_count < 4:
        return LAND_QUADRANT_COSTS[unlocked_quadrants_count - 1]
    return None
