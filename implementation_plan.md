# Kaggriculture — Strategy Improvement Plan (replay-driven)

**Status:** Phase 1 (schema/API compliance) complete. Phase 2 as originally written was
speculative; this revision replaces it with work items derived from measured replay evidence.

> [!IMPORTANT]
> **Cycle 1 ran on 2026-08-04. W0 landed; G1 did not move. Three premises below are now
> contradicted by measurement — read `walkthrough.md` before acting on them.**
>
> 1. **"Where the headroom is — the market, not the land" is wrong.** Every product except
>    melon trades *above* base for the entire season; the market is supply-starved, not
>    glutted. Melon is the sole exception because no shop buys it. This is the stated
>    rationale for W2 and W8, and it does not hold.
> 2. **The binding constraint is labour**, not land and not the price curves. Scaling the
>    herd from 10 to 22 animals added $29k of revenue and $27k of cost, and starved the crop
>    loop (strawberry fell to 1.6 units/tile against a possible 4.0).
> 3. **G1 and G2 actively conflict.** The Cycle-1 variant scores $86,282 self-play against
>    the incumbent's $79,407, yet loses 77% of paired head-to-heads. Since the ladder ranks
>    on win/loss only, it was rejected under this plan's own acceptance rule.
>
> Also settled: **W9b's price model is exact, not 89%.** The engine ships inside
> `kaggle_environments`, so its price function, shop tables and town-demand schedule can be
> read rather than inferred — and asserted against in tests. Prefer reading the engine to
> inferring from replays for anything mechanical.

> [!IMPORTANT]
> **Cycle 2 ran on 2026-08-05. Two more premises are now settled by measurement —
> `walkthrough.md` has the numbers.**
>
> 4. **G1 is *not* out of reach because the market is too small.** Cycle 1's ~$305k
>    absorption figure valued the town's drain at *base* price, but inventory sits below I0
>    all season so every unit is quoted above base. At achievable prices the same drain is
>    worth **$468,476**; paced at the drain rate it is $304,416. G1's $320,000 of combined
>    bank sits *inside* that band. **G1 stays as specified.**
> 5. **The binding constraint is production, and it is not the opponent.** Given the whole
>    market to itself against `pass`, the agent still sells only **34%** of the ceiling and
>    banks $133,477. Wool ($81,668), tomato ($25,956) and egg ($20,632) are at **0% capture
>    on every seed** — $128,256 an episode that nobody touches. Labour is the part of
>    production that binds first (Cycle 1), so raising output per hand-turn comes before
>    adding animals to service.

> [!CAUTION]
> **Cycle 3 ran on 2026-08-05 and closed steps 1 and 2 of Cycle 2's next-cycle list. Both
> failed, and the failures point at the acceptance gate itself, not at the strategy.**
>
> 6. **Freeing labour does not raise the bank.** Porting the allocator's `_needs_water` —
>    the strongest named lead on the labour constraint, and strictly more faithful to the
>    engine — cost **−$12,600** median. The hand-turns were genuinely freed; they were spent
>    planting wheat at net zero margin. Relieving the constraint is not sufficient while the
>    marginal use of a spare hand is worthless.
> 7. **Wool is blocked by animal escapes, not by feed or market access.** Both affordable
>    sheep configurations lost $21k–$27k. A real bug was found and confirmed en route (the
>    feed *buy* target counts unowned animals while the sell guard counts owned ones, so the
>    gap is bought and sold back daily — wheat turnover 1,706 units → 105 when fixed), but
>    with the churn removed the sheep runs still **lose 4.10 animals per episode** against a
>    baseline 0.02. Sheep are bought and then starve.
> 8. **G1 is the wrong acceptance gate, and this is now measured three times.** Self-play is
>    a *mirror match* — the opponent is a copy of the candidate, so a symmetric improvement
>    lifts both sides and the win rate cannot move off ~50% at any bank level. Three
>    independent changes improved self-play bank and did nothing to head-to-head:
>
>    | change | self-play bank | head-to-head |
>    | --- | ---: | ---: |
>    | Cycle 1 allocator | $86,282 vs $79,407 | **23%** |
>    | Cycle 3 counter fix | +$1,982 | 52% |
>    | Cycle 3 counter + standing-wheat | +$2,893 | 50% |
>
>    Premise 4 above ("G1 stays as specified") is not refuted on feasibility — the band
>    argument still holds — but it is **superseded on relevance**. The ladder ranks on
>    win/loss only. `walkthrough.md` recorded in Cycle 1 that *"G2 is the closer proxy for
>    rating than G1"*; the plan wrote that down and kept optimising G1 anyway. Cycle 3 is the
>    third payment of that cost.
>
> Also settled: **G1 asks for more bank while sharing a market than the agent earns with a
> monopoly.** Against `pass`, with no competitor at all, it banks $133,477. G1 wants $160,000
> in self-play, where an equally strong opponent is taking half the demand. That is not a
> stretch target on the same axis — it is a target on an axis the competition does not score.

---

## GOAL — beat opponents, measured against an opponent that can beat us

**The competition ranks on win/loss only.** From `overview.md`: *"The actual coin difference
in a match does not affect the rating change—only the win, loss, or tie outcome matters."*
The goal is therefore **win rate against a real adversary**, and bank is a diagnostic that
explains win rate rather than a target in its own right.

This is a revision, not a softening. G1 was the goal for Cycles 1–3 and produced three
changes that raised self-play bank while leaving head-to-head at 50%, 52% and 23%. The reason
is structural and was not appreciated when the target was set: **self-play is a mirror match**
— the opponent is a copy of the candidate. Improving the candidate improves the opponent
identically, so self-play win rate is pinned near 50% at any bank level, and self-play *bank*
measures capability without ever testing superiority. See Cycle 3 callout, premise 8.

### The target must name its measurement context

A bank figure is meaningless without stating who the opponent was — the agent scores
**$136,548 vs `starter`**, **$133,477 vs `pass`** and **$70k–$102k** against real ladder
agents, all with identical code. What changes is who is taking the other half of the demand.
Any bar quoted without its opponent is unusable, and `RECORD_MILESTONE = 154615` is a
vs-weak-opponent number (D6).

The gates, reordered so the primary one is the one the ladder actually scores:

| # | Condition | Bar | Today |
| --- | --- | --- | --- |
| **G0** | **Win rate vs the adversarial opponent** (W10), ≥30 paired seeds | **≥ 60%** | **63%** / 62% at 60 seeds |
| G2 | Head-to-head vs previous approved artifact | win rate ≥ 60%, never < 50% | **85%** |
| G3 | Worst-seed bank vs the adversary — robustness, not a lucky seed | no seed loses by > 20% | −18% at 30 seeds, **−37% at 60** |
| G4 | Smoke tier vs `pass`/`random`/`starter` | 100% pass, 0 errors | passing; 2 weed-cap misses off-tier |
| G1 | Self-play median final bank, ≥30 seeds — **capability tracker, not a gate** | report only | **$83,244** |

Today's column is W11 as measured on 2026-08-05; the pre-W11 artifact scored G0 3%, G2 50–52%,
G3 −55%, G1 $80,656.

**G0 replaces G1 as the acceptance gate.** G1 stays in the table because absolute capability
does matter against a stronger opponent — an agent that cannot produce cannot win — but it is
reported, not gated on, and **no change is accepted or rejected on G1 alone**. A change that
raises G1 and lowers G0 is a regression.

**The $160,000 figure is retired as a gate.** For the record of why, so it is not
reintroduced: it is ~27% above the best score by any agent in any analysed replay ($125,896),
and above what this agent banks with the entire market to itself and no competitor
($133,477). Meanwhile ladder opponents finish at **$84,682–$125,241** — a range the agent is
already inside at $70k–$102k. The gap that loses 6 of 7 ladder games is therefore not a
2× production gap; it is close games lost in a shared market. That is what G0 measures.

### Is there a secondary bank floor? No — decided Cycle 4

There is **no absolute bank gate at any number.** Not $160k, not $120k, not $80k. The W10
measurement settled it: the adversary wins at a median bank of **$83,366**, and it wins by a
median of only 13%. Any absolute floor above that would reject a change that beats the
adversary 70% of the time — which is the one thing the ladder actually pays for. Any floor
below it would never bind and is decoration.

What replaces it is a **relative no-collapse guard**, already written into W11: G1 may not
fall more than 10% from the accepted artifact's G1. That blocks the real failure mode — an
agent that wins by denying the opponent while producing nothing — without asserting a
production number the evidence does not support.

