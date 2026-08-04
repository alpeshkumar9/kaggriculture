# AI Agent Guidelines - Kaggriculture

This file contains instructions for AI coding assistants (Gemini, Codex, Claude, ChatGPT, Cursor, Antigravity, etc.) working on the **Kaggriculture** repository.

> [!IMPORTANT]  
> **MANDATORY CONTEXT READ BEFORE PROCEEDING**  
> Before making any code changes, creating implementation plans, or debugging issues, you **MUST** read the following documentation files to understand the project domain, rules, state schema, and architecture:

## Mandatory Files to Read

1. **[`overview.md`](file:///Volumes/Important/Office/White%20Way%20Web/Github/kaggriculture/overview.md)**
   * **What it contains:** The complete rules, mechanics, action formats, price curves, unit yields, town demand schedules, and observation JSON schemas for the Kaggle Kaggriculture simulation competition.
   * **Why read it:** All bot logic, action choices, price estimations, and simulation handling MUST adhere strictly to the mechanics detailed in this document.

2. **[`python_bot/README.md`](file:///Volumes/Important/Office/White%20Way%20Web/Github/kaggriculture/python_bot/README.md)**
   * **What it contains:** Architecture and test instructions for the Python submission agent (`agent.py`, `strategy_rules.py`, `test_agent.py`).

3. **[`web/README.md`](file:///Volumes/Important/Office/White%20Way%20Web/Github/kaggriculture/web/README.md)**
   * **What it contains:** Setup and running instructions for the web frontend / visualizer app.

4. **[`implementation_plan.md`](file:///Volumes/Important/Office/White%20Way%20Web/Github/kaggriculture/implementation_plan.md)** & **[`walkthrough.md`](file:///Volumes/Important/Office/White%20Way%20Web/Github/kaggriculture/walkthrough.md)**
   * **What it contains:** Current implementation state, goals, and test verifications.

---

## Workspace Structure

```
kaggriculture/
├── AGENTS.md                  # AI agent instructions (this file)
├── CLAUDE.md                  # Claude Code entry point -> defers to this file
├── logs/                      # Official ladder replay JSON (evidence base)
├── overview.md                # Full competition specification & rules
├── Kaggriculture-Kaggle-*.pdf # Original Kaggle competition PDF
├── python_bot/                # Submission bot codebase
│   ├── agent.py               # Main agent entry point (kaggle_environments compatible)
│   ├── strategy_rules.py      # Rule engine for farm management & market trading
│   ├── test_agent.py          # Unit tests & local simulation runner
│   └── README.md
└── web/                       # Web frontend / visualization interface
    ├── src/                   # React / Vite source code
    └── README.md
```

---

## Core Operational Rules for AI Agents

1. **Check Domain Rules First:** Always consult [`overview.md`](file:///Volumes/Important/Office/White%20Way%20Web/Github/kaggriculture/overview.md) whenever altering bot behavior, price logic, crop selection, feeding, watering, or market order formatting.
2. **Preserve API & Submission Compatibility:** `python_bot/agent.py` must expose a valid `agent(obs)` entry point compatible with `kaggle_environments` and Kaggle submission constraints (<=100 MiB tar.gz).
3. **Run Tests After Changes:** Always verify changes by running unit tests (e.g. `python3 -m unittest python_bot/test_agent.py` or `pytest`) and checking web build (`npm run build` in `web/`).
4. **Benchmark Every Strategy Change:** Any change to `python_bot/agent.py` that can alter game decisions must be run through `python_bot/run_official_tournament.py` before it is described as verified, packaged for release, or submitted. If the official engine is unavailable, report the benchmark as blocked and do not claim a performance improvement.

> [!WARNING]
> **The built-in opponents are not a performance benchmark.** Measured on the official
> engine: `pass` finishes at $3,000, `random` at $0, `starter` at $3,514 — while real
> ladder opponents finish at $84,682–$125,241. Our agent scores $136,548 against `starter`
> and still loses 6 of 7 ladder games. Because the market is *shared* and these opponents
> barely sell, the harness market never sees a second seller and prices do not behave as
> they do on the ladder.
>
> Treat `pass`/`random`/`starter` as a **liveness smoke test only**. For anything about
> score, use **self-play** (reproduces the real 70k–102k band) and **head-to-head against
> the previous approved artifact**. `kaggle_environments` accepts a **file path** as an
> agent, so `--opponents path/to/previous_agent.py` works today.
>
> Never quote a vs-`starter` bank, or `RECORD_MILESTONE = 154615`, as evidence that a
> strategy change helped. See `implementation_plan.md` §D6 and work item W0.

5. **Verify Against the Diagnosis, Not Just the Bank:** A change is accepted only when the
   specific metric it targets moves in the predicted direction (see the per-item acceptance
   table in `implementation_plan.md`). A bank improvement with no matching movement in the
   targeted metric is noise, not a result.

6. **The $160,000 Goal:** The bot must score **above $160,000**, measured as the **median
   final bank over ≥30 self-play seeds** (goal G1 in `implementation_plan.md`). Work does not
   stop until this is met — strategy and benchmark are iterated together in cycles until it
   is. Current standing: $70k–$102k self-play; best score by *any* agent across all analysed
   replays is $125,896.

   A bank figure without its opponent named is not a result. **Never report the goal as
   reached using a vs-`pass`/`random`/`starter` bank** — those conditions inflate by ~40%.
   When a cycle cannot distinguish two candidates, the next work item is a *benchmark*
   improvement, not a strategy change.

7. **Keep the Solution Scalable Past the Goal:** $160,000 is a milestone, not a finish line —
   the ladder converges through October 2026 and opponents keep improving. Every change must
   leave the bot tunable further:

   - **No new hard-coded decision literals.** Tuning numbers enter as named constants threaded
     through as function parameters, as `strawberry_target` / `melon_target` already are.
     A change that buries a magic number in decision code is rejected even if it improves the
     bank.
   - **Prefer derived decisions over fixed targets** where the observation allows it. Fixed
     targets are an acceptable first step; note what it would take to derive each one.
   - **Do not overfit to the current meta.** Justify changes from game mechanics (the
     glut-tolerance table at `overview.md:257-267`, the production clocks) rather than from
     "a winning replay did it."
   - **The benchmark's thresholds, seed count and opponent roster are config,** so raising
     the bar past $160,000 is a one-line change rather than a rewrite.
