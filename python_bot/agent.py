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
    "TOMATO": {"cost": 50, "ongoing": True},
    "STRAWBERRY": {"cost": 100, "ongoing": True},
}
HANDS_PER_DAY = 7
SEED_BUFFER = 10
# The fourth quadrant costs $4k with too little remaining season to recover
# its labour and weed-management cost.  The proven high-output replay uses
# three quadrants, so expansion stops after NE and SW.
LAND_PLAN = ((7, 1800), (14, 3300))
MOVES = ((0, -1, "NORTH"), (0, 1, "SOUTH"), (1, 0, "EAST"), (-1, 0, "WEST"))
PRODUCTS = {"WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"}
EARLY_COW_TARGET = 0
STRAWBERRY_TARGET = 8
TOMATO_TARGET = 12
SHED_CAPACITY = 100
FINAL_LIQUIDATION_DAY = 28
BASE_PRICES = {
    "WHEAT": 25,
    "CARROT": 35,
    "TOMATO": 60,
    "STRAWBERRY": 120,
    "MELON": 250,
    "EGG": 50,
    "MILK": 160,
    "WOOL": 200,
    "FERTILIZER": 100,
}
PREMIUM_PRODUCTS = {"STRAWBERRY", "MELON", "MILK", "WOOL"}


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
        "market": _market_actions(farm, private, day, tiles, livestock, obs.get("market", {})),
    }


def _pass_action():
    return {"farmer": ["PASS"], "hands": [], "market": []}


