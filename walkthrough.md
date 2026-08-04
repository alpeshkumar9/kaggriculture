# Walkthrough — Kaggriculture Implementation & Verification

Running record of what has actually been **measured**. Every number below comes from
`python_bot/run_official_tournament.py` on the official engine.

---

## Status — 2026-08-05

| Goal | Bar | Measured | |
| --- | --- | --- | :---: |
| **G1** self-play median bank, 30 seeds | ≥ $160,000 | **$80,656** | ✗ |
| **G2** head-to-head vs previous artifact | ≥ 60% wins | **75%** (60 paired episodes) | ✓ |
| **G3** self-play worst seed | ≥ $120,000 | **$44,807** | ✗ |
| **G4** smoke tier vs `pass`/`random`/`starter` | 100% pass, 0 errors | 90/90 | ✓ |

**G1 is still not met.** Cycle 2 ported two of the four Cycle-1 bug fixes into `agent.py`
and measured them; the other two were measured and rejected. See *Cycle 2* below.

---

## W0 — benchmark rebuilt *(done)*

`run_official_tournament.py` was rewritten because the old one could not tell a winning agent
from a losing one (D6).

- **Self-play is the default opponent.** Built-ins are a `--smoke` liveness tier only.
- **Exact trade accounting.** The harness wraps the engine's `_commit_unit` for the duration
  of an episode, so every reported unit is one that *executed*. This removes the "orders are
  intent, not execution" ambiguity that limited the replay analysis to 54–59% coverage.
- **Score gates the exit code.** G1/G3 thresholds are `--goal` / `--worst-goal`; G2 needs
  `--baseline <path>` and runs every seed with sides swapped.
- **Diagnostics per product**: units, revenue, realised price vs base, fraction sold below
  base, purchases, peak tiles per crop, herd size and completion day, animals lost,
  unharvested value and shed contents at turn 720.
- **Day-aware weed cap**, so the endgame behaviour in P6 is no longer a FAIL.
- **Parallel**: 120 episodes in 64s on 11 workers, so a 30-seed decision costs ~35s.

**Caveat found while running it:** the built-in `random` agent seeds its own RNG with no
seed, so episodes against it are *not* reproducible — and because the market is shared, its
trades perturb our prices and therefore our decisions. Self-play and head-to-head are exactly
reproducible; the `random` smoke episodes are not. Another reason to treat that tier as
liveness only.

**Acceptance met**: run against the unmodified agent it reproduces the 70k–102k self-play
band, and it *shows* the known defects — wool and egg revenue $0 (D1), melon 83% below base
at a realised $138 against a $250 base (D2).

Baseline of record, `agent.py`, 30 seeds: **median $79,407, worst $44,013, best $112,464.**

---

## Cycle 1 — findings

### The plan's central premise is wrong: the market is starved, not glutted

The plan attributes the ladder's 85k–126k ceiling to glut tolerance. Measured market
inventory through a full episode says otherwise — **every product except melon trades above
base for the whole season**, because the town drains faster than either farm supplies:

| Day | WHEAT | CARROT | STRAWBERRY | MELON | MILK | WOOL | EGG |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | $38 | $29 | $198 | $277 | $214 | $226 | $51 |
| 20 | $49 | $40 | $263 | $142 | $212 | $235 | $58 |
| 28 | $54 | $42 | $276 | $48 | $131 | $244 | $68 |

Only melon ever gluts, and only because **no shop buys melon** — the town centre alone
drains it. So the binding constraint is production, not price discipline, and *"sell only at
or above base"* is close to a no-op for seven of nine products.

This invalidates the stated rationale for W2 and W8. It does not invalidate W8's *conclusion*
— egg is genuinely untapped — but for the opposite reason: egg is scarce, not merely
glut-tolerant.

### W9b price model: exact, not 89%

The engine ships with `kaggle_environments`, so `MARKET_PARAMS`, the shop tables and the
town-demand schedule are readable rather than inferred. The agent's `_market_price` now
**matches `engine.market_price` exactly at every tested inventory**, and `_daily_town_demand`
matches the engine's consumption schedule. Both are asserted in
`python_bot/test_agent_allocator.py`, so drift fails a test rather than a benchmark.

