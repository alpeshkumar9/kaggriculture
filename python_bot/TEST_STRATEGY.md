# Kaggriculture Bot Test Strategy

## Purpose

This strategy prevents another submission that validates successfully but fails to farm in a real episode.  The current `test_agent.py` is a schema smoke test with a simplified simulator; its cash result is **not** a Kaggle performance result.

## Evidence behind these gates

The supplied Kaggle replays show the same failure at several ratings and seeds:

| Recording | Observed failure |
| --- | --- |
| `11.17.26 am` | By day 2, the bot has spent most of its cash but has no productive crop loop. |
| `11.26.14 am` | By day 15, the farm is largely weeds; cash is $32 while the opponent has $3,103. |
| `11.40.16 am` | By day 5, the opponent has a planted, staffed field while our farm is idle near the shed. |
| `12.14.22 pm` | Cash falls from $3,000 to $99 on day 16 and $6 on day 26; opponent reaches $55,336. |

These are not market-optimisation failures. They are action-execution failures, so functional replay checks come before economic tuning.

## Test layers

### 1. Pure decision tests (every change)

Use fixed observations to test one decision at a time.  Do not simulate the game here.

- An empty, unlocked tile with a seed returns `PLANT <crop>`.
- A worker off-target with a seed returns a legal movement action toward an empty unlocked tile.
- An unwatered plant returns `WATER` before non-essential work.
- A mature plant returns `HARVEST` before planting more seeds.
- A full or near-full shed produces sale orders.
- A worker action exists for every hired hand and is legal for its observed position.
- Before the first successful plant, market purchases are capped to a small, explicit starter budget.

The test must assert exact commands, not merely that the return value contains `farmer`, `hands`, and `market`.

### 2. State-transition trace test (every change)

Maintain a deliberately small test fixture that records action effects, not profit.  Run at least the first 72 turns and assert these invariants:

| Deadline | Required invariant |
| --- | --- |
| Turn 1 | Market order count is within the configured limit and all orders are affordable. |
| Turn 4 | At least one worker has left the shed or planted a seed. |
| End of day 1 | At least one seed has been consumed into a plant; cash remains positive. |
| End of day 3 | At least one crop has been watered on each required day; zero weeds caused by missed watering. |
| End of day 6 | At least one mature crop has been harvested and sold; cash is greater than the starting balance minus deliberate capital investments. |
| End of day 10 | No purchased animal is unplaced, unfed, or abandoned; if this cannot be guaranteed, livestock purchasing remains disabled. |

This fixture is a regression guard only. It must use the official observation and action shapes and cannot claim a leaderboard score.

### 3. Official-engine integration test (required before submission)

Run the submitted artifact in the actual `kaggle_environments` Kaggriculture environment.  The environment is not currently installed in this workspace, so this test is a required setup item, not optional work.

```bash
cd python_bot
python3 -m pip install -U kaggle-environments
python3 run_official_tournament.py --agent agent.py --replay-dir replays/official
```

`run_official_tournament.py` uses `kaggle_environments.make("kaggriculture", configuration={"episodeSteps": 720, "seed": SEED}, debug=True)`, runs the supplied agent file, and saves `env.toJSON()` for every episode.

Required checks from the resulting replay:

- agent status is `DONE`, never `ERROR`, `TIMEOUT`, or `INVALID`;
- the first 72 turns contain planting, watering, and movement actions as applicable;
- there is at least one crop harvest and sale before turn 240;
- no runaway purchases: cash cannot fall below a defined reserve before the first harvest;
- no more than 10 simultaneous weeds (a small number can spawn randomly); investigate any preventable weeds or escaped animals;
- final bank balance, not inventory value, is recorded.

Start with the replay seeds visible in the recordings: `1281355554`, `2050554103`, `1208590292`, and `910788726`.  They become permanent regressions once replay JSON is captured.

### 4. Benchmark suite (before strategic changes or upload)

This is mandatory for **every** decision-changing edit to `agent.py`. Do not
describe a result as verified, rebuild a release artifact, or submit it until
this suite has completed. If the official engine is unavailable, record the
benchmark as blocked and stop short of any performance claim.

