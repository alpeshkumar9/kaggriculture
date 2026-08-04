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

LAND_QUADRANT_COSTS = [1000, 2000] # Quadrants 2 and 3 only (never buy 4!)
LAND_EXPANSION_THRESHOLDS = [1500, 3000]
MAX_QUADRANTS = 3
MAX_COWS = 6
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

def get_opponent_crop_distribution(opponent_tiles):
    """
    Opponent Farm Telemetry: Scans opponent's 10x10 farm grid for active crop counts.
    """
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
    """
    Town Shop Demand Tracker: Collects set of items currently demanded by active shops.
    """
    demands = set()
    if not unlocked_shops:
        return demands
    for shop in unlocked_shops:
        shop_upper = str(shop).upper()
        if shop_upper in TOWN_SHOP_DEMANDS:
            for item in TOWN_SHOP_DEMANDS[shop_upper]:
                demands.add(item)
    return demands

def get_adversarial_crop_choice(day, money, unlocked_quadrants_count, step=0, opponent_tiles=None, town_shops=None):
    """
    Grandmaster Opponent Avoidance & Town Demand Matching Scheduler.
    - Avoids crops heavily mass-produced by opponent (prevents selling into crashed market floors).
    - Prioritizes crops demanded by active town shops (captures town inventory drain price surges).
    """
    if day >= 25:
        return 'WHEAT' if day < 29 else None

    opponent_crops = get_opponent_crop_distribution(opponent_tiles)
    town_demands = get_active_town_demands(town_shops)

    candidates = ['WHEAT', 'CARROT']
    if day >= 10 and money >= 150:
        candidates.extend(['TOMATO', 'STRAWBERRY', 'MELON'])

    best_crop = 'WHEAT'
    best_score = -999.0

    for crop in candidates:
        base_cost = COMMODITIES[crop]['seed_cost']
        if money < base_cost:
            continue

        score = 10.0
        # Fast turnover bonus for Wheat/Carrot early game
        if crop == 'WHEAT': score += 15.0
        elif crop == 'CARROT': score += 12.0

        # Town Demand Bonus (+20 points if town shop consumes this crop)
        if crop in town_demands:
            score += 20.0

        # Opponent Glut Avoidance (-15 points per opponent tile of this crop)
        opp_count = opponent_crops.get(crop, 0)
        score -= opp_count * 15.0

        if score > best_score:
            best_score = score
            best_crop = crop

    return best_crop

def should_undercut_market(item, qty, current_price, base_price, day, opponent_tiles=None):
    """
    Adversarial Market Undercutting:
    If opponent has crops maturing within 1 day, liquidate shed stock 1 turn early to capture peak price.
    """
    if qty <= 0:
        return 0
    if day >= 25 or current_price >= base_price * 0.90:
        return qty

    # Scan opponent tiles for maturing crops of same item
    if opponent_tiles:
        for r in range(len(opponent_tiles)):
            for c in range(len(opponent_tiles[r])):
                t = opponent_tiles[r][c]
                if isinstance(t, dict) and t.get('kind') == 'PLANT' and t.get('crop') == item:
                    age = day - t.get('planted_day', 0)
                    maturity = COMMODITIES.get(item, {}).get('first_yield_days', 2)
                    if age >= maturity - 1: # Opponent matures tomorrow! Undercut now!
                        return qty

    return 0



