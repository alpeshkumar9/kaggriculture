"""Build one runnable benchmark opponent for every full Kaggle replay log.

The builder learns crop/herd targets, expansion timing, sell batches and
reserve behavior rather than replaying one seed's action sequence. Generated
agents therefore run on unseen seeds.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median


BASE_PRICES = {
    "WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120,
    "MELON": 250, "EGG": 50, "MILK": 160, "WOOL": 200,
    "FERTILIZER": 100,
}
PRODUCTS = tuple(BASE_PRICES)
PREMIUM = {"STRAWBERRY", "MELON", "MILK", "WOOL"}
KNOWN_PLAYER_NAMES = {"Alpesh Kumar"}


def _opponent_seat(replay):
    agents = replay.get("info", {}).get("Agents", [])
    names = [entry.get("Name", "unknown") for entry in agents]
    candidates = [index for index, name in enumerate(names) if name not in KNOWN_PLAYER_NAMES]
    if len(candidates) == 1:
        return candidates[0], "non-player seat"
    rewards = replay.get("rewards") or [
        replay["steps"][-1][index].get("reward", 0) for index in range(len(names))
    ]
    seat = max(range(len(names)), key=lambda index: rewards[index])
    return seat, "higher-scoring seat (player identity absent)"


def _price_multiplier(below_fraction):
    if below_fraction >= 0.75:
        return 0.0
    if below_fraction >= 0.40:
        return 0.5
    return 1.0


def profile_replay(path):
    replay = json.loads(path.read_text(encoding="utf-8"))
    seat, selection = _opponent_seat(replay)
    agent_info = replay.get("info", {}).get("Agents", [{}])[seat]
    name = agent_info.get("Name", f"seat-{seat}")
    rewards = replay.get("rewards") or [
        replay["steps"][-1][index].get("reward", 0) for index in range(2)
    ]

    peaks = Counter()
    buys = Counter()
    buy_days = defaultdict(list)
    sell_batches = defaultdict(list)
    sell_quantity = Counter()
    below_base = Counter()
    land_days = []
    max_hands = 0
    first_seed_day = {}

    for step in replay["steps"]:
        state = step[seat]
        observation = state.get("observation") or {}
        action = state.get("action") or {}
        day = int(observation.get("day", 0))
        farms = observation.get("farms") or []
        farm = farms[seat] if seat < len(farms) else {}
        max_hands = max(max_hands, len(farm.get("hands", [])))
        counts = Counter()
        for row in farm.get("tiles", []):
            for tile in row:
                if isinstance(tile, dict):
                    item = tile.get("animal") or tile.get("crop")
                    if item:
                        counts[item] += 1
        for item, quantity in counts.items():
            peaks[item] = max(peaks[item], quantity)

        prices = (observation.get("market") or {}).get("prices", {})
        for order in action.get("market", []):
            if not order:
                continue
            operation = order[0]
            if operation == "BUY_LAND":
                land_days.append(day)
            elif operation.startswith("BUY_") and len(order) >= 3:
                item, quantity = order[1], int(order[2])
                buys[(operation, item)] += quantity
                buy_days[(operation, item)].append(day)
                if operation == "BUY_SEED":
                    first_seed_day.setdefault(item, day)
            elif operation == "SELL" and len(order) >= 3:
                item, quantity = order[1], max(1, int(order[2]))
                sell_batches[item].append(quantity)
                sell_quantity[item] += quantity
                if float(prices.get(item, BASE_PRICES.get(item, 0))) < BASE_PRICES.get(item, 0):
                    below_base[item] += quantity

    cow_target = max(0, peaks["COW"])
    sheep_target = max(0, peaks["SHEEP"])
    goose_target = max(0, peaks["GOOSE"])
    livestock_slots = max(cow_target, cow_target + sheep_target + goose_target)
    sheep_days = buy_days.get(("BUY_ANIMAL", "SHEEP"), [])
    cow_days = buy_days.get(("BUY_ANIMAL", "COW"), [])
    strawberry_day = first_seed_day.get("STRAWBERRY", 10)
    fertilizer_batches = sell_batches.get("FERTILIZER", [6])

    unique_land_days = []
    for day in land_days:
        if day not in unique_land_days:
            unique_land_days.append(day)
    land_plan = [
        [day, (1600, 3200, 6400)[index]]
        for index, day in enumerate(unique_land_days[:3])
    ]
    batches = {
        item: max(1, min(100, int(round(median(values)))))
        for item, values in sell_batches.items() if values
    }
    multipliers = {}
    below_fractions = {}
    for item in PRODUCTS:
        fraction = below_base[item] / sell_quantity[item] if sell_quantity[item] else 0.0
        below_fractions[item] = round(fraction, 3)
        multipliers[item] = _price_multiplier(fraction)

    premium_values = [value for item, values in sell_batches.items() if item in PREMIUM for value in values]
    staple_values = [value for item, values in sell_batches.items() if item not in PREMIUM for value in values]
    settings = {
        "HANDS_PER_DAY": max(4, min(13, max_hands)),
        "COW_TARGET": cow_target,
        "LIVESTOCK_SLOT_TARGET": max(1, min(20, livestock_slots)),
        "EARLY_GOOSE_TARGET": goose_target,
        "LATE_SHEEP_TARGET": sheep_target,
        "COW_PURCHASE_LAST_DAY": max(cow_days) if cow_days else 20,
        "SHEEP_PURCHASE_START_DAY": min(sheep_days) if sheep_days else 16,
        "SHEEP_PURCHASE_END_DAY": max(sheep_days) if sheep_days else 18,
        "LAND_PLAN": land_plan,
        "MELON_TARGET": max(1, peaks["MELON"]),
        "STRAWBERRY_TARGET": max(1, peaks["STRAWBERRY"]),
        "PROFILE_CROP_PLAN": [
            max(4, min(16, strawberry_day)), max(1, peaks["STRAWBERRY"]),
            max(1, peaks["MELON"]),
            max(1, min(10, int(round(median(fertilizer_batches))))),
        ],
        "PREMIUM_SELL_BATCH": max(1, min(100, int(round(median(premium_values or [8]))))),
        "STAPLE_SELL_BATCH": max(1, min(100, int(round(median(staple_values or [20]))))),
        "SELL_BATCHES": batches,
        "SELL_PRICE_MULTIPLIERS": multipliers,
    }
    return {
        "episode_id": path.stem,
        "source_file": path.name,
        "source_seed": replay.get("info", {}).get("seed"),
        "source_name": name,
        "source_seat": seat,
        "selection": selection,
        "source_bank": rewards[seat],
        "source_result": "win" if rewards[seat] > rewards[1 - seat] else "loss",
        "observed": {
            "peak_tiles": dict(peaks),
            "animal_buys": {
                item: buys[("BUY_ANIMAL", item)] for item in ("COW", "SHEEP", "GOOSE")
            },
            "land_days": unique_land_days,
            "below_base_fraction": below_fractions,
        },
        "settings": settings,
    }


def ensure_opponents_synced(force=False) -> bool:
    """Rebuild the replay-derived opponent roster from ``logs/`` if it is stale.

    Compares ``logs/*.json`` (excluding sub-episode files with a ``-`` in the
    stem) against ``opponents/profiles.json`` by key set and mtime so repeat
    calls -- e.g. once per tournament run -- are cheap when nothing changed.

    Returns:
        bool: True if a rebuild happened, False if the roster was already current.
    """
    root = Path(__file__).resolve().parents[1]
    log_dir = root / "logs"
    output_dir = Path(__file__).resolve().parent / "opponents"
    profiles_path = output_dir / "profiles.json"
    ghost_actions_path = output_dir / "ghost_actions.json"

    log_files = sorted(path for path in log_dir.glob("*.json") if "-" not in path.stem)
    log_stems = {path.stem for path in log_files}

    if not force and profiles_path.exists() and ghost_actions_path.exists():
        try:
            existing_profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
        except Exception:
            existing_profiles = None
        if existing_profiles is not None and set(existing_profiles) == log_stems:
            profiles_mtime = profiles_path.stat().st_mtime
            if all(path.stat().st_mtime <= profiles_mtime for path in log_files):
                return False

    # ghost_fidelity is measured by validate_ghosts.py, not derived from the
    # logs, so a rebuild must carry it across or the roster silently loses its
    # broken-ghost filter the next time a log is added.
    try:
        previous_fidelity = {
            episode_id: profile["ghost_fidelity"]
            for episode_id, profile in json.loads(
                profiles_path.read_text(encoding="utf-8")
            ).items()
            if profile.get("ghost_fidelity") is not None
        }
    except Exception:
        previous_fidelity = {}

    output_dir.mkdir(parents=True, exist_ok=True)
    profiles = {}
    ghost_actions = {}
    for path in log_files:
        replay = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(replay, dict) or not replay.get("steps"):
            continue
        profile = profile_replay(path)
        episode_id = profile["episode_id"]
        if episode_id in previous_fidelity:
            profile["ghost_fidelity"] = previous_fidelity[episode_id]
        profiles[episode_id] = profile
        seat = profile["source_seat"]
        ghost_actions[episode_id] = [
            (step[seat].get("action") or {"farmer": ["PASS"], "hands": [], "market": []})
            for step in replay["steps"]
        ]
    # Opponents are resolved by episode ID against profiles.json/ghost_actions.json
    # (see run_official_tournament.resolve_opponent and opponents/_profile.py,
    # opponents/_ghost.py) -- no per-episode wrapper .py file needs to exist.
    profiles_path.write_text(
        json.dumps(profiles, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    ghost_actions_path.write_text(
        json.dumps(ghost_actions, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    carried = sum(1 for p in profiles.values() if p.get("ghost_fidelity") is not None)
    unscored = len(profiles) - carried
    print(f"Built {len(profiles)} replay opponents in {output_dir}")
    if unscored:
        print(
            f"  {unscored} have no ghost_fidelity yet; run validate_ghosts.py --write "
            f"so the broken-ghost filter can see them."
        )
    return True


def main():
    ensure_opponents_synced(force=True)


if __name__ == "__main__":
    main()
