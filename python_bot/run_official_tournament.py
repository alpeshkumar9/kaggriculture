"""Run Kaggriculture agents in the official Kaggle environment.

This is a release gate, not a replacement simulation.  It loads the exact
Python entry point supplied on the command line, plays deterministic matches,
writes the official replay JSON, and fails when the bot does not execute the
minimum crop-production loop.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import median
from typing import Any, Callable, Iterable


Agent = Callable[[dict[str, Any], Any], dict[str, Any]]
REQUIRED_ACTIONS = ("PLANT", "WATER", "HARVEST", "SELL")
DEFAULT_SEEDS = (1281355554, 2050554103, 1208590292, 910788726)


@dataclass
class EpisodeResult:
    opponent: str
    seed: int
    candidate_status: str
    opponent_status: str
    candidate_bank: float
    opponent_bank: float
    outcome: str
    actions: dict[str, int]
    max_plants: int
    max_weeds: int
    checks: list[str]
    replay: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", type=Path, required=True, help="Python file exposing agent(obs, configuration=None).")
    parser.add_argument("--opponents", default="pass,random,starter", help="Comma-separated official built-in opponents.")
    parser.add_argument("--seeds", default=",".join(map(str, DEFAULT_SEEDS)), help="Comma-separated deterministic episode seeds.")
    parser.add_argument("--replay-dir", type=Path, default=Path("replays/official"))
    parser.add_argument("--turns", type=int, default=720, help="Episode length; use 720 for release decisions.")
    return parser.parse_args()


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


def player_bank(step: Any, player: int) -> float:
    farms = step[player].observation.get("farms", [])
    return float(farms[player].get("money", 0.0)) if player < len(farms) else 0.0


def farm_tile_counts(step: Any, player: int) -> tuple[int, int]:
    farms = step[player].observation.get("farms", [])
    tiles = farms[player].get("tiles", []) if player < len(farms) else []
    plants = weeds = 0
    for row in tiles:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            plants += tile.get("kind") == "PLANT"
            weeds += tile.get("kind") == "WEED"
    return plants, weeds


def action_names(action: Any) -> Iterable[str]:
    if not isinstance(action, dict):
        return ()
    workers = [action.get("farmer", [])] + action.get("hands", [])
    market = action.get("market", [])
    commands = []
    for instruction in [*workers, *market]:
        if isinstance(instruction, list) and instruction:
            commands.append(str(instruction[0]))
    return commands


def evaluate_checks(actions: Counter[str], max_plants: int, max_weeds: int, candidate_status: str) -> list[str]:
    failures = []
    if candidate_status != "DONE":
        failures.append(f"candidate status is {candidate_status}, expected DONE")
    if max_plants == 0:
        failures.append("no planted crop was observed")
    for command in REQUIRED_ACTIONS:
        if actions[command] == 0:
            failures.append(f"no {command} action was issued")
    if max_weeds > 0:
        failures.append(f"{max_weeds} weed tile(s) were observed")
    return failures


def run_episode(candidate: Agent, opponent: str, seed: int, turns: int, replay_dir: Path) -> EpisodeResult:
    from kaggle_environments import make

    environment = make("kaggriculture", configuration={"episodeSteps": turns, "seed": seed}, debug=True)
    environment.run([candidate, opponent])

    commands: Counter[str] = Counter()
    max_plants = max_weeds = 0
    for step in environment.steps:
        commands.update(action_names(step[0].action))
        plants, weeds = farm_tile_counts(step, player=0)
        max_plants = max(max_plants, plants)
        max_weeds = max(max_weeds, weeds)

    final = environment.steps[-1]
    candidate_bank = player_bank(final, player=0)
    opponent_bank = player_bank(final, player=1)
    candidate_status, opponent_status = final[0].status, final[1].status
    outcome = "win" if candidate_bank > opponent_bank else "loss" if candidate_bank < opponent_bank else "tie"
    checks = evaluate_checks(commands, max_plants, max_weeds, candidate_status)

    replay_dir.mkdir(parents=True, exist_ok=True)
    replay = replay_dir / f"candidate-vs-{opponent}-seed-{seed}.json"
    replay.write_text(json.dumps(environment.toJSON()), encoding="utf-8")

    return EpisodeResult(
        opponent=opponent,
        seed=seed,
        candidate_status=candidate_status,
        opponent_status=opponent_status,
        candidate_bank=candidate_bank,
        opponent_bank=opponent_bank,
        outcome=outcome,
        actions=dict(commands),
        max_plants=max_plants,
        max_weeds=max_weeds,
        checks=checks,
        replay=str(replay),
    )


def print_summary(results: list[EpisodeResult]) -> None:
    wins = sum(result.outcome == "win" for result in results)
    losses = sum(result.outcome == "loss" for result in results)
    ties = len(results) - wins - losses
    banks = [result.candidate_bank for result in results]
    failed = [result for result in results if result.checks]
    print("\nOfficial Kaggriculture tournament")
    print(f"Episodes: {len(results)} | wins: {wins} | losses: {losses} | ties: {ties}")
    print(f"Candidate final bank — median: ${median(banks):.0f}, minimum: ${min(banks):.0f}, maximum: ${max(banks):.0f}")
    print(f"Replay/action gates: {len(results) - len(failed)}/{len(results)} passed")
    for opponent in sorted({result.opponent for result in results}):
        matchup = [result for result in results if result.opponent == opponent]
        matchup_wins = sum(result.outcome == "win" for result in matchup)
        print(
            f"  vs {opponent}: {matchup_wins}/{len(matchup)} wins, "
            f"median bank ${median([result.candidate_bank for result in matchup]):.0f}"
        )
    for result in results:
        status = "PASS" if not result.checks else "FAIL"
        print(f"[{status}] vs {result.opponent}, seed {result.seed}: ${result.candidate_bank:.0f} vs ${result.opponent_bank:.0f} ({result.outcome})")
        for failure in result.checks:
            print(f"  - {failure}")
        print(f"  replay: {result.replay}")


def main() -> int:
    args = parse_args()
    candidate = load_agent(args.agent)
    opponents = tuple(opponent.strip() for opponent in args.opponents.split(",") if opponent.strip())
    seeds = tuple(int(seed.strip()) for seed in args.seeds.split(",") if seed.strip())
    if not opponents or not seeds:
        raise ValueError("At least one opponent and one seed are required")

    results = [
        run_episode(candidate, opponent, seed, args.turns, args.replay_dir)
        for opponent in opponents
        for seed in seeds
    ]
    report = args.replay_dir / "report.json"
    report.write_text(json.dumps([asdict(result) for result in results], indent=2), encoding="utf-8")
    print_summary(results)
    print(f"Machine-readable report: {report}")
    return 1 if any(result.checks for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
