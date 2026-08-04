"""
Official Kaggle Kaggriculture Competition Submission Bot - Phase 2 Engine
Fully compliant with Kaggle Environments kaggriculture simulation engine.
"""

import collections

try:
    from strategy_rules import (
        COMMODITIES, LAND_QUADRANT_COSTS as LAND_COSTS,
        get_seasonal_crop_choice, get_fibonacci_hire_cost,
        should_hire_farmhand, calculate_market_sell_quantity,
        get_adversarial_crop_choice, should_undercut_market
    )
except ImportError:
    # Standalone Fallback for single-file Kaggle submission
    COMMODITIES = {
        'WHEAT': {'seed_cost': 10, 'base_price': 25, 'first_yield_days': 2},
        'CARROT': {'seed_cost': 20, 'base_price': 35, 'first_yield_days': 2},
        'TOMATO': {'seed_cost': 50, 'base_price': 60, 'first_yield_days': 7},
        'STRAWBERRY': {'seed_cost': 100, 'base_price': 120, 'first_yield_days': 10},
        'MELON': {'seed_cost': 80, 'base_price': 250, 'first_yield_days': 10},
        'EGG': {'base_price': 50},
        'MILK': {'base_price': 160},
        'WOOL': {'base_price': 200},
        'FERTILIZER': {'base_price': 100}
    }
    LAND_COSTS = [1000, 2000, 4000]

    def get_seasonal_crop_choice(day, money, quad_count=1, step=0):
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

    def get_fibonacci_hire_cost(hires_today, mult=1):
        fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        idx = min(hires_today, len(fib) - 1)
        return mult * fib[idx]

    def should_hire_farmhand(workload_count, money, hires_today, mult=1):
        cost = get_fibonacci_hire_cost(hires_today, mult)
        needed = (1 + hires_today) * 5
        return workload_count >= needed and money >= cost + 100

    def calculate_market_sell_quantity(item, qty, current_price, base_price, day, shed_total=0):
        if qty <= 0:
            return 0
        if day >= 24 or shed_total >= 50:
            return qty
        if current_price >= base_price * 0.85:
            return qty
        return min(qty, 2)


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
    hires_today = me.get('hires_today', 0)
    
    market_obs = obs.get('market', {})
    prices = market_obs.get('prices', {})
    inv_market = market_obs.get('inventory', {})
    
    private_obs = obs.get('private', {})
    shed = private_obs.get('shed', {})
    seeds = private_obs.get('seeds', {})
    
    day = obs.get('day', 0)
    hour = obs.get('hour', 0)
    step = day * 24 + hour
    
    market_orders = []
    
    # Calculate farm workload across entire unlocked grid
    workload = 0
    rows = len(tiles)
    cols = len(tiles[0]) if rows > 0 else 0
    empty_unlocked_tiles = 0
    for r in range(rows):
        for c in range(cols):
            t = tiles[r][c]
            if t != "LOCKED":
                if t is None:
                    empty_unlocked_tiles += 1
                elif isinstance(t, dict):
                    if t.get('kind') == 'WEED' or t.get('yield_units', 0) > 0 or not t.get('watered_today', True) or not t.get('fed_today', True):
                        workload += 1

    opp_id = 1 - player_id
    opp_farm = farms[opp_id] if opp_id < len(farms) else {}
    opp_tiles = opp_farm.get('tiles', [])
    town_shops = obs.get('town', {}).get('unlocked_shops', [])

    # 1. Market Orders: Land Expansion (Quadrants 2 & 3: $1,000, $2,000)
    quad_count = len(unlocked_quads)
    if quad_count < 3:
        thresholds = [1200, 2400]
        thresh = thresholds[quad_count - 1]
        next_cost = LAND_COSTS[quad_count - 1]
        if money >= thresh and len(market_orders) < 10:
            market_orders.append(["BUY_LAND"])
            money -= next_cost

    # 2. Market Orders: Workload-based Farmhand Scaling
    if hires_today < 5 and len(market_orders) < 10:
        if should_hire_farmhand(workload + empty_unlocked_tiles, money, hires_today):
            hire_cost = get_fibonacci_hire_cost(hires_today)
            market_orders.append(["HIRE"])
            money -= hire_cost
            hires_today += 1

    # 3. Market Orders: Fertilizer Stocking for Premium Crops
    fertilizer_qty = shed.get('FERTILIZER', 0)
    if fertilizer_qty < 3 and money >= 200 and day < 24 and len(market_orders) < 10:
        market_orders.append(["BUY_PRODUCT", "FERTILIZER", 2])
        money -= 200

    # 4. Market Orders: Shed Liquidation & Continuous Selling
    shed_total = sum(shed.values())
    for item, qty in shed.items():
        if qty > 0 and len(market_orders) < 10:
            current_price = prices.get(item, COMMODITIES.get(item, {}).get('base_price', 25))
            base_price = COMMODITIES.get(item, {}).get('base_price', 25)

            sell_qty = calculate_market_sell_quantity(item, qty, current_price, base_price, day, shed_total)
            if sell_qty > 0:
                market_orders.append(["SELL", item, sell_qty])

    # 5. Market Orders: Dynamic Seed Buying
    total_seeds = sum(seeds.values())
    if total_seeds < (empty_unlocked_tiles + 4) and money >= 20 and day < 28 and len(market_orders) < 10:
        if 'get_adversarial_crop_choice' in globals() or 'get_adversarial_crop_choice' in locals():
            crop_choice = get_adversarial_crop_choice(day, money, quad_count, step, opp_tiles, town_shops)
        else:
            crop_choice = get_seasonal_crop_choice(day, money, quad_count, step)

        if crop_choice:
            cost = COMMODITIES.get(crop_choice, {}).get('seed_cost', 10)
            buy_qty = min(8, max(2, int(money // cost)))
            if buy_qty > 0 and money >= cost * buy_qty:
                market_orders.append(["BUY_SEED", crop_choice, buy_qty])
                money -= cost * buy_qty

    # 6. Worker Actions (Farmer & Hired Farmhands)
    all_workers = [farmer_pos] + list(hands_pos)
    reserved_targets = set()
    worker_actions = []

    for idx, (w_x, w_y) in enumerate(all_workers):
        current_tile = tiles[w_y][w_x] if (0 <= w_y < rows and 0 <= w_x < cols) else None
        act = ["PASS"]

        # Action on current standing tile
        if current_tile is not None and isinstance(current_tile, dict):
            kind = current_tile.get('kind')
            if kind == 'WEED':
                act = ["DIG"]
            elif kind == 'PLANT':
                yield_units = current_tile.get('yield_units', 0)
                watered = current_tile.get('watered_today', False)
                fertilized = current_tile.get('fertilized_until_day', -1) >= day
                if yield_units > 0:
                    act = ["HARVEST"]
                elif not watered:
                    act = ["WATER"]
                elif not fertilized and shed.get('FERTILIZER', 0) > 0 and current_tile.get('crop') in ['TOMATO', 'STRAWBERRY', 'MELON']:
                    act = ["FERTILIZE"]

        elif current_tile is None: # Empty unlocked tile -> PLANT seed if available
            available_crops = [c for c, q in seeds.items() if q > 0]
            if available_crops:
                act = ["PLANT", available_crops[0]]

        # If no immediate action on current tile, BFS pathfind across entire unlocked grid
        if act == ["PASS"]:
            move_dir, target_coords = get_best_move(w_x, w_y, tiles, seeds, reserved_targets)
            if move_dir:
                act = [move_dir]
                if target_coords:
                    reserved_targets.add(target_coords)

        worker_actions.append(act)

    farmer_action = worker_actions[0] if worker_actions else ["PASS"]
    hands_actions = worker_actions[1:] if len(worker_actions) > 1 else []

    return {
        "farmer": farmer_action,
        "hands": hands_actions,
        "market": market_orders
    }


def get_best_move(fx, fy, tiles, seeds, reserved_targets=None):
    """
    Full-Grid BFS Pathfinder:
    Calculates shortest path direction (NORTH, SOUTH, EAST, WEST) across all unlocked tiles.
    """
    if not tiles:
        return None, None

    if reserved_targets is None:
        reserved_targets = set()

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
        if len(path) > 20: # Path depth limit
            break

        # Check tile for actionable work across entire unlocked grid
        t = tiles[cy][cx]
        if t != "LOCKED" and (cx, cy) not in reserved_targets:
            if (cx, cy) != (fx, fy):
                if t is None and sum(seeds.values()) > 0:
                    return path[0], (cx, cy)
                elif isinstance(t, dict):
                    kind = t.get('kind')
                    if kind == 'WEED' or t.get('yield_units', 0) > 0 or not t.get('watered_today', True) or not t.get('fed_today', True):
                        return path[0], (cx, cy)

        for dx, dy, move in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= ny < rows and 0 <= nx < cols and (nx, ny) not in visited:
                if tiles[ny][nx] != "LOCKED":
                    visited.add((nx, ny))
                    queue.append((nx, ny, path + [move]))

    return None, None


def my_agent(observation, configuration=None):
    return agent(observation, configuration)