The feasibility argument for a higher ceiling (the untapped egg and wheat curves below) is
untouched by this. It remains a reason to *pursue* more bank; it is not a reason to *reject*
a change that banks less and wins more.

~~**G1 is the goal.**~~ Superseded by G0. Self-play remains the *cleanest* bank measurement —
two real sellers competing into a shared price curve, landing in the same 70k–102k band as
our real ladder results — which is why it is still reported. But it is a mirror match, so it
cannot separate a real improvement from one that lifts both sides equally, and that is
exactly the failure recorded in the Cycle 3 callout. G3 now measures robustness against the
W10 adversary rather than against a copy of ourselves.

For scale, kept because it is the reason $160,000 was retired rather than merely missed: the
best score across all 8 replays analysed, by anyone, is **$125,896**, and the W10 adversary —
the first local opponent that actually beats us — wins at a median of **$83,366**.

### One caveat, stated once, then we proceed

The ladder does not rank on cash. From `overview.md`: *"The actual coin difference in a match
does not affect the rating change—only the win, loss, or tie outcome matters."* Past the
point where we reliably beat opponents, extra bank buys no rating. A strategy tuned purely
for bank could even trade away win probability — for instance holding stock for a better
price and losing a close game on timing.

G2 is in the table for exactly this reason: it must not regress while G1 is pursued. If G1
and G2 ever conflict, that is a finding to surface, not to resolve silently.

### Where the headroom is — the market, not the land

Land is not the binding constraint; the price curves are. From `overview.md:257-267`, glut
tolerance differs by more than two orders of magnitude:

| Resource | Base | Price after +T units | after +2T | Verdict |
| --- | ---: | ---: | ---: | --- |
| **Egg** | $50 | **$40** (80%) | **$34** (68%) | Barely gluts — scales |
| **Wheat** | $25 | $20 (80%) | $17 (68%) | Barely gluts — scales |
| Fertilizer | $100 | $60 | $20 | Moderate |
| Tomato | $60 | $24 | $9 | Moderate |
| Carrot | $35 | $10 | $1 | Poor |
| Strawberry | $120 | **$1** | $1 | Collapses |
| Milk | $160 | **$1** | $1 | Collapses |
| Wool | $200 | **$1** | $1 | Collapses |
| Melon | $250 | **$1** | $1 | Collapses |

Every product our agent and every observed opponent leans on — strawberry, milk, wool, melon
— goes **to the $1 floor** within one field's production of oversupply. That is the ceiling
holding the whole ladder at 85k–126k. More tiles of strawberry cannot break it.

**Eggs are the untapped curve.** Across all 8 replays, total egg sales by anyone were **8
units**. A goose costs $300, first yields at 4 days, then produces **every day** at up to
2/tile/day (`overview.md:94`) — and 664 eggs above equilibrium still fetch $34. Ten geese
producing ~20 eggs/day from day 4 is roughly 500 eggs across a season into a curve that does
not crash. `EARLY_GOOSE_TARGET` is currently `0`.

Wheat has the same property from the other direction: observed prices sit at **$45–$52 all
season** (inventory drained below $I_0$ by both players buying feed), so it absorbs volume at
prices well above its $25 base.

This makes **W8 (geese/eggs)** the leading candidate for the step from ~125k to 160k, since
W1–W7 only bring us level with the best observed agents. It is a hypothesis to test, not a
certainty — the goose action cost (1 + 1 for the coop) and the feed overhead may eat the
margin.

### The solution must keep scaling past $160,000

$160,000 is a milestone, not a finish line. The competition runs to 30 September 2026 with
the ladder converging through mid-October, and opponents improve continuously. A solution
that reaches G1 and then cannot be pushed further has failed, even if it passes the gate.

**This is a design constraint on every work item, not a later phase.**

#### The tension, and how it is resolved

W1–W8 are largely **constant tuning**, and those constants come from agents scoring
118–126k. Copying their numbers caps us at their level by construction — yet G1 needs 160k.

**Resolution: go at G1 directly. Do not detour through a fully tuned Stage A.**

An earlier draft of this plan sequenced all of W1–W8 (constant tuning, ~125–140k) ahead of
W9. That was wrong: **the target is $160,000, and constant tuning cannot reach it by
construction**, because the constants come from agents at 118–126k. Time spent perfecting
numbers that W9 computes from first principles is time spent doing the allocator's job by
hand.

The clearest example is W8. Geese/eggs were identified as the untapped curve because nobody
sells eggs — but a marginal-revenue allocator evaluating every product against its own price
curve *discovers eggs automatically*. Hand-tuning `EARLY_GOOSE_TARGET` is performing the
exact calculation W9 exists to perform.

Work items therefore split by whether W9 makes them redundant:

| Keep — needed regardless of W9 | Why it survives |
| --- | --- |
| **W0** benchmark | Nothing is measurable without it. Blocking for everything. |
| **W9a** read `configuration` | Standalone bug fix. |
| **W2** distressed-sale defect | W9c rewrites `_sell_orders`, but W2 is a few lines against a ~$29k leak — cheap insurance if W9 slips. |
| **W6** starvation guard | A correctness invariant, not a tuning target. The allocator will not derive "do not let animals starve" for free. |
| **W1** sheep constants | Two constants, ~$30k measured effect (P2), strongest evidence in the plan. Near-free insurance; keep. |

| Demote to fallback values | Why W9 subsumes it |
| --- | --- |
| **W3** crop targets | Allocator derives tile counts per crop. |
| **W4** wheat feed sizing | Falls out of herd size. |
| **W5 / W7** liquidation day, late wheat pivot | Horizon effects fall out of marginal revenue against remaining turns. |
| **W8** goose/egg targets | The allocator's core calculation. The *insight* (egg's flat glut curve) stays as a validation check: if W9 does not buy geese, either the model or the allocator is wrong. |

The demoted items keep their analysis and become **seed values and a fallback path** for W9,
plus **acceptance checks on it** — if the allocator's derived melon count lands nowhere near
the ~10 rolling tiles that P3 observed, that discrepancy is a bug to investigate in one or
the other.

**Baseline for regressing W9:** today's unmodified agent, already measured at 70–102k
self-play. A tuned 140k intermediate is not needed for this and is not worth building.

Not every number should be derived, though. Three distinct kinds of constant live in
`agent.py` and they have opposite requirements:

| Tier | Examples | Rule |
| --- | --- | --- |
| **1. Game constants** — fixed by the spec | Seed costs, base prices, animal prices, land $1k/$2k/$4k, price-curve `base`/`T`/`func`/`target`, yield schedules | **Hard-code them.** `overview.md:368` states seed costs and base prices are *not configurable*, and animals/seeds sell at fixed prices. These are the *inputs to derivation*, not tuning knobs. Keep as named tables. |
| **2. Configurable knobs** — set per episode | `shedCapacity`, `maxMarketOrdersPerTurn`, `turnsPerDay`, `episodeSteps`, `boardSize`, `startingMoney`, `farmHandCostMult`, `weedSpawnChance`, town intervals | **Read from `configuration`.** Never hard-code. See the defect below. |
| **3. Strategy targets** — our choices | `STRAWBERRY_TARGET`, `MELON_TARGET`, `COMPACT_COW_TARGET`, sheep/goose targets, sell-batch sizes, `LAND_PLAN`, liquidation day | **These are the ones that must become derived** (W9). They are what caps us at the copied meta. |

**Live defect found while writing this:** `agent.py` accepts `configuration` at
`agent.py:947` and `_agent_impl` at `agent.py:69` — and **never reads it**. Every Tier-2 knob
is hard-coded or implied: `SHED_CAPACITY = 100`, `MAX_SELL_ORDER_TYPES = 5` against a
`maxMarketOrdersPerTurn` of 10, and `LAST_PLANTING_DAY`/`FINAL_LIQUIDATION_DAY` assume a
720-turn/30-day season. If Kaggle changes a default, tunes an episode, or runs the
`kaggriculture_beginner` variant, the agent silently misplays. Folded into W9 as a
prerequisite.

The existing commit *"Refactor crop planning with parameterized targets and magic number
extraction"* already moves the right way — `_market_actions` and `_next_crop` take
`strawberry_target` / `melon_target` as parameters rather than reading globals. Continue in
that direction; do not add new hard-coded numbers on top.

