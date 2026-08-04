"""A reliable, crop-first Kaggriculture submission agent.

The agent deliberately earns from a repeatable crop loop before attempting
expansion: hire affordable daily labour, plant only available seeds, water
every crop, harvest only at the crop's best one-time yield day, and sell all
stored produce.  This keeps the public ``agent`` entry point self-contained
for direct Kaggle uploads.
"""

from collections import deque


CROPS = {
    "WHEAT": {"cost": 10, "harvest_day": 4},
    "CARROT": {"cost": 20, "harvest_day": 3},
}
HANDS_PER_DAY = 6
SEED_BUFFER = 10
LAND_PLAN = ((7, 1800), (14, 3300), (20, 7000))
MOVES = ((0, -1, "NORTH"), (0, 1, "SOUTH"), (1, 0, "EAST"), (-1, 0, "WEST"))
PRODUCTS = {"WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"}
EARLY_COW_TARGET = 4


def agent(observation, configuration=None):
    """Return legal worker and market actions for one Kaggriculture turn."""
    obs = observation if isinstance(observation, dict) else getattr(observation, "__dict__", {})
    farms = obs.get("farms", [])
    player = obs.get("player", 0)
    if player >= len(farms):
        return _pass_action()

    farm = farms[player]
    tiles = farm.get("tiles", [])
    if not tiles:
        return _pass_action()

    private = obs.get("private", {}) or {}
    day = int(obs.get("day", 0))
    workers = [farm.get("farmer", [0, 0]), *farm.get("hands", [])]
    seed_budget = dict(private.get("seeds", {}))
    inventories = private.get("inventories", [])
    livestock = _livestock_state(tiles, private, day)
    reserved = set()
    actions = [
        _choose_worker_action(
            position, tiles, seed_budget, day, reserved,
            inventories[index] if index < len(inventories) else {}, private, livestock,
        )
        for index, position in enumerate(workers)
    ]

    return {
        "farmer": actions[0] if actions else ["PASS"],
        "hands": actions[1:],
        "market": _market_actions(farm, private, day, tiles, livestock),
    }


def _pass_action():
    return {"farmer": ["PASS"], "hands": [], "market": []}