### Four real defects found (fixed in the variant, still present in `agent.py`)

1. **Animals stranded in worker inventories.** A worker carrying an animal only routed to
   *unbuilt* cells, so once its block was built it carried the animal forever. Measured:
   7–10 animals in hand beside 6–11 empty structures. Fixing it took the herd from an
   oscillating 8–16 to a stable 22 and cut animals lost from 8.9/episode to 0.4.
2. **Feeding was not farm-wide.** Only service workers fed, and each finished one animal
   completely (feed→care→harvest→collect) before moving on. Half the herd went unfed daily.
   Making "an animal that will escape tonight" a precondition on every hand: $41.7k → $60.3k.
3. **Day-29 wheat churn.** Liquidation dumped the feed reserve, the feed logic re-bought it
   the same turn: 273 units bought for $16,487 and 284 sold for $17,128, every episode.
4. **Final-day harvest only collected melon**, abandoning ~$5.3k of standing crop.

### Labour is the binding constraint, not land or market

Adding 12 animals raised revenue by $29k but cost $27k more in feed and purchases *and*
starved the crop loop — strawberry fell to 1.6 units per tile against a possible 4.0, with
weeds at 26. Measured consequences:

- **Geese are net-negative** at market feed prices: $6.0k of egg against ~$9k of wheat, plus
  ~30 hand-turns a day. Removing them was worth roughly $23k of median bank.
- **The fourth quadrant is net-negative** — more travel and more weed spawn than the extra
  tiles repay.
- A labour cap on the crop plan left the median flat and cost $16k on the worst seed.

### G1 and G2 conflict — measured, not hypothetical

The plan flags this risk once and moves on. It is real, and it decided this cycle. Median
final bank, 30 paired seeds:

| | vs `agent.py` | vs allocator |
| --- | ---: | ---: |
| **`agent.py`** | $79,407 | **$91,321** |
| **allocator** | $72,806 | $86,282 |

The allocator variant is **better against a copy of itself and worse against the incumbent**
— it wins 23% of 60 paired head-to-heads. The mechanism is visible in the diagnostics: our
melon revenue drops from $27.4k to $18.2k against an opponent that dumps. Holding stock for a
reserve price hands the scarcity premium to whoever sells first. Lowering the reserve ratios
and raising planned volume were both tried; neither moved G2 off 23%.

Since the ladder ranks on **win/loss only**, G2 is the closer proxy for rating than G1.
Under the plan's own acceptance rule — *a change that improves the bank but fails its guard
is not accepted* — the variant is rejected and kept as `python_bot/agent_allocator.py`.

### Where the ceiling probably sits

Total town absorption over a 30-day season, valued at base prices, is about **$305k for both
farms combined** (town centre ≈ $126k: 140 units per product at the 1×/2×/4× schedule; shops
≈ $179k: eight shops, six ticks a day, averaging 16.5 active days). Scarcity pricing lifts
the realised value well above that, but only by selling *below* the drain rate.

G1 asks each farm for $160k of bank — i.e. roughly $210k of revenue at current cost ratios —
from a market both farms share. That is not obviously reachable in **self-play**, where the
opponent is by construction equally good. This is a hypothesis worth testing directly before
another tuning cycle: if it holds, G1 needs restating against a named opponent rather than
against a mirror.

---

## Cycle 2 — porting the bug fixes *(accepted, 2026-08-05)*

Cycle 1's four defects were ported into `agent.py` on their own, with no strategy change.
Baseline for every number below is the previous `agent.py` (commit `93927cf`) measured on
the same 30 seeds with the same harness.

**Two of the four are inert in this agent and were rejected.** Fixes 1 (animals stranded in
worker inventories) and 2 (feeding not farm-wide) need a large herd to bite. `agent.py` caps
at 10 cows against 15 candidate slots in `_compact_cow_slots`, so the block never builds out
and no carrier is ever stranded; 2 service workers cover 10 animals, so nothing starves.
`animals lost` is already **0.00 across all 30 baseline seeds**. Ported anyway, they moved no
target metric and tripped their own guards — herd completion slipped day 13 → 15, peak weeds
9 → 11, milk revenue −$1,633, G1 −$1,200, and G2 fell to 55%, below the bar. Reverted.