#### Requirements for every change

1. **Parameterise, don't hard-code.** Any new tuning number enters as a named module-level
   constant threaded through as a function parameter, exactly as `strawberry_target` is
   today. No literals buried in decision code. A change that adds a magic number is not
   accepted even if it improves the bank.

2. **Prefer derived decisions over fixed targets.** Where a number can be computed from the
   observation — expected marginal revenue of the next tile given the current price curve,
   the ROI of hand *n* given unworked tiles — compute it. Fixed targets are acceptable as a
   first step, but each should carry a note on what it would take to derive it. The
   long-term ceiling comes from the market model (`overview.md:257-267`), which is fully
   specified and can be evaluated at runtime.

3. **Keep the strategy legible.** One decision per function, named for the decision it
   makes. The reason D2 survived so long is that a correct price guard was bypassed by an
   unrelated overflow term three lines away. Changes must not increase that kind of coupling.

4. **No overfitting to the current meta.** P1–P7 describe one widely-copied bot. Tuning to
   beat *that specific* opponent is fragile — it is common now and may not be in October.
   Prefer changes justified by the game's mechanics (the glut-tolerance table, the
   production clocks) over changes justified only by "the winner did it."

5. **The benchmark must scale too.** Seed count, opponent roster and metric set are all
   inputs, not fixed constants. When the goal moves to $180,000, raising the bar must be a
   config change, not a rewrite. G1's threshold lives in one place.

6. **Preserve the submission constraint.** `agent.py` stays a single self-contained entry
   point compatible with `kaggle_environments`, under the 100 MiB packaging limit, whatever
   else changes.

#### Acceptance

Every work item carries this in addition to its own metric: **no new hard-coded decision
literals, and the item's own targets must be adjustable without touching decision logic.**
After G0 is met, the immediate next question is *"what is the new binding constraint"* — the
iteration protocol below is written to keep running, not to terminate.

---

**Evidence base:** 7 official ladder episodes in `logs/` — 1 win, 6 losses.
All 14 agent-runs finished `DONE` (no crashes, no timeouts). Every loss is strategic,
not a defect in action execution.

| Episode | Opponent | Ours | Theirs | Result | Margin |
| --- | --- | ---: | ---: | :---: | ---: |
| 89985050 | m-toshi desu | 97,925 | 84,682 | **W** | +13,243 |
| 89978502 | MarvelousXun | 47,674 | 50,411 | L | −2,737 |
| 89989543 | Sutee | 88,842 | 92,645 | L | −3,803 |
| 89983749 | Max Manushin | 105,111 | 118,099 | L | −12,988 |
| 89983092 | Aleks Lviv | 110,825 | 125,241 | L | −14,416 |
| 89984407 | KodamaSec Labs | 94,617 | 112,376 | L | −17,759 |
| 89980458 | vlad101 | 56,611 | 100,262 | L | −43,651 |

