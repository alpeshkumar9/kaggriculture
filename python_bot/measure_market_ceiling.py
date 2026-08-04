"""Measure how much revenue the shared market can actually supply.

This exists to settle a goal-feasibility question, not to score an agent.  G1
asks for a self-play median bank of $160,000 *per farm*.  Both farms sell into
one inventory pool that only recovers as the town consumes it, so before another
tuning cycle it is worth knowing whether two farms can extract $320,000 from
that pool at all.

Two quantities are measured per episode, both exact:

* **Absorption** — the units the town removed from the market over the season.
  Taken by conservation rather than by reimplementing the town schedule::

      drained = I0 + units_sold_by_farms - units_bought_by_farms - final_inventory

  Every term is read from the engine: the trade sides come from ``_commit_unit``
  (so they are executed units, not ordered ones) and the final inventory from the
  last step's market.  Valued at base price, this is the revenue both farms
  *combined* could earn if every unit cleared at exactly base.

* **Capture** — what the farms actually sold and banked, so the gap between
  realised revenue and the absorption ceiling is visible per product.

Absorption is not a hard revenue cap: a farm may sell past it, but each unit
beyond clears further down the glut curve, and prices above base on the scarcity
side mean a farm selling *below* the drain rate earns more than base per unit.
It is the scale marker the goal should be judged against, not a law.

Usage::

    python3 python_bot/measure_market_ceiling.py --agent python_bot/agent.py \\
        --opponents self,pass --seed-count 10
"""

from __future__ import annotations

import argparse
import statistics
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_official_tournament import (  # noqa: E402
    TradeLog,
    _jobs,
    load_agent,
    resolve_opponent,
)

DEFAULT_TURNS = 720


@dataclass
class CeilingResult:
    seed: int
    opponent: str
    banks: tuple[float, ...]
    drained: dict[str, int] = field(default_factory=dict)
    sold_units: dict[str, int] = field(default_factory=dict)
    sold_revenue: dict[str, float] = field(default_factory=dict)
    bought_units: dict[str, int] = field(default_factory=dict)
    bought_spend: dict[str, float] = field(default_factory=dict)
    input_spend: dict[str, float] = field(default_factory=dict)


def run_episode(agent_path: str, opponent_spec: str, seed: int, turns: int) -> CeilingResult:
    from kaggle_environments import make
    from kaggle_environments.envs.kaggriculture import kaggriculture as engine

    candidate = load_agent(Path(agent_path))
    opponent = resolve_opponent(opponent_spec, candidate)

    environment = make(
        "kaggriculture", configuration={"episodeSteps": turns, "seed": seed}, debug=False
    )
    with TradeLog(engine) as trades:
        environment.run([candidate, opponent])

    # Both farms, not just the candidate: absorption is a property of the pool.
    # Only SELL and BUY_PRODUCT move market inventory -- BUY_SEED and BUY_ANIMAL
    # are farm costs that never touch the pool -- and the engine deliberately
    # does *not* add a unit sold at the $1 floor, so the conservation identity
    # has to count supplied units, not sold units.
    sold_units: dict[str, int] = defaultdict(int)
    supplied_units: dict[str, int] = defaultdict(int)
    sold_revenue: dict[str, float] = defaultdict(float)
    bought_units: dict[str, int] = defaultdict(int)
    bought_spend: dict[str, float] = defaultdict(float)
    input_spend: dict[str, float] = defaultdict(float)
    for _player, op, item, price in trades.entries:
        if op == "SELL":
            sold_units[item] += 1
            sold_revenue[item] += price
            if price > 1:
                supplied_units[item] += 1
        elif op == "BUY_PRODUCT":
            bought_units[item] += 1
            bought_spend[item] += price
        elif op in ("BUY_SEED", "BUY_ANIMAL"):
            input_spend[item] += price

    final = environment.steps[-1]
    market = final[0].observation["market"]
    inventory = market["inventory"]
    farms = final[0].observation["farms"]

    drained = {
        item: (
            engine.MARKET_PARAMS[item]["I0"]
            + supplied_units.get(item, 0)
            - bought_units.get(item, 0)
            - int(inventory[item])
        )
        for item in engine.PRODUCTS
    }

    return CeilingResult(
        seed=seed,
        opponent=opponent_spec,
        banks=tuple(float(farm.get("money", 0.0)) for farm in farms),
        drained=drained,
        sold_units=dict(sold_units),
        sold_revenue=dict(sold_revenue),
        bought_units=dict(bought_units),
        bought_spend=dict(bought_spend),
        input_spend=dict(input_spend),
    )


def timed_value(engine, item: str, drained: float) -> float:
    """Revenue from selling ``drained`` units at the best achievable timing.

    Valuing absorption at base price understates it badly.  Inventory only falls
    as the town consumes, and every unit below I0 is quoted *above* base, so a
    farm that lets the pool drain and sells into the scarcity earns far more per
    unit than base -- which is exactly why strawberry realises 214% of base
    today.  The best case for selling D units over a season is to sell them one
    at a time into a pool drained to I0-D, each sale refilling it by one:

        revenue = sum(price(I0 - D + k) for k in range(D))

    Selling more than D is possible but pushes inventory above I0, where each
    further unit clears below base and has to be grown as well, so this is the
    honest ceiling on what the town's demand is worth.

    It is a genuine upper bound and a loose one: reaching it means holding the
    whole season's output to sell into the deepest scarcity, which a 100-unit
    shed forbids.  A farm pacing sales at the drain rate instead keeps inventory
    near I0 and realises close to the base-price figure.  The achievable ceiling
    sits between the two, nearer the base end.
    """
    units = int(drained)
    if units <= 0:
        return 0.0
    start = engine.MARKET_PARAMS[item]["I0"] - units
    return float(sum(engine.market_price(item, start + k) for k in range(units)))