This corrects a Cycle-1 claim: those two fixes were measured large *in the allocator*, whose
herd is 22. They are not general correctness wins, they are large-herd wins. If a future
change raises the herd, port them again and re-measure.

**Two were confirmed and are now in `agent.py`.**

| Metric | Baseline | Fixes 3+4 | |
| --- | ---: | ---: | :---: |
| **G1** self-play median | $79,407 | **$80,656** | +$1,249 |
| **G2** head-to-head, 60 paired | — | **75%** (45W/15L) | ✓ |
| **G3** worst seed | $44,013 | $44,807 | +$794 |
| **G4** smoke | 89/90 | **90/90** | ✓ |
| Unharvested at turn 720 | $5,878 | **$3,378** | −$2,500 |
| Shed at turn 720 | 12.0 u | **5.4 u** | −6.6 |
| Wheat bought/ep | $18,958 | $9,487 | −$9,471 |
| Wheat sold/ep | $14,093 | $5,303 | −$8,790 |
| Herd complete day | 13 | 13 | guard clean |
| Animals lost | 0.00 | 0.00 | guard clean |
| Peak weeds | 9 | 9 | guard clean |
| Milk revenue | $36,287 | $36,848 | guard clean |

45–15 on paired head-to-heads is far outside noise (binomial p ≈ 6e-5).

### The day-29 wheat churn was a per-turn loop, and it was cash-neutral

`_sell_orders` releases the feed reserve once `day >= FINAL_LIQUIDATION_DAY`, and the feed
purchase in `_market_actions` had no day guard — so on day 29 the agent sold its whole wheat
reserve and re-bought it **every turn, 24 times**. That is the whole of the 276.6 wheat units
per episode reported in Cycle 1, not a season-long wash trade.

Measuring it settled what it actually cost. Baseline net wheat position was
$14,093 − $18,958 = **−$4,865**; with all four fixes it was −$4,720, a difference of **$145**.
The round trip really was near cash-neutral, exactly as D4 predicted — its cost is market-order
slots and hand-turns, not bank. The +$1,249 in this cycle comes mostly from fix 4.

### Final-day harvest: use the engine's `first_yield_day`, not `harvest_day`

`agent.py`'s `CROPS["harvest_day"]` is the engine's `max_yield_day` (wheat 4, carrot 3,
melon 12). The engine actually accepts a HARVEST from `first_yield_day` (2, 2, 10). On the
final day that difference is free money: a wheat two days old holds units the old gate
refused to collect. `first_yield_day` is now in `CROPS` as a Tier-1 game constant and
`_has_standing_yield` gates on it, so the last day harvests every standing unit — any crop
or animal, not just ripe melon.

This is a deliberate deviation from the variant, which reused `payback_days` (= `max_yield_day`)
and was therefore also too strict. It only affects the final day and only in one direction.

---

## Cycle 2b — G1 feasibility: the hypothesis is refuted

New tool: `python_bot/measure_market_ceiling.py`. It measures the pool rather than an agent.
Absorption is taken by conservation instead of by reimplementing the town schedule —
`drained = I0 + supplied − bought_back − final_inventory` — with every term read from the
engine. `FERTILIZER` comes out at exactly 0 drained, which is the correct answer (no shop and
no town centre buys it) and a good check that the identity holds.

**Two engine details had to be read to get this right**, both of which would have silently
corrupted the numbers: the commit op is `BUY_PRODUCT`, not `BUY`; and *a sale at the $1 floor
does not add a unit to inventory*, so the identity must count supplied units, not sold units.

### The Cycle-1 estimate of $305k was the wrong quantity

30 self-play seeds, both farms combined, per episode:

