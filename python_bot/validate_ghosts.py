#!/usr/bin/env python3
"""Measure how faithfully each replay ghost reproduces its source game.

Ghosts in ``opponents/`` replay a real opponent's recorded action list verbatim
(see ``_ghost.py``).  That only reproduces the original game while the ghost's
farm state stays on the recorded trajectory.  As soon as it diverges -- a land
purchase that no longer fits the cash on hand, a SELL for more stock than the
shed actually holds -- the recorded actions stop matching the situation and the
ghost can collapse to a fraction of the score its human counterpart achieved.

A collapsed ghost is not a benchmark opponent, it is a free win, and it silently
inflates the roster: measured across the 132-opponent roster, 29 ghosts scored
under 80% of their original bank and the candidate beat *all 29*, lifting the
reported roster win rate from 44% to 64%.

This script scores each ghost against a neutral ``pass`` opponent on its own
source seed, so the result measures replay fidelity rather than how the ghost
fares against any particular candidate.  ``pass`` never trades, so it leaves the
shared market alone and gives the ghost the most favourable possible conditions:
a ghost that still collapses here is broken outright, not merely out-competed.
The resulting ratio is written back into ``profiles.json`` as ``ghost_fidelity``
for ``run_official_tournament.py --min-ghost-fidelity`` to filter on.
"""

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

OPPONENTS = Path(__file__).resolve().parent / "opponents"


def score_ghost(args: tuple[str, int, int, int]) -> tuple[str, float | None]:
    """Return the ghost's final bank when replayed against a passive opponent."""
    episode_id, seed, seat, turns = args
    from kaggle_environments import make
    from opponents._ghost import build_ghost_agent

    ghost = build_ghost_agent(episode_id)
    # Seat the ghost exactly where it sat in the source episode; the engine's
    # per-seat starting position and quadrant layout are not symmetric.
    players = [ghost, "pass"] if seat == 0 else ["pass", ghost]
    environment = make(
        "kaggriculture",
        configuration={"episodeSteps": turns, "seed": seed},
        debug=False,
    )
    try:
        environment.run(players)
    except Exception:
        return episode_id, None
    final = environment.steps[-1]
    if seat >= len(final):
        return episode_id, None
    return episode_id, float(final[seat].reward or 0.0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--turns", type=int, default=720)
    parser.add_argument("--jobs", type=int, default=0)
    parser.add_argument(
        "--write", action="store_true",
        help="Persist ghost_fidelity into profiles.json (otherwise report only).",
    )
    arguments = parser.parse_args()

    profiles_path = OPPONENTS / "profiles.json"
    profiles = json.loads(profiles_path.read_text(encoding="utf-8"))

    work = [
        (
            episode_id,
            int(profile["source_seed"]),
            int(profile["source_seat"]),
            arguments.turns,
        )
        for episode_id, profile in sorted(profiles.items())
        if profile.get("source_bank")
    ]
    import os
    jobs = arguments.jobs or max(1, (os.cpu_count() or 2) - 1)
    print(f"Scoring {len(work)} ghosts against a passive opponent on {jobs} workers…")

    results: dict[str, float | None] = {}
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        for episode_id, bank in pool.map(score_ghost, work):
            results[episode_id] = bank

    rows = []
    for episode_id, bank in results.items():
        source_bank = float(profiles[episode_id]["source_bank"])
        fidelity = (bank / source_bank) if (bank is not None and source_bank > 0) else 0.0
        profiles[episode_id]["ghost_fidelity"] = round(fidelity, 4)
        rows.append((fidelity, episode_id, source_bank, bank))

    rows.sort()
    broken = [r for r in rows if r[0] < 0.8]
    print(f"\n{'episode':>12}  {'original':>10}  {'ghost':>10}  fidelity")
    for fidelity, episode_id, source_bank, bank in rows[:12]:
        shown = f"{bank:,.0f}" if bank is not None else "CRASH"
        print(f"{episode_id:>12}  {source_bank:>10,.0f}  {shown:>10}  {fidelity:>6.0%}")
    print(f"\n{len(broken)}/{len(rows)} ghosts fall below 80% fidelity "
          f"({len(broken) / max(1, len(rows)):.0%} of the roster)")

    if arguments.write:
        profiles_path.write_text(json.dumps(profiles, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote ghost_fidelity into {profiles_path}")
    else:
        print("Report only; pass --write to persist ghost_fidelity.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
