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

**Median final bank above $160,000 over ≥30 self-play seeds** (G1). Current standing:
$70k–$102k self-play. Best score by *any* agent across all analysed replays: $125,896.

Work iterates — strategy and benchmark together — until G1 is met, then the bar is raised.
See the Iteration Protocol in the plan.

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
   point for `kaggle_environments`, under the 100 MiB packaging limit.

## Commands

```bash
python3 -m unittest python_bot/test_agent.py
```

```bash
python3 python_bot/run_official_tournament.py --agent python_bot/agent.py --replay-dir replays/official
```

```bash
python3 python_bot/run_official_tournament.py --agent python_bot/agent.py --opponents self --seed-count 30 --replay-dir replays/self-play
```

`kaggle_environments` accepts a **file path** as an agent, so the previous approved artifact
can be used directly as an opponent for regression runs.

## Working notes

- Replays in `logs/` are large (23–28 MB). Analyse them with scripts; do not read them whole.
- **Market orders in replays are intent, not execution.** Some ladder agents spam sell orders
  — 74% of theirs exceed available stock and silently fail. Reconstruct executed trades from
  state or money deltas, and state the confidence when reporting a revenue mix.
- Game state (tiles, animals, cash, quadrants) is exact and is the reliable basis for
  conclusions.
- Findings that hold across many episodes are trustworthy; single-episode observations are
  not. Label which is which.
