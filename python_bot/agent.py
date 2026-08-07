"""A reliable, crop-first Kaggriculture submission agent.

The agent deliberately earns from a repeatable crop loop before attempting
expansion: hire affordable daily labour, plant only available seeds, water
every crop, harvest only at the crop's best one-time yield day, and sell all
stored produce.  This keeps the public ``agent`` entry point self-contained
for direct Kaggle uploads.
"""

from collections import deque


# ``harvest_day`` is the engine's ``max_yield_day`` -- the age at which a
# one-time crop holds its full yield and is worth collecting.  ``first_yield_day``
# is the earlier age at which the engine will *accept* a HARVEST at all, which is
# what matters on the final day when partial yield still beats leaving it standing.
CROPS = {
    "WHEAT": {"cost": 10, "harvest_day": 4, "bonus_start": 2, "first_yield_day": 2},
    "CARROT": {"cost": 20, "harvest_day": 3, "bonus_start": 2, "first_yield_day": 2},
    "TOMATO": {"cost": 50, "ongoing": True, "first_yield_day": 8},
    "STRAWBERRY": {"cost": 100, "ongoing": True, "first_yield_day": 10},
    "MELON": {"cost": 80, "harvest_day": 12, "bonus_start": 6, "first_yield_day": 10},
}
HANDS_PER_DAY = 14
HIRE_COSTS = (1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610)
SEED_BUFFER = 25
MAX_SEED_PURCHASE = 12
# Wheat tiles needed to cover feed for the typical 8-cow herd at WHEAT_RESERVE_DAYS=2.
# (8 cows × 2 days) / ~4 units per tile = 4 tiles minimum; +2 buffer for weed gaps.
# Keeping this well below the workload ceiling (60 crop tiles at 14 hands) is what
# prevents the weed-cap liveness failure seen in Cycle 13.
WHEAT_TILE_CAP = 6
# The fourth quadrant costs $4k with too little remaining season to recover
# its labour and weed-management cost.  The proven high-output replay uses
# three quadrants, so expansion stops after NE and SW.
LAND_PLAN = ((7, 1600), (11, 3200))
MOVES = ((0, -1, "NORTH"), (0, 1, "SOUTH"), (1, 0, "EAST"), (-1, 0, "WEST"))
PRODUCTS = {"WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"}
COMPACT_COW_TARGET = 8
LIVESTOCK_SLOT_TARGET = 36
ANIMALS_PER_SERVICE_WORKER = 5
MAX_FERTILIZER_COLLECTIONS_PER_TURN = 1
LIVESTOCK_CASH_BUFFER = 500
ANIMAL_AT_RISK_UNFED_DAYS = 1
SHEEP_PURCHASE_BATCH = 2
FERTILIZER_BATCH_SIZE = 6
MAX_SELL_ORDER_TYPES = 5
PREMIUM_SELL_BATCH = 8
STAPLE_SELL_BATCH = 20
STRAWBERRY_PRIORITY_DAY = 7
STRAWBERRY_DEMAND_PRIORITY_DAY = 8
STRAWBERRY_DEMAND_SHOPS = {
    "BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET",
}
LAST_PLANTING_DAY = 28
FINAL_GLOBAL_MELON_THRESHOLD = 8
EARLY_GOOSE_TARGET = 0
EARLY_SHEEP_TARGET = 0
LATE_SHEEP_TARGET = 6
SHEEP_PURCHASE_START_DAY = 0
SHEEP_PURCHASE_END_DAY = 20
STRAWBERRY_TARGET = 42
TOMATO_TARGET = 0
MELON_TARGET = 12
SHED_CAPACITY = 100
WHEAT_RESERVE_DAYS = 2
CROP_WORKLOAD_PER_WORKER = 6
FINAL_LIQUIDATION_DAY = 29
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
    "WHEAT": 1.0,
    "CARROT": 1.0,
    "TOMATO": 1.0,
    "STRAWBERRY": 1.0,
    "MELON": 0.0,
    "EGG": 1.0,
    "MILK": 0.0,
    "WOOL": 1.0,
    # Fertilizer: 0.0 means the W11 adaptive floor ($55 when opponent oversupplies)
    # governs when we sell.  The 98% below-base figure is expected — the $100 base
    # is above the adaptive floor.  Phi ($186k, the strongest observed agent) also
    # uses 0.0 here.  Cycle 15 tried 1.0; bank fell $2,490, win rate unchanged.
    "FERTILIZER": 0.0,
}
SELL_BATCHES = {
    "WHEAT": 4,
    "CARROT": 4,
    "TOMATO": 4,
    "STRAWBERRY": 8,
    "MELON": 6,
    "EGG": 4,
    "MILK": 3,
    "WOOL": 4,
    "FERTILIZER": 3,
}
# W11 — adaptive reserve price.  The reserve above is correct against a patient
# opponent and wrong against one that dumps: holding for a price the opponent is
# actively destroying just moves the sale to a worse turn.  These govern how the
# reserve responds once the opponent is measurably out-supplying the town.
#
# The window is one game day.  A first attempt counted *consecutive* turns of
# net inflow and never fired: opponents sell in bursts after a harvest and sit
# idle in between, so the measured streak never exceeded 1 for any product.
# Summing over a day nets the bursts against the town's drain, which is the
# quantity that actually decides whether the price recovers.
SUPPLY_WINDOW_TURNS = 24
SUPPLY_SURPLUS_TO_CAPITULATE = 0
# Measured over 120 paired episodes against the W10 adversary: the batch is the
# lever and the reserve cut is not.  Batch 100 scored 64%/62% at reserve cuts
# 0.35/0.55; batch 40 scored 59%/59% at cuts 0.55/0.75.  Since the cut shows no
# consistent effect it is left at the middle value rather than tuned to the
# single best-scoring run, which would be fitting noise on this fixture.
ADAPTIVE_RESERVE_CUT = 0.55
ADAPTIVE_SELL_BATCH = 100