Gross revenue is broadly competitive (94k–162k vs opponents' 86k–202k). The losses come
from **product mix** and **realised price**, not from throughput.

---

## Diagnosis

### D1 — Zero sheep, zero wool, in all seven episodes

`EARLY_SHEEP_TARGET`, `LATE_SHEEP_TARGET`, `EARLY_GOOSE_TARGET` and `TOMATO_TARGET` are all
hard-zeroed at `python_bot/agent.py:39-43`. The purchase, pasture-build and carry logic
already exists and is reachable — only the targets are zero.

Every one of the seven opponents bought sheep (6–37 ordered, 4–11 alive at the end) and
earned **$25k–$46k** of wool revenue. Ours is **$0** in every episode. Peak animal count:
ours exactly 10 (capped by `COMPACT_COW_TARGET = 10`), opponents 11–16.

### D2 — Melon synchronised-harvest crash (the largest single leak)

`MELON_TARGET = 40` produces 24–46 simultaneous melon tiles. Melon is a **one-time** crop
with a 10–12 day maturation, so **every tile matures within the same 3–4 day window**.
~46 tiles × 6 units ≈ 276 units land in a 100-capacity shed across four days.

The mechanism that turns this into lost cash is in `_sell_orders` (`python_bot/agent.py:609`):

```
overflow = max(0, total_stock + incoming_stock + projected_harvest_units - SHED_CAPACITY)
...
price_is_healthy = quoted_price >= target_price
...
else:  # price NOT healthy
    sell_quantity = min(quantity, overflow)
```

The `price_is_healthy` guard is written correctly, but `incoming_stock` (units held in
worker inventories) sits at **44–79 units** during the melon window. Overflow is therefore
permanently positive and the distressed-sale branch fires continuously, bypassing the price
guard. Traced in ep89985050, days 17→20:

| Step | Day | Melon price | Qty sold | Shed | Incoming |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 414 | 17 | $246 | 4 | 56 | 44 |
| 421 | 17 | $223 | 19 | 25 | 68 |
| 447 | 18 | $202 | 6 | 41 | 59 |
| 468 | 19 | $156 | 9 | 47 | 54 |
| 495 | 20 | $120 | 3 | 45 | 55 |

Melon has the harshest curve in the game (`overview.md:263` — `above_func = sq`,
`above_target = 3.60`, P(I₀+300) = $1). We sell into our own collapse.

**Result: 75–100% of all melon units are sold below base price**, realising $114–$241
against a $250 base. Discount vs base by episode: −$29.3k, −$26.3k, −$23.5k, −$12.5k,
−$6.8k, −$5.5k, −$1.5k. The worst cases exceed the entire loss margin.

Strawberry does not suffer this because it is an *ongoing* crop — its yield self-staggers,
and it consistently realises **above** base ($174–$285 vs $120 base).

### D3 — Land allocated to low-value crops

Peak simultaneous tiles:

| | CARROT | WHEAT | MELON | STRAWBERRY |
| --- | ---: | ---: | ---: | ---: |
| Ours | 19 (every episode) | 19–35 | 24–46 | 17–35 |
| Opponents | 0–2 | 4–14 | 9–24 | 18–39 |

Carrot realises **$31/unit against a $35 base** — roughly $1.5k for 19 tiles of season-long
watering. Opponents plant essentially none.

### D4 — Wheat wash-trade

Every episode: sell ~500 wheat, buy back ~450 wheat as animal feed. The round trip nets
about +$5/unit by timing accident, so it is not a cash loss — but it consumes 19–35 tiles,
~950 market-order slots and substantial hand-turns to net ~50 units. Opponents grow 4–14
tiles of wheat purely as feed and sell 57–140 units.

### D5 — Unharvested value at turn 720

`FINAL_LIQUIDATION_DAY = 29` fires too late to clear ongoing crops.

| Episode | Ours | Opponent |
| --- | ---: | ---: |
| 89989543 | 53 units ≈ $6,765 | 0 |
| 89983092 | 47 units ≈ $5,585 | 0 |
| 89978502 | 44 units ≈ $3,380 | 3 units |
| 89983749 | 39 units ≈ $1,735 | 18 units |

Five of seven opponents finish at exactly zero.

### D6 — The current benchmark cannot detect any of D1–D5

Measured on this machine (`kaggle-environments` is installed and `kaggriculture` is
available, so the gate does run). Final bank after 720 turns:

| Agent | Final bank |
| --- | ---: |
| `pass` | $3,000 (starting money — does nothing) |
| `random` | $0 |
| `starter` | $3,514 |
| **Real ladder opponents** | **$84,682 – $125,241** |

The strongest built-in scores **~3% of a real opponent**. Three consequences:

1. **No discrimination.** Our agent scores **$136,548 vs `starter`**. On the ladder it loses
   6 of 7. The harness cannot tell a 95k agent from a 125k agent, so it cannot validate or
   refute any item in this plan.

2. **The failure mode is structurally invisible.** The market is *shared*. `pass`, `random`
   and `starter` barely sell, so the harness market never sees a second seller and prices
   never behave as they do on the ladder — which is precisely the mechanism behind D2.
   Self-play, which does put a realistic second seller in the market, reproduces ladder
   conditions closely:

   | Seed | Self-play result | vs `starter` |
   | --- | --- | ---: |
   | 1281355554 | 97,234 vs 99,152 | 136,548 |
   | 2050554103 | 86,143 vs 86,143 | — |
   | 1208590292 | 101,458 vs 102,381 | — |
   | 910788726 | 70,812 vs 71,146 | — |

   Self-play lands at 70k–102k, matching our real ladder range of 47k–110k. The
   vs-`starter` number is inflated by roughly 40%.

3. **`RECORD_MILESTONE = 154615` is not a ladder-comparable target.** It is a
   vs-weak-opponent bank. Chasing it optimises for the wrong market conditions.

Further gaps in `run_official_tournament.py`:

- **The exit code never gates on score.** `main()` returns non-zero only when
  `result.checks` is non-empty — i.e. only for crash/no-plant/no-sell/weed failures. An
  agent that regresses by $40k still exits 0 and reads as a pass.
- **No baseline comparison, despite `AGENTS.md` requiring one.** The `--opponents` help text
  says "Comma-separated built-ins; use self for candidate self-play." In fact
  `kaggle_environments` accepts a **file path** as an agent — verified working
  (`agent.py` vs `starter` ran clean this way). Candidate-vs-previous-artifact is available
  today and simply undocumented.
- **4 seeds, single side.** The candidate always plays `player=0`; sides are never swapped.
  Ladder margins run 2.7k–43k on ~100k banks, so 4 unpaired episodes cannot resolve a real
  10k difference from noise.
- **No diagnostic metrics.** The report carries bank plus raw action counts. It does not
  carry the measures that actually explain D1–D5 — wool revenue, realised price vs base per
  product, fraction of units sold below base, unharvested value at turn 720.

Episode cost is ~5s for self-play, ~3s vs a built-in, so a statistically useful benchmark
(100+ episodes ≈ 9 minutes) is entirely affordable. There is no throughput reason for the
current 4-episode default.

---

## Winner pattern study — ep90006347 (`somewhere after` 125,896 vs `CARLOS CAADA ROSTRO` 118,008)

Neither player is ours. The two agents are **near-identical bots** (63% of turns have
byte-identical worker actions; cash is identical to the dollar through day 9), almost
certainly the same widely-copied ladder strategy. That makes this episode unusually
informative in two ways: it shows a top strategy's full build order, and the single
divergence between the two runs is close to a controlled experiment.

> **Measurement caveat.** These bots spam market orders — **74% of their SELL orders exceed
> available shed stock** and simply fail (`maxMarketOrdersPerTurn: 10`, no penalty for
> infeasible orders). Order quantities are therefore *intent*, not execution. Everything
> below marked **exact** is read from game state; the revenue mix is attributed from
> per-turn money deltas at only **54–59% coverage** and is indicative, not precise.

### P1 — Day-0 animal rush, herd frozen by day 12 *(exact)*

The winner buys **3 cows and 1 sheep on day 0**, driving cash from $3,000 to **$7 by hour 9**.
Herd growth: day 0 → 3 animals, day 8 → 8, day 10 → 12, **day 12 → 14 (8 cow + 6 sheep)**,
then **completely frozen for the remaining 18 days**.

The rationale is the production clock: cows first yield at 8 days then every 2 days, sheep at
6 days then every 3 (`overview.md:94-96`). Every day of delay costs a whole production cycle,
so the herd is a day-0 capital decision, not a mid-game one.

Ours buys cows 2 at a time, gated on `day <= 20` and a $500 cash buffer, reaching 10 cows
late. **Our plan's W1 specifies the herd mix but says nothing about timing — that is the
larger half of the gap.**

### P2 — Marginal sheep measured at ~$7,900 *(near-controlled)*

The two bots are cash-identical through day 9 (both exactly $623 on day 8, $268 on day 9)
and hold 8 cows each for the whole game. The **only** state difference: the winner acquires a
3rd sheep on day 8, the loser does not — 6 sheep vs 5 from day 9 onward.

The cash gap then grows monotonically and never reverses:

| Day | 9 | 12 | 16 | 20 | 24 | 29 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Gap | $0 | −$8 | +$1,500 | +$2,229 | +$3,574 | **+$7,959** |

Final margin +$7,888. **One sheep bought on day 8, at a cost of $500, tracks to roughly
$7,900 over 21 days.** Single episode, and some of the gap is certainly noise — but the
divergence begins exactly where the herds diverge and compounds steadily. This is the
strongest available evidence for W1.

### P3 — Small *rolling* melon block, planted from day 0 *(exact)*

The winner holds a steady **9–11 melon tiles from day 2 through day 22**, planted starting
day 0 and continuously replanted — never a large synchronised block. Realised melon price
$170–$235.

Ours runs 24–46 melon tiles that all mature in the same 3–4 day window and realise $114–$149
(D2). This directly confirms the staggering half of W3 and supplies the target: **a rolling
block of ~10 tiles, not a 40-tile batch.**

### P4 — Strawberry is the anchor at ~40 tiles *(exact)*

Ramped to exactly **40 tiles by day 16** and held through day 20. Ours targets 30
(`STRAWBERRY_TARGET`).

### P5 — Late-season pivot to wheat *(exact, and absent from our plan)*

| Day | Strawberry | Melon | Wheat | Weeds | Unharvested value |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 24 | 34 | 5 | 0 | 4 | $9,210 |
| 26 | 23 | 3 | 12 | 6 | $5,490 |
| 27 | 18 | 2 | 32 | 7 | $4,760 |
| 28 | 12 | 0 | 32 | 13 | $1,950 |
| 29 | 6 | 0 | 2 | 19 | **$245** |

From day 25 they dig out strawberry and convert the land to **32 tiles of wheat** — a 2-day
crop — harvested on days 28–29. Wheat sells at ~$46–$50 against a $25 base, because wheat
inventory is drained all season by *both* players buying it as animal feed. Wheat is the one
commodity whose price rises monotonically and is never glutted.

Final state: **shed completely empty, 2 units unharvested (~$50)**. Ours leaves $1,100–$6,800
standing (D5).

### P6 — Weeding is abandoned in the endgame *(exact)*

Weeds are allowed to reach **19 by day 29**; labour goes to harvesting and selling instead.
Weeds cost nothing at turn 720.

**This collides with our release gate.** `MAX_ACCEPTABLE_WEEDS = 10` in
`run_official_tournament.py` would mark this winning agent as a **FAIL**. The check must
become day-aware (or endgame-exempt) or it will reject the correct endgame behaviour —
folded into W0.

### P7 — Just-in-time feed buying *(exact)*

Feed is bought in **1–6 unit increments almost every hour**, never as a bulk reserve, keeping
cash free for animals during the day-0–12 build. Ours buys
`animals × WHEAT_RESERVE_DAYS − on_hand` in bulk.

### Explicitly NOT problems (previously suspected, disproved by the data)

- **Labour efficiency** — our hands idle 12–16% vs opponents' 7–31%. At or better than par.
- **The 4th quadrant** — we stop at 3 (`LAND_PLAN`, `agent.py:27`), but so do 6 of 7
  opponents. Not a differentiator.
- **Selling fertilizer** — opponents sell *more* than us (170–331 units vs our 93–188).
- **Animal starvation** — 14 animals lost in ep89980458, but **0 in the other six**.
  A single-episode artifact, not systemic. Worth a cheap guard (W6), not a redesign.
- **Weeds** — we carry fewer than most opponents.

---

## Work items

Ordered here by topic; **the build order is in *Suggested sequencing* at the end** and is
deliberately not W0→W9. Constant tuning (W3, W4, W5, W7, W8) is *not* on the critical path
to G1 — those items become seed values and acceptance checks for W9 rather than
implementation passes. **W0 lands first** regardless: without it nothing else can be shown
to work.

### W0 — Make the benchmark able to measure a strategy change *(blocking prerequisite)*
*File: `python_bot/run_official_tournament.py`*

Per D6 the current gate cannot discriminate between a winning and a losing agent. It must
be fixed before any strategy work is benchmarked, or every subsequent result is
uninterpretable.

- **Make self-play the primary opponent.** Change the `--opponents` default from
  `pass,random,starter` to `self`. Keep the built-ins as a cheap *smoke* tier, not as the
  performance measure. Self-play reproduces ladder score ranges; the built-ins inflate by
  ~40%.
- **Add a baseline-regression gate.** Add `--baseline <path>` accepting the previously
  approved artifact, run candidate vs baseline head-to-head on every seed, and **fail the
  run** when the candidate's win rate or median bank falls below the baseline by more than
  a stated tolerance. File-path opponents already work — this is mostly plumbing plus a new
  check. Update the `--opponents` help text to document that a path is accepted.
- **Gate the exit code on score, not just on liveness.** `main()` must return non-zero on a
  score regression as well as on `result.checks` failures.
- **Raise the episode count and pair the seeds.** Default to ≥30 seeds; run each seed with
  the candidate on **both** sides to cancel positional bias; report win rate with a
  confidence interval and median/IQR bank rather than a bare median.
- **Report the diagnostic metrics** that explain D1–D5, per episode and aggregated:
  wool/milk/melon/strawberry revenue and units, realised price vs base per product,
  fraction of units sold below base, unharvested tile value at turn 720, peak tiles per
  crop, animals lost. The analysis scripts used to produce this plan already compute all of
  these from replay JSON and can be adapted directly.
- **Make the weed check day-aware.** `MAX_ACCEPTABLE_WEEDS = 10` would mark ep90006347's
  *winner* as a FAIL — it ends on 19 weeds because abandoning weed control in the endgame is
  correct (P6). Exempt the final days, or apply the cap only up to ~day 25, or the gate will
  reject W7.
- **Retire or re-scope `RECORD_MILESTONE = 154615`.** Either drop it or relabel it
  explicitly as a vs-weak-opponent figure, and establish a new self-play reference number
  from the current agent (~70k–102k on the four default seeds).

**Acceptance:** running W0's harness against today's unmodified `agent.py` must reproduce
self-play banks in the 70k–102k band and must report a wool revenue of $0 and a
below-base melon sale fraction of 75–100% — i.e. it must *show* the known defects. A
benchmark that cannot see D1 and D2 in the current agent is not yet fit to judge a fix.

### W1 — Rebalance livestock toward a cow/sheep mix, **and buy it early**
*Files: `python_bot/agent.py:30,40-41`, `_compact_cow_slots`, `_market_actions`*

- Set `EARLY_SHEEP_TARGET` / `LATE_SHEEP_TARGET` to a combined 6; reduce
  `COMPACT_COW_TARGET` from 10 to ~8. Target the **8-cow / 6-sheep** herd that ep90006347's
  winner runs (P1) — consistent with the 11–16 animals every ladder opponent fields.
- **Front-load the purchase schedule (P1).** This is at least as important as the mix.
  Buy the first animals on **day 0** and complete the herd by **~day 12**; today's
  `day <= 20` window with 2-at-a-time purchases and a $500 buffer arrives far too late.
  Cows first yield at 8 days then every 2; sheep at 6 days then every 3 — a herd finished on
  day 20 forfeits most of its production cycles.
- Accept a near-zero cash floor during the day-0–12 build. The winner runs at **$7–$600
  through day 10** and this is not the same failure as our mid-game cash starvation: it is
  spending on compounding assets, then never spending again.
- `_compact_cow_slots` currently returns cow placements only — generalise it to allocate
  pasture slots across both species, or add a parallel sheep-slot selector.
- Scale the `WHEAT_RESERVE_DAYS` feed buffer off total animals, not `owned_cows`
  (`_sell_orders` already takes `owned_cows` — widen it to `owned_animals`).

**Rationale:** opens a second high-value price curve (wool realises $198–$248/unit for
opponents) and relieves the milk curve we currently over-dump (230 units at $40/unit in
ep89978502 against a $160 base). P2 puts a near-controlled figure on the marginal animal:
**one extra sheep bought on day 8 tracked to ~$7,900** in ep90006347.

### W2 — Fix the distressed-sale bypass
*File: `python_bot/agent.py:609-670` (`_sell_orders`)*

This is a genuine logic defect, independent of any tuning:

- Exclude in-transit `incoming_stock` from the overflow trigger, or compare against a
  headroom threshold rather than raw `SHED_CAPACITY`. Workers holding cargo are not the
  same as a full shed — the shed was ≥95 units in only 1–4% of turns while melon was being
  dumped continuously.
- Add a hard price floor for `sq`-curve products (MELON, WOOL): never sell below a
  configurable fraction of base except at final liquidation.
- Prefer `DROP`/hold over a below-base sale when the shed has real headroom.

**Rationale:** directly addresses the largest measured leak. Worth up to ~$29k in the worst
episode.

### W3 — Retune the crop portfolio
*File: `python_bot/agent.py:42-44`, `_next_crop`*

- Cut `MELON_TARGET` from 40 to **~10, held as a *rolling* block** — plant from day 0 and
  replant continuously rather than filling a batch (P3). A smaller target alone still
  synchronises; the rolling discipline is the structural half of D2.
- Remove carrot from the rotation (`_next_crop` falls back to a wheat-vs-carrot rate
  comparison; carrot has never realised above base).
- Raise `STRAWBERRY_TARGET` from 30 to **~40**, reached by day 16 and held (P4). Strawberry
  is the only crop that reliably realises above base.

### W4 — Size wheat to feed demand only
*File: `python_bot/agent.py`, `_next_crop` fallback*

Plant wheat to cover `animals × WHEAT_RESERVE_DAYS` plus a margin, and stop selling surplus
wheat before day 25. Frees 15–25 tiles for strawberry.

### W5 — Earlier and more complete liquidation
*File: `python_bot/agent.py:38,655` (`FINAL_LIQUIDATION_DAY`)*

Move liquidation earlier and force-harvest ongoing crops (strawberry especially) over the
final two days. Worth $1.1k–$6.8k per episode. Target the winner's end state: **empty shed,
≤2 units standing** (P5).

### W6 — Cheap starvation guard
*File: `python_bot/agent.py`, `_choose_worker_action`*

Make "any animal at `consecutive_unfed >= 1` gets fed this turn" a hard precondition ahead
of other hand tasks. Low cost; prevents the ep89980458 tail case ($5,600 of animals lost
plus forgone production).

### W7 — Late-season wheat conversion *(new, from P5)*
*Files: `python_bot/agent.py`, `_next_crop`, `LAST_PLANTING_DAY`*

From ~day 25, dig out spent strawberry and convert the freed land to **wheat** — a 2-day
crop that still completes before turn 720. ep90006347's winner runs 32 wheat tiles on
days 27–28 and sells at **$46–$50 against a $25 base**.

Wheat is the one commodity whose price rises monotonically all season (25 → 52) because both
players continuously drain inventory buying it as feed, so it is never glutted. This is the
opposite end of the same trade as W4: buy feed wheat early when it is cheap, sell grown wheat
late when it is expensive.

Pair with **abandoning weed control after ~day 26** (P6) — weeds cost nothing at turn 720 and
the labour is worth more on harvest and sale. Note this interacts with the benchmark's weed
check; see W0.

### W8 — Geese and eggs: the untapped price curve *(the G1 candidate)*
*Files: `python_bot/agent.py:39` (`EARLY_GOOSE_TARGET`), `_compact_cow_slots`, `BUILD_COOP` path*

W1–W7 bring us level with the best observed agents (~125k). **W8 is the item most likely to
clear $160,000**, because it adds revenue on a curve nobody is competing for.

- Raise `EARLY_GOOSE_TARGET` from 0 to ~10, bought early on the P1 schedule.
- The coop-build path already exists (`BUILD_COOP` at `agent.py:725`) but is unreachable
  while the target is 0 — verify placement and the +1 action cost.
- Sell eggs in volume rather than in tranches. Egg is the one product where the
  premium-glut discipline of W2 does **not** apply: at +2T units it still fetches $34 of a
  $50 base. The sell-batch logic must special-case it rather than treating it like milk.

**Rationale:** total egg sales across all 8 analysed replays are 8 units. A goose yields
daily from day 4 at up to 2/tile/day into a curve that holds 68% of base under heavy
oversupply, whereas milk, wool, strawberry and melon all hit the $1 floor within one field's
overproduction. This is the only identified route to revenue that does not crash its own
price.

**Risks:** the goose's 1 + 1 action cost (build coop, then daily feed and care) may make it
labour-negative at 12 hands; eggs at $34–$50 are low-value per unit, so the volume must
actually materialise. Benchmark before believing it — if geese prove labour-negative, the
alternative route to G1 is wheat volume (also a 68%-at-+2T curve, already selling at
$45–$52).

---

### W9 — Runtime price model and marginal-revenue allocator *(the G1 attempt; on the critical path)*
*Files: new pricing module inside `python_bot/agent.py`, then `_next_crop`, `_sell_orders`, `_market_actions`*

This is the item that resolves the constants tension. It replaces Tier-3 strategy targets
with decisions computed from the game's own economics.

**W9a — Read `configuration`.** Prerequisite and a standalone bug fix. Thread the episode
config through `_agent_impl` and derive every Tier-2 knob from it (`shedCapacity`,
`maxMarketOrdersPerTurn`, `turnsPerDay`, `episodeSteps`, `farmHandCostMult`, town
intervals), with the current constants as defaults. Season-relative days become
`episodeSteps / turnsPerDay` rather than a literal 30.

**W9b — Implement the price function.** It is fully specified at `overview.md:242-267` and
closed-form:

```
price(inv) = base + sign * amp * f(|inv - I0|)      sign = +1 below I0, -1 above
amp        = target * base / f(T)                   floored at $1, rounded
```

The observation already carries `market.inventory` per resource, so the agent can compute
the exact price of the *n*-th unit it is about to sell, instead of reacting to a quoted spot
price after the damage is done.

*Verified while writing this plan:* with `f` applied to the **normalised** argument `x/T` on
the glut side, the model reproduces **all nine** published `P(I0-T)`, `P(I0+T)`, `P(I0+2T)`
values exactly. The prose at `overview.md:249` says "log uses ln(1+x)"; taken literally
(raw `x`) it misses WHEAT ($19 vs $17) and EGG ($39 vs $34). On the scarcity side the raw
form is the better fit. Against 927 live market quotes from ep90006347 the combined model is
**89% exact**, with the residual confined to WHEAT's scarcity side — that gap must be closed
or bounded before the allocator trusts it. **Validate against replay quotes; do not assume.**

**W9c — Marginal-revenue allocation.** With the price curve available, the Tier-3 constants
become outputs rather than inputs:

- *How many melon tiles?* Not `MELON_TARGET`. Add tiles while the marginal revenue of the
  next tile's projected harvest — priced at the inventory that harvest will itself create —
  exceeds the best alternative use of that tile-day.
- *How much to sell now?* Not `PREMIUM_SELL_BATCH`. Sell while marginal unit price exceeds
  the discounted expected price of holding, using the known town-consumption drain
  (`overview.md:207-222`: shops every 4 turns, town centre every 12, rising to 2× after day
  10 and 4× after day 20) to project recovery.
- *Which crop next?* Compare expected revenue per tile-day across crops at *achievable*
  prices, not base prices.

**Why this is the route past 125k:** the ladder's ceiling is the glut curves, not the land
(see *Where the headroom is*). Strawberry, milk, wool and melon all hit the $1 floor within
one field of oversupply. A fixed target cannot know where that edge sits on a given turn —
it depends on the shared inventory, which the opponent is also moving. A marginal-revenue
rule does, and it adapts to an opponent who dumps.

**Acceptance:** the allocator must beat its Stage-A constants on G1 median *and* worst seed.
Keep the constants as a fallback path and as the regression baseline — if W9 underperforms
on any seed, that is a bug to find, not a reason to revert silently.

**Risk:** this is the largest and most failure-prone item in the plan, and it is now on the
critical path rather than behind a tuning phase. Mitigations:

- Regress against **today's agent** (70–102k self-play, already measured) — no tuned
  intermediate is needed.
- Keep the constant path switchable behind a flag, so a regression is one toggle from being
  isolated to the allocator.
- Seed the allocator with the P1–P7 observed values so its first run starts from known-good
  behaviour rather than from nothing.
- If W9c stalls, the demoted items (W3, W4, W5, W7, W8) are the fallback — but promote them
  only where the diagnostics point, not as a blanket tuning pass.

---

### W10 — An opponent that can beat us *(blocking prerequisite for G0)*

**The problem.** There is no adversary in the repo. `pass`, `random` and `starter` are a
liveness test (measured: $3,000 / $0 / $3,514). Self-play is a mirror. Head-to-head against
the previous artifact is a near-mirror. So the condition that loses 6 of 7 ladder games —
a competent opponent competing into the same price curve — **has never been reproduced
locally**, and no change has ever been tested against it.

The ladder agents' code is not available; `logs/` holds replay JSON, which is a recording,
not a policy. Three ways to close the gap, cheapest first:

1. **Open-loop replay agent** (~15 lines): return `steps[turn][idx]["action"]` from the JSON,
   ignoring the observation. Faithful to what the winner did, and their *market* orders are
   already state-blind (74% of ladder sell orders exceed available stock and silently fail).
   But their *farm* actions assume their board: against a different opponent, workers move
   onto tiles that are not theirs, harvests hit empty ground, production collapses and they
   have nothing left to sell. Degrades into a weak opponent. Sanity check only.
2. **Dumper derived from `agent.py`** — *do this first.* No log parsing. Copy the agent and
   change two constants: `SELL_PRICE_MULTIPLIERS` → all `0.0` (so `price_is_healthy` at
   `agent.py:665` is always true and it never waits for a price), and `PREMIUM_SELL_BATCH` /
   `STAPLE_SELL_BATCH` → large (so it clears the shed instead of 8/20 units a turn). The
   result farms competently — so it *has* stock — and dumps immediately, taking the scarcity
   premium first. That is exactly the mechanism already measured as costing us melon revenue
   **$27.4k → $18.2k** in Cycle 1. Runs today via `--opponents`; genuinely not a mirror.
3. **Behavioural clone from the logs**: extract the winner's policy statistics across all 720
   steps — sell timing and volume per product, planting mix, hire curve, land timing — and
   write a closed-loop policy reproducing them. Most faithful, most work. Promote only if (2)
   fails to reproduce the ladder losses.

**Acceptance:** the dumper **beats the current `agent.py`** over ≥30 paired seeds. That is
the success condition — an adversary that loses to us is not an adversary, and if (2) cannot
beat us, escalate to (3) rather than declaring the agent healthy. On success this is the
first local reproduction of the ladder result, and G0 becomes measurable.

**Guard:** the dumper is a *test fixture*, never a submission candidate. It must not be
tuned to win; it is fixed once built so that G0 stays comparable across cycles.

#### Outcome — BUILT AND ACCEPTED (Cycle 4)

Approach (2) was enough; (1) and (3) were not needed. `python_bot/opponent_dumper.py` is a
frozen copy of `agent.py` at commit `93f333a` with exactly the two constant changes above —
`SELL_PRICE_MULTIPLIERS` all `0.0` (extended to *every* product, since the `.get(item, 1.0)`
fallback would otherwise have left MILK/WOOL/EGG patient and made it only a partial dumper)
and both sell batches raised to the shed capacity of 100.

The harness gained a fourth tier. `--adversary <file>` runs paired, sides swapped, and is
now where G0 and G3 are decided; G1 was demoted to a printed tracker and no longer fails the
run, matching the gate table above.

**Result over 30 paired seeds (60 episodes):**

| | value |
| --- | --- |
| **G0 win rate** | **3%** — 2 wins, 0 ties, 58 losses |
| Our median bank | $70,254 |
| **Adversary median bank** | **$83,366** (range $46,320–$128,479) |
| Median margin | −13% |
| **G3 worst seed** | 718043812 swapped, $51,174 vs $114,368 = **−55%** |
| Liveness | 60/60 passed, 0 errors |

Acceptance was *the dumper beats us*, and it does, 58–2. **This is the first local
reproduction of the ladder result** — we lose 6 of 7 ladder games, and we lose 58 of 60 here.
Two independent signs the fixture is faithful rather than merely strong:

- the adversary finishes at a median $83,366, essentially on top of the observed ladder band
  of **$84,682–$125,241**, while we finish at $70,254 — the same shape as the real gap;
- the losses are not blowouts. Median margin is −13% and our best seed is +29%; these are
  close games lost in a shared market, exactly what the retired $160k target mis-diagnosed
  as a 2× production gap.

The mechanism is visible in the diagnostics: **82% of our melon units and 50% of our milk
units clear below base price**, at a realised $114 against a $250 melon base. We wait for a
price that the dumper has already taken. Strawberry, which it cannot flood as fast, still
clears at $260 against a $120 base — 0% below base. That is W11's target, and it is now
measurable.

G0 is live. Every subsequent change is judged on it.

### W11 — Adaptive reserve price *(the G0 attempt)*

**The defect.** The sell logic holds stock until the quoted price recovers to a fixed
multiple of base. Against a patient opponent that is optimal — which is precisely why
self-play looks healthy and hides this. Against a dumper, patience hands the scarcity premium
to whoever sells first and we sell into the floor. Cycle 1 measured the result (melon $27.4k
→ $18.2k) and tried lowering the reserve ratios and raising planned volume; **neither moved
G2 off 23%**, because both are static responses to a dynamic opponent.

**The change.** Make the reserve price a function of the opponent's observed selling rate.
Market inventory is in the observation, and the engine's price curve and town-drain schedule
are exact and already asserted in `test_agent_allocator.py` — so the inventory trend
separates *our* sales and the town's drain from the residual, which is the opponent's supply.
Sell aggressively into a curve the opponent is draining; stay patient when they are not.

**Metric that must move:** G0 win rate, and melon/premium realised price against the dumper.
**Guard that must not regress:** G2 never below 50%, and G1 not down more than 10% — a purely
defensive agent that wins by denying the opponent while producing nothing is not the goal.

**Note:** this is the *only* item in the plan aimed at win rate rather than at bank, and it
requires no additional production. It is the cheapest untested lever remaining.

#### Outcome — LARGELY SUCCESSFUL, one gate still open (Cycle 4)

**G0 3% → 63%.** The single largest movement any change in this plan has produced. G2 went
50–52% → **85%**, and G1 rose $80,656 → $83,244 rather than falling, so the "defensive agent
that produces nothing" failure mode did not occur.

| gate | pre-W11 | W11 | verdict |
| --- | ---: | ---: | --- |
| **G0** win rate vs adversary, 30 seeds | 3% | **63%** | **MET** |
| G0 at 60 seeds (30 held out) | 13% | 62% | MET |
| G2 vs previous artifact | 50–52% | **85%** | MET |
| G1 self-play median | $80,656 | $83,244 | up 3.2% — guard held |
| G3 worst seed, 30 seeds | −55% | −18% | MET |
| **G3 worst seed, 60 seeds** | −55% | **−37%** | **NOT MET** |

**The change.** `_supply_pressure` reconstructs the opponent's net supply from the shared
market inventory. The engine moves inventory by exactly *our trades + theirs − the town
drain*, so subtracting what we ourselves put through the market leaves *their sales − the
drain*. Summed over a game day, a positive figure means the market is filling faster than the
town empties it — a statement about tomorrow's price, not today's. When that holds for a
product, the reserve is cut and the sell batch raised.

**Two findings that contradict the item as written.**

1. **The stated metric did not move.** W11 named "melon/premium realised price against the
   dumper" as the metric that must move. It did not: melon stayed at **85% below base and a
   realised ~$115**, and milk got slightly *worse*. The win came from **volume** instead —
   melon 156.5 → 187.1 units/episode, wheat 102.9 → 165.3, and end-of-season unharvested
   value $5,008 → $2,738. Selling earlier frees shed capacity and capital, which compounds
   into more production. The hypothesis was right about the defect and wrong about the
   mechanism of the cure.
2. **The reserve cut is not the lever; the batch size is.** Over 120 paired episodes per
   configuration: batch 100 scored 64%/62% at reserve cuts 0.35/0.55, while batch 40 scored
   59%/59% at cuts 0.55/0.75. The batch effect is consistent across both reserve levels; the
   reserve effect is not consistent across either batch. The shipped configuration therefore
   takes batch 100 and leaves the cut at the middle value 0.55, rather than adopting the
   single top-scoring run — which at a ~4.5pp standard error would be fitting noise on a
   fixture. This is consistent with (1): throughput, not price discipline.

**A first attempt that measured zero.** The initial estimator counted *consecutive* turns of
net inflow. It produced a byte-identical benchmark, and instrumentation showed why: the
measured streak never exceeded **1** for any product, because opponents sell in bursts after
a harvest and sit idle between. Summing over a one-day window fixed it. Recording this
because the failure was invisible in the result and only a direct trace found it.

**Two defects left open, neither hidden:**

- **G3 fails on the wider seed set** (−37% on seed 391611974, outside the first 30). This is
  *pre-existing and improved, not introduced*: the previous artifact scores −55% on the same
  60 seeds. W11 halves the worst-case collapse without clearing the 20% bar.
- **A weed-cap liveness regression on one seed.** Seed 1232444148 reaches 11–12 weed tiles
  against the harness limit of 10, in the self-play and head-to-head tiers; the previous
  artifact is clean at 90/90 and 30/30. Cause is mechanical: more cash buys more land, peak
  melon tiles go 32.4 → 38.0 against an unchanged labour cap, so weeding falls behind. It is
  one seed and the harness cap is a heuristic rather than a game rule, but it is a real
  regression and should be closed by the labour routing, not by raising the cap.

Both belong to the next cycle. Neither is a reason to withhold W11, which clears G0 and G2
and improves G1 and G3.

---

## Validation gate

Per `AGENTS.md`, no item above may be described as verified, packaged, or submitted until it
passes the official-engine benchmark. Unit tests alone never establish a score change.

**Every work item W1–W6 must be benchmarked individually against the W0 harness before it is
called done.** No item is merged on reasoning alone, however obvious the diagnosis looks —
D6 is exactly what happens when a gate is trusted without checking what it measures.

### Before W0 lands

The existing harness is a **liveness check only**. It may be used to confirm an agent still
farms and does not crash. It must **not** be cited as evidence of a score improvement, and
its vs-`starter` bank must not be quoted as a performance figure.

### After W0 lands — required per change set

1. `python3 -m unittest python_bot/test_agent.py` — schema compliance, 720 valid turns.
2. **Smoke tier:** vs `pass`, `random`, `starter`. Confirms the crop loop still runs
   (PLANT/WATER/HARVEST/SELL present, weeds ≤ `MAX_ACCEPTABLE_WEEDS`, status `DONE`).
   Pass/fail only — banks from this tier are not a performance measure.
3. **Performance tier:** candidate vs the previous approved artifact, ≥30 paired seeds,
   candidate on both sides of each seed. This is the number that decides the change.
4. **Self-play tier:** candidate vs itself, same seeds, to observe behaviour under realistic
   two-seller market pressure.
5. **Diagnostic tier:** the D1–D5 metrics must move in the predicted direction. A bank
   improvement with no matching movement in the targeted metric is treated as noise, not a
   result, and the item goes back for re-analysis.

### Per-item acceptance criteria

| Item | Primary metric that must move | Guard against |
| --- | --- | --- |
| W1 | Wool revenue > $0; **herd complete by day 12**; total animals 11–16 | Milk revenue collapsing; animals lost > 0; cash starvation persisting past day 12 |
| W2 | Below-base melon sale fraction drops from 75–100% toward 0 | Stock held to turn 720 unsold |
| W3 | Realised melon price approaches base; melon tiles ~10 and rolling; strawberry ~40; carrot → 0 | Total revenue falling |
| W4 | Wheat tiles down to feed-sizing; wheat units sold down | Animals going unfed |
| W5 | Unharvested value at turn 720 → ~0; shed empty | Premature dumping crashing a price curve |
| W6 | Animals lost = 0 across all seeds | Feed actions crowding out productive work |
| W7 | Wheat tiles ≥20 on days 27–28; realised late wheat ≥ $45 | Strawberry dug out too early, losing ongoing yield |
| W8 | Egg revenue > $0; realised egg price ≥ $34 at volume | Goose labour cost crowding out crop/animal work |
| W9 | Price model ≥89% exact vs replay quotes; G1 median **and** worst seed beat the Stage-A constants | Allocator losing to its own fallback on any seed |

Reference targets from ep90006347's winner (P1–P7): herd 8 cow + 6 sheep complete by day 12;
strawberry 40 by day 16; melon ~10 rolling; 12 hands from day 10; 3 quadrants by day 12;
32 wheat tiles on day 27; final shed empty with ≤2 units standing.

**Applies to every item in addition to the above:** no new hard-coded decision literals, and
the item's targets must be adjustable without editing decision logic (see *The solution must
keep scaling past $160,000*). These reference targets are starting points to be tuned past,
not values to freeze — they come from agents that score 118–126k, which is below G1.