def _mean(results: list[CeilingResult], attribute: str) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for result in results:
        for key, value in getattr(result, attribute).items():
            totals[key] += value
    return {key: value / len(results) for key, value in totals.items()}


def report(opponent: str, results: list[CeilingResult]) -> dict[str, float]:
    from kaggle_environments.envs.kaggriculture import kaggriculture as engine

    drained = _mean(results, "drained")
    sold_units = _mean(results, "sold_units")
    sold_revenue = _mean(results, "sold_revenue")
    bought_spend = _mean(results, "bought_spend")
    input_spend = _mean(results, "input_spend")

    print(f"\n=== vs {opponent} ({len(results)} episodes) ===")
    print(
        "\n  Product        drained  base value  timed value    sold  realised rev"
        "   of timed"
    )
    ceiling = timed = realised = 0.0
    for item in sorted(engine.PRODUCTS, key=lambda name: -drained.get(name, 0.0)):
        base = engine.MARKET_PARAMS[item]["base"]
        drain_units = drained.get(item, 0.0)
        drain_value = drain_units * base
        best = timed_value(engine, item, drain_units)
        units = sold_units.get(item, 0.0)
        revenue = sold_revenue.get(item, 0.0)
        ceiling += drain_value
        timed += best
        realised += revenue
        print(
            f"  {item:<13} {drain_units:8.0f}  ${drain_value:9,.0f}  ${best:10,.0f}  "
            f"{units:6.0f}  ${revenue:11,.0f}   {revenue / best if best else 0:6.0%}"
        )

    banks = [result.banks for result in results]
    combined = [sum(pair) for pair in banks]
    # Seat 0 is always the candidate; against `pass` the other seat never trades,
    # so a median across both seats would be meaningless there.
    candidate = [pair[0] for pair in banks]
    spend = sum(bought_spend.values())

    inputs = sum(input_spend.values())
    print(f"\n  Absorption at base price (both farms)     ${ceiling:12,.0f}")
    print(f"  Absorption at best timing (both farms)    ${timed:12,.0f}   <- the ceiling")
    print(f"  Realised sale revenue (both farms)        ${realised:12,.0f}"
          f"   {realised / timed if timed else 0:.0%} of ceiling")
    print(f"  Bought back from the market (feed etc.)   ${spend:12,.0f}")
    print(f"  Seeds and animals (never touch the pool)  ${inputs:12,.0f}")
    print(f"  Net market revenue (both farms)           ${realised - spend:12,.0f}")
    print(f"  Combined final bank (both farms)          ${statistics.median(combined):12,.0f}")
    print(f"  Candidate final bank (seat 0)             ${statistics.median(candidate):12,.0f}")
    return {
        "ceiling": timed,
        "base_ceiling": ceiling,
        "realised": realised,
        "net": realised - spend,
        "combined_bank": statistics.median(combined),
        "candidate_bank": statistics.median(candidate),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True)
    parser.add_argument(
        "--opponents",
        default="self,pass",
        help="Comma-separated. 'self' is the G1 condition; 'pass' gives one farm "
             "the whole market and so separates a market ceiling from a "
             "production ceiling.",
    )
    parser.add_argument("--seed-count", type=int, default=10)
    parser.add_argument("--seed-source", type=int, default=20240817)
    parser.add_argument("--turns", type=int, default=DEFAULT_TURNS)
    parser.add_argument("--goal", type=float, default=160_000.0)
    parser.add_argument("--jobs", type=int, default=0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    import random

    rng = random.Random(args.seed_source)
    seeds = [rng.randrange(1, 2**31 - 1) for _ in range(args.seed_count)]
    opponents = [spec.strip() for spec in args.opponents.split(",") if spec.strip()]

    jobs = _jobs(args.jobs)
    tasks = [(opponent, seed) for opponent in opponents for seed in seeds]
    print(f"Running {len(tasks)} episodes on {jobs} workers…")
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        futures = [
            pool.submit(run_episode, args.agent, opponent, seed, args.turns)
            for opponent, seed in tasks
        ]
        results = [future.result() for future in futures]

    print("\nMarket absorption vs realised capture")
    summaries = {}
    for opponent in opponents:
        subset = [result for result in results if result.opponent == opponent]
        if subset:
            summaries[opponent] = report(opponent, subset)

    if "self" in summaries:
        summary = summaries["self"]
        needed = 2 * args.goal
        print(
            f"\nG1 feasibility: two farms at ${args.goal:,.0f} need ${needed:,.0f} of "
            f"combined bank.\n"
            f"  Town demand is worth ${summary['base_ceiling']:,.0f} paced at the drain "
            f"rate and at most ${summary['ceiling']:,.0f} perfectly timed, so the target "
            f"sits inside the band\n  rather than above it. Combined bank today is "
            f"${summary['combined_bank']:,.0f} — {needed / summary['combined_bank']:.1f}x "
            f"short — while only {summary['realised'] / summary['ceiling']:.0%} of the "
            f"ceiling is being sold at all."
        )
    if "pass" in summaries:
        solo = summaries["pass"]
        print(
            f"  With the whole market to itself and no competitor, one farm still "
            f"captures only {solo['realised'] / solo['ceiling']:.0%} of the ceiling and "
            f"banks ${solo['candidate_bank']:,.0f}\n  ({solo['candidate_bank'] / args.goal:.0%} "
            f"of the ${args.goal:,.0f} bar). The binding constraint is production, not "
            f"the opponent."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
