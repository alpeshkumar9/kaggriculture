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
> **Use the replay-derived roster for competitive measurement.** Every full Kaggle replay
> in `logs/` produces one exact action ghost on its original seed and seat. Run
> `python_bot/build_replay_opponents.py` after adding logs, then run the default official
> tournament. Self-play is a production tracker; previous-artifact head-to-head is the
> regression guard. A bank figure without its opponent named is not a result.

5. **Verify Against the Diagnosis, Not Just the Bank:** A change is accepted only when the
   specific metric it targets moves in the predicted direction (see the per-item acceptance
   table in `implementation_plan.md`). A bank improvement with no matching movement in the
   targeted metric is noise, not a result.

6. **The Primary Goal is Win Rate, Not Bank:** The ladder ranks on win/loss only — the
   coin difference does not affect rating. The acceptance gate is **G2: head-to-head win rate
   ≥ 60% against the previous approved artifact, never < 50%**, measured over ≥60 paired
   episodes (sides swapped). G1 (self-play median bank) is a capability tracker reported
   alongside G2 but never used alone to accept or reject a change. A change that raises G1
   and lowers G2 is a regression. (The $160,000 G1 target was retired in Cycle 3 after three
   independent changes each raised self-play bank while head-to-head stayed at 50%/52%/23%.
   See `walkthrough.md` Cycle 3, premise 8.)

   A bank figure without its opponent named is not a result. Never report the goal as
   reached from a non-competitive fixture.
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
     the bar is a one-line change rather than a rewrite.

---

## Negative-Result Database Rules

Cycles 1–13 have already measured and closed the most tempting strategy directions.
Re-proposing a closed direction wastes a benchmark run (~35 s) and produces false confidence
when a re-try scores differently due to seed variance.

8. **Read `walkthrough.md` before proposing any strategy change.** Every cycle records what
   was changed, what metric it targeted, and whether it was accepted or rejected with exact
   numbers. If a proposal matches a rejected experiment, do not re-propose it without a new
   hypothesis that explains why the outcome would differ this time.