A change that improves the bank but fails its guard column is not accepted — that is the
pattern that produced D2, where a correct price guard was silently bypassed.

If the official engine cannot run, report the benchmark as **blocked** and do not claim an
improvement.

### Suggested sequencing

**W0 first, and alone.** It changes no game decisions, so its own validation is simply that
it reproduces the known defects in the current agent (see W0 acceptance).

**Superseded after Cycle 3.** The sequencing below was built around reaching G1 and is kept
only as a record. W0 landed; W9c was built, rejected on G2, and survives as
`python_bot/agent_allocator.py`; W1 was measured twice and rejected both times.

| Order | Item | Rationale |
| ---: | --- | --- |
| 1 | ~~**W0** benchmark~~ | Landed. The most valuable asset in the repo — Cycle 3 alone caught four plausible regressions with it. |
| 2 | **W9a** read `configuration` | Still unshipped, still a live bug, independent of everything else. |
| 3 | ~~**W2** distressed-sale defect~~ | Landed. |
| 4 | ~~**W1** sheep constants~~ | Rejected twice (Cycles 1 and 3). Blocked on animal escapes — see W12. |
| 5 | **W6** starvation guard | Now the *precondition* for W1, not its protection. See W12. |
| 6 | ~~**W9b** price model~~ | Landed, and exact rather than 89% — read from the engine. |
| 7 | ~~**W9c** allocator~~ | Built, rejected on G2 (23%). Kept as reference. |

