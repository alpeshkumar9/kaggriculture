"""
Official Kaggle Kaggriculture Competition Submission Bot
Compatible with kaggle_environments kaggriculture simulation engine.
"""

import collections

COMMODITIES = {
    'WHEAT': {'seed_cost': 10, 'base_price': 25, 'first_yield_days': 2},
    'CARROT': {'seed_cost': 20, 'base_price': 35, 'first_yield_days': 2},
    'TOMATO': {'seed_cost': 50, 'base_price': 60, 'first_yield_days': 7},
    'STRAWBERRY': {'seed_cost': 100, 'base_price': 120, 'first_yield_days': 10},
    'MELON': {'seed_cost': 80, 'base_price': 250, 'first_yield_days': 10},
}

LAND_COSTS = [1000, 2000, 4000]

def agent(observation, configuration=None):
    """
    Kaggle Environments Entry Point
    - observation: dict containing full game state
    - returns: {"farmer": [...], "hands": [[...]], "market": [[...]]}
    """
    obs = observation if isinstance(observation, dict) else getattr(observation, '__dict__', {})
    
    player_id = obs.get('player', 0)
    farms = obs.get('farms', [{}, {}])
    me = farms[player_id] if player_id < len(farms) else {}
    
    money = me.get('money', 1000.0)
    tiles = me.get('tiles', [])
    farmer_pos = me.get('farmer', [0, 0])
    hands_pos = me.get('hands', [])
    unlocked_quads = me.get('unlocked_quadrants', ['NW'])
    
    market_obs = obs.get('market', {})
    prices = market_obs.get('prices', {})
    
    private_obs = obs.get('private', {})
    shed = private_obs.get('shed', {})
    seeds = private_obs.get('seeds', {})
    
    day = obs.get('day', 0)
    hour = obs.get('hour', 0)
    step = day * 24 + hour
    
    market_orders = []
    
    # 1. Market Orders: Land Expansion
    quad_count = len(unlocked_quads)
    if quad_count < 4:
        next_cost = LAND_COSTS[quad_count - 1]
        if money >= next_cost + 200:
            market_orders.append(["BUY_LAND"])
            money -= next_cost

    # 2. Market Orders: Sell Shed Produce
    for item, qty in shed.items():
        if qty > 0 and item in prices:
            base_price = COMMODITIES.get(item, {}).get('base_price', 25)
            # Sell if price is good (>= base) or near season end (day >= 28)
            if prices[item] >= base_price * 0.95 or day >= 28:
                market_orders.append(["SELL", item, qty])

    # 3. Market Orders: Buy Seeds
    total_seeds = sum(seeds.values())
    if total_seeds < 5 and money >= 20:
        # Choose crop based on season phase
        if day < 10:
            crop = 'WHEAT' if step % 2 == 0 else 'CARROT'
        elif day < 24:
            crop = 'TOMATO' if money > 150 else 'CARROT'
        else:
            crop = 'WHEAT' # Fast late-season crop
            
        cost = COMMODITIES.get(crop, {}).get('seed_cost', 10)
        if money >= cost:
            market_orders.append(["BUY_SEED", crop, 2])
            money -= cost * 2

    # 4. Farmer Action Selection
    fx, fy = farmer_pos[0], farmer_pos[1]
    current_tile = None
    if 0 <= fy < len(tiles) and 0 <= fx < len(tiles[fy]):
        current_tile = tiles[fy][fx]

    farmer_action = ["PASS"]

    # Action priority on current tile
    if current_tile is not None and isinstance(current_tile, dict):
        kind = current_tile.get('kind')
        if kind == 'WEED':
            farmer_action = ["DIG"]
        elif kind == 'PLANT':
            yield_units = current_tile.get('yield_units', 0)
            watered = current_tile.get('watered_today', False)
            if yield_units > 0:
                farmer_action = ["HARVEST"]
            elif not watered:
                farmer_action = ["WATER"]
    elif current_tile is None: # Empty unlocked tile
        # Try to plant seed
        available_crops = [c for c, q in seeds.items() if q > 0]
        if available_crops:
            crop_to_plant = available_crops[0]
            farmer_action = ["PLANT", crop_to_plant]

    # If no action on current tile, move towards work
    if farmer_action == ["PASS"]:
        move_dir = get_best_move(fx, fy, tiles, seeds)
        if move_dir:
            farmer_action = [move_dir]

    # 5. Hired Hands Actions
    hands_actions = [["PASS"] for _ in hands_pos]

    return {
        "farmer": farmer_action,
        "hands": hands_actions,
        "market": market_orders
    }

def get_best_move(fx, fy, tiles, seeds):
    """
    Finds shortest path direction (NORTH, SOUTH, EAST, WEST) to nearest actionable tile.
    """
    if not tiles:
        return None

    rows = len(tiles)
    cols = len(tiles[0]) if rows > 0 else 0

    queue = collections.deque([(fx, fy, [])])
    visited = {(fx, fy)}

    directions = [
        (0, -1, "NORTH"),
        (0, 1, "SOUTH"),
        (1, 0, "EAST"),
        (-1, 0, "WEST")
    ]

    while queue:
        cx, cy, path = queue.popleft()
        if len(path) > 10: # Path limit
            break

        # Check if tile needs action
        if 0 <= cy < rows and 0 <= cx < cols:
            t = tiles[cy][cx]
            if t != "LOCKED":
                if (cx, cy) != (fx, fy):
                    if t is None and sum(seeds.values()) > 0: # Empty tile to plant
                        return path[0]
                    elif isinstance(t, dict):
                        if t.get('kind') == 'WEED' or t.get('yield_units', 0) > 0 or not t.get('watered_today', True):
                            return path[0]

        for dx, dy, move in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= ny < rows and 0 <= nx < cols and (nx, ny) not in visited:
                if tiles[ny][nx] != "LOCKED":
                    visited.add((nx, ny))
                    queue.append((nx, ny, path + [move]))

    return None

def my_agent(observation, configuration=None):
    return agent(observation, configuration)