#### What the built-in opponents actually measure

Measured on the official engine (final bank, 720 turns): `pass` $3,000,
`random` $0, `starter` $3,514. Real ladder opponents finish at
$84,682–$125,241. `agent.py` scores **$136,548 vs `starter`** and loses 6 of 7
ladder games.

The market is shared between both players. These opponents barely sell, so the
harness market never sees a second seller and prices never behave as they do in
a real match — which hides the price-crash failures that decide ladder games.

**`pass`/`random`/`starter` are a liveness tier, not a performance tier.** A
vs-`starter` bank is never evidence that a strategy change helped, and
`RECORD_MILESTONE = 154615` is a vs-weak-opponent figure that is not comparable
to a ladder score.

#### Tiers

| Tier | Matchup | Episodes | What it decides |
| --- | --- | --- | --- |
| Smoke | vs `pass`, `random`, `starter` | 4 seeds | Agent still farms and does not error. Pass/fail only. |
| **Performance** | vs previous approved artifact | ≥30 paired seeds, candidate on **both** sides | **Whether the change ships.** |
| Realism | self-play | same seeds | Behaviour under a realistic two-seller market (70k–102k band). |
| Diagnostic | any tier | — | Whether the targeted metric actually moved. |

`kaggle_environments` accepts a **file path** as an agent, so the previous
artifact can be used directly as an opponent:

```bash
python3 run_official_tournament.py --agent agent.py --opponents ../artifacts/approved_agent.py --seed-count 30 --replay-dir replays/regression
```

Report win rate with a confidence interval, median and IQR of the final bank,
error count, the diagnostic metrics below, and the worst replay link. The
official-engine tournament runner is the sole benchmark; do not substitute a
custom simulator.

#### Diagnostic metrics (required alongside the bank)

Derived from replay JSON, per episode and aggregated: revenue and units per
product; realised price vs base per product; fraction of units sold below base;
unharvested tile value at turn 720; peak tiles per crop; animals lost; peak
animal count by species.

A bank improvement with **no matching movement in the metric the change
targeted** is treated as noise, not a result. See the per-item acceptance table
in `../implementation_plan.md`.

#### Goal gate — $160,000

The project target is a **median final bank above $160,000 over ≥30 self-play seeds**
(G1 in `../implementation_plan.md`), with a worst-seed bank ≥ $120,000 and no regression
in head-to-head win rate against the previous artifact.

Self-play is the measurement condition because it is the only one that reproduces ladder
market pressure. Current standing is $70k–$102k. Report progress against G1 only —
a vs-`starter` bank is never evidence of progress toward the goal.

#### Release criteria

- 0 invalid/error episodes;
- 100% of replays meet all action-execution checks;
- candidate does not regress against the previous approved artifact on win rate
  or median bank beyond the stated tolerance;
- the targeted diagnostic metric moved in the predicted direction and no guard
  metric regressed.

> **Known harness gap.** The runner's exit code currently gates only on
> liveness checks (`result.checks`), never on score — a $40k regression still
> exits 0. It also runs 4 unpaired seeds with the candidate always on side 0.
> Work item W0 in `../implementation_plan.md` covers fixing this and is a
> blocking prerequisite for benchmarking any strategy change.

### 5. Artifact and upload gate (every submission)

Package the exact file that is tested.  For an archive, it must expose `agent` at archive-root `main.py`; `my_agent` alone is insufficient.

```bash
tar -tzf submission.tar.gz
tar -xOf submission.tar.gz main.py | rg '^def agent\('
```

Then execute the extracted archive with the official-engine smoke test.  Upload only that verified artifact, including its commit hash and benchmark report in the submission message or release notes.

## Delivery order

1. Fix the entry point and use `run_official_tournament.py` as the release gate.
2. Replace the current profit-claiming test with decision and trace assertions.
3. Implement a conservative wheat/carrot loop until it passes every replay gate.
4. Benchmark against `starter`.
5. Add one strategic feature at a time (farmhands, land, then livestock), rerunning the entire suite after each feature.

No price prediction, fertilizer optimisation, land expansion, or livestock code should be enabled until the conservative crop loop passes the official-engine replay checks.