### Current sequencing — the G0 route

| Order | Item | Rationale |
| ---: | --- | --- |
| 1 | ~~**W10** adversarial opponent~~ | **Done, Cycle 4.** Two-constant dumper beats us 58–2 over 30 paired seeds; G0 = 3%. Unblocked. |
| 2 | ~~**W11** adaptive reserve price~~ | **Done, Cycle 4.** G0 3% → 63%, G2 → 85%. Leaves G3 at −37% on 60 seeds and a one-seed weed-cap regression. |
| 2a | **G3 robustness** — why seed 391611974 collapses | Now the only failing gate. Pre-existing (−55% before W11), so it is a standing weakness, not W11 fallout. Trace the seed, do not infer. |
| 2b | **Weed-cap regression** on seed 1232444148 | 11–12 weeds vs a limit of 10, caused by W11's extra land against an unchanged labour cap. Fix the routing; do not raise the cap. |
| 3 | **W9a** read `configuration` | Independent bug fix, cheap, unrelated to G0. |
| 4 | **W12** animal-escape diagnosis | Unblocks wool ($81,668/season at above-base prices) — but only after G0 is measurable. |

**W12 — why sheep starve** is new from Cycle 3 and not yet written up as a full item. The
measurement: with the feed churn removed, the late-sheep configuration still loses **4.10
animals per episode** (baseline 0.02) and reaches only 3.8 of 6 sheep ordered. Animals are
bought, placed, and then not serviced. That is a labour-routing failure in
`_livestock_action`, and it is the actual blocker on every livestock item in this plan —
W1 was rejected twice for what is probably this bug. Diagnose before retrying W1 or W8.