def _market_actions(farm, private, day, tiles, livestock):
    money = float(farm.get("money", 0))
    market = []

    # Realise proceeds before committing money to the next planting round.
    for item, quantity in private.get("shed", {}).items():
        if item in PRODUCTS and quantity > 0:
            market.append(["SELL", item, quantity])

    # Six helpers cost twenty coins per day (1 + 1 + 2 + 3 + 5 + 8), leaving
    # enough labour to water a full expanded field and clear spawned weeds.
    hires_today = int(farm.get("hires_today", 0))
    for _ in range(max(0, HANDS_PER_DAY - hires_today)):
        market.append(["HIRE"])

    # Milk is the first scalable premium revenue stream.  Four cows keep the
    # operational burden bounded while giving the crop engine time to fund
    # further expansion.
    cows_to_buy = max(0, EARLY_COW_TARGET - livestock["owned_cows"])
    if day <= 2 and cows_to_buy and money >= 400 * cows_to_buy + 500:
        market.append(["BUY_ANIMAL", "COW", cows_to_buy])
        money -= 400 * cows_to_buy

    unlocked = len(farm.get("unlocked_quadrants", ["NW"]))
    if unlocked <= len(LAND_PLAN):
        unlock_day, cash_threshold = LAND_PLAN[unlocked - 1]
        if day >= unlock_day and money >= cash_threshold:
            market.append(["BUY_LAND"])
            money -= (1000, 2000, 4000)[unlocked - 1]

    seed_count = sum(int(quantity) for quantity in private.get("seeds", {}).values())
    open_tiles = sum(tile is None for row in tiles for tile in row)
    if seed_count < min(open_tiles, SEED_BUFFER) and money >= CROPS["WHEAT"]["cost"]:
        crop = _next_crop(private.get("seeds", {}), private.get("shed", {}), day)
        quantity = min(12, max(1, min(open_tiles, SEED_BUFFER) - seed_count), int(money // CROPS[crop]["cost"]))
        if quantity:
            market.append(["BUY_SEED", crop, quantity])

    return market[:10]


def _next_crop(seeds, shed, day):
    """Mix staple crops so one market glut cannot erase the whole harvest."""
    wheat = int(seeds.get("WHEAT", 0)) + int(shed.get("WHEAT", 0))
    carrots = int(seeds.get("CARROT", 0)) + int(shed.get("CARROT", 0))
    if day >= 26:
        return "CARROT" if day <= 27 else "WHEAT"
    return "CARROT" if carrots <= wheat else "WHEAT"


def _choose_worker_action(position, tiles, seed_budget, day, reserved, inventory, private, livestock):
    x, y = position
    if not _in_bounds(x, y, tiles):
        return ["PASS"]

    tile = tiles[y][x]
    livestock_action = _livestock_action(
        x, y, tile, inventory, tiles, private, livestock, reserved,
    )
    if livestock_action:
        return livestock_action
    action = _action_for_tile(tile, seed_budget, day)
    if tile is None:
        urgent_target = _nearest_target(x, y, tiles, seed_budget, day, reserved, urgent_only=True)
        if urgent_target is not None:
            direction, coordinates = urgent_target
            reserved.add(coordinates)
            return [direction]
    if action:
        if action[0] == "PLANT":
            seed_budget[action[1]] -= 1
        reserved.add((x, y))
        return action

    target = _nearest_target(x, y, tiles, seed_budget, day, reserved)
    if target is None:
        return ["PASS"]
    direction, coordinates = target
    reserved.add(coordinates)
    return [direction]


def _action_for_tile(tile, seed_budget, day):
    if tile is None:
        crop = _available_crop(seed_budget, day)
        return ["PLANT", crop] if crop else None
    if not isinstance(tile, dict):
        return None
    if tile.get("kind") == "WEED":
        return ["DIG"]
    if tile.get("kind") != "PLANT":
        return None

    crop = tile.get("crop")
    harvest_day = CROPS.get(crop, {}).get("harvest_day")
    if harvest_day is not None and day - int(tile.get("planted_day", day)) >= harvest_day:
        return ["HARVEST"]
    if not tile.get("watered_today", False):
        return ["WATER"]
    return None


def _available_crop(seed_budget, day):
    available = [crop for crop in CROPS if seed_budget.get(crop, 0) > 0]
    if not available:
        return None
    if day >= 26 and seed_budget.get("CARROT", 0) > 0:
        return "CARROT"
    return min(available, key=lambda crop: -seed_budget[crop])


def _nearest_target(start_x, start_y, tiles, seed_budget, day, reserved, urgent_only=False):
    queue = deque([(start_x, start_y, None)])
    visited = {(start_x, start_y)}
    candidates = {}
    while queue:
        x, y, first_move = queue.popleft()
        if (x, y) != (start_x, start_y) and (x, y) not in reserved:
            priority = _target_priority(tiles[y][x], seed_budget, day)
            if priority is not None and (not urgent_only or priority < 3):
                candidates.setdefault(priority, (first_move, (x, y)))
        for dx, dy, move in MOVES:
            next_x, next_y = x + dx, y + dy
            if not _in_bounds(next_x, next_y, tiles) or (next_x, next_y) in visited:
                continue
            if tiles[next_y][next_x] == "LOCKED":
                continue
            visited.add((next_x, next_y))
            queue.append((next_x, next_y, first_move or move))
    return candidates[min(candidates)] if candidates else None


def _target_priority(tile, seed_budget, day):
    """Smaller values are assigned first across the whole farm."""
    if tile is None:
        return 3 if _available_crop(seed_budget, day) else None
    if not isinstance(tile, dict):
        return None
    if tile.get("kind") == "WEED":
        return 2
    if tile.get("kind") != "PLANT":
        return None
    crop = tile.get("crop")
    harvest_day = CROPS.get(crop, {}).get("harvest_day")
    if harvest_day is not None and day - int(tile.get("planted_day", day)) >= harvest_day:
        return 0
    return 1 if not tile.get("watered_today", False) else None


def _in_bounds(x, y, tiles):
    return 0 <= y < len(tiles) and 0 <= x < len(tiles[y])


def _livestock_state(tiles, private, day):
    cows = []
    for y, row in enumerate(tiles):
        for x, tile in enumerate(row):
            if isinstance(tile, dict) and tile.get("animal") == "COW":
                cows.append((x, y, tile))
    shed_cows = int(private.get("shed", {}).get("COW", 0))
    carried_cows = sum(int(inventory.get("COW", 0)) for inventory in private.get("inventories", []))
    return {
        "cows": cows,
        "owned_cows": len(cows) + shed_cows + carried_cows,
        "unfed": [(x, y) for x, y, tile in cows if not tile.get("fed_today", False)],
    }


def _livestock_action(x, y, tile, inventory, tiles, private, livestock, reserved):
    """Run cow logistics before non-essential crop work.

    Cows must be fed and cared for daily.  Workers carry wheat from the shed,
    then feed and care on consecutive turns.  A worker carrying a cow builds
    its own pasture on the first empty tile it reaches, avoiding a separate
    fragile construction schedule.
    """
    carrying_cow = inventory.get("COW", 0) > 0
    carrying_wheat = inventory.get("WHEAT", 0) > 0
    at_shed = _is_shed_access(x, y, len(tiles))

    if isinstance(tile, dict) and tile.get("animal") == "COW":
        if not tile.get("fed_today", False):
            if carrying_wheat:
                return ["FEED"]
            return _move_to(x, y, tiles, _shed_targets(len(tiles)), reserved)
        if not tile.get("cared_today", False):
            return ["CARE"]
        if tile.get("yield_units", 0) > 0:
            return ["HARVEST"]

    if carrying_cow:
        if tile is None:
            return ["BUILD_PASTURE"]
        if isinstance(tile, dict) and tile.get("kind") == "PASTURE" and "animal" not in tile:
            return ["PLACE", "COW"]
        return _move_to_empty(x, y, tiles, reserved)

    if at_shed and private.get("shed", {}).get("COW", 0) > 0:
        return ["PICKUP", "COW", 1]
    if livestock["unfed"]:
        if at_shed and not carrying_wheat and private.get("shed", {}).get("WHEAT", 0) > 0:
            return ["PICKUP", "WHEAT", 2]
        if carrying_wheat:
            return _move_to(x, y, tiles, livestock["unfed"], reserved)
        return _move_to(x, y, tiles, _shed_targets(len(tiles)), reserved)
    return None


def _move_to_empty(x, y, tiles, reserved):
    targets = [
        (target_x, target_y)
        for target_y, row in enumerate(tiles)
        for target_x, tile in enumerate(row)
        if tile is None
    ]
    return _move_to(x, y, tiles, targets, reserved)


def _shed_targets(board_size):
    half = board_size // 2
    return ((half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half))


def _is_shed_access(x, y, board_size):
    return (x, y) in _shed_targets(board_size)


def _move_to(start_x, start_y, tiles, targets, reserved):
    targets = set(targets) - reserved
    if not targets:
        return None
    queue = deque([(start_x, start_y, None)])
    visited = {(start_x, start_y)}
    while queue:
        x, y, first_move = queue.popleft()
        if (x, y) in targets and (x, y) != (start_x, start_y):
            reserved.add((x, y))
            return [first_move]
        for dx, dy, move in MOVES:
            next_x, next_y = x + dx, y + dy
            if not _in_bounds(next_x, next_y, tiles) or (next_x, next_y) in visited:
                continue
            if tiles[next_y][next_x] == "LOCKED":
                continue
            visited.add((next_x, next_y))
            queue.append((next_x, next_y, first_move or move))
    return None