def _agent_impl(observation, configuration=None):
    """Return legal worker and market actions for one Kaggriculture turn."""
    episode = _episode_config(configuration)
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
    (
        strawberry_priority_day,
        strawberry_target,
        melon_target,
        fertilizer_batch_size,
    ) = _premium_crop_plan(
        obs.get("town", {})
    )
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
            index, len(workers), strawberry_priority_day,
            fertilizer_batch_size, episode["turns_per_day"],
            episode["final_liquidation_day"],
        ))

    projected_harvest_units = 0
    for position, action in zip(workers, actions):
        if not action or action[0] != "HARVEST":
            continue
        x, y = position
        tile = tiles[y][x] if _in_bounds(x, y, tiles) else None
        if isinstance(tile, dict):
            projected_harvest_units += max(0, int(tile.get("yield_units", 0)))

    step = day * episode["turns_per_day"] + int(obs.get("hour", 0))
    supply_streak = _supply_pressure(
        player, step, obs.get("market", {}), episode["turns_per_day"],
    )
    market_actions = _market_actions(
        farm, private, day, tiles, livestock, obs.get("market", {}),
        projected_harvest_units, strawberry_priority_day, strawberry_target,
        melon_target, supply_streak, episode,
    )
    _record_issued_orders(player, market_actions)

    return {
        "farmer": actions[0] if actions else ["PASS"],
        "hands": actions[1:],
        "market": market_actions,
    }


def _pass_action():
    return {"farmer": ["PASS"], "hands": [], "market": []}