Benchmark each alone so attribution stays readable. **Do not tune toward a bank figure**;
report G1 and let G0 decide.

**W3, W4, W5, W7, W8 are not implemented as tuning passes.** They become seed values,
the fallback path, and acceptance checks for W9c. Promote one to real work only if W9c
underperforms and the diagnostic metrics point at that specific decision.

Record each step's benchmark output in `walkthrough.md` as it lands, so the record shows
what was measured rather than what was intended.

---

## Iteration protocol — run until G0 is met

The goal is a **loop**, not a checklist. W0–W9 were the first pass; W10–W12 are the second,
and the loop continues with new hypotheses generated the same way this plan was.

**One method rule, added after Cycle 3.** Of that cycle's four hypotheses, the two stated by
reading the code were both wrong — the `owned_cows` parameter at `agent.py:695` is
misleadingly named but is passed `owned_animals`, and routing feed from own production did
not make the herd solvent. The one that held was traced from a specific measured anomaly
(1,706 wheat units of turnover) back to the line that produced it. **Trace from a measurement
to its cause; do not infer a cause from reading the code and then go looking for a win.**

### One cycle

1. **Measure.** Run the full benchmark (W0 harness). Record G1–G4 in `walkthrough.md`.
2. **Locate the binding constraint.** From the diagnostic metrics, find the largest single
   gap between realised and achievable revenue — the product being sold furthest below base,
   the idle tile-days, the unsold stock. Do not guess; the metric names the constraint.