| Product | drained | at base | **timed value** | sold | realised | of timed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| STRAWBERRY | 526 | $63,168 | **$130,774** | 234 | $59,613 | 46% |
| MILK | 447 | $71,456 | **$126,029** | 498 | $76,844 | 61% |
| WOOL | 338 | $67,600 | **$81,668** | **0** | **$0** | **0%** |
| MELON | 140 | $35,000 | $39,907 | 319 | $47,024 | 118% |
| WHEAT | 632 | $15,800 | $26,400 | 203 | $9,712 | 37% |
| TOMATO | 327 | $19,596 | **$25,956** | **0** | **$0** | **0%** |
| EGG | 342 | $17,110 | **$20,632** | **0** | **$0** | **0%** |
| CARROT | 420 | $14,686 | $17,110 | 110 | $3,436 | 20% |
| **Total** | | **$304,416** | **$468,476** | | **$219,474** | **47%** |

Cycle 1 valued absorption at *base price* and got ~$305k, which reproduces exactly. But base
price is the wrong valuation: inventory sits **below** I0 all season, so every unit is quoted
above base — which is why strawberry realises 214% of base today. Valuing the same drain at
achievable prices gives **$468,476**.

`timed value` is the revenue from selling the drained quantity one unit at a time into a pool
drained to `I0 − D`. It is a true upper bound and a loose one: reaching it means holding a
season of output to sell into the deepest scarcity, which a 100-unit shed forbids. A farm
pacing sales at the drain rate keeps inventory near I0 and lands near the base figure. **The
achievable ceiling is the band $304k–$468k, nearer the low end.**

G1 needs $320,000 of combined bank. That is *inside* the band, not above it. **The hypothesis
that G1 is unreachable because the market is too small is refuted** — it survived only on a
base-price valuation. G1 stays as specified.

### The binding constraint is production, and it is not the opponent

The decisive number is the `pass` condition — one farm, whole market to itself, no competitor:

| | self-play | vs `pass` |
| --- | ---: | ---: |
| Ceiling (timed) | $468,476 | $471,408 |
| Realised, both farms | $219,474 (47%) | $161,199 (**34%**) |
| Candidate bank | $81,549 | $133,477 |

Alone in the market with nothing to compete against, the agent still leaves **66% of the
ceiling unsold** and banks $133,477 — 83% of the bar. It cannot produce enough to claim
demand it already has exclusive access to. Competition is not what caps us.

**$128,256 per episode is demand nobody touches at all**: wool $81,668, tomato $25,956, egg
$20,632, all at 0% capture across every seed. `EARLY_SHEEP_TARGET`, `LATE_SHEEP_TARGET`,
`TOMATO_TARGET` and `EARLY_GOOSE_TARGET` are all still hard-zeroed at `agent.py:39-43`.

This does not simply reinstate W1/W8. Cycle 1 measured the allocator adding 12 animals for
+$29k revenue and +$27k cost, and measured geese net-negative — because **labour**, not
market access, was what ran out. That is consistent with what is measured here: production is
the constraint, and labour is the part of production that binds first. Wool is the largest
untouched pool, but it is not free.

---

## Next cycle — where the evidence points

1. **Raise production per hand-turn.** This is now the named constraint, on direct evidence:
   34% capture with no competitor. The allocator's `_needs_water` is the strongest lead —
   watering is the largest consumer of hand-turns, and it skips waterings that buy nothing
   (an ongoing crop's yield is on a fixed clock). That change is *in the rejected variant*
   and was never measured on its own. Port and benchmark it alone, as with fixes 3 and 4.
2. **Then reconsider wool** with the labour saved, not before. The guard is Cycle 1's
   result: revenue up, cost up, crop loop starved. Sheep only pay if hand-turns exist to
   service them.
3. **Resolve G1 vs G2.** Selling patience is right in self-play, wrong against a dumper. A
   reserve price that adapts to the opponent's observed selling rate — market inventory
   trend is in the observation — remains the candidate.
4. **W9a — read `configuration`.** Still unshipped in `agent.py`, still a live bug,
   independent of everything else.

Melon is the one product sold *past* its drain (118% of timed value, 319 units against 140
drained) and is 83% below base as a result. It is the clearest case of selling into our own
collapse, and it is a pacing problem, not a production one.

---

## Cycle 3 — steps 1 and 2 measured, both rejected

All figures are 30-seed self-play, `run_official_tournament.py --seed-count 30 --no-gate`.
Baseline is the committed `agent.py` at 594d160, re-measured in the same session: **median
$80,656, worst $44,807, best $114,108, peak weeds 9.**

### Step 1 — porting the allocator's `_needs_water` alone: rejected, −$12.6k

| | baseline | + `_needs_water` | + urgency priority |
| --- | ---: | ---: | ---: |
| Median bank | **$80,656** | $69,057 | $68,040 |
| Worst seed | $44,807 | $37,495 | $42,196 |
| Peak weeds | 9 | 11 (**liveness FAIL**) | 8 |
| Wheat units/ep | 113.7 | 175.1 | 176.2 |

The port needs a second half the plan did not name. Skipping a watering leaves the tile one
dry day from becoming a weed, and the existing priority table ranks that tile at 1 — behind
weed clearing and harvesting — so labour did not reliably reach it and plants died. Adding
the allocator's `-3` priority for `consecutive_unwatered >= 1` (and the matching branch in
`_next_action`, ahead of `HARVEST`, since watering preserves the plant while harvesting does
not) restored the weed count to 8 and cleared the liveness gate. It did not restore the bank.