def _episode_config(configuration=None):
    """Normalize configurable engine knobs while preserving official defaults."""
    if isinstance(configuration, dict):
        get_value = configuration.get
    else:
        get_value = lambda key, default: getattr(configuration, key, default)

    turns_per_day = max(1, int(get_value("turnsPerDay", 24)))
    episode_steps = max(1, int(get_value("episodeSteps", 720)))
    season_days = max(1, (episode_steps + turns_per_day - 1) // turns_per_day)
    return {
        "turns_per_day": turns_per_day,
        "episode_steps": episode_steps,
        "season_days": season_days,
        "last_planting_day": max(0, season_days - 2),
        "final_liquidation_day": max(0, season_days - 1),
        "shed_capacity": max(1, int(get_value("shedCapacity", SHED_CAPACITY))),
        "max_market_orders": max(0, int(get_value("maxMarketOrdersPerTurn", 10))),
        "farm_hand_cost_mult": max(0.0, float(get_value("farmHandCostMult", 1))),
        "board_size": max(1, int(get_value("boardSize", 10))),
        "starting_money": float(get_value("startingMoney", 3000)),
        "weed_spawn_chance": max(0.0, float(get_value("weedSpawnChance", 0.005))),
        "town_shop_unlock_interval": max(1, int(get_value("townShopUnlockInterval", 3))),
        "town_shop_sell_interval": max(1, int(get_value("townShopSellInterval", 4))),
    }


# Keyed by player index because a self-play harness may hand the *same* module
# to both sides; keeping one entry per side stops one player's history from
# being read as the other's.
_SUPPLY_MEMORY = {}


def _supply_pressure(player, step, market_state, window=SUPPLY_WINDOW_TURNS):
    """Net units the opponent has added to the market over the last game day.

    The engine moves market inventory by exactly ``our trades + theirs - the
    town drain`` (`kaggriculture.py:635,642,712-717`), so subtracting the
    quantity we ourselves put through the market leaves ``their sales - the
    drain``.  Summed over a day, a positive figure means the market is filling
    faster than the town empties it.  That is a statement about tomorrow's
    price rather than today's: the quote is going to be lower, so waiting for a
    reserve price is waiting for something that is not coming.

    Deliberately not modelled: the town drain itself.  Omitting it is what
    makes the figure mean *net* oversupply rather than gross opponent volume,
    and net oversupply is the condition that actually makes patience lose.
    """
    inventory = market_state.get("inventory", {}) if isinstance(market_state, dict) else {}
    memory = _SUPPLY_MEMORY.get(player)
    # A step that does not advance is a new episode in a reused process.
    if memory is None or step <= memory["step"]:
        memory = {"step": step, "inventory": {}, "traded": {}, "history": {}}
        _SUPPLY_MEMORY[player] = memory

    history = memory["history"]
    for item, level in inventory.items():
        if item not in PRODUCTS:
            continue
        previous = memory["inventory"].get(item)
        if previous is None:
            continue
        residual = (int(level) - previous) - memory["traded"].get(item, 0)
        window_residuals = history.setdefault(item, deque(maxlen=window))
        window_residuals.append(residual)

    memory["step"] = step
    memory["inventory"] = {
        item: int(level) for item, level in inventory.items() if item in PRODUCTS
    }
    memory["traded"] = {}
    # A partial window would read a single harvest burst as a trend.
    return {
        item: sum(residuals)
        for item, residuals in history.items()
        if len(residuals) == residuals.maxlen
    }


def _record_issued_orders(player, orders):
    """Remember what we put through the market so the next turn can net it out."""
    memory = _SUPPLY_MEMORY.get(player)
    if memory is None:
        return
    traded = memory["traded"]
    for order in orders:
        if len(order) != 3 or order[1] not in PRODUCTS:
            continue
        if order[0] == "SELL":
            traded[order[1]] = traded.get(order[1], 0) + int(order[2])
        elif order[0] == "BUY_PRODUCT":
            traded[order[1]] = traded.get(order[1], 0) - int(order[2])


def _market_actions(
    farm, private, day, tiles, livestock, market_state,
    projected_harvest_units=0,
    strawberry_priority_day=STRAWBERRY_PRIORITY_DAY,
    strawberry_target=STRAWBERRY_TARGET,
    melon_target=MELON_TARGET,
    supply_streak=None,
    episode=None,
):
    episode = episode or _episode_config()
    final_day = episode["final_liquidation_day"]
    last_planting_day = episode["last_planting_day"]
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
    if day >= final_day:
        desired_hands = min(HANDS_PER_DAY, desired_hands + 1)
    hires_today = int(farm.get("hires_today", 0))
    for hire_index in range(hires_today, desired_hands):
        hire_cost = HIRE_COSTS[hire_index] * episode["farm_hand_cost_mult"]
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
        projected_harvest_units, supply_streak,
        shed_capacity=episode["shed_capacity"], final_liquidation_day=final_day,
    )[:MAX_SELL_ORDER_TYPES]
    market.extend(sell_orders)

    # Milk is the first scalable premium revenue stream.  Four cows keep the
    # operational burden bounded while giving the crop engine time to fund
    # further expansion.
    unlocked_count = len(farm.get("unlocked_quadrants", ["NW"]))
    compact_cow_target = min(COMPACT_COW_TARGET, len(_compact_cow_slots(tiles)))
    cows_to_buy_max = 1 if money < 1200 else 2
    cows_to_buy = min(cows_to_buy_max, max(0, compact_cow_target - livestock["owned_cows"]))
    cows_ordered = 0
    if day <= 20 and cows_to_buy and money >= 400 * cows_to_buy + 300:
        market.append(["BUY_ANIMAL", "COW", cows_to_buy])
        money -= 400 * cows_to_buy
        cows_ordered = cows_to_buy

    geese_to_buy = max(0, EARLY_GOOSE_TARGET - livestock["owned_geese"])
    geese_ordered = 0
    if day <= 2 and geese_to_buy and money >= geese_to_buy * 300 + 700:
        market.append(["BUY_ANIMAL", "GOOSE", geese_to_buy])
        money -= geese_to_buy * 300
        geese_ordered = geese_to_buy

    early_sheep_to_buy = max(0, EARLY_SHEEP_TARGET - livestock["owned_sheep"])
    early_sheep_ordered = 0
    if day <= 2 and early_sheep_to_buy and money >= early_sheep_to_buy * 500 + 700:
        market.append(["BUY_ANIMAL", "SHEEP", early_sheep_to_buy])
        money -= early_sheep_to_buy * 500
        early_sheep_ordered = early_sheep_to_buy

    sheep_to_buy = min(SHEEP_PURCHASE_BATCH, max(0, LATE_SHEEP_TARGET - livestock["owned_sheep"]))
    sheep_ordered = 0
    sheep_budget = sheep_to_buy * 500 + sheep_to_buy * BASE_PRICES["WHEAT"] * 3
    herd_stable = not livestock["at_risk"] and livestock["unplaced_animals"] == 0
    if (
        SHEEP_PURCHASE_START_DAY <= day <= SHEEP_PURCHASE_END_DAY
        and herd_stable
        and sheep_to_buy
        and money >= sheep_budget + 300
    ):
        market.append(["BUY_ANIMAL", "SHEEP", sheep_to_buy])
        money -= sheep_to_buy * 500
        sheep_ordered = sheep_to_buy

    # Livestock is only a worthwhile capital investment if placed animals can
    # be fed through the construction phase.  Buy a small wheat reserve before
    # the first cow can become hungry instead of relying on a crop that has not
    # matured yet.
    wheat_on_hand = int(private.get("shed", {}).get("WHEAT", 0)) + sum(
        int(inventory.get("WHEAT", 0)) for inventory in private.get("inventories", [])
    )
    protected_animals = (
        livestock["owned_animals"] + cows_ordered
        + geese_ordered + early_sheep_ordered + sheep_ordered
    )
    # Expose WHEAT_SHED to the BFS by hiding it in the first tile temporarily
    # (since _target_priority takes seed_budget but not shed)
    wheat_shed = private.get("shed", {}).get("WHEAT", 0)
    seed_budget = private.get("seeds", {}).copy()
    seed_budget["WHEAT_SHED"] = wheat_shed
    wheat_needed = max(0, protected_animals * WHEAT_RESERVE_DAYS - wheat_on_hand)
    # Liquidation releases the feed reserve on the final day, and the escape
    # check only runs in the end-of-day update, so an animal left unfed then
    # costs nothing.  Without this guard the reserve is sold and re-bought on
    # the same turn, every episode.
    if day < final_day and protected_animals and wheat_needed and money >= wheat_needed * BASE_PRICES["WHEAT"]:
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
        strawberry_priority_day,
        strawberry_target,
        melon_target,
        last_planting_day,
        livestock["owned_animals"] + cows_ordered + geese_ordered + early_sheep_ordered + sheep_ordered,
    )
    current_crop_counts = {}
    for row in tiles:
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                crop_name = tile.get("crop")
                current_crop_counts[crop_name] = current_crop_counts.get(crop_name, 0) + 1

    if crop is None:
        target_seed_count = 0
    else:
        base_target = {
            "STRAWBERRY": strawberry_target,
            "TOMATO": TOMATO_TARGET,
            "MELON": melon_target,
            "WHEAT": WHEAT_TILE_CAP,
        }.get(crop, SEED_BUFFER)
        target_seed_count = max(0, base_target - current_crop_counts.get(crop, 0))
    crop_seed_count = int(private.get("seeds", {}).get(crop, 0))
    payroll_reserve = 0 if day >= final_day else (
        sum(HIRE_COSTS[:desired_hands]) * episode["farm_hand_cost_mult"]
    )
    spendable = max(0, money - payroll_reserve)
    if crop and day < last_planting_day and crop_seed_count < min(open_tiles, target_seed_count) and spendable >= CROPS[crop]["cost"]:
        quantity = min(
            MAX_SEED_PURCHASE,
            max(1, min(open_tiles, target_seed_count) - crop_seed_count),
            int(spendable // CROPS[crop]["cost"]),
        )
        if quantity:
            market.append(["BUY_SEED", crop, quantity])

    return market[:episode["max_market_orders"]]


def _desired_hands(tiles):
    """Scale payroll to the field: one worker can service six nearby tiles."""
    workload = 0
    for row in tiles:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            workload += 3 if tile.get("animal") else tile.get("kind") in {"PLANT", "WEED"}
    total_workers = max(
        5,
        (workload + CROP_WORKLOAD_PER_WORKER - 1) // CROP_WORKLOAD_PER_WORKER,
    )
    return min(HANDS_PER_DAY, total_workers - 1)


def _premium_crop_plan(town_state):
    """Use a fixed, proven premium crop configuration."""
    return (
        STRAWBERRY_PRIORITY_DAY, STRAWBERRY_TARGET, MELON_TARGET,
        FERTILIZER_BATCH_SIZE,
    )


def _next_crop(
    seeds, shed, day, tiles, prices=None,
    strawberry_priority_day=STRAWBERRY_PRIORITY_DAY,
    strawberry_target=STRAWBERRY_TARGET,
    melon_target=MELON_TARGET,
    last_planting_day=LAST_PLANTING_DAY,
    owned_animals=0,
):
    """Choose the highest-value crop whose production window still fits."""
    strawberries = sum(
        isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "STRAWBERRY"
        for row in tiles for tile in row
    )
    melons = sum(
        isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "MELON"
        for row in tiles for tile in row
    )
    open_tiles = sum(tile is None for row in tiles for tile in row)

    # Premium crops take priority — strawberry and melon are the high-value
    # engines.  Extend the planting window to capture late-season yields:
    # strawberry planted day 19 → first yield day 29; melon planted day 17 →
    # harvest day 29.
    if strawberry_priority_day <= day <= 19 and strawberries < strawberry_target:
        return "STRAWBERRY"
    if 4 <= day <= 17 and melons < melon_target:
        return "MELON"
    tomatoes = sum(
        isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "TOMATO"
        for row in tiles for tile in row
    )
    if 4 <= day <= 21 and tomatoes < TOMATO_TARGET:
        return "TOMATO"
    
    wheat = sum(
        isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "WHEAT"
        for row in tiles for tile in row
    )
    if wheat < WHEAT_TILE_CAP:
        return "WHEAT"

    return None


def _choose_worker_action(
    position, tiles, seed_budget, day, reserved, inventory, private, livestock,
    worker_index, worker_count,
    strawberry_priority_day=STRAWBERRY_PRIORITY_DAY,
    fertilizer_batch_size=FERTILIZER_BATCH_SIZE,
    turns_per_day=SUPPLY_WINDOW_TURNS,
    final_liquidation_day=FINAL_LIQUIDATION_DAY,
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
        day == final_liquidation_day
        and carrying_non_melon
        and isinstance(tile, dict)
        and (
            tile.get("kind") == "WEED"
            or (
                tile.get("kind") == "PLANT"
                and int(tile.get("yield_units", 0)) <= 0
                and 0 <= int(tile.get("max_lifespan_step", -1)) <= (day + 1) * turns_per_day
            )
        )
    ):
        reserved.add((x, y))
        return ["DIG"]
    if (
        inventory.get("MELON", 0) > 0
        or (day == final_liquidation_day and carrying_non_melon)
        or (day >= final_liquidation_day and carrying_products)
    ):
        if _is_shed_access(x, y, len(tiles)):
            return ["DROP"]
        return _move_to(x, y, tiles, _shed_targets(len(tiles)), reserved) or ["PASS"]

    livestock_action = None
    if day < final_liquidation_day:
        livestock_action = _livestock_action(
            x, y, tile, inventory, tiles, private, livestock, reserved, day,
            worker_index, fertilizer_batch_size,
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
        else _action_for_tile(
            tile, seed_budget, day, tiles, livestock, strawberry_priority_day,
            turns_per_day, final_liquidation_day,
        )
    )
    ripe_melons = sum(
        isinstance(target, dict)
        and target.get("crop") == "MELON"
        and day - int(target.get("planted_day", day)) >= CROPS["MELON"]["harvest_day"]
        for row in tiles
        for target in row
    )
    use_global_liquidation = (
        day >= final_liquidation_day and ripe_melons <= FINAL_GLOBAL_MELON_THRESHOLD
    )
    service_workers = _service_worker_count(livestock)
    crop_worker_count = max(1, worker_count - service_workers)
    crop_worker_index = worker_index - service_workers
    region = (
        None
        if use_global_liquidation or crop_worker_index < 0
        else _worker_region(tiles, crop_worker_index, crop_worker_count)
    )
    if tile is None:
        urgent_target = _nearest_target(
            x, y, tiles, seed_budget, day, reserved, livestock, urgent_only=True,
            allowed=region, strawberry_priority_day=strawberry_priority_day,
            turns_per_day=turns_per_day,
            final_liquidation_day=final_liquidation_day,
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
        x, y, tiles, seed_budget, day, reserved, livestock, allowed=region,
        strawberry_priority_day=strawberry_priority_day,
        turns_per_day=turns_per_day,
        final_liquidation_day=final_liquidation_day,
    )
    if target is None:
        target = _nearest_target(
            x, y, tiles, seed_budget, day, reserved, livestock, urgent_only=True,
            strawberry_priority_day=strawberry_priority_day,
            turns_per_day=turns_per_day,
            final_liquidation_day=final_liquidation_day,
        )
    if target is None:
        return ["PASS"]
    direction, coordinates = target
    reserved.add(coordinates)
    return [direction]


def _action_for_tile(
    tile, seed_budget, day, tiles, livestock,
    strawberry_priority_day=STRAWBERRY_PRIORITY_DAY,
    turns_per_day=SUPPLY_WINDOW_TURNS,
    final_liquidation_day=FINAL_LIQUIDATION_DAY,
):
    if day >= final_liquidation_day:
        # Nothing planted or watered on the last day can pay back, so every
        # hand-turn goes to banking yield that is already standing -- from any
        # crop or animal, not just melon.  Anything left in the ground at turn
        # 720 is worth nothing.
        return ["HARVEST"] if _has_standing_yield(tile, day) else None
    if tile is None:
        crop = _available_crop(
            seed_budget, day, tiles, livestock, strawberry_priority_day
        )
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
        day == final_liquidation_day
        and 0 <= int(tile.get("max_lifespan_step", -1)) <= (day + 1) * turns_per_day
        and int(tile.get("yield_units", 0)) <= 0
    ):
        return ["DIG"]
    if crop_data.get("ongoing") and tile.get("yield_units", 0) > 0:
        return ["HARVEST"]
    if crop_data.get("ongoing") and _expires_by_next_day(tile, day, turns_per_day):
        return ["DIG"]
    harvest_day = crop_data.get("harvest_day")
    if harvest_day is not None and day - int(tile.get("planted_day", day)) >= harvest_day:
        return ["HARVEST"]
    if _needs_water(tile, day):
        return ["WATER"]
    return None