3. **Form one hypothesis** targeting that constraint, with a predicted direction for a
   specific metric.
4. **Implement the smallest change** that tests it.
5. **Benchmark it alone.** Accept only if **G0** and the item's predicted metric both move,
   and no guard regresses. Revert otherwise. A change that helps self-play bank without
   moving G0 is not evidence of anything — that exact pattern has now been produced three
   times by three unrelated changes.
6. **Repeat.** If G0 is met, run two more cycles on fresh seeds to confirm it holds, then
   raise the adversary (escalate W10 from the dumper to the behavioural clone) rather than
   raising a bank number.

### When the benchmark is the blocker

If a cycle cannot distinguish two candidates — differences inside the noise band, or a metric
the harness does not report — **the next work item is a benchmark improvement, not a strategy
change.** D6 is what happens when this rule is skipped. Concretely, improve the benchmark
when any of these appear:

- the seed-to-seed spread exceeds the effect being measured;
- an accepted change fails to reproduce on fresh seeds;
- a metric needed to explain a result is not in the report;
- a gate rejects a behaviour that is known to be correct (as `MAX_ACCEPTABLE_WEEDS` does
  for the P6 endgame).

### Stopping conditions

- **Goal met:** G1 ≥ $160,000 median over ≥30 seeds, G3 ≥ $120,000, G2 not regressed,
  reproduced on a second independent seed set. **This pauses the loop, it does not end it** —
  raise the G1 threshold (a one-line config change, by design) and resume from step 1. The
  competition runs to 30 September 2026 and opponents keep improving; a strategy frozen at
  $160,000 will be overtaken.
- **Goal contested:** if several cycles converge and G1 stalls well short of $160,000, the
  finding to report is *where* the ceiling sits and *what enforces it* — most likely a
  specific price curve's glut tolerance. That is a result, and it is reported with the
  evidence rather than quietly abandoned or papered over with a vs-`starter` number.

Never report the goal as reached on a smoke-tier bank. G1 is the only bar that counts.

---

## Current checkpoint — Cycle 5 (2026-08-05)

- **Landed:** the narrow fertilizer-pickup weed guard and W9a configuration support.
- **Verified:** 36 unit tests; 30-seed self-play median **$82,488**, liveness 30/30;
  60 side-swapped adversary episodes at **60% G0**, **−18% G3**, liveness 60/60.
- **Rejected:** three G3 seed-specific variants; broad crop rescue; six-sheep W12 routing.
  W12 eliminated escapes in its experiment but damaged the competitive gate when retained.
- **Still open:** the independent 30 held-out seeds contain seed 391611974 at **−37%**;
  G1 remains far below $160,000. The next cycle must trace a fresh losing seed or improve the
  benchmark's per-day labour/cash diagnostics before another strategy change. Do not retry
  sheep until a schedule predicts pasture placement, feed trips, and crop-worker displacement.

Release evidence is stored in `replays/final-selfplay-30-seed-report.json` and
`replays/final-adversary-30-seed-report.json`. The failed W12 control is retained as
`replays/w9a-w12-release-gate-30-seed-report.json` so the rejection remains reproducible.

---

## Risks and open questions

- **Pasture/coop capacity.** Sheep and cows both need pasture; adding 7 sheep while keeping
  10 cows would need ~17 pasture tiles. W1 assumes the cow reduction pays for it — verify
  the placement logic does not deadlock when slots run short.
- **Shared market.** Both players sell into the same inventory pool, so an opponent dumping
  melon crashes the price regardless of our own volume. The price floor in W2 must not
  cause us to hold stock indefinitely into a price that never recovers.
- **Correlation, not causation.** The winning agents buy sheep *and* differ in several other
  ways. The benchmark gate exists precisely to settle whether W1 alone is what moves score.
- **Sample size.** Seven episodes across seven different opponents. Consistent patterns
  (0 sheep in 7/7, melon below base in 7/7) are trustworthy; single-episode observations
  are not.
- **ep90006347 is one episode.** P1–P7 come from a single game between two near-identical
  bots. The state observations are exact, but the $7,900 marginal-sheep figure (P2) is one
  sample and includes noise — treat it as a strong prior for prioritising W1, not as a
  forecast. The revenue mix from that episode has only 54–59% attribution coverage.
- **Copying a common ladder strategy caps us at its level.** P1–P7 describe a widely-copied
  bot that scores 118–126k. Matching it is a large improvement on our 47–110k, but the
  strategy is evidently common on the ladder, so it is a floor to reach rather than a
  winning edge to defend.