**The watering logic is not what was wrong.** It is strictly more faithful to the engine —
verified against `kaggriculture.py`: the `WATER` op only adds yield to a non-ongoing crop
inside `(max_yield_day+1)//2 <= age <= max_yield_day` (l.383), and an ongoing crop's yield is
on a fixed `interval` clock where watering matters only for survival and the fertilizer
bonus (l.769). The hand-turns were genuinely freed. They went into **wheat**: purchases
$9,487 → $11,867 (+$2,380) for +$2,389 revenue. Net zero.

**Finding: freeing labour does not raise the bank while the marginal use of a spare hand is
wheat.** The constraint named in Cycle 2 is real, but relieving it is not sufficient — the
value of the marginal hand-turn has to be raised first, or the freed labour is spent at cost.

### Step 2 — wool with the labour saved: rejected, and blocked upstream

Tested on top of the water port, both affordable configurations (`EARLY_SHEEP_TARGET = 6`
cannot fire at all — it needs $3,700 against $3,000 `startingMoney`):

| | baseline | early sheep 2 | late sheep 6 |
| --- | ---: | ---: | ---: |
| Median bank | **$80,656** | $53,650 | $59,844 |
| Wool revenue | $0 | $9,539 | $1,548 |
| Wheat purchases | $9,487 | $27,456 | **$86,027** |
| Wheat revenue | $5,303 | $29,508 | **$87,859** |
| Cow peak | 10.0 | 8.1 | — |
| Animals lost | 0.00 | 1.93 | — |

The feed loop is the blocker, and it is visible at baseline: **the agent already spends more
on wheat than wheat earns** ($9,487 out, $5,303 in). That spend scales with herd size, so 16
animals turn it into $86k of near-zero-margin turnover that consumes market orders and
capital and starves the cows. Wool returned $1,548 against it.

Wool demand itself is not the problem and the Cycle 2 reading of it holds: at 42.9 units the
realised price was **$222.50 against a $200 base, 21% below-base** — the pool is genuinely
unexploited and pays above base. It cannot be reached through the current feeding path.

`agent.py` was reverted to 594d160 byte-for-byte; 31 tests pass. Nothing from this cycle is
in the artifact.

### Where this leaves the plan

Steps 1 and 2 are now measured and closed. The next lever is not more labour and not more
animals — it is **the marginal use of a hand-turn and the feed economics that price it**:

1. **Make wheat feed cheaper than wheat bought.** The feed reserve buys at market; the farm
   grows wheat at $10/seed for 6 units. Routing feed from own production instead of
   `BUY_PRODUCT` is what would make any herd expansion — wool included — solvent. This is
   the precondition step 2 actually needed, and it was not identified before.
2. **Then re-run step 2.** Wool is worth $81,668 a season at above-base prices.
3. G1-vs-G2 adaptive reserve price, and W9a, are unchanged and independent.

---

## Schema compliance

`python3 -m unittest python_bot/test_agent.py python_bot/test_agent_allocator.py` — 31 tests,
all passing: 720 valid turns, Kaggle action schema, price/town-demand models exact against
the engine. Unit tests never establish a score change; the tournament harness does.