def _available_crop(
    seed_budget, day, tiles, livestock,
    strawberry_priority_day=STRAWBERRY_PRIORITY_DAY,
):
    if day >= 26:
        return None
    available = [crop for crop in CROPS if seed_budget.get(crop, 0) > 0]
    if not available:
        return None

    owned_animals = livestock.get("owned_animals", 0) if isinstance(livestock, dict) else 0
    open_tiles = sum(tile is None for row in tiles for tile in row)

    if strawberry_priority_day <= day <= 16 and seed_budget.get("STRAWBERRY", 0) > 0:
        return "STRAWBERRY"
    if 4 <= day <= 16 and seed_budget.get("MELON", 0) > 0:
        return "MELON"
    if 4 <= day <= 21 and seed_budget.get("TOMATO", 0) > 0:
        return "TOMATO"
    # Wheat only up to the feed-sized tile cap — no uncapped fallback.
    # Carrot is removed: it realises below base, opponents plant none (D3), and
    # every tile it occupies is a tile that cannot clear weeds or grow strawberry.
    current_wheat = sum(
        isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "WHEAT"
        for row in tiles for t in row
    )
    if current_wheat < WHEAT_TILE_CAP and seed_budget.get("WHEAT", 0) > 0:
        return "WHEAT"
    return None


