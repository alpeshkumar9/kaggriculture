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
LAND_EXPANSION_THRESHOLDS = [2500, 5000, 9000]

def get_base_price(item):
    if item in COMMODITIES:
        return COMMODITIES[item].get('base_price', 25)
    return 25

def get_next_land_cost(unlocked_quadrants_count):
    if unlocked_quadrants_count < 4:
        return LAND_QUADRANT_COSTS[unlocked_quadrants_count - 1]
    return None

def get_seasonal_crop_choice(day, money, unlocked_quadrants_count, step=0):
    """
    High Velocity ROI Crop Scheduler:
    Prioritizes fast-turnover Wheat & Carrots ($140 profit / 2 days) to build maximum cash.
    """
    if day < 20:
        return 'WHEAT' if step % 2 == 0 else 'CARROT'
    elif day <= 27:
        return 'WHEAT'
    else:
        return 'WHEAT' if day < 29 else None

def get_fibonacci_hire_cost(hires_today, mult=1):
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    idx = min(hires_today, len(fib) - 1)
    return mult * fib[idx]

def should_hire_farmhand(workload_count, money, hires_today, mult=1):
    cost = get_fibonacci_hire_cost(hires_today, mult)
    if workload_count >= 12 and money >= cost + 200:
        return True
    return False

def calculate_market_sell_quantity(item, qty, current_price, base_price, day):
    if qty <= 0:
        return 0
    if day >= 25 or current_price >= base_price * 0.90:
        return qty
    return 0


