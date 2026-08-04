"""EXPERIMENTAL — marginal-revenue allocator variant.  NOT the submission.

Measured on 30 paired self-play seeds against `agent.py` (the approved
artifact), 2026-08-04:

    G1 self-play median   $86,282   vs  $79,407   (better)
    G3 self-play worst    $63,107   vs  $44,013   (better)
    G2 head-to-head        23% win rate over 60 paired episodes  (FAILS)

It banks more against a copy of itself but *loses* to `agent.py` head to head,
$72,806 to $91,321.  Under the acceptance rule in `implementation_plan.md`, a
change that fails its guard is not accepted however good its headline number
looks, so `agent.py` remains the submission.  See `walkthrough.md` for the
mechanism and for what would have to change before this can ship.
"""

import math
from collections import deque


# ---------------------------------------------------------------------------
# Tier 1 — game constants fixed by the specification (overview.md:242-267).
# These are the *inputs to derivation*, not tuning knobs.
# ---------------------------------------------------------------------------
MARKET_I0 = 10000
PRICE_FLOOR = 1
MARKET_PARAMS = {
    "WHEAT":      {"base":  25, "T": 400, "below_func": "sqrt",   "below_target": 0.80, "above_func": "log",    "above_target": 0.20},
    "CARROT":     {"base":  35, "T": 450, "below_func": "log",    "below_target": 0.20, "above_func": "sqrt",   "above_target": 0.70},
    "TOMATO":     {"base":  60, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "sqrt",   "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "T": 100, "below_func": "sqrt",   "below_target": 0.70, "above_func": "linear", "above_target": 1.60},
    "MELON":      {"base": 250, "T": 300, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.60},
    "EGG":        {"base":  50, "T": 332, "below_func": "linear", "below_target": 0.40, "above_func": "log",    "above_target": 0.20},
    "MILK":       {"base": 160, "T": 122, "below_func": "sqrt",   "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL":       {"base": 200, "T": 105, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.20},
    "FERTILIZER": {"base": 100, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40},
}
SHOP_PRODUCTS = {
    "BAKERY":         ("EGG", "WHEAT"),
    "PIZZA_SHOP":     ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT":    ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE":     ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE":       ("CARROT",),
    "SMOOTHIE_SHOP":  ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}
# Highest day threshold first; the town centre buys this multiple of each
# product every ``townCenterSellInterval`` turns.
TOWN_CENTER_DEMAND_SCHEDULE = ((20, 4), (10, 2), (0, 1))
# The town centre buys everything the farms can produce except fertilizer,
# which therefore has no natural price recovery at all.
TOWN_CENTER_EXCLUDED = ("FERTILIZER",)

DEFAULT_CONFIG = {
    "turnsPerDay": 24,
    "episodeSteps": 720,
    "shedCapacity": 100,
    "maxMarketOrdersPerTurn": 10,
    "boardSize": 10,
    "startingMoney": 3000,
    "farmHandCostMult": 1,
    "townShopSellInterval": 4,
    "townCenterSellInterval": 12,
    "townShopUnlockInterval": 3,
}

# ``units_per_tile_day`` is total units divided by the days the tile is held,
# and ``payback_days`` is the age at which those units can first be banked --
# both read off the engine's yield schedule, so both are game constants.
# A one-time crop yields 1 unit at planting plus 1 per watering inside
# [(max_yield_day+1)//2, max_yield_day]; an ongoing crop yields max_yield times
# at `interval` days apart from first_yield_day, then dies a day later.
CROPS = {
    "WHEAT":      {"cost":  10, "harvest_day":  4, "bonus_start": 2,
                   "units_per_tile_day": 4 / 5, "payback_days": 4, "max_yield": 6},
    "CARROT":     {"cost":  20, "harvest_day":  3, "bonus_start": 2,
                   "units_per_tile_day": 3 / 4, "payback_days": 3, "max_yield": 4},
    "TOMATO":     {"cost":  50, "ongoing": True,
                   "units_per_tile_day": 4 / 12, "payback_days": 8, "max_yield": 4},
    "STRAWBERRY": {"cost": 100, "ongoing": True,
                   "units_per_tile_day": 4 / 17, "payback_days": 10, "max_yield": 4},
    "MELON":      {"cost":  80, "harvest_day": 12, "bonus_start": 6,
                   "units_per_tile_day": 6 / 13, "payback_days": 12, "max_yield": 6},
}
HANDS_PER_DAY = 13
HIRE_COSTS = (1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377)
MAX_SEED_PURCHASE = 12
# (earliest day, cash required) for the NE, SW and SE quadrants.  The fourth
# is worth its $4k once the herd is large: feeding it needs roughly 1.25 wheat
# tiles per animal, which does not fit in three quadrants alongside the
# strawberry block.
LAND_PLAN = ((4, 1600), (8, 3200))
MOVES = ((0, -1, "NORTH"), (0, 1, "SOUTH"), (1, 0, "EAST"), (-1, 0, "WEST"))
PRODUCTS = {"WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"}
# Livestock is the densest use of a tile in the game.  A sheep returns roughly
# 1.33 wool a day from day 6, a cow 1.5 milk from day 8 and a goose 2 eggs from
# day 4 (care bonus included), against a crop tile's 0.24-0.5 units a day — and
# wool, milk and egg all trade above base all season because nobody supplies
# them.  Ordered by how early the animal starts paying for itself.
LIVESTOCK_PLAN = (("COW", 10), ("SHEEP", 6))
ANIMAL_COSTS = {"GOOSE": 300, "SHEEP": 500, "COW": 400}
ANIMAL_STRUCTURES = {"GOOSE": "COOP", "SHEEP": "PASTURE", "COW": "PASTURE"}
ANIMAL_KINDS = ("COOP", "PASTURE")
ANIMAL_SLOT_BUFFER = 2
ANIMALS_PER_SERVICE_WORKER = 3
# Buying stops once too little season is left for the animal to repay its cost.
LAST_ANIMAL_PURCHASE_DAY = 20
# Working capital kept back from an animal purchase, on top of the payroll and
# feed the herd already owes.  An animal bought out of that money costs more
# than it earns: an unhired hand is lost actions and an unfed animal escapes.
ANIMAL_PURCHASE_CASH_FLOOR = 500
MAX_ANIMALS_PER_ORDER = 2
FERTILIZER_BATCH_SIZE = 6
MAX_SELL_ORDER_TYPES = 6
FINAL_GLOBAL_MELON_THRESHOLD = 8
# Prices sit above base for every product but melon all season, so the market
# is under-supplied rather than glutted: plan to serve the whole town drain and
# let the sell-side reserve price stop us if the opponent gets there first.
# Both farms sell into one inventory, so a tile's own output is only half of
# what will have moved the price by the time it is sold.  Self-play is the
# measurement condition, so a mirror opponent is the honest assumption.
SUPPLY_MIRROR = 2.0
WHEAT_RESERVE_DAYS = 2
CROP_WORKLOAD_PER_WORKER = 6
# An animal needs feeding, care, collection and a walk each day; a crop tile
# needs about a watering.  Used both to size the payroll and to cap the field.
ANIMAL_WORKLOAD = 3
BASE_PRICES = {item: params["base"] for item, params in MARKET_PARAMS.items()}

# Tier 3 — strategy targets.  The reserve ratio is the fraction of base price
# below which a unit is worth more held than sold.  It is set from each
# product's glut tolerance: a product whose price recovers quickly (town demand
# large relative to the curve's slope) can afford to wait for base, while
# fertilizer has *no* town demand at all and never recovers, so holding it
# earns nothing and the only question is whether we sell before the opponent.
SELL_RESERVE_RATIOS = {
    "WHEAT": 0.90,
    "CARROT": 0.85,
    "TOMATO": 0.85,
    "STRAWBERRY": 1.00,
    "MELON": 1.00,
    "EGG": 0.75,
    "MILK": 1.00,
    "WOOL": 1.00,
    "FERTILIZER": 0.30,
}
DEFAULT_SELL_RESERVE_RATIO = 1.00
# Stock still held this close to the end will never clear at base, so the
# reserve price is walked down by days remaining rather than dumped at once.
ENDGAME_RESERVE_RATIOS = ((2, 0.70), (1, 0.35), (0, 0.0))


def _config_value(configuration, key, default):
    if isinstance(configuration, dict):
        value = configuration.get(key, default)
    else:
        value = getattr(configuration, key, default)
    return default if value is None else value


def _episode_config(configuration):
    """Derive every per-episode knob from ``configuration`` (W9a).

    Nothing here may be hard-coded: Kaggle can tune an episode or run the
    beginner variant, and a silently wrong season length or shed capacity
    misplays the whole game.
    """
    values = {
        key: type(default)(_config_value(configuration, key, default))
        for key, default in DEFAULT_CONFIG.items()
    }
    turns_per_day = max(1, values["turnsPerDay"])
    total_days = max(1, values["episodeSteps"] // turns_per_day)
    values["turnsPerDay"] = turns_per_day
    values["totalDays"] = total_days
    # The last day is the liquidation day; nothing planted after this can be
    # harvested, so both are season-relative rather than a literal 28/29.
    values["finalDay"] = total_days - 1
    return values


def _shape(func, value):
    value = max(0.0, value)
    if func == "sq":
        return value * value
    if func == "sqrt":
        return math.sqrt(value)
    if func == "log":
        return math.log(1.0 + value)
    if func == "log10":
        return math.log10(1.0 + value)
    return value


def _market_price(item, inventory):
    """The exact price the engine will quote for one unit at ``inventory``."""
    params = MARKET_PARAMS[item]
    base = params["base"]
    if inventory < MARKET_I0:
        func, target = params["below_func"], params["below_target"]
        amplitude = target * base / _shape(func, params["T"])
        price = base + amplitude * _shape(func, MARKET_I0 - inventory)
    else:
        func, target = params["above_func"], params["above_target"]
        amplitude = target * base / _shape(func, params["T"])
        price = base - amplitude * _shape(func, inventory - MARKET_I0)
    return max(PRICE_FLOOR, int(round(price)))


def _daily_town_demand(item, day, town_state, config):
    """Units of ``item`` the town removes from the market each day.

    This is the rate at which a glutted price recovers, and therefore the rate
    at which the product can be sold indefinitely without moving the price.
    """
    shops = town_state.get("unlocked_shops", []) if isinstance(town_state, dict) else []
    shop_events = config["turnsPerDay"] / max(1, config["townShopSellInterval"])
    demand = 0.0
    for shop in shops:
        products = SHOP_PRODUCTS.get(shop, ())
        if item in products:
            demand += (2 if len(products) == 1 else 1) * shop_events
    if item not in TOWN_CENTER_EXCLUDED:
        multiplier = next(
            value for threshold, value in TOWN_CENTER_DEMAND_SCHEDULE if day >= threshold
        )
        demand += multiplier * config["turnsPerDay"] / max(1, config["townCenterSellInterval"])
    return demand


def _units_above_price(item, inventory, available, reserve_price):
    """How many of ``available`` units still clear at or above ``reserve_price``.

    Prices are strictly non-increasing in inventory, so a binary search over
    the marginal unit is exact.
    """
    if available <= 0 or reserve_price <= PRICE_FLOOR:
        return available if reserve_price <= PRICE_FLOOR else 0
    if _market_price(item, inventory) < reserve_price:
        return 0
    low, high = 1, available
    while low < high:
        middle = (low + high + 1) // 2
        if _market_price(item, inventory + middle - 1) >= reserve_price:
            low = middle
        else:
            high = middle - 1
    return low


def _reserve_ratio(item, day, config):
    days_left = config["totalDays"] - 1 - day
    for threshold, ratio in ENDGAME_RESERVE_RATIOS:
        if days_left <= threshold:
            return ratio
    return SELL_RESERVE_RATIOS.get(item, DEFAULT_SELL_RESERVE_RATIO)


def _agent_impl(observation, configuration=None):
    """Return legal worker and market actions for one Kaggriculture turn."""
    obs = observation if isinstance(observation, dict) else getattr(observation, "__dict__", {})
    config = _episode_config(configuration)
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
    plan = _crop_plan(
        day, tiles, obs.get("market", {}), obs.get("town", {}), config,
        feed_demand_per_day=livestock["owned_animals"],
        croppable_tiles=_croppable_tiles(tiles, livestock),
    )
    reserved = set()
    actions = []
    for index, position in enumerate(workers):
        actions.append(_choose_worker_action(
            position, tiles, seed_budget, day, reserved,
            inventories[index] if index < len(inventories) else {}, private, livestock,
            index, len(workers), plan, config,
        ))

    projected_harvest_units = 0
    for position, action in zip(workers, actions):
        if not action or action[0] != "HARVEST":
            continue
        x, y = position
        tile = tiles[y][x] if _in_bounds(x, y, tiles) else None
        if isinstance(tile, dict):
            projected_harvest_units += max(0, int(tile.get("yield_units", 0)))

    return {
        "farmer": actions[0] if actions else ["PASS"],
        "hands": actions[1:],
        "market": _market_actions(
            farm, private, day, tiles, livestock, obs.get("market", {}),
            obs.get("town", {}), config, plan, projected_harvest_units,
        ),
    }


def _pass_action():
    return {"farmer": ["PASS"], "hands": [], "market": []}


def _market_actions(
    farm, private, day, tiles, livestock, market_state, town_state, config,
    plan, projected_harvest_units=0,
):
    money = float(farm.get("money", 0))
    market = []

    # Establish the full workforce first. Purchases and sales can execute on
    # following turns, but a missed hire permanently loses useful actions.
    desired_hands = _desired_hands(tiles)
    if _fertilizer_reserve(tiles, day):
        desired_hands = min(HANDS_PER_DAY, desired_hands + 1)
    if day >= config["finalDay"]:
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
    fertilizer_reserve = _fertilizer_reserve(tiles, day)
    sell_orders = _sell_orders(
        private, day, market_state, town_state, config,
        livestock["owned_animals"], projected_harvest_units, fertilizer_reserve,
    )[:MAX_SELL_ORDER_TYPES]
    market.extend(sell_orders)

    # An animal that goes unfed for two days escapes, taking its purchase price
    # and every remaining production cycle with it, so feed outranks every
    # other purchase.
    unlocked_count = len(farm.get("unlocked_quadrants", ["NW"]))
    final_day = config["finalDay"]
    wheat_on_hand = _wheat_on_hand(private)
    protected_animals = livestock["owned_animals"]
    wheat_needed = max(0, protected_animals * WHEAT_RESERVE_DAYS - wheat_on_hand)
    # Both players drain wheat all season buying feed, so it trades far above
    # base on the scarcity side; budgeting at base under-reserves cash badly.
    market_inventory = (
        market_state.get("inventory", {}) if isinstance(market_state, dict) else {}
    )
    wheat_price = _market_price("WHEAT", int(market_inventory.get("WHEAT", MARKET_I0)) - 1)
    if day < final_day and protected_animals and wheat_needed and money >= wheat_needed * wheat_price:
        market.append(["BUY_PRODUCT", "WHEAT", wheat_needed])
        money -= wheat_needed * wheat_price

    unlocked = unlocked_count
    if unlocked <= len(LAND_PLAN):
        unlock_day, cash_threshold = LAND_PLAN[unlocked - 1]
        if day >= unlock_day and money >= cash_threshold:
            market.append(["BUY_LAND"])
            money -= (1000, 2000, 4000)[unlocked - 1]

    open_tiles = sum(tile is None for row in tiles for tile in row)
    if not plan:
        return market[:config["maxMarketOrdersPerTurn"]]
    crop, target_seed_count = _next_crop(plan)
    crop_seed_count = int(private.get("seeds", {}).get(crop, 0))
    payroll_reserve = 0 if day >= config["finalDay"] else sum(HIRE_COSTS[:desired_hands])
    spendable = max(0, money - payroll_reserve)
    if crop_seed_count < min(open_tiles, target_seed_count) and spendable >= CROPS[crop]["cost"]:
        quantity = min(
            MAX_SEED_PURCHASE,
            max(1, min(open_tiles, target_seed_count) - crop_seed_count),
            int(spendable // CROPS[crop]["cost"]),
        )
        if quantity:
            market.append(["BUY_SEED", crop, quantity])
            money -= quantity * CROPS[crop]["cost"]

    # Livestock is bought last, out of genuine surplus.  An animal is the
    # densest earner on the board, but it is funded *by* the crop loop: buying
    # one out of the seed budget stalls the engine that pays for the next.
    # Within that budget, buy as early as the season allows — an animal's value
    # is the number of production cycles it has left, so delay is a permanent
    # loss rather than a deferred cost.
    animal_cash_floor = (
        ANIMAL_PURCHASE_CASH_FLOOR
        + payroll_reserve
        + protected_animals * WHEAT_RESERVE_DAYS * wheat_price
    )
    if day <= LAST_ANIMAL_PURCHASE_DAY:
        for animal, target in LIVESTOCK_PLAN:
            shortfall = max(0, target - livestock[f"owned_{animal.lower()}"])
            cost = ANIMAL_COSTS[animal]
            affordable = int(max(0, money - animal_cash_floor) // cost)
            quantity = min(shortfall, affordable, MAX_ANIMALS_PER_ORDER)
            if quantity:
                market.append(["BUY_ANIMAL", animal, quantity])
                money -= quantity * cost

    return market[:10]


def _fertilizer_reserve(tiles, day):
    """Units held back for the field instead of sold.

    A fertilized ongoing crop yields two units instead of one on each of its
    production days, so a unit spent on a strawberry returns a multiple of what
    it fetches on a market that has no town demand at all and never recovers.
    The reserve is therefore one unit per tile that can still be doubled.
    """
    return sum(
        isinstance(tile, dict)
        and tile.get("kind") == "PLANT"
        and tile.get("crop") == "STRAWBERRY"
        and _strawberry_needs_fertilizer(tile, day)
        for row in tiles for tile in row
    )


def _desired_hands(tiles):
    """Scale payroll to the field: one worker can service six nearby tiles."""
    workload = 0
    for row in tiles:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            workload += ANIMAL_WORKLOAD if tile.get("animal") else tile.get("kind") in {"PLANT", "WEED"}
    total_workers = max(
        5,
        (workload + CROP_WORKLOAD_PER_WORKER - 1) // CROP_WORKLOAD_PER_WORKER,
    )
    return min(HANDS_PER_DAY, total_workers - 1)


def _crop_plan(
    day, tiles, market_state, town_state, config,
    feed_demand_per_day=0, croppable_tiles=0,
):
    """Allocate the field by marginal revenue per tile-day.

    This replaces the fixed STRAWBERRY/MELON/TOMATO targets.  Tiles are handed
    out one at a time to whichever crop the *next* tile is worth most on, where
    a tile's worth is its yield rate times the price its own output will
    actually clear at — the price after the crop's projected supply, net of
    what the town drains, has moved the curve.

    That marginal test is what a flat demand cap gets wrong in both directions.
    Melon is drained by the town centre alone, so its price collapses quickly
    and the allocator stops at a handful of tiles; but it starts from a $250
    base, so those tiles stay worth more per day than wheat even well below
    base, which a "never exceed town demand" rule would refuse to plant.
    """
    counts = _crop_tile_counts(tiles)
    market_inventory = (
        market_state.get("inventory", {}) if isinstance(market_state, dict) else {}
    )
    remaining_days = max(1, config["finalDay"] - day)
    # Every animal eats a wheat a day.  Feed is worth what it would otherwise
    # cost to buy, so it enters as a floor on the wheat acreage rather than
    # competing on its sale price.
    feed_tiles = int(math.ceil(
        feed_demand_per_day / CROPS["WHEAT"]["units_per_tile_day"]
    )) if feed_demand_per_day else 0

    candidates = [
        crop for crop, data in CROPS.items()
        # Nothing is worth planting that cannot reach its yield in time.
        if day + data["payback_days"] <= config["finalDay"]
    ]
    if not candidates:
        return []

    def marginal_value(crop, tile_count):
        data = CROPS[crop]
        rate = data["units_per_tile_day"]
        lag = data["payback_days"]
        horizon = min(remaining_days, lag + 1)
        # The tile is priced at what its output will fetch when it is actually
        # sold, not today.  A strawberry sown now reaches the market ten days
        # later, by which time the town has drained ten days of supply out of
        # it — which is why it holds well above base all season while melon,
        # drained by the town centre alone, does not.
        demand = _daily_town_demand(crop, day, town_state, config)
        supply = tile_count * rate * horizon * SUPPLY_MIRROR
        inventory = (
            int(market_inventory.get(crop, MARKET_I0))
            + supply
            - demand * (lag + horizon)
        )
        seed_cost_per_day = data["cost"] / max(1, lag)
        return rate * _market_price(crop, int(inventory)) - seed_cost_per_day

    allocation = {crop: 0 for crop in candidates}
    if "WHEAT" in allocation:
        allocation["WHEAT"] = min(feed_tiles, croppable_tiles)
    budget = max(0, croppable_tiles - sum(allocation.values()))
    for _ in range(budget):
        best = max(candidates, key=lambda crop: marginal_value(crop, allocation[crop] + 1))
        if marginal_value(best, allocation[best] + 1) <= 0:
            break
        allocation[best] += 1

    plan = [
        (marginal_value(crop, allocation[crop]), crop, allocation[crop], counts.get(crop, 0))
        for crop in candidates
    ]
    plan.sort(reverse=True)
    return plan


def _wheat_on_hand(private):
    return int(private.get("shed", {}).get("WHEAT", 0)) + sum(
        int(inventory.get("WHEAT", 0)) for inventory in private.get("inventories", [])
    )


def _croppable_tiles(tiles, livestock):
    """Unlocked tiles the field can plant, once the herd's block is set aside.

    Capping this by the payroll's workload model was measured and rejected: it
    left the median flat and cost $16k on the worst seed, so the field is left
    land-bound and the watering priorities decide what actually gets serviced.
    """
    plantable = sum(
        tile is None
        or (isinstance(tile, dict) and tile.get("kind") in ("PLANT", "WEED"))
        for row in tiles for tile in row
    )
    return max(0, plantable - len(_animal_slots(tiles, livestock["slot_target"])))


def _crop_tile_counts(tiles):
    counts = {}
    for row in tiles:
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                crop = tile.get("crop")
                counts[crop] = counts.get(crop, 0) + 1
    return counts


def _next_crop(plan):
    """The most valuable crop still short of its demand-derived tile count."""
    for _value, crop, cap, planted in plan:
        if planted < cap:
            return crop, cap
    return (plan[0][1], plan[0][2]) if plan else ("WHEAT", 0)


def _choose_worker_action(
    position, tiles, seed_budget, day, reserved, inventory, private, livestock,
    worker_index, worker_count, plan, config,
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
        day == config["finalDay"]
        and carrying_non_melon
        and isinstance(tile, dict)
        and (
            tile.get("kind") == "WEED"
            or (
                tile.get("kind") == "PLANT"
                and int(tile.get("yield_units", 0)) <= 0
                and 0 <= int(tile.get("max_lifespan_step", -1)) <= (day + 1) * config["turnsPerDay"]
            )
        )
    ):
        reserved.add((x, y))
        return ["DIG"]
    if (
        (inventory.get("MELON", 0) > 0 and day <= 16)
        or (day == config["finalDay"] and carrying_non_melon)
        or (day >= config["finalDay"] and carrying_products)
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
    # Keep the cells nearest the shed clear for animals.  A stationary service
    # lane avoids paying movement for the feed/care/collect actions each animal
    # needs every day.
    animal_slots = set(_animal_slots(tiles, livestock["slot_target"]))
    action = (
        None
        if (x, y) in animal_slots and tile is None
        else _action_for_tile(tile, seed_budget, day, plan, config)
    )
    ripe_melons = sum(
        isinstance(target, dict)
        and target.get("crop") == "MELON"
        and day - int(target.get("planted_day", day)) >= CROPS["MELON"]["harvest_day"]
        for row in tiles
        for target in row
    )
    use_global_liquidation = (
        day >= config["finalDay"] and ripe_melons <= FINAL_GLOBAL_MELON_THRESHOLD
    )
    service_workers = livestock["service_workers"]
    crop_worker_count = max(1, worker_count - service_workers)
    crop_worker_index = worker_index - service_workers
    region = (
        None
        if use_global_liquidation or crop_worker_index < 0
        else _worker_region(tiles, crop_worker_index, crop_worker_count)
    )
    if tile is None:
        urgent_target = _nearest_target(
            x, y, tiles, seed_budget, day, reserved, plan, config,
            urgent_only=True, allowed=region,
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

    target = _nearest_target(
        x, y, tiles, seed_budget, day, reserved, plan, config, allowed=region,
    )
    if target is None:
        target = _nearest_target(
            x, y, tiles, seed_budget, day, reserved, plan, config, urgent_only=True,
        )
    if target is None:
        return ["PASS"]
    direction, coordinates = target
    reserved.add(coordinates)
    return [direction]


def _action_for_tile(tile, seed_budget, day, plan, config):
    if day >= config["finalDay"]:
        # Nothing planted or watered on the last day can pay back, so every
        # hand-turn goes to banking yield that is already standing — from any
        # crop or animal, not just melon.  Anything left in the ground at turn
        # 720 is worth nothing.
        return ["HARVEST"] if _has_standing_yield(tile, day) else None
    if tile is None:
        crop = _available_crop(seed_budget, plan)
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
        day == config["finalDay"]
        and 0 <= int(tile.get("max_lifespan_step", -1)) <= (day + 1) * config["turnsPerDay"]
        and int(tile.get("yield_units", 0)) <= 0
    ):
        return ["DIG"]
    if crop_data.get("ongoing") and tile.get("yield_units", 0) > 0:
        return ["HARVEST"]
    if crop_data.get("ongoing") and _expires_by_next_day(tile, day, config):
        return ["DIG"]
    harvest_day = crop_data.get("harvest_day")
    if harvest_day is not None and day - int(tile.get("planted_day", day)) >= harvest_day:
        return ["HARVEST"]
    if _needs_water(tile, day):
        return ["WATER"]
    return None


def _available_crop(seed_budget, plan):
    """The most valuable planned crop that has a seed in hand and room left."""
    for _value, crop, cap, planted in plan:
        if seed_budget.get(crop, 0) > 0 and planted < cap:
            return crop
    # A bought seed is sunk cost and an empty tile only grows weeds, so plant
    # it anyway once the allocator has moved on — but only where the crop can
    # still reach its yield, which is what keeps it out of `plan` otherwise.
    for _value, crop, _cap, _planted in plan:
        if seed_budget.get(crop, 0) > 0:
            return crop
    return None


def _nearest_target(
    start_x, start_y, tiles, seed_budget, day, reserved, plan, config,
    urgent_only=False, allowed=None,
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
            priority = _target_priority(tiles[y][x], seed_budget, day, plan, config)
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


def _target_priority(tile, seed_budget, day, plan, config):
    """Smaller values are assigned first across the whole farm."""
    if day >= config["finalDay"]:
        return -10 if _has_standing_yield(tile, day) else None
    if tile is None:
        return 3 if _available_crop(seed_budget, plan) else None
    if not isinstance(tile, dict):
        return None
    if tile.get("kind") == "WEED":
        # Clearing a weed immediately protects the small worker budget from
        # accumulating a permanent traversal and planting bottleneck.
        return -1 if day < config["finalDay"] else 2
    if tile.get("kind") != "PLANT":
        return None
    crop = tile.get("crop")
    crop_data = CROPS.get(crop, {})
    if (
        day == config["finalDay"]
        and 0 <= int(tile.get("max_lifespan_step", -1)) <= (day + 1) * config["turnsPerDay"]
    ):
        return -20 if int(tile.get("yield_units", 0)) > 0 else -19
    if crop_data.get("ongoing") and tile.get("yield_units", 0) > 0:
        return 0
    if crop_data.get("ongoing") and _expires_by_next_day(tile, day, config):
        return -1
    harvest_day = crop_data.get("harvest_day")
    if harvest_day is not None and day - int(tile.get("planted_day", day)) >= harvest_day:
        return -2 if crop == "MELON" and day in {16, 28} else 0
    if not _needs_water(tile, day):
        return None
    # A plant on its second dry day becomes a weed tonight, losing every unit
    # it had left.  That outranks clearing a weed that has already happened.
    return -3 if int(tile.get("consecutive_unwatered", 0)) >= 1 else 1


def _has_standing_yield(tile, day):
    """True when the tile holds units a HARVEST would actually collect."""
    if not isinstance(tile, dict) or int(tile.get("yield_units", 0)) <= 0:
        return False
    if tile.get("animal"):
        return True
    if tile.get("kind") != "PLANT":
        return False
    crop_data = CROPS.get(tile.get("crop"), {})
    # The engine refuses a harvest before the crop's first yield day.
    return day - int(tile.get("planted_day", day)) >= crop_data.get("payback_days", 0)


def _needs_water(tile, day):
    """Water only where the watering actually buys something.

    A plant turns to weed after two consecutive dry days, so a crop watered
    yesterday can safely be skipped today.  Beyond staying alive, watering pays
    in exactly two places: a one-time crop gains a unit for each watering
    inside its bonus window, and a fertilized ongoing crop only banks the
    fertilizer bonus on a day it was watered.  An ongoing crop's yield is
    otherwise on a fixed clock and no amount of watering advances it.

    Watering is the single largest consumer of hand-turns, so skipping the ones
    that buy nothing is what pays for the herd.
    """
    if tile.get("watered_today", False):
        return False
    # One more dry day and the tile becomes a weed.
    if int(tile.get("consecutive_unwatered", 0)) >= 1:
        return True
    crop_data = CROPS.get(tile.get("crop"), {})
    if crop_data.get("ongoing"):
        return int(tile.get("fertilized_until_day", -1)) >= day
    age = day - int(tile.get("planted_day", day))
    return (
        crop_data.get("bonus_start", 0) <= age <= crop_data.get("harvest_day", 0)
        and int(tile.get("yield_units", 0)) < crop_data.get("max_yield", 0)
    )


def _expires_by_next_day(tile, day, config):
    """True after an ongoing crop's last held yield has been collected."""
    max_lifespan_step = int(tile.get("max_lifespan_step", -1))
    return (
        tile.get("yield_units", 0) <= 0
        and max_lifespan_step >= 0
        and max_lifespan_step <= (day + 1) * config["turnsPerDay"]
    )


def _in_bounds(x, y, tiles):
    return 0 <= y < len(tiles) and 0 <= x < len(tiles[y])


def _sell_orders(
    private, day, market_state, town_state, config, owned_animals=0,
    projected_harvest_units=0, fertilizer_reserve=0,
):
    """Sell every unit that still clears its reserve price, and no more.

    The engine's price curve is closed-form and its inventory is in the
    observation, so the price of the *n*-th unit about to be sold is known
    exactly before the order is issued.  Selling down to the reserve price and
    stopping is what paces sales against town demand: the town drains a fixed
    number of units per day, which is precisely the volume that reappears above
    the reserve price by the next turn.  No fixed batch size is involved.
    """
    shed = private.get("shed", {})
    inventories = private.get("inventories", [])
    market_inventory = (
        market_state.get("inventory", {}) if isinstance(market_state, dict) else {}
    )
    product_stock = {
        item: int(quantity)
        for item, quantity in shed.items()
        if item in PRODUCTS and quantity > 0
    }
    total_stock = sum(max(0, int(quantity)) for quantity in shed.values())
    # Worker inventories are dropped into the shed automatically overnight, so
    # cargo already in flight competes for the same capacity.
    incoming_stock = sum(
        max(0, int(quantity))
        for inventory in inventories
        for item, quantity in inventory.items()
        if item in PRODUCTS
    )
    overflow = max(
        0,
        total_stock + incoming_stock + projected_harvest_units - config["shedCapacity"],
    )
    final_day = config["finalDay"]
    orders = []

    for item in sorted(
        product_stock,
        key=lambda name: -_market_price(
            name, int(market_inventory.get(name, MARKET_I0))
        ) * product_stock[name],
    ):
        quantity = product_stock[item]
        # Wheat is operating inventory, not sale inventory, while animals are
        # alive: it is far cheaper to feed grown wheat than to buy it back on a
        # scarcity curve that both players are draining.
        if item == "WHEAT" and day < final_day:
            feed_days = max(WHEAT_RESERVE_DAYS, final_day - day)
            quantity = max(0, quantity - owned_animals * feed_days)
        # Fertilizer applied to an ongoing crop doubles that crop's yield,
        # which is worth several times its sale price.
        if item == "FERTILIZER" and day < final_day:
            quantity = max(0, quantity - fertilizer_reserve)
        if quantity <= 0:
            continue

        inventory = int(market_inventory.get(item, MARKET_I0))
        reserve_price = BASE_PRICES[item] * _reserve_ratio(item, day, config)
        sell_quantity = _units_above_price(item, inventory, quantity, reserve_price)
        # Holding is only worth anything while the town is still draining the
        # product back below the reserve price.  Stock beyond what the rest of
        # the season can absorb will never clear at that price, so it is
        # released now rather than written off at turn 720.
        demand = _daily_town_demand(item, day, town_state, config)
        absorbable = demand * max(0, final_day - day)
        if demand > 0 and quantity > absorbable:
            sell_quantity = max(sell_quantity, int(quantity - absorbable))
        # Stock that would be destroyed by the shed cap is worth its floor
        # price rather than nothing, so capacity still forces a release — but
        # only of the units that actually do not fit.
        if overflow > 0:
            sell_quantity = max(sell_quantity, min(quantity, overflow))
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
    owned_animals = owned_cows + owned_sheep + owned_geese
    return {
        "animals": animals,
        "owned_cow": owned_cows,
        "owned_sheep": owned_sheep,
        "owned_goose": owned_geese,
        "owned_animals": owned_animals,
        # One structure per animal owned, plus room to build ahead of the next
        # delivery so a carried animal always has somewhere to go.
        "slot_target": owned_animals + ANIMAL_SLOT_BUFFER if owned_animals else 0,
        "service_workers": (
            max(1, -(-owned_animals // ANIMALS_PER_SERVICE_WORKER))
            if owned_animals else 0
        ),
        "unfed": [(x, y) for x, y, tile in animals if not tile.get("fed_today", False)],
        # An animal that has already missed a day escapes tonight unless it is
        # fed, forfeiting its price and every remaining production cycle.
        "starving": [
            (x, y) for x, y, tile in animals
            if not tile.get("fed_today", False)
            and int(tile.get("consecutive_unfed", 0)) >= 1
        ],
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
    service_workers = livestock["service_workers"]

    # Once a worker has an animal, finish that deployment before considering
    # another shed pickup or any routine farm service.
    if carried_animal:
        cow_slots = set(_animal_slots(tiles, livestock["slot_target"]))
        structure = ANIMAL_STRUCTURES[carried_animal]
        if tile is None and (x, y) in cow_slots:
            reserved.add((x, y))
            return ["BUILD_COOP" if structure == "COOP" else "BUILD_PASTURE"]
        if (
            isinstance(tile, dict)
            and tile.get("kind") == structure
            and "animal" not in tile
            and (x, y) not in reserved
        ):
            reserved.add((x, y))
            return ["PLACE", carried_animal]
        # A slot is usable if it is bare ground to build on *or* an empty
        # structure of this animal's own kind.  Routing only to bare ground
        # strands the animal once the block is built out — and a coop is no
        # use to a cow.
        usable_slots = [
            (slot_x, slot_y)
            for slot_x, slot_y in cow_slots
            if tiles[slot_y][slot_x] is None
            or (
                isinstance(tiles[slot_y][slot_x], dict)
                and tiles[slot_y][slot_x].get("kind") == structure
                and "animal" not in tiles[slot_y][slot_x]
            )
        ]
        return _move_to(x, y, tiles, usable_slots, reserved)

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
                return ["PICKUP", "WHEAT", _feed_batch(livestock, service_workers)]
            return _move_to(x, y, tiles, _shed_targets(len(tiles)), reserved)
        if not tile.get("cared_today", False):
            reserved.add((x, y))
            return ["CARE"]
        if tile.get("yield_units", 0) > 0:
            reserved.add((x, y))
            return ["HARVEST"]
        if tile.get("fertilizer_available", False):
            reserved.add((x, y))
            return ["COLLECT_FERTILIZER"]

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
        worker_index >= service_workers
        and at_shed
        and private.get("shed", {}).get("FERTILIZER", 0) > 0
        and _fertilizer_reserve(tiles, day) > 0
    ):
        return [
            "PICKUP", "FERTILIZER",
            min(FERTILIZER_BATCH_SIZE, int(private.get("shed", {}).get("FERTILIZER", 0))),
        ]

    # Rescue feeding is farm-wide: at full herd the service workers alone
    # cannot reach every animal within a day, and a missed second day is a
    # permanent loss rather than a delayed one.
    if livestock["starving"]:
        if carrying_wheat:
            rescue = _move_to(x, y, tiles, livestock["starving"], reserved)
            if rescue:
                return rescue
        elif at_shed and private.get("shed", {}).get("WHEAT", 0) > 0:
            return ["PICKUP", "WHEAT", _feed_batch(livestock, service_workers)]

    if worker_index >= service_workers:
        return None

    if livestock["unfed"]:
        if at_shed and not carrying_wheat:
            if private.get("shed", {}).get("WHEAT", 0) > 0:
                return ["PICKUP", "WHEAT", _feed_batch(livestock, service_workers)]
            return None
        if carrying_wheat:
            return _move_to(x, y, tiles, livestock["unfed"], reserved)
        return _move_to(x, y, tiles, _shed_targets(len(tiles)), reserved)
    if at_shed:
        for animal in ("GOOSE", "SHEEP", "COW"):
            if private.get("shed", {}).get(animal, 0) > 0:
                return ["PICKUP", animal, 1]
    return None


def _feed_batch(livestock, service_workers):
    """Wheat to carry so one trip services this worker's share of the herd."""
    return max(1, -(-len(livestock["unfed"]) // max(1, service_workers)))


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


def _shed_targets(board_size):
    half = board_size // 2
    return ((half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half))


def _animal_slots(tiles, target):
    """Unlocked cells nearest the shed, one per animal the farm has to house.

    Feeding, caring and collecting are three actions per animal per day, all of
    which start from the shed, so the herd is packed as tightly around it as
    the unlocked land allows.  The block only grows as animals are acquired,
    leaving the rest of the field free to be planted.
    """
    board_size = len(tiles)
    if board_size < 4 or target <= 0:
        return ()
    half = board_size // 2
    cells = [
        (x, y)
        for y in range(board_size)
        for x in range(board_size)
        if tiles[y][x] is None
        or (isinstance(tiles[y][x], dict) and tiles[y][x].get("kind") in ANIMAL_KINDS)
    ]
    cells.sort(key=lambda cell: (
        abs(cell[0] - half + 0.5) + abs(cell[1] - half + 0.5), cell[1], cell[0]
    ))
    return tuple(cells[:target])


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


def agent(observation, configuration=None):
    """Kaggle submission entry point; intentionally the final callable."""
    return _agent_impl(observation, configuration)