def _nearest_target(
    start_x, start_y, tiles, seed_budget, day, reserved, livestock, urgent_only=False,
    allowed=None, strawberry_priority_day=STRAWBERRY_PRIORITY_DAY,
    turns_per_day=SUPPLY_WINDOW_TURNS,
    final_liquidation_day=FINAL_LIQUIDATION_DAY,
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
            # Inject WHEAT_SHED into seed_budget so _target_priority can read it
            if "WHEAT_SHED" not in seed_budget:
                seed_budget["WHEAT_SHED"] = tiles[0][0].get("_wheat_shed", 0) if isinstance(tiles[0][0], dict) else 0

            priority = _target_priority(
                tiles[y][x], seed_budget, day, tiles, livestock, strawberry_priority_day,
                turns_per_day, final_liquidation_day,
            )
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


def _target_priority(
    tile, seed_budget, day, tiles, livestock,
    strawberry_priority_day=STRAWBERRY_PRIORITY_DAY,
    turns_per_day=SUPPLY_WINDOW_TURNS,
    final_liquidation_day=FINAL_LIQUIDATION_DAY,
):
    """Smaller values are assigned first across the whole farm."""
    if day >= final_liquidation_day:
        return -10 if _has_standing_yield(tile, day) else None
    if tile is None:
        return 3 if _available_crop(seed_budget, day, tiles, livestock, strawberry_priority_day) else None
    if not isinstance(tile, dict):
        return None
    if tile.get("kind") == "WEED":
        # Clearing a weed immediately protects the small worker budget from
        # accumulating a permanent traversal and planting bottleneck.
        return -1 if day < final_liquidation_day else 2
    if tile.get("kind") != "PLANT":
        return None
    crop = tile.get("crop")
    crop_data = CROPS.get(crop, {})
    if (
        day == final_liquidation_day
        and 0 <= int(tile.get("max_lifespan_step", -1)) <= (day + 1) * turns_per_day
    ):
        return -20 if int(tile.get("yield_units", 0)) > 0 else -19
    if crop_data.get("ongoing") and tile.get("yield_units", 0) > 0:
        return 0
    if crop_data.get("ongoing") and _expires_by_next_day(tile, day, turns_per_day):
        return -1
    
    harvest_day = crop_data.get("harvest_day")
    if harvest_day is not None and day - int(tile.get("planted_day", day)) >= harvest_day:
        return -2 if crop == "MELON" and day in {16, 28} else 0
    return 1 if _needs_water(tile, day) else None


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
    return day - int(tile.get("planted_day", day)) >= crop_data.get("first_yield_day", 0)


def _needs_water(tile, day):
    """Daily watering is the measured reliable policy for this workforce."""
    if (
        tile.get("crop") == "MELON"
        and int(tile.get("yield_units", 0)) >= 6
        and int(tile.get("consecutive_unwatered", 0)) == 0
    ):
        return False
    return not tile.get("watered_today", False)


def _expires_by_next_day(tile, day, turns_per_day=SUPPLY_WINDOW_TURNS):
    """True after an ongoing crop's last held yield has been collected."""
    max_lifespan_step = int(tile.get("max_lifespan_step", -1))
    return (
        tile.get("yield_units", 0) <= 0
        and max_lifespan_step >= 0
        and max_lifespan_step <= (day + 1) * turns_per_day
    )


def _in_bounds(x, y, tiles):
    return 0 <= y < len(tiles) and 0 <= x < len(tiles[y])


def _sell_orders(
    private, day, market_state, owned_animals=0, projected_harvest_units=0,
    supply_streak=None,
    surplus_to_capitulate=SUPPLY_SURPLUS_TO_CAPITULATE,
    reserve_cut=ADAPTIVE_RESERVE_CUT,
    adaptive_batch=ADAPTIVE_SELL_BATCH,
    shed_capacity=SHED_CAPACITY,
    final_liquidation_day=FINAL_LIQUIDATION_DAY,
):
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
    overflow = max(
        0,
        total_stock + incoming_stock + projected_harvest_units - shed_capacity,
    )
    fertilizer_reserve = 10 if 19 <= day <= 25 else 0
    excess_fertilizer = max(
        0, int(shed.get("FERTILIZER", 0)) - fertilizer_reserve,
    )
    if owned_animals and excess_fertilizer:
        product_stock["FERTILIZER"] = excess_fertilizer
    orders = []

    for item, quantity in sorted(product_stock.items(), key=lambda entry: (entry[0] == "WHEAT", -entry[1])):
        # Wheat is operating inventory, not sale inventory, while cows exist.
        # Three feed-days cover a placement delay and a missed route without
        # leaving an animal exposed to the two-day escape rule.
        if item == "WHEAT" and day < final_liquidation_day:
            quantity = max(0, quantity - owned_animals * WHEAT_RESERVE_DAYS)
            if quantity == 0:
                continue
        base_price = BASE_PRICES[item]
        quoted_price = float(prices.get(item, base_price))
        # W11: once the opponent is adding more of this product per day than
        # the town removes, the reserve is a price the market is not going to
        # offer again.  Cut it and clear larger tranches while the quote is
        # still above the floor, rather than meeting the reserve on day 29 at $1.
        out_supplied = (supply_streak or {}).get(item, 0) > surplus_to_capitulate
        ratio = SELL_PRICE_MULTIPLIERS.get(item, 1.0)
        if out_supplied:
            ratio *= reserve_cut
        target_price = base_price * ratio
        # FERTILIZER multiplier is 0.0: target_price = 0, so price_is_healthy is
        # always True. The W11 adaptive floor ($55 when oversupplied) governs timing;
        # the 98% below-base figure is expected, not a defect. Phi ($186k) does this.
        price_is_healthy = (
            (item == "WHEAT" and not owned_animals and quoted_price >= target_price)
            or (item not in ("WHEAT",) and quoted_price >= target_price)
        )

        # Top opponents sell melon/fertilizer below base to keep cash liquid.
        # Never block overflow selling — a shed at 100 items loses harvests.

        if day >= final_liquidation_day:
            sell_quantity = quantity
        elif price_is_healthy:
            batch = SELL_BATCHES.get(item, 4)
            if out_supplied:
                # The small tranche exists to let town consumption rebuild the
                # price between calls.  It cannot rebuild faster than the
                # opponent is destroying it, so pacing only defers the sale.
                batch = max(batch, adaptive_batch)
            sell_quantity = min(quantity, batch)
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
    owned_animals = owned_cows + owned_sheep + owned_geese
    unfed_animals = sorted(
        ((x, y, tile) for x, y, tile in animals if not tile.get("fed_today", False)),
        key=lambda entry: -int(entry[2].get("consecutive_unfed", 0)),
    )
    unfed = [(x, y) for x, y, _ in unfed_animals]
    at_risk = [
        (x, y) for x, y, tile in unfed_animals
        if int(tile.get("consecutive_unfed", 0)) >= ANIMAL_AT_RISK_UNFED_DAYS
    ]
    return {
        "animals": animals,
        "owned_cows": owned_cows,
        "owned_sheep": owned_sheep,
        "owned_geese": owned_geese,
        "owned_animals": owned_animals,
        "live_animals": len(animals),
        "unplaced_animals": max(0, owned_animals - len(animals)),
        "unfed": unfed,
        "at_risk": at_risk,
        "crop_rescue_needed": sum(
            isinstance(tile, dict)
            and tile.get("kind") == "PLANT"
            and not tile.get("watered_today", False)
            and int(tile.get("consecutive_unwatered", 0)) >= 1
            for row in tiles for tile in row
        ) >= CROP_WORKLOAD_PER_WORKER,
        "deployments_assigned": 0,
        "fertilizer_collections_assigned": 0,
    }


def _service_worker_count(livestock):
    """Workers reserved for daily feed, care, and animal-yield collection."""
    animal_count = int(livestock.get("owned_animals", 0))
    if animal_count <= 0:
        return 0
    return min(
        HANDS_PER_DAY,
        -(-animal_count // ANIMALS_PER_SERVICE_WORKER),
    )


def _livestock_action(
    x, y, tile, inventory, tiles, private, livestock, reserved, day,
    worker_index, fertilizer_batch_size=FERTILIZER_BATCH_SIZE,
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
    service_workers = _service_worker_count(livestock)

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
                return ["PICKUP", "WHEAT", _feed_batch(livestock, service_workers)]
            return _move_to(x, y, tiles, _shed_targets(len(tiles)), reserved)
        if not tile.get("cared_today", False):
            reserved.add((x, y))
            return ["CARE"]
        if tile.get("yield_units", 0) > 0:
            reserved.add((x, y))
            return ["HARVEST"]
        if (
            tile.get("fertilizer_available", False)
            and not livestock.get("unfed", [])
            and livestock.get("fertilizer_collections_assigned", 0)
            < MAX_FERTILIZER_COLLECTIONS_PER_TURN
        ):
            livestock["fertilizer_collections_assigned"] = (
                livestock.get("fertilizer_collections_assigned", 0) + 1
            )
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
        19 <= day <= 25
        and worker_index >= service_workers
        and not livestock["crop_rescue_needed"]
        and at_shed
        and private.get("shed", {}).get("FERTILIZER", 0) > 0
    ):
        return [
            "PICKUP", "FERTILIZER",
            min(fertilizer_batch_size, int(private.get("shed", {}).get("FERTILIZER", 0))),
        ]

    if worker_index >= service_workers:
        return None

    if livestock["unfed"]:
        feed_targets = livestock.get("at_risk", []) or livestock["unfed"]
        if at_shed and not carrying_wheat:
            if private.get("shed", {}).get("WHEAT", 0) > 0:
                return ["PICKUP", "WHEAT", _feed_batch(livestock, service_workers)]
            return None
        if carrying_wheat:
            return _move_to(x, y, tiles, feed_targets, reserved)
        return _move_to(x, y, tiles, _shed_targets(len(tiles)), reserved)
    if at_shed:
        for animal in ("GOOSE", "SHEEP", "COW"):
            if private.get("shed", {}).get(animal, 0) > 0:
                return ["PICKUP", animal, 1]
    return None


def _feed_batch(livestock, service_workers):
    """Wheat to carry so one trip services this worker's share of the herd."""
    return max(1, -(-len(livestock["unfed"]) // max(1, service_workers)))


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
    )[:LIVESTOCK_SLOT_TARGET]


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
