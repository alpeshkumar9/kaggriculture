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
    reserved = set()
    actions = [
        _choose_worker_action(position, tiles, seed_budget, day, reserved)
        for position in workers
    ]

    return {
        "farmer": actions[0] if actions else ["PASS"],
        "hands": actions[1:],
        "market": _market_actions(farm, private, day, tiles),
    }


def _pass_action():
    return {"farmer": ["PASS"], "hands": [], "market": []}


def _market_actions(farm, private, day, tiles):
    money = float(farm.get("money", 0))
    market = []

    # Realise proceeds before committing money to the next planting round.
    for item, quantity in private.get("shed", {}).items():
        if quantity > 0:
            market.append(["SELL", item, quantity])

    # Six helpers cost twenty coins per day (1 + 1 + 2 + 3 + 5 + 8), leaving
    # enough labour to water a full expanded field and clear spawned weeds.
    hires_today = int(farm.get("hires_today", 0))
    for _ in range(max(0, HANDS_PER_DAY - hires_today)):
        market.append(["HIRE"])

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


def _choose_worker_action(position, tiles, seed_budget, day, reserved):
    x, y = position
    if not _in_bounds(x, y, tiles):
        return ["PASS"]

    tile = tiles[y][x]
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
