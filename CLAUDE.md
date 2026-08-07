# CLAUDE.md — Kaggriculture

Guidance for Claude Code when working in this repository.

## Read these first

The operating rules for this repo live in **[`AGENTS.md`](AGENTS.md)** — read it before
making any code change, and follow all seven of its Core Operational Rules. It applies to
Claude exactly as written.

Mandatory context before touching bot logic:

| File | Why |
| --- | --- |
| [`overview.md`](overview.md) | Full competition spec: rules, action formats, price curves, yields, town demand, observation schema. All bot logic must match it. |
| [`implementation_plan.md`](implementation_plan.md) | The goal, the replay-driven diagnosis (D1–D6), winner patterns (P1–P7), work items (W0–W9), and the validation gate. **This is the source of truth for what to do next.** |
| [`python_bot/TEST_STRATEGY.md`](python_bot/TEST_STRATEGY.md) | Release criteria and benchmark tiers. |
| [`walkthrough.md`](walkthrough.md) | Running record of what has actually been measured. |

## What this project is

A submission bot for the Kaggle Kaggriculture simulation competition ($50,000, ends
30 September 2026). Two agents each manage a 10×10 farm over 720 turns and compete for the
most cash. Ranking is Bradley-Terry on **win/loss only — coin margin does not affect
rating.**

- `python_bot/agent.py` — the submission. Single self-contained `agent(observation, configuration)`.
- `python_bot/run_official_tournament.py` — the release gate.
- `web/` — React/Vite simulator and visualiser.
- `logs/` — official ladder replay JSON. The evidence base for every claim in the plan.

## The goal

**There is no fixed win-rate target and no threshold that counts as "done."** The live
competition is a continuous Bradley-Terry skill ladder (`overview.md`, "Ranking System"):
submissions are matched against opponents near their own current rating, win/loss moves the
rating, and as the rating climbs the matchmaking pool gets tougher. There is no bracket to
finish and no fixed opponent set to "beat all of" — the 79-opponent roster below is a fixed
sample of *past* ladder games used offline as a proxy for "would this change raise the
rating," not the live matchmaking pool. The only real objective is: **maximize win rate,
keep raising it, and never ship a change that lowers it.** A specific percentage (50%
aggregate / 25% floor) was written into this file in a past session (Cycle 6,
`implementation_plan.md`) as an interim checkpoint bookkeeping figure — it is not a
competition rule and is not a stopping point. Ignore it as a target; keep chasing the higher
number.

The `roster` tier in `run_official_tournament.py` (`--roster-goal` / `--opponent-floor`) is
still the primary **measurement** — it's the best offline proxy for rating available, built
from real Kaggle ladder replays in `logs/`, replayed via `python_bot/opponents/_ghost.py`.
Paired head-to-head against the previous artifact (`--baseline`, G2) is the more decisive
signal for any individual change, since it's a same-seed A/B comparison independent of
whatever the roster's current aggregate number happens to be.

Last recorded checkpoint (Cycle 11, `implementation_plan.md`, 2026-08-06): roster win rate
15/25 (60%), median bank $104,344; head-to-head vs the previous artifact 36/60 (60%);
self-play median $106,984; frozen-adversary guard 58/60 (97%). The roster was since
regenerated (commit `c0b5a0b`) and grew to 79 opponents; the 31/79 (39%) figure recorded
right after that regeneration is now itself stale. **Current verified baseline (2026-08-08,
`agent.py` at this commit, deterministic — the roster replays real recorded actions, so
reruns reproduce it exactly): roster 27/79 (34%); paired head-to-head vs the pre-fix
artifact 62/120 (52%, n=120 — a smaller n=60 run initially read as a 45% regression, which
was noise, not signal; always re-run at n≥60 before trusting a G2 read near the boundary).**
Re-measure with `run_official_tournament.py` before trusting any older number in this file,
and update this line when it moves.

