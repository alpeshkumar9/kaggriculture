"""
Official Strategy Rules & Constants for Kaggle Kaggriculture Competition.
Fully compliant with official specs in overview.md and AGENTS.md.
"""

import collections

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

LAND_QUADRANT_COSTS = [1000, 2000] # Quadrants 2 and 3 only
LAND_EXPANSION_THRESHOLDS = [1200, 2400]
MAX_QUADRANTS = 3
TARGET_FARMHANDS = 5

TOWN_SHOP_DEMANDS = {
    'BAKERY': ['EGG', 'WHEAT'],
    'PIZZA_SHOP': ['MILK', 'TOMATO', 'WHEAT'],
    'BRUNCH_SPOT': ['EGG', 'WHEAT', 'STRAWBERRY'],
    'YARN_STORE': ['WOOL'],
    'ICE_CREAM_SHOP': ['STRAWBERRY', 'MILK', 'WHEAT'],
    'PET_CAFE': ['CARROT'],
    'SMOOTHIE_SHOP': ['STRAWBERRY', 'MILK'],
    'FARMERS_MARKET': ['WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY']
}

def get_fibonacci_hire_cost(hires_today, mult=1):
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    idx = min(hires_today, len(fib) - 1)
    return mult * fib[idx]

def should_hire_farmhand(workload_count, money, hires_today, mult=1):
    """
    Workload-based Farmhand Scaling:
    Only hire additional labor if active unwatered/unharvested tiles > (1 + hires_today) * 5
    and money reserves are healthy.
    """
    cost = get_fibonacci_hire_cost(hires_today, mult)
    needed = (1 + hires_today) * 5
    return workload_count >= needed and money >= cost + 100

def get_opponent_crop_distribution(opponent_tiles):
    dist = collections.defaultdict(int)
    if not opponent_tiles:
        return dist
    for r in range(len(opponent_tiles)):
        for c in range(len(opponent_tiles[r])):
            t = opponent_tiles[r][c]
            if isinstance(t, dict) and t.get('kind') == 'PLANT':
                crop = t.get('crop')
                if crop:
                    dist[crop] += 1
    return dist

def get_active_town_demands(unlocked_shops):
    demands = set()
    if not unlocked_shops:
        return demands
    for shop in unlocked_shops:
        shop_upper = str(shop).upper()
        if shop_upper in TOWN_SHOP_DEMANDS:
            for item in TOWN_SHOP_DEMANDS[shop_upper]:
                demands.add(item)
    return demands

def get_seasonal_crop_choice(day, money, quad_count=1, step=0):
    """
    Seasonal Crop Selector:
    - Days 1-10: Fast cash turnover (Wheat & Carrot)
    - Days 11-23: High-value crops (Melon, Strawberry, Tomato)
    - Days 24-30: Late harvest sweep (Wheat & Carrot)
    """
    if day < 10:
        return 'CARROT' if (step % 2 == 0 or money < 30) else 'WHEAT'
    elif day <= 23:
        if money >= 200 and step % 3 == 0:
            return 'MELON'
        elif money >= 120 and step % 2 == 0:
            return 'STRAWBERRY'
        elif money >= 60:
            return 'TOMATO'
        else:
            return 'CARROT'
    elif day <= 27:
        return 'CARROT' if step % 2 == 0 else 'WHEAT'
    else:
        return 'WHEAT' if day < 29 else None

def get_adversarial_crop_choice(day, money, unlocked_quadrants_count=1, step=0, opponent_tiles=None, town_shops=None):
    if day >= 24:
        return 'WHEAT' if day < 29 else None

    opponent_crops = get_opponent_crop_distribution(opponent_tiles)
    town_demands = get_active_town_demands(town_shops)

    candidates = ['WHEAT', 'CARROT']
    if day >= 10 and money >= 120:
        candidates.extend(['TOMATO', 'STRAWBERRY', 'MELON'])

    best_crop = 'WHEAT'
    best_score = -999.0

    for crop in candidates:
        base_cost = COMMODITIES[crop]['seed_cost']
        if money < base_cost:
            continue

        score = 10.0
        if crop == 'WHEAT': score += 15.0
        elif crop == 'CARROT': score += 12.0

        if crop in town_demands:
            score += 25.0

        opp_count = opponent_crops.get(crop, 0)
        score -= opp_count * 15.0

        if score > best_score:
            best_score = score
            best_crop = crop

    return best_crop

def calculate_market_sell_quantity(item, qty, current_price, base_price, day, shed_total=0):
    """
    Shed Overflow Protection & Market Sell Logic:
    - If day >= 24 or shed_total >= 50, sell all quantity immediately to avoid cap discards.
    - Otherwise, sell if current_price >= base_price * 0.85.
    """
    if qty <= 0:
        return 0
    if day >= 24 or shed_total >= 50:
        return qty
    if current_price >= base_price * 0.85:
        return qty
    return min(qty, 2)

def should_undercut_market(item, qty, current_price, base_price, day, opponent_tiles=None):
    if qty <= 0:
        return 0
    if day >= 24 or current_price >= base_price * 0.85:
        return qty
    return qty





