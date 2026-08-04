"""A reliable, crop-first Kaggriculture submission agent.

The agent deliberately earns from a repeatable crop loop before attempting
expansion: hire affordable daily labour, plant only available seeds, water
every crop, harvest only at the crop's best one-time yield day, and sell all
stored produce.  This keeps the public ``agent`` entry point self-contained
for direct Kaggle uploads.
"""

from collections import deque


CROPS = {
    "WHEAT": {"cost": 10, "harvest_day": 4, "bonus_start": 2},
    "CARROT": {"cost": 20, "harvest_day": 3, "bonus_start": 2},
    "TOMATO": {"cost": 50, "ongoing": True},
    "STRAWBERRY": {"cost": 100, "ongoing": True},
    "MELON": {"cost": 80, "harvest_day": 12, "bonus_start": 6},
}
HANDS_PER_DAY = 13
HIRE_COSTS = (1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377)
SEED_BUFFER = 10
# The fourth quadrant costs $4k with too little remaining season to recover
# its labour and weed-management cost.  The proven high-output replay uses
# three quadrants, so expansion stops after NE and SW.
LAND_PLAN = ((4, 1600), (8, 3200))
MOVES = ((0, -1, "NORTH"), (0, 1, "SOUTH"), (1, 0, "EAST"), (-1, 0, "WEST"))
PRODUCTS = {"WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"}
COMPACT_COW_TARGET = 10
COWS_PER_SERVICE_WORKER = 5
FERTILIZER_BATCH_SIZE = 6
MAX_SELL_ORDER_TYPES = 5
STRAWBERRY_PRIORITY_DAY = 10
LAST_PLANTING_DAY = 28
EARLY_GOOSE_TARGET = 0
EARLY_SHEEP_TARGET = 0
LATE_SHEEP_TARGET = 0
STRAWBERRY_TARGET = 30
TOMATO_TARGET = 0
MELON_TARGET = 40
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
SELL_PRICE_MULTIPLIERS = {
    "WHEAT": 1.00,
    "CARROT": 1.00,
    "STRAWBERRY": 1.00,
    "MELON": 1.00,
}


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
    actions = []
    for index, position in enumerate(workers):
        actions.append(_choose_worker_action(
            position, tiles, seed_budget, day, reserved,
            inventories[index] if index < len(inventories) else {}, private, livestock,
            index, len(workers),
        ))

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

    # Establish the full workforce first. Purchases and sales can execute on
    # following turns, but a missed hire permanently loses useful actions.
    desired_hands = _desired_hands(tiles)
    if 19 <= day <= 25 and any(
        isinstance(tile, dict)
        and tile.get("crop") == "STRAWBERRY"
        and _strawberry_needs_fertilizer(tile, day)
        for row in tiles
        for tile in row
    ):
        desired_hands = min(HANDS_PER_DAY, desired_hands + 1)
    if day >= 29:
        desired_hands = min(HANDS_PER_DAY, desired_hands + 1)
    hires_today = int(farm.get("hires_today", 0))
    for hire_index in range(hires_today, desired_hands):
        hire_cost = HIRE_COSTS[hire_index]
        if money < hire_cost:
            break
        market.append(["HIRE"])
        money -= hire_cost

    # Premium markets punish a large glut.  Sell only when the visible price
    # has recovered to at least base, except when capacity or season-end makes
    # holding stock unsafe.  Small tranches let town consumption rebuild price
    # between calls instead of collapsing it with one shed-wide dump.
    sell_orders = _sell_orders(
        private, day, market_state, livestock["owned_animals"],
    )[:MAX_SELL_ORDER_TYPES]
    market.extend(sell_orders)

    # Milk is the first scalable premium revenue stream.  Four cows keep the
    # operational burden bounded while giving the crop engine time to fund
    # further expansion.
    unlocked_count = len(farm.get("unlocked_quadrants", ["NW"]))
    compact_cow_target = len(_compact_cow_slots(tiles))
    cows_to_buy = min(2, max(0, compact_cow_target - livestock["owned_cows"]))
    if day <= 20 and cows_to_buy and money >= 400 * cows_to_buy + 500:
        market.append(["BUY_ANIMAL", "COW", cows_to_buy])
        money -= 400 * cows_to_buy

    geese_to_buy = max(0, EARLY_GOOSE_TARGET - livestock["owned_geese"])
    if day <= 2 and geese_to_buy and money >= geese_to_buy * 300 + 700:
        market.append(["BUY_ANIMAL", "GOOSE", geese_to_buy])
        money -= geese_to_buy * 300

    early_sheep_to_buy = max(0, EARLY_SHEEP_TARGET - livestock["owned_sheep"])
    if day <= 2 and early_sheep_to_buy and money >= early_sheep_to_buy * 500 + 700:
        market.append(["BUY_ANIMAL", "SHEEP", early_sheep_to_buy])
        money -= early_sheep_to_buy * 500

    sheep_to_buy = max(0, LATE_SHEEP_TARGET - livestock["owned_sheep"])
    sheep_budget = sheep_to_buy * 500 + sheep_to_buy * BASE_PRICES["WHEAT"] * 3
    if 16 <= day <= 18 and sheep_to_buy and money >= sheep_budget + 500:
        market.append(["BUY_ANIMAL", "SHEEP", sheep_to_buy])
        money -= sheep_to_buy * 500

    # Livestock is only a worthwhile capital investment if placed animals can
    # be fed through the construction phase.  Buy a small wheat reserve before
    # the first cow can become hungry instead of relying on a crop that has not
    # matured yet.
    wheat_on_hand = int(private.get("shed", {}).get("WHEAT", 0)) + sum(
        int(inventory.get("WHEAT", 0)) for inventory in private.get("inventories", [])
    )
    protected_animals = (
        livestock["owned_animals"] + cows_to_buy
        + geese_to_buy + early_sheep_to_buy + sheep_to_buy
    )
    wheat_needed = max(0, protected_animals * 3 - wheat_on_hand)
    if protected_animals and wheat_needed and money >= wheat_needed * BASE_PRICES["WHEAT"]:
        market.append(["BUY_PRODUCT", "WHEAT", wheat_needed])
        money -= wheat_needed * BASE_PRICES["WHEAT"]

    if 19 <= day <= 25:
        fertilizer_in_flight = int(private.get("shed", {}).get("FERTILIZER", 0)) + sum(
            int(inventory.get("FERTILIZER", 0)) for inventory in private.get("inventories", [])
        )
        refresh_targets = sum(
            isinstance(tile, dict)
            and tile.get("kind") == "PLANT"
            and tile.get("crop") == "STRAWBERRY"
            and _strawberry_needs_fertilizer(tile, day)
            for row in tiles for tile in row
        )
        fertilizer_to_buy = min(10, max(0, refresh_targets - fertilizer_in_flight))
        if fertilizer_to_buy and money >= fertilizer_to_buy * BASE_PRICES["FERTILIZER"] + 200:
            market.append(["BUY_PRODUCT", "FERTILIZER", fertilizer_to_buy])
            money -= fertilizer_to_buy * BASE_PRICES["FERTILIZER"]

    unlocked = unlocked_count
    if unlocked <= len(LAND_PLAN):
        unlock_day, cash_threshold = LAND_PLAN[unlocked - 1]
        if day >= unlock_day and money >= cash_threshold:
            market.append(["BUY_LAND"])
            money -= (1000, 2000, 4000)[unlocked - 1]

    open_tiles = sum(tile is None for row in tiles for tile in row)
    crop = _next_crop(
        private.get("seeds", {}), private.get("shed", {}), day, tiles,
        market_state.get("prices", {}) if isinstance(market_state, dict) else {},
    )
    target_seed_count = {
        "STRAWBERRY": STRAWBERRY_TARGET,
        "TOMATO": TOMATO_TARGET,
        "MELON": MELON_TARGET,
    }.get(crop, SEED_BUFFER)
    crop_seed_count = int(private.get("seeds", {}).get(crop, 0))
    payroll_reserve = 0 if day >= FINAL_LIQUIDATION_DAY else sum(HIRE_COSTS[:desired_hands])
    spendable = max(0, money - payroll_reserve)
    if day < LAST_PLANTING_DAY and crop_seed_count < min(open_tiles, target_seed_count) and spendable >= CROPS[crop]["cost"]:
        quantity = min(
            12,
            max(1, min(open_tiles, target_seed_count) - crop_seed_count),
            int(spendable // CROPS[crop]["cost"]),
        )
        if quantity:
            market.append(["BUY_SEED", crop, quantity])

    return market[:10]


def _desired_hands(tiles):
    """Scale payroll to the field: one worker can service six nearby tiles."""
    workload = 0
    for row in tiles:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            workload += 3 if tile.get("animal") else tile.get("kind") in {"PLANT", "WEED"}
    total_workers = max(5, (workload + 5) // 6)
    return min(HANDS_PER_DAY, total_workers - 1)


def _next_crop(seeds, shed, day, tiles, prices=None):
    """Choose the highest-value crop whose production window still fits."""
    strawberries = sum(
        isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "STRAWBERRY"
        for row in tiles for tile in row
    )
    melons = sum(
        isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "MELON"
        for row in tiles for tile in row
    )
    # A small late block captures high strawberry scarcity prices without
    # flooding its extremely glut-sensitive market.
    if STRAWBERRY_PRIORITY_DAY <= day <= 16 and strawberries < STRAWBERRY_TARGET:
        return "STRAWBERRY"
    if 4 <= day <= 16 and melons < MELON_TARGET:
        return "MELON"
    tomatoes = sum(
        isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "TOMATO"
        for row in tiles for tile in row
    )
    # Tomatoes are the dense middle-season loop: daily production after their
    # seven-day setup, with a much gentler glut curve than strawberries.
    if 4 <= day <= 21 and tomatoes < TOMATO_TARGET:
        return "TOMATO"
    prices = prices or BASE_PRICES
    if day >= LAST_PLANTING_DAY:
        return "CARROT" if day <= 27 else "WHEAT"
    wheat_rate = (float(prices.get("WHEAT", 25)) * 4 - 10) / 4
    carrot_rate = (float(prices.get("CARROT", 35)) * 3 - 20) / 3
    return "WHEAT" if wheat_rate >= carrot_rate else "CARROT"


def _choose_worker_action(
    position, tiles, seed_budget, day, reserved, inventory, private, livestock,
    worker_index, worker_count,
):
    x, y = position
    if not _in_bounds(x, y, tiles):
        return ["PASS"]
    tile = tiles[y][x]
    # Melons fund the next production cycle. Move each six-unit harvest to the
    # shed immediately so it can be sold and reinvested before day 16 ends.
    carrying_products = any(inventory.get(item, 0) > 0 for item in PRODUCTS)
    carrying_non_melon = any(
        item != "MELON" and inventory.get(item, 0) > 0 for item in PRODUCTS
    )
    if (
        day == FINAL_LIQUIDATION_DAY
        and carrying_non_melon
        and isinstance(tile, dict)
        and (
            tile.get("kind") == "WEED"
            or (
                tile.get("kind") == "PLANT"
                and int(tile.get("yield_units", 0)) <= 0
                and 0 <= int(tile.get("max_lifespan_step", -1)) <= (day + 1) * 24
            )
        )
    ):
        reserved.add((x, y))
        return ["DIG"]
    if (
        (inventory.get("MELON", 0) > 0 and day <= 16)
        or (day == FINAL_LIQUIDATION_DAY and carrying_non_melon)
        or (day >= 29 and carrying_products)
    ):
        if _is_shed_access(x, y, len(tiles)):
            return ["DROP"]
        return _move_to(x, y, tiles, _shed_targets(len(tiles)), reserved) or ["PASS"]

    livestock_action = _livestock_action(
        x, y, tile, inventory, tiles, private, livestock, reserved, day,
        worker_index,
    )
    if livestock_action:
        return livestock_action
    # Keep the northwest shed-access cell clear for the first compact cow.
    # A stationary service lane avoids paying movement for five recurring
    # pickup/feed/care/collect actions every day.
    compact_cow_slots = set(_compact_cow_slots(tiles))
    action = (
        None
        if (x, y) in compact_cow_slots and tile is None
        else _action_for_tile(tile, seed_budget, day)
    )
    ripe_melons = sum(
        isinstance(target, dict)
        and target.get("crop") == "MELON"
        and day - int(target.get("planted_day", day)) >= CROPS["MELON"]["harvest_day"]
        for row in tiles
        for target in row
    )
    use_global_liquidation = day >= 29 and ripe_melons <= 8
    service_workers = (
        max(1, livestock["owned_animals"] // COWS_PER_SERVICE_WORKER)
        if livestock["owned_animals"] else 0
    )
    crop_worker_count = max(1, worker_count - service_workers)
    crop_worker_index = worker_index - service_workers
    region = (
        None
        if use_global_liquidation or crop_worker_index < 0
        else _worker_region(tiles, crop_worker_index, crop_worker_count)
    )
    if tile is None:
        urgent_target = _nearest_target(
            x, y, tiles, seed_budget, day, reserved, urgent_only=True,
            allowed=region,
        )
        if urgent_target is not None:
            direction, coordinates = urgent_target
            reserved.add(coordinates)
            return [direction]
    if action:
        if action[0] == "PLANT":
            seed_budget[action[1]] -= 1
        reserved.add((x, y))
        return action

    target = _nearest_target(x, y, tiles, seed_budget, day, reserved, allowed=region)
    if target is None:
        target = _nearest_target(
            x, y, tiles, seed_budget, day, reserved, urgent_only=True,
        )
    if target is None:
        return ["PASS"]
    direction, coordinates = target
    reserved.add(coordinates)
    return [direction]


def _action_for_tile(tile, seed_budget, day):
    if day >= 29:
        if isinstance(tile, dict) and tile.get("kind") == "PLANT":
            crop = tile.get("crop")
            if (
                crop == "MELON"
                and day - int(tile.get("planted_day", day)) >= CROPS["MELON"]["harvest_day"]
            ):
                return ["HARVEST"]
        return None
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
    if (
        day == FINAL_LIQUIDATION_DAY
        and 0 <= int(tile.get("max_lifespan_step", -1)) <= (day + 1) * 24
        and int(tile.get("yield_units", 0)) <= 0
    ):
        return ["DIG"]
    if crop_data.get("ongoing") and tile.get("yield_units", 0) > 0:
        return ["HARVEST"]
    if crop_data.get("ongoing") and _expires_by_next_day(tile, day):
        return ["DIG"]
    harvest_day = crop_data.get("harvest_day")
    if harvest_day is not None and day - int(tile.get("planted_day", day)) >= harvest_day:
        return ["HARVEST"]
    if _needs_water(tile, day):
        return ["WATER"]
    return None


def _available_crop(seed_budget, day):
    if day >= 26:
        return None
    available = [crop for crop in CROPS if seed_budget.get(crop, 0) > 0]
    if not available:
        return None
    if STRAWBERRY_PRIORITY_DAY <= day <= 16 and seed_budget.get("STRAWBERRY", 0) > 0:
        return "STRAWBERRY"
    if 4 <= day <= 16 and seed_budget.get("MELON", 0) > 0:
        return "MELON"
    if 4 <= day <= 21 and seed_budget.get("TOMATO", 0) > 0:
        return "TOMATO"
    if day >= 26 and seed_budget.get("CARROT", 0) > 0:
        return "CARROT"
    return min(available, key=lambda crop: -seed_budget[crop])


def _nearest_target(
    start_x, start_y, tiles, seed_budget, day, reserved, urgent_only=False,
    allowed=None,
):
    queue = deque([(start_x, start_y, None)])
    visited = {(start_x, start_y)}
    candidates = {}
    while queue:
        x, y, first_move = queue.popleft()
        if (
            (x, y) != (start_x, start_y)
            and (x, y) not in reserved
            and (allowed is None or (x, y) in allowed)
        ):
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


def _worker_region(tiles, worker_index, worker_count):
    """Assign each worker a stable contiguous segment of a snake traversal."""
    cells = []
    for y, row in enumerate(tiles):
        xs = range(len(row)) if y % 2 == 0 else range(len(row) - 1, -1, -1)
        cells.extend((x, y) for x in xs if row[x] != "LOCKED")
    if not cells:
        return set()
    chunk_size = (len(cells) + worker_count - 1) // worker_count
    start = worker_index * chunk_size
    return set(cells[start:start + chunk_size])


def _target_priority(tile, seed_budget, day):
    """Smaller values are assigned first across the whole farm."""
    if day >= 29:
        if isinstance(tile, dict) and tile.get("kind") == "PLANT":
            crop = tile.get("crop")
            if (
                crop == "MELON"
                and day - int(tile.get("planted_day", day)) >= CROPS["MELON"]["harvest_day"]
            ):
                return -10
        return None
    if tile is None:
        return 3 if _available_crop(seed_budget, day) else None
    if not isinstance(tile, dict):
        return None
    if tile.get("kind") == "WEED":
        # Clearing a weed immediately protects the small worker budget from
        # accumulating a permanent traversal and planting bottleneck.
        return -1 if day < FINAL_LIQUIDATION_DAY else 2
    if tile.get("kind") != "PLANT":
        return None
    crop = tile.get("crop")
    crop_data = CROPS.get(crop, {})
    if (
        day == FINAL_LIQUIDATION_DAY
        and 0 <= int(tile.get("max_lifespan_step", -1)) <= (day + 1) * 24
    ):
        return -20 if int(tile.get("yield_units", 0)) > 0 else -19
    if crop_data.get("ongoing") and tile.get("yield_units", 0) > 0:
        return 0
    if crop_data.get("ongoing") and _expires_by_next_day(tile, day):
        return -1
    harvest_day = crop_data.get("harvest_day")
    if harvest_day is not None and day - int(tile.get("planted_day", day)) >= harvest_day:
        return -2 if crop == "MELON" and day in {16, 28} else 0
    return 1 if _needs_water(tile, day) else None


def _needs_water(tile, day):
    """Daily watering is the measured reliable policy for this workforce."""
    if (
        tile.get("crop") == "MELON"
        and int(tile.get("yield_units", 0)) >= 6
        and int(tile.get("consecutive_unwatered", 0)) == 0
    ):
        return False
    return not tile.get("watered_today", False)


def _expires_by_next_day(tile, day):
    """True after an ongoing crop's last held yield has been collected."""
    max_lifespan_step = int(tile.get("max_lifespan_step", -1))
    return (
        tile.get("yield_units", 0) <= 0
        and max_lifespan_step >= 0
        and max_lifespan_step <= (day + 1) * 24
    )


def _in_bounds(x, y, tiles):
    return 0 <= y < len(tiles) and 0 <= x < len(tiles[y])


def _sell_orders(private, day, market_state, owned_cows=0):
    """Return market-aware sales while preserving shed and livestock reserves."""
    shed = private.get("shed", {})
    prices = market_state.get("prices", {}) if isinstance(market_state, dict) else {}
    product_stock = {
        item: int(quantity)
        for item, quantity in shed.items()
        # Fertilizer is production input.  Selling it at the same base price
        # immediately after purchase only starves the scheduled field refresh.
        if item in PRODUCTS and item != "FERTILIZER" and quantity > 0
    }
    total_stock = sum(max(0, int(quantity)) for quantity in shed.values())
    # Worker inventories are dropped into the shed automatically overnight.
    # Reserve room for the actual cargo already in flight instead of a fixed
    # twelve-unit guess; otherwise a large harvest is silently discarded.
    incoming_stock = sum(
        max(0, int(quantity))
        for inventory in private.get("inventories", [])
        for item, quantity in inventory.items()
        if item in PRODUCTS
    )
    overflow = max(0, total_stock + incoming_stock - SHED_CAPACITY)
    fertilizer_reserve = 10 if 19 <= day <= 25 else 0
    excess_fertilizer = max(
        0, int(shed.get("FERTILIZER", 0)) - fertilizer_reserve,
    )
    if owned_cows and excess_fertilizer:
        product_stock["FERTILIZER"] = excess_fertilizer
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
        target_price = base_price * SELL_PRICE_MULTIPLIERS.get(item, 1.0)
        price_is_healthy = item == "FERTILIZER" or quoted_price >= target_price
        if day >= 29 or (day >= FINAL_LIQUIDATION_DAY and item not in {"STRAWBERRY", "MILK", "WOOL"}):
            sell_quantity = quantity
        elif day == FINAL_LIQUIDATION_DAY:
            sell_quantity = min(quantity, overflow)
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
    animals = []
    for y, row in enumerate(tiles):
        for x, tile in enumerate(row):
            if isinstance(tile, dict) and tile.get("animal") in {"GOOSE", "COW", "SHEEP"}:
                animals.append((x, y, tile))
    shed = private.get("shed", {})
    inventories = private.get("inventories", [])
    owned_cows = sum(tile.get("animal") == "COW" for _, _, tile in animals)
    owned_cows += int(shed.get("COW", 0)) + sum(int(inv.get("COW", 0)) for inv in inventories)
    owned_sheep = sum(tile.get("animal") == "SHEEP" for _, _, tile in animals)
    owned_sheep += int(shed.get("SHEEP", 0)) + sum(int(inv.get("SHEEP", 0)) for inv in inventories)
    owned_geese = sum(tile.get("animal") == "GOOSE" for _, _, tile in animals)
    owned_geese += int(shed.get("GOOSE", 0)) + sum(int(inv.get("GOOSE", 0)) for inv in inventories)
    return {
        "animals": animals,
        "owned_cows": owned_cows,
        "owned_sheep": owned_sheep,
        "owned_geese": owned_geese,
        "owned_animals": owned_cows + owned_sheep + owned_geese,
        "unfed": [(x, y) for x, y, tile in animals if not tile.get("fed_today", False)],
        "deployments_assigned": 0,
    }


def _livestock_action(
    x, y, tile, inventory, tiles, private, livestock, reserved, day,
    worker_index,
):
    """Run cow logistics before non-essential crop work.

    Cows must be fed and cared for daily.  Workers carry wheat from the shed,
    then feed and care on consecutive turns.  A worker carrying a cow builds
    its own pasture on the first empty tile it reaches, avoiding a separate
    fragile construction schedule.
    """
    carried_animal = next((item for item in ("GOOSE", "SHEEP", "COW") if inventory.get(item, 0) > 0), None)
    carrying_wheat = inventory.get("WHEAT", 0) > 0
    carrying_fertilizer = inventory.get("FERTILIZER", 0) > 0
    at_shed = _is_shed_access(x, y, len(tiles))
    service_workers = (
        max(1, livestock["owned_animals"] // COWS_PER_SERVICE_WORKER)
        if livestock["owned_animals"] else 0
    )

    # Once a worker has an animal, finish that deployment before considering
    # another shed pickup or any routine farm service.
    if carried_animal:
        cow_slots = set(_compact_cow_slots(tiles))
        if tile is None and (x, y) in cow_slots:
            reserved.add((x, y))
            return ["BUILD_COOP" if carried_animal == "GOOSE" else "BUILD_PASTURE"]
        structure = "COOP" if carried_animal == "GOOSE" else "PASTURE"
        if (
            isinstance(tile, dict)
            and tile.get("kind") == structure
            and "animal" not in tile
            and (x, y) not in reserved
        ):
            reserved.add((x, y))
            return ["PLACE", carried_animal]
        empty_slots = [
            (slot_x, slot_y)
            for slot_x, slot_y in cow_slots
            if tiles[slot_y][slot_x] is None
        ]
        return _move_to(x, y, tiles, empty_slots, reserved)

    # Deployment is a short, separate responsibility: assign one worker per
    # shed animal so a growing serviced herd cannot permanently starve the
    # placement queue.  Unit actions execute in worker order, so these bounded
    # slots also avoid every hand attempting the same pickup.
    animals_in_shed = sum(
        int(private.get("shed", {}).get(animal, 0))
        for animal in ("GOOSE", "SHEEP", "COW")
    )
    if (
        at_shed
        and not carried_animal
        and (
            not (isinstance(tile, dict) and tile.get("animal"))
            or (
                tile.get("fed_today", False)
                and tile.get("cared_today", False)
                and not tile.get("fertilizer_available", False)
                and int(tile.get("yield_units", 0)) <= 0
            )
        )
        and (x, y) not in reserved
        and livestock["deployments_assigned"] < animals_in_shed
    ):
        for animal in ("SHEEP", "COW", "GOOSE"):
            if private.get("shed", {}).get(animal, 0) > 0:
                livestock["deployments_assigned"] += 1
                reserved.add((x, y))
                return ["PICKUP", animal, 1]

    if isinstance(tile, dict) and tile.get("animal") in {"GOOSE", "COW", "SHEEP"}:
        # A cow can receive only one useful worker action per turn.  Reserving
        # the tile prevents every nearby hand from feeding the same animal and
        # wasting the entire wheat reserve while other cows go hungry.
        if (x, y) in reserved:
            return None
        if not tile.get("fed_today", False):
            if carrying_wheat:
                reserved.add((x, y))
                return ["FEED"]
            if at_shed and private.get("shed", {}).get("WHEAT", 0) > 0:
                reserved.add((x, y))
                batch = max(1, (len(livestock["unfed"]) + service_workers - 1) // service_workers)
                return ["PICKUP", "WHEAT", batch]
            return _move_to(x, y, tiles, _shed_targets(len(tiles)), reserved)
        if not tile.get("cared_today", False):
            reserved.add((x, y))
            return ["CARE"]
        if tile.get("fertilizer_available", False):
            reserved.add((x, y))
            return ["COLLECT_FERTILIZER"]
        if tile.get("yield_units", 0) > 0:
            reserved.add((x, y))
            return ["HARVEST"]

    if carrying_fertilizer and worker_index >= service_workers:
        fertilizable = [
            (target_x, target_y)
            for target_y, row in enumerate(tiles)
            for target_x, target in enumerate(row)
            if isinstance(target, dict)
            and target.get("kind") == "PLANT"
            and target.get("crop") == "STRAWBERRY"
            and _strawberry_needs_fertilizer(target, day)
        ]
        if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "STRAWBERRY":
            if _strawberry_needs_fertilizer(tile, day):
                return ["FERTILIZE"]
        if fertilizable:
            return _move_to(x, y, tiles, fertilizable, reserved)

    if (
        19 <= day <= 25
        and worker_index >= service_workers
        and at_shed
        and private.get("shed", {}).get("FERTILIZER", 0) > 0
    ):
        return [
            "PICKUP", "FERTILIZER",
            min(FERTILIZER_BATCH_SIZE, int(private.get("shed", {}).get("FERTILIZER", 0))),
        ]

    if worker_index >= service_workers:
        return None

    if livestock["unfed"]:
        if at_shed and not carrying_wheat:
            if private.get("shed", {}).get("WHEAT", 0) > 0:
                batch = max(1, (len(livestock["unfed"]) + service_workers - 1) // service_workers)
                return ["PICKUP", "WHEAT", batch]
            return None
        if carrying_wheat:
            return _move_to(x, y, tiles, livestock["unfed"], reserved)
        return _move_to(x, y, tiles, _shed_targets(len(tiles)), reserved)
    if at_shed:
        for animal in ("GOOSE", "SHEEP", "COW"):
            if private.get("shed", {}).get(animal, 0) > 0:
                return ["PICKUP", animal, 1]
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
        and _strawberry_needs_fertilizer(tile, day)
        for row in tiles
        for tile in row
    )


def _strawberry_needs_fertilizer(tile, day):
    """Apply only when the three-day window covers a scheduled production.

    Ongoing production is created during the end-of-day refresh immediately
    before its visible yield day.  Keying to that refresh avoids paying for
    fertilizer that expires before a strawberry can benefit.
    """
    planted_day = int(tile.get("planted_day", day))
    last_refresh_day = planted_day + 15
    for refresh_day in range(planted_day + 9, last_refresh_day + 1, 2):
        if refresh_day < day:
            continue
        return (
            refresh_day == day
            and int(tile.get("fertilized_until_day", -1)) < refresh_day
        )
    return False


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


def _compact_cow_slots(tiles):
    """Return unlocked pasture cells ordered by service distance to the shed."""
    board_size = len(tiles)
    if board_size < 4:
        return ()
    half = board_size // 2
    candidates = (
        (half - 1, half - 1), (half, half - 1),
        (half - 1, half), (half, half),
        (half - 2, half - 1), (half + 1, half - 1),
        (half - 1, half - 2), (half, half - 2),
        (half - 2, half), (half - 1, half + 1),
        (half + 1, half), (half, half + 1),
        (half - 2, half - 2), (half + 1, half - 2),
        (half - 2, half + 1),
    )
    return tuple(
        (x, y)
        for x, y in candidates
        if _in_bounds(x, y, tiles) and tiles[y][x] != "LOCKED"
    )[:COMPACT_COW_TARGET]


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