Landed fix (2026-08-08): `_market_actions`' payroll-reserve calculation was reserving cash
for the *entire* day's hiring cost from index 0 (`HIRE_COSTS[:desired_hands]`) even though
hands already hired that day (via `hires_today` and the current turn's HIRE loop) were
already paid for out of `money` — double-reserving and starving `BUY_SEED` orders. Fixed to
reserve only the unhired remainder (`HIRE_COSTS[hired_through:desired_hands]`). Found via
turn-by-turn tracing of a real lost roster game (`replay_90462373`): candidate money was
stuck near $0–90 for days 5–11 while workers spent 30–46% of their turns on `PASS` because
no seeds were affordable, while the opponent front-loaded a seed purchase on day 0 and paced
hiring more conservatively. Verify with `--seed-count 60` or higher before trusting any G2
read on future changes to this function — it is noisy at n=60 (30 seed-pairs).

**Self-play bank (G1) is a capability tracker, not a gate.** Currently ~$80k. Do not accept
or reject a change on G1 alone. Self-play is a *mirror match* — the opponent is a copy of the
candidate — so a symmetric improvement lifts both sides and win rate stays pinned near 50%.
Three changes have now raised self-play bank while head-to-head stayed at 50%, 52% and 23%.

The retired $160,000 target is above the best score by any agent in any analysed replay
($125,896) and above what this agent banks with no competitor at all ($133,477). Ladder
opponents finish at $84,682–$125,241 — a range we are already inside. See the plan's Cycle 3
callout before reintroducing any bank-based gate.

## Non-negotiables

1. **Benchmark before claiming anything.** Any change that alters game decisions goes through
   `run_official_tournament.py` before being called verified, packaged, or submitted. If the
   engine cannot run, report the benchmark as **blocked** — never substitute reasoning for a
   measurement.

2. **The built-in opponents are a liveness test, not a benchmark.** Measured: `pass` $3,000,
   `random` $0, `starter` $3,514 — against real ladder opponents at $84,682–$125,241. Our
   agent scores $136,548 vs `starter` and loses 6 of 7 ladder games. **Never quote a
   vs-`starter` bank, or `RECORD_MILESTONE = 154615`, as evidence of improvement.** Use
   the replay-derived roster, self-play, and head-to-head against the previous artifact.

3. **A bank improvement without movement in the targeted metric is noise.** Each work item
   names the metric that must move and a guard that must not regress. Both are checked.

4. **No new hard-coded decision literals.** Respect the three-tier constant taxonomy in the
   plan: game constants (hard-code), configurable knobs (read from `configuration`),
   strategy targets (must become derived). Tuning numbers enter as named constants threaded
   through as parameters, as `strawberry_target` already is.

5. **Preserve submission compatibility.** `agent.py` stays a single self-contained entry
   point for `kaggle_environments` — stdlib imports only, exposing `agent(observation,
   configuration)`. It is submitted as a single file **renamed to `main.py`**, which is the
   entry-point name Kaggle requires. Never add a local-module import to it.

## Commands

```bash
python3 -m unittest python_bot.test_agent python_bot.test_agent_allocator
```

The release gate. Default `--opponents` is the replay-derived roster (`replay-roster`) — the
primary measurement, scored against `--roster-goal` / `--opponent-floor` thresholds that
exist as CLI defaults for the exit-code check, not as an accepted target (see "The goal"
above — there is no win-rate number that counts as done). Add `--baseline <path>` for the
paired head-to-head (G2, `--h2h-goal` default 60%, hard floor 50%) — treat G2 as the more
decisive per-change signal, since it's a same-seed A/B comparison independent of the
roster's current aggregate. Self-play is opt-in via `--opponents self` and is reported (G1)
but never gates. Exits non-zero when the roster gate, G2, or per-episode liveness checks
fail; a non-zero exit means "this change measurably lost," not "stop working."

```bash
python3 python_bot/run_official_tournament.py --agent python_bot/agent.py --seed-count 30 --baseline python_bot/agent_allocator.py
```

The full roster is 79 opponents and runs paired seeds against each — heavier than a quick
check.

A quick during-development check — 30 self-play seeds, no roster, no gate:

```bash
python3 python_bot/run_official_tournament.py --agent python_bot/agent.py --opponents self --seed-count 30 --no-gate
```

`kaggle_environments` accepts a **file path** as an agent, so any previous artifact works
directly as `--baseline` or in `--opponents`. Full replay JSON is off by default (it is
~25 MB per episode); pass `--replay-dir` when a replay is actually needed.

**Read the engine, don't infer it.** `kaggle_environments/envs/kaggriculture/kaggriculture.py`
is the authoritative spec — price curves, yield schedules, shop tables and the town-demand
schedule are all readable, and the agent's models are asserted against them in
`test_agent_allocator.py`.

## Working notes

- Replays in `logs/` are large (23–28 MB). Analyse them with scripts; do not read them whole.
- **Market orders in replays are intent, not execution.** Some ladder agents spam sell orders
  — 74% of theirs exceed available stock and silently fail. Reconstruct executed trades from
  state or money deltas, and state the confidence when reporting a revenue mix.
- Game state (tiles, animals, cash, quadrants) is exact and is the reliable basis for
  conclusions.
- Findings that hold across many episodes are trustworthy; single-episode observations are
  not. Label which is which.