def _market_actions(farm, private, day, tiles, livestock, market_state):
    money = float(farm.get("money", 0))
    market = []

    # Premium markets punish a large glut.  Sell only when the visible price
    # has recovered to at least base, except when capacity or season-end makes
    # holding stock unsafe.  Small tranches let town consumption rebuild price
    # between calls instead of collapsing it with one shed-wide dump.
    market.extend(_sell_orders(private, day, market_state, livestock["owned_cows"])[:3])

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

    # Livestock is only a worthwhile capital investment if placed animals can
    # be fed through the construction phase.  Buy a small wheat reserve before
    # the first cow can become hungry instead of relying on a crop that has not
    # matured yet.
    wheat_on_hand = int(private.get("shed", {}).get("WHEAT", 0)) + sum(
        int(inventory.get("WHEAT", 0)) for inventory in private.get("inventories", [])
    )
    protected_cows = livestock["owned_cows"] + cows_to_buy
    wheat_needed = max(0, protected_cows * 3 - wheat_on_hand)
    if day <= 3 and wheat_needed and money >= wheat_needed * BASE_PRICES["WHEAT"]:
        market.append(["BUY_PRODUCT", "WHEAT", wheat_needed])
        money -= wheat_needed * BASE_PRICES["WHEAT"]

    unlocked = len(farm.get("unlocked_quadrants", ["NW"]))
    if unlocked <= len(LAND_PLAN):
        unlock_day, cash_threshold = LAND_PLAN[unlocked - 1]
        if day >= unlock_day and money >= cash_threshold:
            market.append(["BUY_LAND"])
            money -= (1000, 2000, 4000)[unlocked - 1]

    open_tiles = sum(tile is None for row in tiles for tile in row)
    crop = _next_crop(private.get("seeds", {}), private.get("shed", {}), day, tiles)
    target_seed_count = {
        "STRAWBERRY": STRAWBERRY_TARGET,
        "TOMATO": TOMATO_TARGET,
    }.get(crop, SEED_BUFFER)
    crop_seed_count = int(private.get("seeds", {}).get(crop, 0))
    if crop_seed_count < min(open_tiles, target_seed_count) and money >= CROPS["WHEAT"]["cost"]:
        quantity = min(12, max(1, min(open_tiles, target_seed_count) - crop_seed_count), int(money // CROPS[crop]["cost"]))
        if quantity:
            market.append(["BUY_SEED", crop, quantity])

    return market[:10]


def _next_crop(seeds, shed, day, tiles):
    """Choose the highest-value crop whose production window still fits."""
    strawberries = sum(
        isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "STRAWBERRY"
        for row in tiles for tile in row
    )
    # A small late block captures high strawberry scarcity prices without
    # flooding its extremely glut-sensitive market.
    if 10 <= day <= 16 and strawberries < STRAWBERRY_TARGET:
        return "STRAWBERRY"
    tomatoes = sum(
        isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "TOMATO"
        for row in tiles for tile in row
    )
    # Tomatoes are the dense middle-season loop: daily production after their
    # seven-day setup, with a much gentler glut curve than strawberries.
    if 4 <= day <= 21 and tomatoes < TOMATO_TARGET:
        return "TOMATO"
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
        x, y, tile, inventory, tiles, private, livestock, reserved, day,
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
    crop_data = CROPS.get(crop, {})
    if crop_data.get("ongoing") and tile.get("yield_units", 0) > 0:
        return ["HARVEST"]
    harvest_day = crop_data.get("harvest_day")
    if harvest_day is not None and day - int(tile.get("planted_day", day)) >= harvest_day:
        return ["HARVEST"]
    if not tile.get("watered_today", False):
        return ["WATER"]
    return None


def _available_crop(seed_budget, day):
    available = [crop for crop in CROPS if seed_budget.get(crop, 0) > 0]
    if not available:
        return None
    if 10 <= day <= 16 and seed_budget.get("STRAWBERRY", 0) > 0:
        return "STRAWBERRY"
    if 4 <= day <= 21 and seed_budget.get("TOMATO", 0) > 0:
        return "TOMATO"
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
        # Clearing a weed immediately protects the small worker budget from
        # accumulating a permanent traversal and planting bottleneck.
        return -1
    if tile.get("kind") != "PLANT":
        return None
    crop = tile.get("crop")
    crop_data = CROPS.get(crop, {})
    if crop_data.get("ongoing") and tile.get("yield_units", 0) > 0:
        return 0
    harvest_day = crop_data.get("harvest_day")
    if harvest_day is not None and day - int(tile.get("planted_day", day)) >= harvest_day:
        return 0
    return 1 if not tile.get("watered_today", False) else None


def _in_bounds(x, y, tiles):
    return 0 <= y < len(tiles) and 0 <= x < len(tiles[y])


def _sell_orders(private, day, market_state, owned_cows=0):
    """Return market-aware sales while preserving shed and livestock reserves."""
    shed = private.get("shed", {})
    prices = market_state.get("prices", {}) if isinstance(market_state, dict) else {}
    product_stock = {
        item: int(quantity)
        for item, quantity in shed.items()
        if item in PRODUCTS and quantity > 0
    }
    total_stock = sum(max(0, int(quantity)) for quantity in shed.values())
    overflow = max(0, total_stock - SHED_CAPACITY + 12)
    orders = []

    for item, quantity in sorted(product_stock.items(), key=lambda entry: entry[1], reverse=True):
        # Wheat is operating inventory, not sale inventory, while cows exist.
        # Three feed-days cover a placement delay and a missed route without
        # leaving an animal exposed to the two-day escape rule.
        if item == "WHEAT" and day < FINAL_LIQUIDATION_DAY:
            quantity = max(0, quantity - owned_cows * 3)
            if quantity == 0:
                continue
        base_price = BASE_PRICES[item]
        quoted_price = float(prices.get(item, base_price))
        price_is_healthy = quoted_price >= base_price
        if day >= FINAL_LIQUIDATION_DAY:
            sell_quantity = quantity
        elif price_is_healthy:
            sell_quantity = min(quantity, 8 if item in PREMIUM_PRODUCTS else 20)
        else:
            # Release only enough low-priced stock to prevent losing a future
            # harvest to the 100-item shed cap.
            sell_quantity = min(quantity, overflow)
        if sell_quantity:
            orders.append(["SELL", item, sell_quantity])
            overflow = max(0, overflow - sell_quantity)
    return orders


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


def _livestock_action(x, y, tile, inventory, tiles, private, livestock, reserved, day):
    """Run cow logistics before non-essential crop work.

    Cows must be fed and cared for daily.  Workers carry wheat from the shed,
    then feed and care on consecutive turns.  A worker carrying a cow builds
    its own pasture on the first empty tile it reaches, avoiding a separate
    fragile construction schedule.
    """
    carrying_cow = inventory.get("COW", 0) > 0
    carrying_wheat = inventory.get("WHEAT", 0) > 0
    carrying_fertilizer = inventory.get("FERTILIZER", 0) > 0
    at_shed = _is_shed_access(x, y, len(tiles))

    if isinstance(tile, dict) and tile.get("animal") == "COW":
        # A cow can receive only one useful worker action per turn.  Reserving
        # the tile prevents every nearby hand from feeding the same animal and
        # wasting the entire wheat reserve while other cows go hungry.
        if (x, y) in reserved:
            return None
        if not tile.get("fed_today", False):
            if carrying_wheat:
                reserved.add((x, y))
                return ["FEED"]
            return _move_to(x, y, tiles, _shed_targets(len(tiles)), reserved)
        if not tile.get("cared_today", False):
            reserved.add((x, y))
            return ["CARE"]
        if _should_collect_fertilizer(private, tiles, day):
            reserved.add((x, y))
            return ["COLLECT_FERTILIZER"]
        if tile.get("yield_units", 0) > 0:
            reserved.add((x, y))
            return ["HARVEST"]

    if carrying_fertilizer:
        fertilizable = [
            (target_x, target_y)
            for target_y, row in enumerate(tiles)
            for target_x, target in enumerate(row)
            if isinstance(target, dict)
            and target.get("kind") == "PLANT"
            and target.get("crop") == "STRAWBERRY"
            and int(target.get("fertilized_until_day", -1)) < day
        ]
        if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "STRAWBERRY":
            if int(tile.get("fertilized_until_day", -1)) < day:
                return ["FERTILIZE"]
        if fertilizable:
            return _move_to(x, y, tiles, fertilizable, reserved)

    if carrying_cow:
        if tile is None:
            return ["BUILD_PASTURE"]
        if isinstance(tile, dict) and tile.get("kind") == "PASTURE" and "animal" not in tile:
            return ["PLACE", "COW"]
        return _move_to_empty(x, y, tiles, reserved)

    if livestock["unfed"]:
        if at_shed and not carrying_wheat and private.get("shed", {}).get("WHEAT", 0) > 0:
            return ["PICKUP", "WHEAT", 1]
        if carrying_wheat:
            return _move_to(x, y, tiles, livestock["unfed"], reserved)
        return _move_to(x, y, tiles, _shed_targets(len(tiles)), reserved)
    if at_shed and private.get("shed", {}).get("COW", 0) > 0:
        return ["PICKUP", "COW", 1]
    return None


def _should_collect_fertilizer(private, tiles, day):
    """Keep at most one fertilizer delivery in flight.

    Four cared-for cows can produce fertilizer faster than the field can use
    it.  Sending every worker on a delivery starves watering and creates more
    weeds than the yield bonus repays.  A single delivery preserves the core
    farm loop while still refreshing one strawberry block every few days.
    """
    if not 15 <= day <= 18:
        return False
    if any(inventory.get("FERTILIZER", 0) > 0 for inventory in private.get("inventories", [])):
        return False
    return any(
        isinstance(tile, dict)
        and tile.get("kind") == "PLANT"
        and tile.get("crop") == "STRAWBERRY"
        and int(tile.get("fertilized_until_day", -1)) < day
        for row in tiles
        for tile in row
    )


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
