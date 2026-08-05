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

**Win rate ≥ 60% against an adversarial opponent** (G0), because the ladder ranks on
win/loss only — coin margin does not affect rating. Current standing: no such opponent
exists yet (W10 builds it); head-to-head against the previous artifact sits at 50–52%.

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
   self-play and head-to-head against the previous artifact.

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

The release gate. `--adversary` runs the paired G0/G3 tier against the W10 dumper — **this
is the acceptance gate**; `--baseline` adds the paired head-to-head (G2); `--smoke` adds the
vs-built-in liveness tier; self-play is the default opponent and reports G1 without gating on
it. Exits non-zero when G0/G2/G3 or the liveness checks fail.

```bash
python3 python_bot/run_official_tournament.py --agent python_bot/agent.py --seed-count 30 --smoke --adversary python_bot/opponent_dumper.py --baseline python_bot/agent_allocator.py
```

The G0 measurement alone — 30 paired seeds vs the adversary, no other tier:

```bash
python3 python_bot/run_official_tournament.py --agent python_bot/agent.py --opponents "" --adversary python_bot/opponent_dumper.py --seed-count 30
```

A quick during-development check — 30 self-play seeds, ~35s on 11 workers, no gate:

```bash
python3 python_bot/run_official_tournament.py --agent python_bot/agent.py --seed-count 30 --no-gate
```

`python_bot/opponent_dumper.py` is a **frozen test fixture** — never tune it, never re-sync
it with `agent.py`, never submit it. G0 is only comparable across cycles while it is fixed.

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
