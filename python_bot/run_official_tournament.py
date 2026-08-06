"""Run Kaggriculture agents in the official Kaggle environment.

This is the release gate.  It loads the exact Python entry points supplied on
the command line, plays deterministic paired matches on the official engine,
records what was actually traded, and fails the run when the candidate is not
good enough — on score as well as on liveness.

Four tiers, per `implementation_plan.md`:

* **roster** — paired matches against every replay-derived Kaggle opponent.
  This is the default and primary release measurement.
* **self-play** — an optional production tracker. Two real sellers push into
  one shared price curve, but mirror-match wins are not a competitive gate.
* **head-to-head** — candidate vs ``--baseline`` (the previous approved
  artifact), sides swapped on every seed (goal G2).

Diagnostics are exact: ``_commit_unit`` in the official engine is wrapped for
the duration of an episode, so every executed trade — not every *ordered*
trade — is recorded with the price it actually cleared at.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import shutil
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path
from statistics import median
from typing import Any, Callable, Iterable


Agent = Callable[..., dict[str, Any]]
REQUIRED_ACTIONS = ("PLANT", "WATER", "HARVEST", "SELL")
DEFAULT_SEEDS = (1281355554, 2050554103, 1208590292, 910788726)

# Weeds are worthless at turn 720 and the labour is worth more on harvesting and
# selling, so the cap is only enforced while weeds still cost yield (P6).
MAX_ACCEPTABLE_WEEDS = 10
WEED_CHECK_LAST_DAY = 25

# G1 is a capability tracker, reported and never gated on (see the Cycle 3
# callout in implementation_plan.md): three changes have raised self-play bank
# while head-to-head win rate stayed at 50%, 52% and 23%.
REPORT_MEDIAN_BANK = 160_000
# G2: candidate must not lose to the previous approved artifact.
GOAL_HEAD_TO_HEAD_WIN_RATE = 0.60
GOAL_HEAD_TO_HEAD_FLOOR = 0.50

ROSTER_TOKEN = "replay-roster"
ROSTER_WIN_RATE = 0.50
ROSTER_OPPONENT_FLOOR = 0.25


@dataclass
class EpisodeResult:
    opponent: str
    seed: int
    swapped: bool
    candidate_status: str
    opponent_status: str
    candidate_bank: float
    opponent_bank: float
    outcome: str
    actions: dict[str, int]
    max_plants: int
    max_weeds: int
    max_weeds_scored: int
    checks: list[str]
    replay: str = ""
    # Diagnostics (candidate side only).
    revenue: dict[str, float] = field(default_factory=dict)
    units_sold: dict[str, int] = field(default_factory=dict)
    realised_price: dict[str, float] = field(default_factory=dict)
    below_base_fraction: dict[str, float] = field(default_factory=dict)
    spend: dict[str, float] = field(default_factory=dict)
    peak_tiles: dict[str, int] = field(default_factory=dict)
    peak_animals: int = 0
    final_animals: int = 0
    animals_lost: int = 0
    unharvested_value: float = 0.0
    final_shed_units: int = 0
    herd_complete_day: int = -1


# --------------------------------------------------------------------------
# agent loading
# --------------------------------------------------------------------------


def load_agent(path: Path) -> Agent:
    source = path.resolve()
    if not source.is_file():
        raise ValueError(f"Agent file does not exist: {source}")

    module_name = f"candidate_{source.stem}_{abs(hash(source))}"
    spec = importlib.util.spec_from_file_location(module_name, source)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load agent file: {source}")

    parent = str(source.parent)
    sys.path.insert(0, parent)
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(parent)

    candidate = getattr(module, "agent", None)
    if not callable(candidate):
        raise ValueError(f"{source.name} must expose callable agent(obs, configuration=None)")
    return candidate


def resolve_opponent(spec: str, candidate: Agent) -> Any:
    """Resolve self-play or an explicit local agent; weak built-ins are excluded."""
    if spec == "self":
        return candidate
    if spec.endswith(".py"):
        return load_agent(Path(spec))
    raise ValueError(
        f"Unsupported opponent {spec!r}; use 'self', '{ROSTER_TOKEN}', or an agent .py path"
    )


def replay_roster_entries() -> tuple[tuple[str, int, bool], ...]:
    """Return ghost path, source seed, and candidate-side swap flag."""
    directory = Path(__file__).resolve().parent / "opponents"
    profiles = json.loads((directory / "profiles.json").read_text(encoding="utf-8"))
    return tuple(
        (
            str(directory / f"replay_{episode_id}.py"),
            int(profile["source_seed"]),
            int(profile["source_seat"]) == 0,
        )
        for episode_id, profile in sorted(profiles.items())
    )


def clean_generated_replays() -> list[Path]:
    """Remove bulky raw replay directories while preserving compact reports."""
    root = Path(__file__).resolve().parents[1] / "replays"
    root.mkdir(parents=True, exist_ok=True)
    removed = []
    for child in root.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
            removed.append(child)
    return removed


# --------------------------------------------------------------------------
# exact trade recording
# --------------------------------------------------------------------------


class TradeLog:
    """Wrap the engine's ``_commit_unit`` so only *executed* units are counted.

    Ladder agents spam infeasible orders; ordered quantity is intent, not
    execution.  Wrapping the commit point removes that ambiguity entirely.
    """

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.original_commit = engine._commit_unit
        self.original_market = engine._process_market
        # Live farm dicts for the running episode; step observations are
        # per-step snapshots, so identity has to be captured mid-episode.
        self.live_farms: list[dict] = []
        self.entries: list[tuple[int, str, str, float]] = []

    def __enter__(self) -> "TradeLog":
        original_commit = self.original_commit
        original_market = self.original_market
        entries = self.entries
        log = self

        def logged_market(state, env):
            log.live_farms = state[0].observation.farms
            return original_market(state, env)

        def logged_commit(op, item, price, farm, private, market, *engine_args):
            # ``shed_capacity`` became an explicit seventh argument in
            # kaggle-environments 1.32.4.  Forward optional engine arguments so
            # the diagnostic wrapper remains compatible with both engine APIs.
            ok = original_commit(
                op, item, price, farm, private, market, *engine_args,
            )
            if ok:
                player = next(
                    (i for i, candidate in enumerate(log.live_farms) if candidate is farm), -1
                )
                entries.append((player, op, item, float(price)))
            return ok

        self.engine._process_market = logged_market
        self.engine._commit_unit = logged_commit
        return self

    def __exit__(self, *exc: Any) -> None:
        self.engine._commit_unit = self.original_commit
        self.engine._process_market = self.original_market

    def for_player(self, player: int) -> list[tuple[str, str, float]]:
        return [(op, item, price) for owner, op, item, price in self.entries if owner == player]


# --------------------------------------------------------------------------
# per-episode measurement
# --------------------------------------------------------------------------


def player_bank(step: Any, player: int) -> float:
    farms = step[0].observation.get("farms", [])
    return float(farms[player].get("money", 0.0)) if player < len(farms) else 0.0


def farm_tile_counts(step: Any, player: int) -> tuple[int, int]:
    farms = step[0].observation.get("farms", [])
    tiles = farms[player].get("tiles", []) if player < len(farms) else []
    plants = weeds = 0
    for row in tiles:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            plants += tile.get("kind") == "PLANT"
            weeds += tile.get("kind") == "WEED"
    return plants, weeds


def crop_tile_counts(step: Any, player: int) -> Counter[str]:
    farms = step[0].observation.get("farms", [])
    tiles = farms[player].get("tiles", []) if player < len(farms) else []
    counts: Counter[str] = Counter()
    for row in tiles:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            if tile.get("kind") == "PLANT":
                counts[tile.get("crop", "?")] += 1
            elif tile.get("animal"):
                counts[tile["animal"]] += 1
    return counts


def action_names(action: Any) -> Iterable[str]:
    if not isinstance(action, dict):
        return ()
    workers = [action.get("farmer", [])] + list(action.get("hands", []))
    market = list(action.get("market", []))
    commands = []
    for instruction in [*workers, *market]:
        if isinstance(instruction, list) and instruction:
            commands.append(str(instruction[0]))
    return commands


def evaluate_checks(
    actions: Counter[str], max_plants: int, max_weeds_scored: int, candidate_status: str
) -> list[str]:
    failures = []
    if candidate_status != "DONE":
        failures.append(f"candidate status is {candidate_status}, expected DONE")
    if max_plants == 0:
        failures.append("no planted crop was observed")
    for command in REQUIRED_ACTIONS:
        if actions[command] == 0:
            failures.append(f"no {command} action was issued")
    if max_weeds_scored > MAX_ACCEPTABLE_WEEDS:
        failures.append(
            f"{max_weeds_scored} weed tile(s) on or before day {WEED_CHECK_LAST_DAY} "
            f"(limit: {MAX_ACCEPTABLE_WEEDS})"
        )
    return failures


def unharvested_value(step: Any, player: int, engine: Any) -> float:
    farms = step[0].observation.get("farms", [])
    tiles = farms[player].get("tiles", []) if player < len(farms) else []
    total = 0.0
    for row in tiles:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            units = int(tile.get("yield_units", 0) or 0)
            if units <= 0:
                continue
            if tile.get("kind") == "PLANT":
                product = tile.get("crop")
            elif tile.get("animal"):
                product = engine.ANIMALS[tile["animal"]]["product"]
            else:
                continue
            total += units * engine.MARKET_PARAMS[product]["base"]
    return total


def run_episode(
    agent_path: str,
    opponent_spec: str,
    seed: int,
    turns: int,
    swapped: bool,
    replay_dir: str | None,
) -> EpisodeResult:
    from kaggle_environments import make
    from kaggle_environments.envs.kaggriculture import kaggriculture as engine

    candidate = load_agent(Path(agent_path))
    opponent = resolve_opponent(opponent_spec, candidate)

    seat = 1 if swapped else 0
    players: list[Any] = [opponent, candidate] if swapped else [candidate, opponent]

    environment = make(
        "kaggriculture", configuration={"episodeSteps": turns, "seed": seed}, debug=False
    )
    with TradeLog(engine) as trades:
        environment.run(players)

    turns_per_day = max(1, int(environment.configuration.get("turnsPerDay", 24)))
    commands: Counter[str] = Counter()
    max_plants = max_weeds = max_weeds_scored = 0
    peak_tiles: Counter[str] = Counter()
    peak_animals = 0
    herd_complete_day = -1
    animals_by_day: dict[int, int] = {}

    for index, step in enumerate(environment.steps):
        commands.update(action_names(step[seat].action))
        plants, weeds = farm_tile_counts(step, seat)
        max_plants = max(max_plants, plants)
        max_weeds = max(max_weeds, weeds)
        day = index // turns_per_day
        if day <= WEED_CHECK_LAST_DAY:
            max_weeds_scored = max(max_weeds_scored, weeds)
        counts = crop_tile_counts(step, seat)
        for name, value in counts.items():
            peak_tiles[name] = max(peak_tiles[name], value)
        animals = sum(counts[a] for a in ("COW", "SHEEP", "GOOSE"))
        peak_animals = max(peak_animals, animals)
        animals_by_day[day] = max(animals_by_day.get(day, 0), animals)

    for day in sorted(animals_by_day):
        if animals_by_day[day] >= peak_animals:
            herd_complete_day = day
            break

    final = environment.steps[-1]
    final_farm = final[0].observation["farms"][seat]
    candidate_bank = float(final_farm.get("money", 0.0))
    opponent_bank = player_bank(final, 1 - seat)
    candidate_status, opponent_status = final[seat].status, final[1 - seat].status
    outcome = (
        "win" if candidate_bank > opponent_bank
        else "loss" if candidate_bank < opponent_bank else "tie"
    )
    checks = evaluate_checks(commands, max_plants, max_weeds_scored, candidate_status)

    revenue: dict[str, float] = defaultdict(float)
    units_sold: dict[str, int] = defaultdict(int)
    below_base: dict[str, int] = defaultdict(int)
    spend: dict[str, float] = defaultdict(float)
    for op, item, price in trades.for_player(seat):
        if op == "SELL":
            revenue[item] += price
            units_sold[item] += 1
            if price < engine.MARKET_PARAMS[item]["base"]:
                below_base[item] += 1
        else:
            spend[item] += price

    realised = {
        item: revenue[item] / units_sold[item] for item in units_sold if units_sold[item]
    }
    below_fraction = {
        item: below_base[item] / units_sold[item] for item in units_sold if units_sold[item]
    }

    final_counts = crop_tile_counts(final, seat)
    final_animals = sum(final_counts[a] for a in ("COW", "SHEEP", "GOOSE"))
    final_private = final[seat].observation.get("private", {}) or {}
    final_shed = final_private.get("shed", {}) or {}

    replay_path = ""
    if replay_dir:
        directory = Path(replay_dir)
        directory.mkdir(parents=True, exist_ok=True)
        suffix = "-swapped" if swapped else ""
        target = directory / f"candidate-vs-{Path(opponent_spec).stem}-seed-{seed}{suffix}.json"
        target.write_text(json.dumps(environment.toJSON()), encoding="utf-8")
        replay_path = str(target)

    return EpisodeResult(
        opponent=opponent_spec,
        seed=seed,
        swapped=swapped,
        candidate_status=candidate_status,
        opponent_status=opponent_status,
        candidate_bank=candidate_bank,
        opponent_bank=opponent_bank,
        outcome=outcome,
        actions=dict(commands),
        max_plants=max_plants,
        max_weeds=max_weeds,
        max_weeds_scored=max_weeds_scored,
        checks=checks,
        replay=replay_path,
        revenue=dict(revenue),
        units_sold=dict(units_sold),
        realised_price=realised,
        below_base_fraction=below_fraction,
        spend=dict(spend),
        peak_tiles=dict(peak_tiles),
        peak_animals=peak_animals,
        final_animals=final_animals,
        animals_lost=max(0, peak_animals - final_animals),
        unharvested_value=unharvested_value(final, seat, engine),
        final_shed_units=sum(int(v) for v in final_shed.values()),
        herd_complete_day=herd_complete_day,
    )


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------


def _aggregate(results: list[EpisodeResult], attribute: str) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for result in results:
        for item, value in getattr(result, attribute).items():
            totals[item] += value
    return dict(totals)


def print_diagnostics(results: list[EpisodeResult]) -> None:
    from kaggle_environments.envs.kaggriculture import kaggriculture as engine

    if not results:
        return
    count = len(results)
    revenue = _aggregate(results, "revenue")
    units = _aggregate(results, "units_sold")
    below = defaultdict(float)
    for result in results:
        for item, value in result.below_base_fraction.items():
            below[item] += value * result.units_sold.get(item, 0)

    print("\n  Product          units/ep   revenue/ep   realised   base   below-base")
    for item in sorted(revenue, key=lambda name: -revenue[name]):
        sold = units.get(item, 0)
        realised = revenue[item] / sold if sold else 0.0
        base = engine.MARKET_PARAMS[item]["base"]
        share = below[item] / sold if sold else 0.0
        print(
            f"  {item:<14} {sold / count:8.1f}   ${revenue[item] / count:9,.0f}   "
            f"${realised:7.1f}  ${base:5}   {share:6.0%}"
        )

    spend = _aggregate(results, "spend")
    if spend:
        line = ", ".join(
            f"{item} ${value / count:,.0f}" for item, value in sorted(spend.items())
        )
        print(f"  Purchases/ep: {line}")

    tiles = _aggregate(results, "peak_tiles")
    print(
        "  Peak tiles/ep: "
        + ", ".join(f"{item} {value / count:.1f}" for item, value in sorted(tiles.items()))
    )
    print(
        f"  Herd: peak {sum(r.peak_animals for r in results) / count:.1f}, "
        f"complete day {median([r.herd_complete_day for r in results]):.0f}, "
        f"lost {sum(r.animals_lost for r in results) / count:.2f}"
    )
    print(
        f"  End of season: unharvested ${sum(r.unharvested_value for r in results) / count:,.0f}, "
        f"shed {sum(r.final_shed_units for r in results) / count:.1f} units, "
        f"peak weeds {max(r.max_weeds for r in results)}"
    )


def summarise_tier(name: str, results: list[EpisodeResult]) -> dict[str, Any]:
    banks = [result.candidate_bank for result in results]
    wins = sum(result.outcome == "win" for result in results)
    ties = sum(result.outcome == "tie" for result in results)
    failed = [result for result in results if result.checks]
    summary = {
        "tier": name,
        "episodes": len(results),
        "wins": wins,
        "ties": ties,
        "losses": len(results) - wins - ties,
        "win_rate": wins / len(results) if results else 0.0,
        "median_bank": median(banks) if banks else 0.0,
        "min_bank": min(banks) if banks else 0.0,
        "max_bank": max(banks) if banks else 0.0,
        "gate_failures": len(failed),
    }
    print(f"\n=== {name} ({len(results)} episodes) ===")
    print(
        f"  wins {wins} | ties {ties} | losses {summary['losses']} "
        f"| win rate {summary['win_rate']:.0%}"
    )
    print(
        f"  bank — median ${summary['median_bank']:,.0f}, "
        f"min ${summary['min_bank']:,.0f}, max ${summary['max_bank']:,.0f}"
    )
    print(f"  liveness gate: {len(results) - len(failed)}/{len(results)} passed")
    for result in failed:
        print(f"  [FAIL] seed {result.seed}{' swapped' if result.swapped else ''}:")
        for failure in result.checks:
            print(f"    - {failure}")
    return summary


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", type=Path, required=True, help="Python file exposing agent(obs, configuration=None).")
    parser.add_argument(
        "--opponents",
        default=ROSTER_TOKEN,
        help=f"Comma-separated opponents: '{ROSTER_TOKEN}', 'self', or agent .py paths. "
        "File opponents are played from both seats. Default: the replay-derived roster.",
    )
    parser.add_argument("--baseline", type=Path, default=None, help="Previous approved artifact; run head-to-head, sides swapped (G2).")
    parser.add_argument("--seeds", default=",".join(map(str, DEFAULT_SEEDS)))
    parser.add_argument("--seed-count", type=int, default=0, help="Generate this many reproducible seeds instead of --seeds.")
    parser.add_argument("--seed-source", type=int, default=20260804)
    parser.add_argument("--goal", type=float, default=REPORT_MEDIAN_BANK, help="G1 reference line for the self-play bank report. Never gated on.")
    parser.add_argument("--h2h-goal", type=float, default=GOAL_HEAD_TO_HEAD_WIN_RATE, help="G2: required win rate vs --baseline.")
    parser.add_argument("--roster-goal", type=float, default=ROSTER_WIN_RATE, help="Required aggregate win rate across replay opponents.")
    parser.add_argument("--opponent-floor", type=float, default=ROSTER_OPPONENT_FLOOR, help="Minimum win rate against every replay opponent.")
    parser.add_argument("--replay-dir", type=Path, default=None, help="Write full replay JSON here (large; off by default).")
    parser.add_argument("--report", type=Path, default=Path("replays/report.json"))
    parser.add_argument("--keep-old-replays", action="store_true", help="Do not remove old raw replay directories before this run; JSON reports are always retained.")
    parser.add_argument("--turns", type=int, default=720)
    parser.add_argument("--jobs", type=int, default=0, help="Parallel worker processes (default: cpu_count - 1).")
    parser.add_argument("--no-gate", action="store_true", help="Report only; always exit 0.")
    return parser.parse_args()


def _seeds_from_args(args: argparse.Namespace) -> tuple[int, ...]:
    if args.seed_count > 0:
        rng = random.Random(args.seed_source)
        return tuple(rng.randrange(1, 2**31) for _ in range(args.seed_count))
    return tuple(int(seed.strip()) for seed in args.seeds.split(",") if seed.strip())


def _jobs(requested: int) -> int:
    import os

    if requested > 0:
        return requested
    return max(1, (os.cpu_count() or 2) - 1)


def main() -> int:
    args = parse_args()
    if not args.keep_old_replays:
        removed = clean_generated_replays()
        if removed:
            print(f"Removed {len(removed)} superseded raw replay directories.")
    load_agent(args.agent)  # fail fast on a broken candidate
    seeds = _seeds_from_args(args)
    requested = tuple(o.strip() for o in args.opponents.split(",") if o.strip())
    use_replay_roster = ROSTER_TOKEN in requested
    opponents = tuple(opponent for opponent in requested if opponent != ROSTER_TOKEN)
    if not seeds:
        raise ValueError("At least one seed is required")

    jobs: list[tuple[str, str, int, int, bool, str | None]] = []
    tiers: list[tuple[str, str, bool]] = []  # (tier name, opponent spec, paired)
    for opponent in opponents:
        tiers.append(
            ("self-play", opponent, False)
            if opponent == "self"
            else ("roster", opponent, True)
        )
    if args.baseline:
        tiers.append(("head-to-head", str(args.baseline), True))

    replay_dir = str(args.replay_dir) if args.replay_dir else None
    job_tiers: list[str] = []
    for tier, opponent, paired in tiers:
        for seed in seeds:
            sides = (False, True) if paired else (False,)
            for swapped in sides:
                jobs.append((str(args.agent), opponent, seed, args.turns, swapped, replay_dir))
                job_tiers.append(tier)
    if use_replay_roster:
        for opponent, source_seed, swapped in replay_roster_entries():
            jobs.append(
                (str(args.agent), opponent, source_seed, args.turns, swapped, replay_dir)
            )
            job_tiers.append("roster")

    if not jobs:
        raise ValueError("No tournament episodes selected")

    worker_count = min(_jobs(args.jobs), len(jobs))
    print(f"Running {len(jobs)} episodes on {worker_count} workers…")
    with ProcessPoolExecutor(max_workers=worker_count) as pool:
        results = list(pool.map(run_episode, *zip(*jobs)))

    by_tier: dict[str, list[EpisodeResult]] = defaultdict(list)
    for tier, result in zip(job_tiers, results):
        by_tier[tier].append(result)

    print("\nOfficial Kaggriculture tournament")
    summaries = []
    for tier in ("self-play", "head-to-head", "roster"):
        if tier not in by_tier:
            continue
        summary = summarise_tier(tier, by_tier[tier])
        summaries.append(summary)
        print_diagnostics(by_tier[tier])

    failures: list[str] = []
    for result in results:
        if result.checks:
            failures.append(f"liveness gate failed on {result.opponent} seed {result.seed}")
            break

    roster = by_tier.get("roster", [])
    if roster:
        overall = sum(result.outcome == "win" for result in roster) / len(roster)
        print(
            f"\nRoster aggregate win rate {overall:.0%} / {args.roster_goal:.0%} — "
            f"{'MET' if overall >= args.roster_goal else 'NOT MET'}"
        )
        if overall < args.roster_goal:
            failures.append(
                f"roster win rate {overall:.0%} below {args.roster_goal:.0%}"
            )
        grouped = defaultdict(list)
        for result in roster:
            grouped[Path(result.opponent).stem].append(result)
        for name, subset in sorted(grouped.items()):
            win_rate = sum(result.outcome == "win" for result in subset) / len(subset)
            candidate_bank = median(result.candidate_bank for result in subset)
            opponent_bank = median(result.opponent_bank for result in subset)
            status = "MET" if win_rate >= args.opponent_floor else "NOT MET"
            print(
                f"  {name}: {win_rate:.0%} wins, median "
                f"${candidate_bank:,.0f} vs ${opponent_bank:,.0f} — {status}"
            )
            if win_rate < args.opponent_floor:
                failures.append(
                    f"{name} win rate {win_rate:.0%} below the "
                    f"{args.opponent_floor:.0%} floor"
                )

    self_play = by_tier.get("self-play", [])
    if self_play:
        banks = [result.candidate_bank for result in self_play]
        # Reported, never gated: self-play is a mirror match, so a symmetric
        # improvement lifts both sides and says nothing about win rate.
        print(
            f"\nG1 self-play median ${median(banks):,.0f} "
            f"(reference ${args.goal:,.0f}), worst ${min(banks):,.0f} — tracker only"
        )

    head_to_head = by_tier.get("head-to-head", [])
    if head_to_head:
        win_rate = sum(r.outcome == "win" for r in head_to_head) / len(head_to_head)
        print(
            f"G2 head-to-head win rate {win_rate:.0%} / {args.h2h_goal:.0%} — "
            f"{'MET' if win_rate >= args.h2h_goal else 'NOT MET'}"
        )
        # The floor is the hard part of G2: a candidate that loses to the
        # artifact it replaces is a regression regardless of anything else.
        if win_rate < GOAL_HEAD_TO_HEAD_FLOOR:
            failures.append(f"G2 win rate {win_rate:.0%} below the {GOAL_HEAD_TO_HEAD_FLOOR:.0%} floor")
        elif win_rate < args.h2h_goal:
            failures.append(f"G2 win rate {win_rate:.0%} below {args.h2h_goal:.0%}")

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(
            {
                "summaries": summaries,
                "episodes": [asdict(result) for result in results],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nMachine-readable report: {args.report}")

    if failures:
        print("\nGATE FAILED:")
        for failure in failures:
            print(f"  - {failure}")
    return 0 if args.no_gate or not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