9. **The following directions are closed — do not re-open without new mechanistic evidence:**

   - **Sheep / wool expansion** — rejected in Cycles 3, 5, 10, 11. Root cause: labour and
     cash cannot support a larger herd without collapsing the crop loop. Symptoms: wheat
     purchases balloon to $86k–$108k/episode, strawberry revenue collapses, roster win rate
     fell from 11/17 to 4/17. Note: `LATE_SHEEP_TARGET = 6` exists in the code but has
     **never shipped** — its presence is not evidence it works. Re-opening requires a
     demonstrated feed-loop and placement fix, not just a new target value.
     **UPDATE (2026-08-07, Cycle 17):** The early-wheat change (`WHEAT_EARLY_CAP = 20`)
     reduced wheat market purchases from $10,831 → $9,323/ep, which is the mechanistic
     feed-loop improvement the closure required. KucingGanteng (`replay_90585757`, C19
     gap $1,656) runs SHEEP=6 and beats our SHEEP=4 baseline in the current meta.
     A controlled `LATE_SHEEP_TARGET = 6` test under the C19 baseline is a **valid new
     hypothesis** — it has never been run under the current feed-efficient setup.
   - **Goose / egg expansion (`EARLY_GOOSE_TARGET > 0`)** — rejected in Cycle 1. Measured
     net-negative: ~$6k egg revenue against ~$9k wheat feed cost plus ~30 hand-turns/day.
   - **Fourth land quadrant** — rejected in Cycle 1. Net-negative: more travel overhead and
     weed spawn than the extra tiles repay.
   - **Watering logic overhaul (porting `_needs_water` from `agent_allocator.py`)** —
     rejected in Cycle 3. Freed labour was spent planting wheat at net-zero margin; median
     bank fell $12.6k.
   - **Wheat surplus harvesting / opportunistic wheat selling** — measured net-zero or
     negative in Cycles 2–3. The round-trip is nearly cash-neutral; capacity freed by
     selling surplus is immediately consumed by more wheat purchases.
   - **Adaptive worker scaling past `HANDS_PER_DAY = 14`** — the cap is already at 14
     (verified `agent.py:24`). Any suggestion to raise it from a lower number has not read
     the current code.
   - **Fertilizer sell-price tuning** — closed in Cycle 15. The 98% below-base figure is
     expected: W11 adaptive capitulation sets the effective floor at $55 (base × 0.55) when
     both players oversupply fertilizer. Phi ($186k, highest observed agent) uses
     `FERTILIZER: 0.0`. Bank fell $2,490 with a 1.0 multiplier, win rate unchanged.
   - **Late-season wheat expansion (`WHEAT_LATE_DAY` / `WHEAT_LATE_CAP`)** — closed in
     Cycle 16. Three sub-runs (cap=18 day=18, cap=18 day=21, cap=12 day=18) all produced
     identical 15/35 wins. Workers planting wheat in days 18–25 compete with the live
     strawberry harvest wave (day 7–19 → harvest days 17–29), costing strawberry revenue
     that cancels the wheat gain. Phi's WHEAT peak=39 is almost certainly early-season
     front-loaded wheat (days 1–6, sold while `owned_animals=0`), not late fill-in.
     The correct W7 to implement is early-season wheat → strawberry conversion, not
     late-season fill. Re-proposing late-season wheat without a new harvest-displacement
     mitigation is not a new hypothesis.
   - **WHEAT_EARLY_CAP above 20** — closed in Cycle 18. The initial field parcel
     saturates at ~21 available tiles. Raising to 25 produced only one extra tile (peak
     21.0 vs 20.0) but caused animal loss (0.06/ep) and milk revenue collapse (below-base
     15% → 31%). Win rate fell 58% → 47%. `WHEAT_EARLY_CAP = 20` is the field saturation
     point under the two-parcel `LAND_PLAN`. Changing `LAND_PLAN` would be a prerequisite
     before raising this cap.
   - **MELON_TARGET above 15** — closed in Cycle 20. Target=18 achieved 13.7 peak tiles
     (vs 12.7 at target=15) but cost one win (`replay_90548189`, gap $348). Median bank
     improved $2,417 but win rate fell 64% → 61%. `MELON_TARGET = 15` (12.7 peak tiles)
     is the accepted optimum under the current land plan. Re-opening requires demonstrating
     the extra tile does not displace the Sida Zuo (`90548189`) matchup.
   - **STRAWBERRY_TARGET above 42** — closed in Cycle 21. Target=46 hit the tile cap (46.0
     peak) but displaced 0.9 melon tiles (12.7→11.8). Net revenue gain +$750 but win rate
     fell 64%→58% (lost 3 wins, gained 1). Field space is binding — raising strawberry costs
     melon tiles which are higher-margin. Re-opening requires a different land plan.
   - **SHEEP_PURCHASE_END_DAY as timing fix** — closed in Cycle 22. Extending from 20→25
     had zero effect (peak sheep still 4.0). Cash is the binding constraint, not the window.
     Real Kaggle games show "Sheep Purchased: 6" consistently; simulation underestimates.
   - **Melon planting before day 4** — closed in Cycle 23. Removing the `4 <= day` lower
     bound caused catastrophic failure: 3% win rate, 2.08 animals lost/ep, 40 peak weeds.
     Early wheat (days 1–3) is the **livestock feed supply** for the construction phase. It
     is not cosmetic revenue. The `4 <= day` gate is structural and must not be removed or
     lowered without simultaneously solving the livestock feed-dependency for days 1–6.
   - **COMPACT_COW_TARGET above 9** — closed in Cycles 24 and 25. `_compact_cow_slots` has 15
     hardcoded candidate positions. On most seeds ~12-13 are accessible (others LOCKED). COW=10
     + SHEEP_TARGET=6 = 16 > 15 list size → in C24, sheep collapsed 4.0 → 2.4 (−3 wins).
     In C25, the list was expanded to 18 positions — but the binding constraint is **accessible
     (unlocked) tiles ≈ 12–13**, not the list length. COW=10 + SHEEP=6 = 16 still exceeds the
     accessible ceiling → win rate fell 62% → 46% (catastrophic). `COMPACT_COW_TARGET = 9`
     (C24b) is the permanently accepted ceiling under the current LAND_PLAN (3 quadrants).
     Raising it requires buying a 4th quadrant (rejected C1) AND unlocking the extra tiles.
   - **Melon planting / seed buying window extension past day 17** — closed in Cycle 26.
     Extending the melon window from day 17 to day 18 in `_next_crop` and `_available_crop` caused
     late seed purchases that drained capital and labor during peak strawberry harvest. Win rate
     fell 62% → 52% (−10pp). `day <= 17` (planting) / `day <= 16` (seed buying) is the optimal ceiling.
   - **Mid-game wheat fill on idle tiles (days 20–25)** — closed in Cycle 27.
     Raising wheat cap from 6 to 20 on days 20–25 when `open_tiles >= 8` caused win rate to drop from
     62% → 52.8% (−9.2pp). Worker labor spent planting, watering, and harvesting late wheat competes
     directly with harvesting live strawberry ($120 base) and melon ($250 base) waves.

10. **Never delete or compress `walkthrough.md` cycles.** They are the evidence base for
    Rules 8–9. A session without them will re-propose the same experiments. If the document
    becomes unwieldy, move detailed traces to `replays/` notes with a reference — do not
    remove the rejection record or the accepted/rejected verdict.

11. **Verify current constant values before proposing changes to them.** Read the relevant
    lines of `agent.py` with `view_file` before stating what a constant currently is. The
    2026-08-07 session received a proposal to change `HANDS_PER_DAY` from 13 → 14; the file
    already had 14. A one-line check would have caught this before the benchmark was discussed.

12. **Auto-proceed through the benchmark cycle without asking permission.** Once a
    benchmark fails and the next step is deterministic (revert → record → propose next
    variant → benchmark), execute it immediately. Do not pause to confirm obvious
    continuations. Ask the user only when there is genuine ambiguity in direction — e.g.,
    choosing between two equally plausible new hypotheses, or when a result is surprising
    enough to warrant human review before proceeding.
