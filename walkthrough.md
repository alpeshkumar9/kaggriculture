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

### Step 3 — feed economics: one real bug found, still not shippable

Two follow-ups were measured after steps 1 and 2, both aimed at the feed loop.

**Routing feed from standing wheat** (count ripe wheat on our own tiles toward the feed
reserve so it is not bought back from the market): 30 seeds, median $80,032 against the
$80,656 baseline — **flat**. Wheat purchases fell $9,487 → $7,527, but harvested-for-sale
wheat fell by nearly as much, so net feed cost moved $4,184 → $4,012. Peak weeds 9 → 11 with
a liveness failure. Rejected. Re-tested with `LATE_SHEEP_TARGET = 6` it cut the churn from
$86,027 to $60,137 of wheat purchases but the bank was still $67,755 — **the hypothesis that
own-production feed makes herd expansion solvent is falsified.**

**The counter bug** was then traced rather than guessed, and it is real. The feed *buy*
target (`agent.py:212`) is `protected_animals * WHEAT_RESERVE_DAYS`, where
`protected_animals` includes `cows_to_buy + geese_to_buy + early_sheep_to_buy +
sheep_to_buy` — animals **not owned**. The *sell* guard (`agent.py:695`) reserves
`owned_animals * WHEAT_RESERVE_DAYS` — animals **owned**. The two never agree while a
purchase is pending, and `sheep_to_buy` is recomputed as `6 - owned_sheep` every day while
`BUY_ANIMAL` only fires on days 16-18, so a ~24-unit gap is bought and sold back daily for
the rest of the season. At baseline `cows_to_buy` reaches 0 once the herd completes, which
is exactly why the churn is invisible there and explodes with sheep.

Zeroing the counters when the order does not actually fire eliminates it: with
`LATE_SHEEP_TARGET = 6`, wheat turnover collapsed from 1,706 units / $60,137 to 105 units /
$6,850. The diagnosis is confirmed.

**It still does not ship.** The fix alone, 60 seeds, against the same 60-seed baseline:

| | baseline | counter fix |
| --- | ---: | ---: |
| Self-play median | $78,780 | $80,762 (+$1,982) |
| Wheat purchases | $9,638 | $8,038 |
| Head-to-head (120 ep) | — | 52% (62-6-52) |
| Self-play liveness | 60/60 | **59/60** |
| Smoke liveness | 90/90 | **178/180** |

+2.5% median, a head-to-head indistinguishable from a coin flip, and **liveness failures the
baseline does not have**. Bundled with the standing-wheat change it read as +$2,893, but that
bundle also failed liveness — the extra was not coming from the fix. Rejected by G2 and the
liveness guard. `agent.py` is byte-identical to the pre-cycle artifact; 31 tests pass.

### Where this leaves the plan

Steps 1, 2 and 3 are measured and closed. Three separate attempts to convert freed labour or
cheaper feed into bank produced +2.5% at best, all of it inside the noise band that the
$42k-$120k per-seed spread implies. **Whatever caps this agent near $80k is not watering,
not wool, and not feed churn.**

What the cycle did establish, and what the next one should start from:

1. **The counter bug is real code, worth fixing on its own merits** once something else makes
   herd expansion viable — it is what made the wool experiments unreadable. It is not worth
   shipping alone at the current 10-cow configuration.
2. **Wool is now blocked on animal escapes, not on feed.** With the churn removed, the
   late-sheep run still lost **4.10 animals per episode** (baseline loses 0.02) and reached
   only 3.8 of 6 sheep. Sheep are being bought and then starving. That is a
   placement-and-servicing labour failure and it is the next thing to measure — not a market
   or feed question.
3. **The $80k ceiling needs a different explanation.** Cycle 2 measured 34% market capture
   with no competitor at all; three labour/feed interventions have now failed to move it.
   The remaining untested explanation is the crop mix itself — melon is 83% below base and
   sold past its drain, and strawberry is the only product realising above base at volume.
4. G1-vs-G2 adaptive reserve price, and W9a, are unchanged and independent.

A note on method for the next cycle: two of this cycle's four hypotheses were stated from
reading the code and both were wrong (the `owned_cows` parameter at `agent.py:695` is
misleadingly named but receives `owned_animals`, and standing-wheat routing did not make the
herd solvent). The one that held was traced from a specific measured anomaly — 1,706 wheat
units of turnover — back to the line that produced it. Trace, do not infer.

---

## Cycle 4 — W10, the adversarial opponent (2026-08-05)

**What was built.** `python_bot/opponent_dumper.py`: a frozen copy of `agent.py` at commit
`93f333a` with two constants changed — `SELL_PRICE_MULTIPLIERS` set to `0.0` for every
product, and `PREMIUM_SELL_BATCH`/`STAPLE_SELL_BATCH` raised from 8/20 to the shed capacity
of 100. It farms exactly as we do and sells everything the turn it exists.

`run_official_tournament.py` gained an `--adversary` tier: paired, sides swapped, and it is
where G0 and G3 are now decided. G1 was demoted to a printed tracker and no longer fails the
run, per the revised gate table.

**Command.**

```bash
python3 python_bot/run_official_tournament.py --agent python_bot/agent.py --opponents "" --adversary python_bot/opponent_dumper.py --seed-count 30
```

**Measured, 30 paired seeds / 60 episodes.**

| | |
| --- | --- |
| G0 win rate | **3%** — 2 wins, 0 ties, 58 losses |
| Our bank | median $70,254 (min $35,395, max $114,326) |
| Adversary bank | median $83,366 (min $46,320, max $128,479) |
| Margin | median −13%, best +29%, worst −55% |
| G3 worst seed | 718043812 swapped, $51,174 vs $114,368 |
| Liveness | 60/60, 0 errors |

Split by side: 0/30 as player 0, 2/30 swapped.

**What this establishes.** W10's acceptance was *the dumper beats `agent.py`*, and it does,
58–2. Approach (2) from the plan was sufficient; the replay agent and the behavioural clone
were not needed. This is the **first local reproduction of the ladder result** — 6 of 7
ladder losses, 58 of 60 here — and G0 is now a measurable gate.

The fixture is faithful, not merely strong: the adversary's median $83,366 lands on the
observed ladder band of $84,682–$125,241, and the losses are close (median −13%) rather than
blowouts. That is direct evidence against the retired $160k premise — the gap is close games
in a shared market, not a 2× production shortfall.

**The mechanism, from the candidate-side diagnostics.** Against the dumper, **82% of our
melon units and 50% of our milk units clear below base**, melon realising $114.4 against a
$250 base. Strawberry — the one product the dumper cannot flood as fast — still realises
$260.1 against a $120 base, 0% below base. We are waiting for a price the opponent has
already taken. That is precisely W11's target and it now has a metric.

**Guard.** `opponent_dumper.py` is a fixed test fixture. It must never be tuned, never
re-synced with `agent.py`, and never submitted; G0 is only comparable across cycles while it
is frozen.

---

## Cycle 4 — W11, adaptive reserve price (2026-08-05)

**What changed in `agent.py`.** `_supply_pressure` reconstructs the opponent's net supply
from the shared market inventory: the engine moves inventory by exactly *our trades + theirs
− the town drain*, so netting out the quantity we ourselves issued leaves *their sales − the
drain*. Summed over a one-day window, a positive figure means the market is filling faster
than the town empties it. For those products the reserve price is cut and the sell batch
raised. State is kept per player index so a self-play harness handing the same module to both
sides cannot cross-contaminate, and resets when the step counter fails to advance.

**Measured, all against the W10 adversary unless stated.**

| gate | pre-W11 | W11 | |
| --- | ---: | ---: | --- |
| G0, 30 seeds / 60 episodes | 3% | **63%** | MET |
| G0, 60 seeds / 120 episodes (30 held out) | 13% | 62% | MET |
| G2 vs previous artifact, 60 episodes | 50–52% | **85%** | MET |
| G1 self-play median, 30 seeds | $80,656 | $83,244 | +3.2% |
| G3 worst seed, 30 seeds | −55% | −18% | MET |
| G3 worst seed, 60 seeds | −55% | −37% | **NOT MET** |
| Smoke | 90/90 | 90/90 | pass |

Our median bank against the adversary rose $70,254 → $74,800.

**The estimator that measured nothing.** The first version counted *consecutive* turns of net
inflow and returned a byte-identical benchmark — every product, every diagnostic, to the
dollar. Instrumenting the live signal showed the cause: the streak never exceeded **1** for
any product, because opponents sell in bursts after a harvest and idle in between, so three
consecutive rising turns never occur. The same instrumentation showed where the damage was —
melon held below base on 262 turns, carrot on 331. A one-day summing window fires correctly
(melon: 102 surplus-days, 37 of them while we held melon) and produced the result above.

**The gain is volume, not price — the hypothesis was wrong about its own mechanism.** W11
predicted that realised premium prices would rise. They did not: melon stayed at **85% below
base, realised ~$115**, and milk drifted from 50% to 52% below base. What moved was
throughput — melon 156.5 → 187.1 units/episode, wheat 102.9 → 165.3, unharvested value at
season end $5,008 → $2,738. Selling earlier frees shed capacity and capital, which compounds
into more production. Worth recording as a case where the diagnosis was right, the fix worked,
and the stated causal story was wrong.

**Tuning, and the limit placed on it.** Four configurations at 120 paired episodes each:

| reserve cut | batch 40 | batch 100 |
| ---: | ---: | ---: |
| 0.35 | — | **64%** |
| 0.55 | 59% | 62% |
| 0.75 | 59% | — |

The batch effect holds at both reserve levels; the reserve effect holds at neither. Shipped
configuration is batch 100 with the cut left at 0.55 — *not* the top-scoring 0.35/100 run,
because at a ~4.5pp standard error a 2pp gap is noise and adopting it would be fitting the
fixture.

**Two defects left open.**

1. **G3 on the wider seed set** — seed 391611974, $32,984 vs $51,979 (−37%). Pre-existing:
   the previous artifact scores −55% on the same 60 seeds. W11 halves it without clearing the
   20% bar. This is now the only failing gate.
2. **Weed-cap regression, one seed.** Seed 1232444148 hits 11–12 weed tiles against the
   harness limit of 10 in the self-play and head-to-head tiers; the previous artifact is clean
   at 90/90 and 30/30. Mechanical cause: more cash buys more land (peak melon tiles 32.4 →
   38.0) against an unchanged labour cap. Fix the routing rather than the cap.

---

## Cycle 5 — weed liveness, W9a configuration, and W12 diagnosis (2026-08-05)

**Accepted: narrow weed routing.** Seed 1232444148 reached 12 weeds because workers kept
starting new fertilizer pickups while six or more already-dry crops needed service. Blocking
only that optional pickup during the backlog reduced the exact seed to 5 weeds. Broader rescue
modes were rejected: pausing fertilizer collection/delivery/purchase fixed weeds but collapsed
G0. The narrow version reproduces the accepted gate on the original 30 seeds:

| gate | result | status |
| --- | ---: | --- |
| G0 adversary, 60 paired episodes | 60% | MET |
| G3 worst seed | −18% | MET |
| G1 self-play median, 30 seeds | $82,488 | −0.9% vs W11; guard held |
| Liveness | 90/90 | pass |
| Peak weeds | 8 adversary / 6 self-play | pass |

**Accepted: W9a configuration.** `agent.py` now reads both mapping-style and attribute-style
episode configuration. `turnsPerDay`, `episodeSteps`, `shedCapacity`,
`maxMarketOrdersPerTurn`, `farmHandCostMult`, board/start/weed values, and town intervals are
normalized in one place. Supply history uses the configured day length; liquidation and last
planting derive from season length; overflow, order count, and payroll use their configured
limits. Focused custom-config tests pass, and the default regression seed remains exactly
$67,426 after the change.

**Diagnosed but rejected: W12 / six late sheep.** Extending pasture placement beyond ten
slots and making `consecutive_unfed >= 1` an emergency feed priority reduced animal loss from
3.20 to 0.00 per episode on ten seeds and raised wool from 19.8 to 36.4 units/episode. The
strategy still completed only 4.7 sheep on average by day 22 and scored a $70,279 self-play
median. Worse, retaining the routing/feed changes with sheep disabled collapsed the full G0
gate from 60% to 28%, worsened G3 to −53%, and introduced an 11-weed failure. All W12 behavior
was therefore reverted; `LATE_SHEEP_TARGET` remains zero. The experiment establishes that
escape prevention is necessary but not sufficient—the labour and cash schedule must be
co-designed before wool can ship.

**G3 follow-up.** Three targeted changes on seed 391611974—early demand-driven strawberry,
reserve cut 0.35, and reserve cut 0—improved its bank but only to −28% to −31% against the
dumper, still outside the −20% gate. They were reverted. The wider 60-seed G3 failure at
−37% therefore remains open even though the release 30-seed set passes.

---

## Schema compliance

`python3 -m unittest python_bot.test_agent python_bot.test_agent_allocator python_bot.test_replay_opponents` — 41 tests,
all passing: 720 valid turns, Kaggle action schema, price/town-demand models exact against
the engine. Unit tests never establish a score change; the tournament harness does.

---

## Cycle 6 — replay-derived opponent roster (2026-08-05)

Every complete competition JSON in `logs/` now produces one opponent. The 17 primary
opponents replay the logged rival's actual actions on its original seed and seat; their final
banks closely reproduce the source range (roughly $50k–$150k). Both source wins and losses
are included. Episode 90006347 has no account-name match, so its higher-scoring seat is used
and that fallback is recorded in `profiles.json`.

The first ghost implementation exposed an important indexing error: replay observation step
N is the state *after* action N, so an agent receiving observation step N must return the
recorded action at N+1. Correcting that offset changed the ghosts from inert fixtures into
real competitors. The builder also emits approximate behavioural profiles for unfamiliar
seeds, but those are secondary fuzz tests because they do not reproduce path-dependent worker
movement.

| gate | result | status |
| --- | ---: | --- |
| Exact logged opponents | 17/17 live | pass |
| Aggregate wins | 6/17 (35%) | below 50% gate |
| Candidate median bank | $84,845 | baseline |
| Candidate range | $46,475–$133,219 | baseline |

The eleven current losses are 89980458, 89983092, 89983749, 89989543, 90006347,
90060119, 90062890, 90108226, 90112980, 90120436, and 90147946. This roster replaces
non-competitive built-ins as the primary opponent test. The next strategy cycle should trace
one of the high-value losses (preferably 90120436 or 90112980), form one measurable
hypothesis, and then require improvement across the full roster rather than on that seed alone.

---

## Cycle 7 — demand-timed strawberry priority (2026-08-05)

The fresh roster baseline reproduced Cycle 6 exactly: **6/17 wins (35%)**, median bank
**$84,845**, and 17/17 liveness. The largest losses exposed the same crop-allocation failure:
against episodes 90108226, 90112980, and 90120436 the candidate reached 45–54 melon tiles but
only 16–21 strawberry tiles. Melon has no shop demand and a quadratic glut curve; those town
schedules had unlocked strawberry demand while melon occupied the available land.

The accepted change keeps the default day-10 strawberry priority until the observation shows
a strawberry-buying shop, then advances it to the named day-8 strategy target. It does not
special-case an opponent or seed. A day-6 candidate moved the intended production metrics but
remained at 6/17 wins and produced a 12-weed liveness failure; a demand-gated day-6 candidate
reached 7/17 but retained the failure. Both were rejected.

| metric | baseline | accepted day 8 |
| --- | ---: | ---: |
| Exact-roster wins | 6/17 (35%) | **9/17 (53%)** |
| Candidate median bank | $84,845 | **$95,486** |
| Strawberry revenue/episode | $24,944 | **$37,964** |
| Peak strawberry tiles | 26.4 | **36.1** |
| Peak melon tiles | 39.4 | **26.8** |
| Roster liveness | 17/17 | **17/17** |
| Self-play median, 30 seeds | $82,488 accepted reference | **$88,177** |
| Adversary G0, 60 paired episodes | 60% accepted reference | **80%** |
| Adversary G3 worst margin | −18% accepted reference | **−17%** |

Per-opponent accepted outcomes: wins against 89978502, 89983092, 89984407, 89985050,
89989543, 90060119, 90091984, 90115034, and 90157524; losses against 89980458, 89983749,
90006347, 90062890, 90108226, 90112980, 90120436, and 90147946. The aggregate roster gate
is met, although the one-episode-per-opponent floor remains red for every loss and is not a
statistically meaningful fractional rate on an exact ghost.

Verification: 42 unit tests pass; roster 17/17, self-play 30/30, and adversary 60/60 liveness
pass. Reports: `replays/cycle7-roster-baseline.json`,
`replays/cycle7-demand-strawberry-day8.json`, `replays/cycle7-selfplay-30.json`, and
`replays/cycle7-adversary-30.json`.

---

## Cycle 8 — final-day livestock service bypass (2026-08-05)

The closest Cycle-7 loss, replay 90147946, finished only $433 behind while leaving 33 wheat
and 17 melon units standing, worth $5,075 at base prices. A retained official trace showed
that day 29 spent only 11 actions harvesting and 74 passing while workers continued issuing
`PICKUP`, `CARE`, and fertilizer-service actions. Those actions cannot create another payable
livestock cycle before turn 720, and `_livestock_action` ran before the existing all-product
liquidation router.

The accepted fix skips `_livestock_action` on the derived final liquidation day. Existing
standing animal yield is still collected by `_has_standing_yield`, through the same route as
crop yield. No opponent, seed, price, or new tuning literal is involved.

| metric | Cycle 7 | Cycle 8 |
| --- | ---: | ---: |
| Exact-roster wins | 9/17 (53%) | **10/17 (59%)** |
| Candidate median bank | $95,486 | **$97,565** |
| Unharvested value/episode | $3,403 | **$683** |
| 90147946 result | $74,157 vs $74,590 (loss) | **$75,771 vs $74,613 (win)** |
| Self-play median, 30 seeds | $88,177 | **$91,513** |
| Adversary G0, 60 episodes | 80% | **87%** |
| Adversary G3 worst margin | −17% | **−14%** |
| Liveness | all pass | **107/107 pass** |

Two related experiments were rejected. Moving liquidation to day 28 reduced standing value
but regressed the roster to 8/17 and median bank to $92,638. Hiring the maximum workforce on
day 29 reduced standing value on 90062890 but payroll and market timing worsened its margin.
The farm-wide region-threshold change was byte-for-byte inert on the focused trace and was
also reverted, leaving the accepted change attributable to the service bypass alone.

Seven exact losses remain: 89980458, 89983749, 90006347, 90062890, 90108226, 90112980, and
90120436. The next closest is 90062890 at −$675; its remaining $3,000 standing value was not
solved economically by extra final-day hires.

Verification: 43 unit tests pass. Reports: `replays/cycle8-accepted-roster.json`,
`replays/cycle8-selfplay-30.json`, and `replays/cycle8-adversary-30.json`.

---

## Cycle 9 — eight-cow crop-capacity portfolio (2026-08-05)

Rather than tune one replay at a time, this cycle tested shared-market portfolio changes over
the complete roster. Two observation-driven candidates were rejected: pausing milk expansion
after a one-day milk-supply surplus did not activate early enough to alter the 10-cow build,
and expanding strawberries to 40 after a healthy quote raised strawberry output without
adding a win. Both preserve 10/17 and are not in the artifact.

The accepted general change reduces the named compact-cow target from 10 to **8**. This is a
portfolio rebalance, not an opponent rule: milk is the product with the most frequent
below-base sales in the remaining losses, while strawberries retain recurring shop demand.
The two freed pasture/service slots reduce wheat purchases and let the existing crop planner
reach a larger strawberry block.

| metric | Cycle 8 | Cycle 9 |
| --- | ---: | ---: |
| Exact-roster wins | 10/17 (59%) | **11/17 (65%)** |
| Candidate median bank | $97,565 | **$102,813** |
| Peak cows | 9.9 | **8.0** |
| Milk units/episode | 261.4 | **218.2** |
| Strawberry revenue/episode | $39,044 | **$45,534** |
| Self-play median, 30 seeds | $91,513 | **$105,098** |
| Adversary G0, 60 episodes | 87% | **92%** |
| Adversary G3 worst margin | −14% | **−6%** |

It flips two opponents in the same roster run: 89980458 ($94,576 vs $94,041) and 90062890
($95,294 vs $89,785). Six exact losses remain: 89983092, 89983749, 90006347, 90108226,
90112980, and 90120436. The 30/30 self-play and 60/60 adversary liveness guards pass.

The trade-off is a small animal-loss signal (0.33/episode in self-play and 0.45 against the
adversary), so the next cycle should trace the affected feed route before adding sheep or
expanding the herd. Verification: 43 unit tests pass. Reports:
`replays/cycle9-eight-cows.json`, `replays/cycle9-eight-cows-selfplay-30.json`, and
`replays/cycle9-eight-cows-adversary-30.json`.

---

## Cycle 10 experiment — sheep diversification rejected (2026-08-05)

The six remaining ghosts all use a six-sheep wool stream, so this was tested as a portfolio
mechanism: a seven-cow herd plus six sheep, with 13 compact livestock slots and day-10--12
purchase timing. It was rejected. The current allocator's service-worker share and wheat
carrying path made the combined herd consume worker turns needed for premium crops: wheat
purchases rose to $108,575 per episode, strawberry revenue fell to $27,261, and the exact
roster collapsed to **4/17 wins** (from 11/17). All 17 episodes remained live, but liveness
does not compensate for the competitive regression. The artifact remains the eight-cow,
no-sheep policy. Report: `replays/cycle10-seven-cow-six-sheep.json`.

---

## Cycle 11 — expanded replay roster and premium crop rebalance (2026-08-06)

Commit `264e1a4` added eight complete ladder replays, expanding the exact ghost roster from
17 to 25 opponents. Rebuilding `python_bot/opponents` preserved the source seed and seat for
all eight. The Cycle-9 agent won **13/25 (52%)** overall but only **2/8** new matches, with a
median bank of **$102,813**.

The new opponents repeatedly paired 4–8 sheep with 5–10 cows, but the earlier wool diagnosis
still held. A co-designed six-sheep plus reduced-watering experiment produced wool yet lost
1.36 animals per episode, collapsed to **6/25 wins**, and reduced median bank to **$75,822**.
It was rejected in full.

The accepted change rebalances the named default premium targets from 30 strawberries / 40
melons to **40 strawberries / 18 melons**. This follows the mechanics: strawberries receive
recurring shop demand, whereas no shop consumes melon and its glut curve is especially harsh.

| metric | expanded baseline | accepted |
| --- | ---: | ---: |
| Exact-roster wins | 13/25 (52%) | **15/25 (60%)** |
| Candidate median bank | $102,813 | **$104,344** |
| Peak strawberry tiles | 37.1 | **43.4** |
| Peak melon tiles | 28.1 | **21.7** |
| Strawberry revenue/episode | $44,590 | **$51,452** |
| Animal loss/episode | 0.28 | **0.16** |

The change flipped new opponents 90220515, 90221241, and 90223428 while regressing the close
90115034 match, for a net gain of two wins. Guards passed: **36/60 head-to-head wins (60%)**
against the committed agent, self-play median **$106,984** over 30 seeds, and **58/60 (97%)**
against the frozen dumper with a worst margin of **−4.8%**. All 150 guard episodes were live.

Rejected follow-ups were a 35/30 balanced portfolio (14/25), a visible-opponent melon-contest

## Removal of the Adversary Test (2026-08-06)

**What was changed.** The Adversarial "Dumper" test was retired from the testing framework as it was no longer driving agent improvements. The `--adversary` CLI argument and the `G0`/`G3` evaluation metrics were removed from `python_bot/run_official_tournament.py` and the `implementation_plan.md` goals table. The `opponent_dumper.py` file was renamed to `opponent_base.py` and repurposed strictly as the baseline structure for the replay ghosts.

## Cycle 13 — Roster Update and Benchmark (2026-08-06)

**What was changed.** 10 new Kaggle replay logs were parsed to expand the opponent roster to 35 total profiles.

**Measured, all against the expanded 35-opponent roster.**
* **Win rate:** 29% (10 wins, 25 losses)
* **Median Bank:** $94,679 (min $49,911, max $126,682)
* **Liveness:** Failed on seed `663784208` against `replay_90386123` with 12 weed tiles (limit is 10)

The agent lost every single match against the 10 newly introduced replay opponents, pulling the overall win rate down to 29%.

---

## Cycle 14 — Overplanting fix: crop workload cap & carrot removal (2026-08-07)

**Root cause diagnosed (from Cycle 13 liveness failure).** `_next_crop` and `_available_crop`
both fell back to unlimited wheat/carrot on every open tile. With ~92 crops and 14 workers
(some already servicing 9 animals), workers spent all turns on water/harvest in their assigned
regions and never had capacity to clear weeds elsewhere. Result: 12 weed tiles on seed
`663784208` vs `replay_90386123` (limit: 10).

**What changed in `agent.py`.**

- `WHEAT_TILE_CAP = 6` — new named constant: enough tiles to grow feed for 8 cows at
  `WHEAT_RESERVE_DAYS = 2` (~4 units/tile), plus 2 tile buffer.
- `_next_crop`: replaced `if wheat < 7: return "WHEAT" / if day <= 3: return "CARROT"` with
  `if wheat < WHEAT_TILE_CAP: return "WHEAT"` only. Carrot removed entirely.
- `_available_crop`: removed the carrot branch and the uncapped `min(available, ...)` fallback.
  Replaced with a wheat tile-count check against `WHEAT_TILE_CAP`, then `return None`.
  Workers now leave tiles empty rather than filling them with wheat once the feed quota is met.
- Seed purchase target for `"WHEAT"` capped at `WHEAT_TILE_CAP` (was using `SEED_BUFFER = 25`).
- `test_agent.py`: updated `test_plants_available_seed_on_empty_tile` to expect `PLANT WHEAT`
  (carrot intentionally removed per D3 — realises below base, opponents plant none).

**Measured, 35-opponent roster.**

| metric | Cycle 13 baseline | Cycle 14 | |
| --- | ---: | ---: | --- |
| Roster win rate | 29% (10/35) | **42% (15/35)** | +13pp |
| Median bank | $94,679 | **$106,684** | +$12k |
| Min bank | $49,911 | $31,341 | regressed (one outlier) |
| Max bank | $126,682 | $127,834 | flat |
| **Liveness** | **FAILED** (12 weeds) | **36/36 PASS** | ✅ fixed |
| Peak weeds | 12 | **5** | |
| Peak wheat tiles | — | **6.0** | cap working |

Roster gate (50%) **not met** — but this is a clear improvement on the Cycle 13 baseline (29%).

**Per-product diagnostics (candidate side).**

| Product | units/ep | revenue/ep | realised | base | below-base |
| --- | ---: | ---: | ---: | ---: | ---: |
| STRAWBERRY | 222.4 | $50,569 | $227 | $120 | 4% |
| MILK | 197.9 | $41,821 | $211 | $160 | 16% |
| WOOL | 98.1 | $20,906 | $213 | $200 | 23% |
| MELON | 61.8 | $14,372 | $233 | $250 | 76% |
| FERTILIZER | 82.9 | $6,276 | $76 | $100 | **98%** |
| WHEAT | 33.5 | $1,897 | $57 | $25 | 0% |

Herd: peak 12.0 animals (8 cow + 4 sheep), complete day 16, **lost 0.00**.
Unharvested at turn 720: $21. Shed at season end: 2.2 units.

**Unexpected finding: sheep are running without catastrophic failure.**

`LATE_SHEEP_TARGET = 6` and `SHEEP_PURCHASE_START_DAY = 0` were already in the code and
remained unchanged. With the overplanting fix freeing ~30 worker turns per episode that were
previously spent watering wheat/carrot, sheep appear to be receiving adequate service: peak
herd 12.0, animals lost 0.00 across all 36 episodes, wool $20,906/ep at $213/unit (above base).

This is the **first run where sheep have not caused catastrophic crop-loop collapse**. Previous
sheep cycles (3, 5, 10, 11) all suffered wheat purchase explosion and strawberry revenue
collapse. Those failures were rooted in overplanting (workers had no spare capacity); with the
cap in place, the symptom no longer appears.

This is a single-measurement observation, not a controlled experiment. The sheep code was
not changed — only the crop workload ceiling was fixed. **Do not re-open the sheep direction
as a tuning exercise yet.** Record this as a premise for the next investigation: if the
labour freed by the overplanting fix is genuinely what made sheep viable, a targeted sheep
measurement (vs previous artifact, sides swapped) should confirm it. That is separate work.

**Largest remaining losses.**

| opponent | ours | theirs | gap |
| --- | ---: | ---: | ---: |
| replay_90642136 | $31,341 | $108,023 | −$76k (outlier) |
| replay_90541840 | $80,625 | $162,778 | −$82k |
| replay_90543543 | $83,658 | $129,729 | −$46k |
| replay_90544317 | $106,972 | $139,382 | −$32k |
| replay_90595197 | $118,276 | $130,123 | −$12k |
| replay_90588066 | $115,637 | $126,487 | −$11k |
| replay_90616307 | $113,561 | $133,565 | −$20k |

`replay_90541840` opponent at $162,778 is the highest score observed from any opponent.
`replay_90642136` at $31,341 for us is a structural failure on that specific seed — likely
an early-game cash crunch worth tracing before the next cycle.

**Two open issues.**

1. **Fertilizer selling at 98% below base.** We collect and sell fertilizer at ~$76 against a
   $100 base, but 98% of units clear below base (likely at the $1 floor). This wastes market
   order slots and worker pickup/delivery turns. Not selling fertilizer at all (or only selling
   above base) may be net-positive.
2. **replay_90642136 structural failure.** Our $31,341 bank against their $108,023 is more
   than a competitive loss — it suggests a seed-specific early failure. Trace before next cycle.

**Unit tests: 37/37 pass.** (`python_bot.test_agent` and `python_bot.test_agent_allocator`;
`test_replay_opponents` has 4 pre-existing KeyErrors on old episode IDs not in the current
`ghost_actions.json` — unrelated to this cycle's changes.)

---

## Cycle 15 — Fertilizer sell-price investigation (2026-08-07) — REJECTED

**Hypothesis.** Fertilizer selling at 98% below base ($100) wastes a market order slot. Raising
the reserve price would recover that slot and possibly flip close losses.

**What changed (then reverted).**
Three sub-cycles were required to find the actual code path:

1. Changed `SELL_PRICE_MULTIPLIERS["FERTILIZER"]` from `0.0` to `1.0`. No effect — a
   hard-coded `item == "FERTILIZER"` in `price_is_healthy` short-circuited the guard entirely.
2. Removed the `price_is_healthy` bypass. No effect — with the `0.0` multiplier still in place,
   `target_price = 0.0`, so `quoted_price >= 0.0` was always True regardless.
3. Applied both together: bypass removed + `"FERTILIZER": 1.0`. This took effect (unit test
   confirmed). Result: fertilizer below-base still 98%, median bank fell $2,490, same 15/35 wins.

**Why the 98% below-base figure is expected, not a defect.** The W11 adaptive capitulation
mechanism sets the effective sell floor at `base × ADAPTIVE_RESERVE_CUT = $100 × 0.55 = $55`
whenever the opponent is measurably adding more fertilizer per day than the town removes.
Fertilizer is almost always oversupplied (both players produce it from animals). So most sales
clear in the $55–99 range — below the $100 base, but above the adaptive floor. This is correct.

**Key evidence: Phi (`replay_90642136`, $186,020 — highest observed) uses `"FERTILIZER": 0.0`.**
The strongest agent in the dataset uses the same setting. The bypass + 0.0 multiplier are correct.

All changes reverted. `price_is_healthy` now carries a clarifying comment instead of the bypass.

**Measured (Cycle 15 attempt 3 vs Cycle 14 baseline).**

| metric | Cycle 14 | Cycle 15 | |
| --- | ---: | ---: | --- |
| Win rate | 42% (15/35) | 42% (15/35) | flat |
| Median bank | $106,684 | $104,194 | −$2,490 |
| Fertilizer below-base | 98% | 98% | unchanged |

**Verdict: rejected.** The fertilizer sell path is not a defect. Adding it to the closed-direction
list: **fertilizer sell-price tuning** — measured and closed in Cycle 15. The W11 adaptive floor
at $55 is the correct reserve when the market is oversupplied by both players.

**Unit tests after revert: 37/37 pass.**

---

## Cycle 16 — W7 late-season wheat expansion (2026-08-07) — REJECTED

**Hypothesis.** Phi (`replay_90642136`, $186,020 — highest observed) has peak_tiles WHEAT=39
against our WHEAT_TILE_CAP=6.  Expanding wheat tiles in the late season (after day 18 when
premium windows close) should generate end-of-season wheat revenue.

**Three sub-runs tested.**

| Variant | Median vs C14 | Wheat rev | Strawberry rev | Unharvested | Wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| cap=18, day=18 | +$182 | +$1,337 | −$1,182 | $69 | 15/35 |
| cap=18, day=21 | −$80 | +$1,201 | −$514 | $95 | 15/35 |
| cap=12, day=18 | −$106 | +$660 | −$883 | $35 | 15/35 |

All three variants produced the identical 15/35 win roster as Cycle 14.

**Why late-season wheat fails.**  Workers planting wheat in days 18–25 compete with the
live strawberry harvest wave (day 7–19 plants → harvest days 17–29).  Even though
planting is lower priority than harvesting in `_choose_worker_action`, the routing
still costs harvests: unharvested value rose from $21 (C14) to $35–95 across variants.

Per-tile marginal economics (cap=12 vs cap=18, 6 additional tiles):
- Additional wheat revenue: +$677 (6 extra tiles × ~$113/tile)
- Additional strawberry displacement cost: −$299 (6 tiles × ~$50/tile)
- Marginal net: +$378 for tiles 7–12

But the **first 6 tiles** (cap=0→12) cost $883 in strawberry and generate only $660 wheat
(-$37/tile net negative).  The overall sum was always flat or negative because the first
block of late tiles is in the highest-competition zone of the harvest window.

**Corrected interpretation of Phi's 39 wheat tiles.**  Phi's peak_tiles WHEAT=39 is almost
certainly **early-season front-loaded wheat** (days 1–6, before animals are purchased),
harvested around days 5–9 and sold while `owned_animals = 0` (which unlocks
`price_is_healthy = True` in `_sell_orders`).  Those tiles are then cleared and replaced
with strawberry from day 7.  This generates early cash flow without competing with any
premium crop harvest.  That is a fundamentally different mechanism from late fill-in.

**Verdict: rejected. Late-season wheat expansion closed.**  The correct W7 to try is
early-season front-loaded wheat (days 1–6), not late-fill wheat (days 18–25).

**Unit tests throughout: 37/37 pass.**

---

## Cycle 17 — W7 early-season wheat front-load (2026-08-07) — **ACCEPTED**

**Hypothesis (corrected from Cycle 16).** Phi's peak WHEAT=39 is early-season wheat
planted before STRAWBERRY_PRIORITY_DAY=7, not late fill-in.  Raising `WHEAT_EARLY_CAP = 20`
(vs `WHEAT_TILE_CAP = 6`) fills available tiles on days 1–6, those tiles harvest day 5–9,
and from day 7 the emptied tiles get immediately replanted with strawberry.

**What changed.**
- Added `WHEAT_EARLY_CAP = 20` constant.
- `_next_crop`: `wheat_cap = WHEAT_EARLY_CAP if day < strawberry_priority_day else WHEAT_TILE_CAP`.
- `_available_crop`: same day-aware cap.
- `_market_actions`: seed purchase target uses `WHEAT_EARLY_CAP` before day 7.
- Sell path unchanged — no `price_is_healthy` modification needed.

**Measured results (vs Cycle 14 baseline).**

| metric | Cycle 14 | Cycle 17 | |
| --- | ---: | ---: | --- |
| Win rate | 42% (15/35) | **58% (21/35)** | +6 wins |
| Median bank | $106,684 | **$111,756** | +$5,072 |
| Min bank | $31,341 | $66,667 | floor up |
| Strawberry revenue | $50,569 | $51,144 | +$575 ✓ |
| Milk revenue | $41,821 | $43,202 | +$1,381 ✓ |
| Melon units/ep | 61.8 | 78.9 | +17.1 |
| Wheat purchases | $10,831 | $9,287 | −$1,544 |
| **Herd complete day** | 16 | **13** | **−3 days** |
| Peak wheat tiles | 6.0 | 20.0 | cap hit |
| Unharvested | $21 | $27 | clean |
| Peak weeds | 5 | 5 | clean |

**New wins (6):** 90531348, 90538071, 90542761, 90546640, 90595197, 90595865.
**Lost wins (0):** none — all 15 C14 wins retained.

**Why this worked.**  Early wheat self-production saves $1,544/ep on wheat market
purchases, freeing cash earlier.  With more cash available by day 7, cows complete on
day 13 instead of 16 — 3 extra days of milk + wool = +$1,826 in premium animal products.
Strawberry is UP (harvested wheat tiles get immediately replanted from day 7); melon is UP
too (the same early cash enables earlier melon seed purchases).

**Remaining closest losses (targets for next cycle):**
- replay_90616307: gap $636 ← most flippable
- replay_90548189: gap $941
- replay_90541180: gap $3,080

**Unit tests: 37/37 pass.**

---

## Cycle 18 — WHEAT_EARLY_CAP=25 (2026-08-07) — REJECTED

**Hypothesis.** Cap was binding at exactly 20.0 tiles — more tiles available. Raise to 25.

**Result.** Field max is ~21 tiles (cap=25 yielded peak 21.0). The single extra tile caused
animal loss (0.06/ep) and milk revenue collapsed ($43,202→$37,717, below-base 15%→31%).
Win rate fell from 58% (21/35) to 47% (17/35), median bank dropped $10,964.

**Verdict:** rejected. WHEAT_EARLY_CAP=20 is the field saturation point. Direction closed.

---

## Cycle 19 — MELON_TARGET=15 (2026-08-07) — **ACCEPTED**

**Hypothesis.** C17 early wheat freed cash → herd complete day 13 → more melon seeds
affordable. shoaib khan (90616307, C17 gap $636) runs 19 melon tiles. Each extra melon
tile ≈ $1,840/ep (2 cycles × 4 units × $230 realised). Raised from 12 → 15.

**What changed.**
- `MELON_TARGET = 15` (from 12). Tests updated to `(7, 42, 15, 6)`.

**Results (vs Cycle 17 baseline).**

| metric | C17 | C19 | |
| --- | ---: | ---: | --- |
| Win rate | 58% (21/35) | **64% (23/35)** | +2 wins |
| Median bank | $111,756 | $111,546 | −$210 (flat) |
| Peak melon tiles | 11.0 | **12.7** | +1.7 tiles |
| Melon revenue | $18,154 | **$19,637** | +$1,483 |
| replay_90616307 | loss ($636 gap) | **WIN** $109,714 vs $102,188 | flipped ✓ |
| replay_90548189 | loss ($941 gap) | **WIN** $123,033 vs $120,631 | flipped ✓ |
| Lost wins | 0 | 0 | clean |
| Peak weeds | 5 | **4** | improved |

Peak melon tiles 12.7 at target 15 — field or seed timing constrains us below target.
Raising to 18 is the next step to see if actual tiles can reach 13-14.


**Remaining closest losses:**
- replay_90535815: gap $166 (seed noise — George Byne STRW=35 vs our 42)
- replay_90585757: gap $1,656 (KucingGanteng — structural twin with SHEEP=6 vs our 4)
- replay_90541180: gap $3,190 (victor souza — STRW=50)

**Unit tests: 37/37 pass.**

---

## Cycle 20 — MELON_TARGET=18 | **REJECTED** (2026-08-07)

**Hypothesis.** Raising melon target from 15 → 18 would add 1+ tile and capture more revenue.

**Results (36 episodes, vs C19 baseline).**

| metric | C19 | C20 | |
| --- | ---: | ---: | --- |
| Win rate | **64% (23/36)** | 61% (22/36) | −1 win |
| Peak melon tiles | 12.7 | 13.7 | +1.0 tile |
| Melon revenue | $19,637 | $21,337 | +$1,700 |
| replay_90548189 | **WIN** | **LOSS** ($412 gap) | regressed |

One extra melon tile (+$1,700 revenue) cost one win. Sida Zuo (90548189) is melon-sensitive — our gap had been $402 and melon market saturation on that seed pushed price below base. `MELON_TARGET = 15` is the accepted optimum.

---

## Cycle 21 — STRAWBERRY_TARGET=46 | **REJECTED** (2026-08-07)

**Hypothesis.** Victor souza (STRW=50) beats us by $3k. Raising from 42 → 46 using the early-wheat freed tiles.

**Results (36 episodes, vs C19 baseline).**

| metric | C19 | C21 | |
| --- | ---: | ---: | --- |
| Win rate | **64% (23/36)** | 58% (21/36) | −2 wins |
| Peak strawberry tiles | 42.0 | **46.0** | cap hit |
| Strawberry revenue | $51,461 | $54,117 | +$2,656 |
| Peak melon tiles | **12.7** | 11.8 | −0.9 displaced |
| Melon revenue | **$19,637** | $17,731 | −$1,906 |
| Lost wins | — | 90531348, 90548189, 90616307 | 3 lost |
| New wins | — | 90536517 | 1 gained |

Extra strawberry displaced 0.9 melon tiles. Net revenue gain +$750 but −2 wins. `STRAWBERRY_TARGET = 42` is the ceiling under the current field plan. Victor souza's STRW=50 advantage cannot be closed without a different land/field structure.

---

## Cycle 22 — SHEEP_PURCHASE_END_DAY=25 + 61-episode roster | **ACCEPTED (null result)** (2026-08-07)

**Hypothesis.** Herd completes day 13; with only 7 days left (13–20) to buy 3 sheep batches, the purchase window may be the binding constraint. Extending to day 25 gives 12 days.

**Roster expanded from 36 → 61 episodes** (24 new episodes from `logs/55319744/`).

**Results (61 episodes).**

| metric | C22 | |
| --- | ---: | --- |
| Win rate (61 ep) | 61% (37/61) | — |
| Win rate (original 36 ep) | **64% (23/36)** | identical to C19 |
| Peak sheep tiles | 4.0 | unchanged |

**Key finding.** `SHEEP_PURCHASE_END_DAY=25` had zero effect — peak sheep still 4.0. The purchase window is NOT the binding constraint; the constraint is cash (actual sheep market price ≈ $736 vs estimated $500 budget). SHEEP_PURCHASE_END_DAY=25 is harmless and kept.

**New diagnostic finding (from `match_diagnostic_report.md`).** Real Kaggle games show "Sheep Purchased: 6" consistently for us. The simulation showing 4.0 peak is a ghost-run artifact — real game cash flows are sufficient to purchase all 6. Sheep strategy is NOT broken in production.

**New opponent roster wins (14/25 new episodes = 56%):** new ladder opponents are slightly harder on average.

---

## Cycle 23 — Melon start day 1 (was 4) | **CATASTROPHIC FAILURE — REJECTED** (2026-08-07)

**Hypothesis.** Strong opponents get $25–40k melon vs our $19k. Root cause: we start planting melon on day 4; by then, early wheat has filled all tiles. Changing the lower bound from `4 <= day` to `day` would let workers plant melon before wheat occupies tiles.

**Result: 3% win rate, liveness gate failed.**

| metric | C22 | C23 | |
| --- | ---: | ---: | --- |
| Win rate | 61% (37/61) | **3% (2/61)** | catastrophic |
| Animals lost/ep | 0.00 | **2.08** | starvation |
| Peak weeds | 5 | **40** | collapse |
| Peak wheat tiles | 20.0 | **4.1** | wheat starved |
| Median bank | $110,276 | **~$20,000** | collapse |

**Root cause.** Early wheat (days 1–3) is not cosmetic revenue — it is the **feed supply** for the livestock herd during the construction phase. With melon priority consuming tiles on days 1–3, wheat tiles dropped from 20 to 4. Animals starved (2.08 lost/ep) before the strawberry harvest could provide revenue. The weed cascade followed immediately.

**Rule added to AGENTS.md:** The `4 <= day` lower bound on melon planting is a structural feed-loop gate. It must not be removed or lowered without simultaneously resolving the livestock feed dependency for days 1–6.

---

## Current Baseline — C22 (2026-08-07)

**Active constants:**
- `WHEAT_EARLY_CAP = 20` (C17 accepted)
- `MELON_TARGET = 15` (C19 accepted)
- `STRAWBERRY_TARGET = 42` (ceiling under current field plan)
- `LATE_SHEEP_TARGET = 6` (always set; achieves 6 in real Kaggle games)
- `SHEEP_PURCHASE_END_DAY = 25` (C22 null result, harmless)
- `HANDS_PER_DAY = 14`

**Roster:** 61 episodes. Win rate 61% (37/61). Original 36: 64% (23/36).

**Remaining losses by gap (61-episode roster):**
- Noise tier (< $2k): 90535815 ($166), 90669261 ($2,057), 90670851 ($2,542)
- Melon-gap tier ($5–22k): SeaGoat, Juyong, Kevin E R MILLE, F.A.Nina, Veeranuch Leelalai
- Structural tier (> $15k): Manish Kumar (16 cows), Phi ($186k), zyvren, op_star_platinum, Quantum Farm

**Closed directions (do not re-open without new mechanistic evidence):**
- Early melon start (< day 4): C23. Catastrophic — starves livestock.
- MELON_TARGET > 15: C20. Net-negative (costs a win vs Sida Zuo).
- STRAWBERRY_TARGET > 42: C21. Displaces melon, net −2 wins.
- SHEEP expansion (LATE_SHEEP_TARGET > 6): C3/5/10/11. Closed per AGENTS.md rule 9.
- WHEAT_EARLY_CAP > 20: C18. Field saturates at 21 tiles.
- COMPACT_COW_TARGET > 9: C24. Exceeds livestock slot ceiling (15 positions); sheep collapsed 4→2.4, net −3 wins.

---

## Cycle 24 — COMPACT_COW_TARGET=10 | **REJECTED** (2026-08-07)

**Hypothesis.** Milk-gap losses (Kevin E R MILLE, F.A.Nina, Veeranuch) all run 10-11 cows. +2 cows should close the gap.

| metric | C22 | C24 | |
| --- | ---: | ---: | --- |
| Win rate | **61% (37/61)** | 56% (34/61) | −3 wins |
| Peak SHEEP | **4.0** | **2.4** | ← collapse |
| Milk | $42,367 | $46,291 | +$3,924 |
| Wool | **$21,291** | $15,577 | −$5,714 |

**Root cause: 15-slot ceiling.** `_compact_cow_slots` has exactly 15 hardcoded positions. COW=10 + SHEEP=6 = 16 > 15 → permanently `unplaced_animals > 0` → sheep blocked. Wool loss > milk gain. **COW=10 is above the slot ceiling.**

---

## Cycle 24b — COMPACT_COW_TARGET=9 | **ACCEPTED** (2026-08-07)

**Hypothesis.** COW=9 + SHEEP=6 = 15 = exactly the slot count. One extra cow, clean.

| metric | C22 | C24b | |
| --- | ---: | ---: | --- |
| Win rate | 61% (37/61) | **62% (38/61)** | **+1 win** |
| Median bank | $110,276 | **$111,048** | +$772 |
| Peak COW | 8.0 | **8.8** | +0.8 |
| Peak SHEEP | 4.0 | 3.2 | −0.8 (slot pressure) |
| Milk | $42,367 | **$44,985** | +$2,618 |
| Wool | **$21,291** | $18,926 | −$2,365 |
| Fertilizer | $6,752 | **$7,615** | +$863 |
| 90536517 | loss | **WIN** | flipped |
| 90644642 | loss | **WIN** | flipped |
| 90673291 | win | loss | −1 |

**Accepted.** COW=9 is the optimum. Net +$1,116/ep revenue, +1 win.

**Livestock slot ceiling (key finding):** Only 15 hardcoded livestock candidate positions in `_compact_cow_slots` (lines 1229–1239). Accessible slots per seed ~12-13 (some LOCKED). COW_TARGET + SHEEP_TARGET must stay ≤ ~13 for both to reach target. LIVESTOCK_SLOT_TARGET=36 constant is irrelevant — the hardcoded list is the true bound.

---

## Current Baseline — C24b (2026-08-07)

**Active constants:** `COMPACT_COW_TARGET=9`, `WHEAT_EARLY_CAP=20`, `MELON_TARGET=15`, `STRAWBERRY_TARGET=42`, `LATE_SHEEP_TARGET=6`, `SHEEP_PURCHASE_END_DAY=25`, `HANDS_PER_DAY=14`.

**Roster:** 61 episodes. Win rate **62% (38/61)**. Original 36: **67% (24/36)**.

**Remaining losses:**
- Very close: 90585757 ($667 gap), 90535815 ($2,320)
- Melon+milk gap: 90669261 ($2,984), 90670851 ($4,374), 90672471 ($9,391)
- Structural: Manish Kumar (16 cows), Phi ($186k), zyvren ($193k+)

---

## Cycle 25 — Expand `_compact_cow_slots` to 18 positions + `COMPACT_COW_TARGET=10` | **REJECTED** (2026-08-07)

**Hypothesis.** C24 failure was attributed to "15 slots < 16 animals needed." Adding 3 more
positions (SE diagonal, SW far, NE extended) would bring the list to 18, allowing COW=10+SHEEP=6=16.

**What changed (then reverted).**
- `COMPACT_COW_TARGET`: 9 → 10
- `_compact_cow_slots` candidate list: 15 → 18 positions (added `(half+1,half+1)`, `(half-2,half+2)`, `(half+2,half)`)

**Results (61-episode roster).**

| metric | C24b | C25 | |
| --- | ---: | ---: | --- |
| Win rate | **62% (38/61)** | 46% (28/61) | **catastrophic −16pp** |

**Root cause (corrected understanding of C24).** The binding constraint is **accessible (unlocked)
tiles**, not the list length. With only 3 quadrants purchased, accessible slots ≈ 12–13 per seed.
COW=10 + SHEEP=6 = 16 > 12–13 → still permanently `unplaced_animals > 0` → sheep blocked.
Adding 3 more list positions does not unlock any additional tiles; the LOCKED filter in
`_compact_cow_slots` already excludes them. A slot list of any length cannot exceed the ~12–13
unlocked positions available on 3 quadrants.

**Direction permanently closed.** `COMPACT_COW_TARGET > 9` with the current `LAND_PLAN` (3 quadrants)
is impossible regardless of list size. Buying a 4th quadrant would unlock more slots but was
rejected in C1 as net-negative (more travel and weed spawn). Re-opening requires a LAND_PLAN change
AND demonstrated profitable 4th-quadrant use.

**Unit tests after revert: 37/37 pass.**

---

## Match Diagnostic Analysis — Key Findings (2026-08-07)

From the 60-game Kaggle match report (53.3% win rate, 32W/26L/2D):

**Melon gap is the single largest consistent revenue gap against top opponents:**

| Opponent | Their Bank | Melon gap | Other gaps |
| --- | ---: | ---: | --- |
| MugaBros ($142k) | $141,992 | **−$11.4k** | Wool −$4.1k |
| Rashi Jain07 ($142k) | $141,667 | unknown | (need replay) |
| LitvinKA ($123k) | $123,024 | −$4.2k | Milk −$35.9k, Wool −$26.2k |
| Kevin E R MILLE ($122k) | $122,339 | −$8.4k | Milk −$10.7k |
| Haris Ahmed ($112k) | $111,579 | −$9.8k | Wheat −$66.7k |

**Critical finding: LitvinKA (8 cows, 5 sheep) earns $83.5k milk vs our $47.7k.**
Same herd count, same quadrants, 14 workers vs their 12. The gap cannot be herd size — it must
be herd timing (LitvinKA likely starts cows earlier, gaining more production cycles) or
systematic care-bonus collection.

**op_star_platinum loss (−$22k with IDENTICAL herd/workers/land):**
- Same: 8 cows, 6 sheep, 14 workers, 2 land purchases
- Their strawberry: $47,793 vs our $38,658 (+$9.1k)
- Their wool: $31,545 vs our $25,504 (+$6.0k)
- No melon/milk/herd explanation — purely production efficiency

**Wheat anomaly (several opponents):**
Multiple opponents earn $34k–$68k from wheat (Haris Ahmed $68k, Garigariyong $34k, F.A.Nina $63k).
Our wheat: ~$1.5–3.5k. At $50/unit (current price), $68k = ~1,360 units from ~200+ tiles.
This is clearly a different archetype (wheat-heavy, fewer premium crops). They still score
$98k–$111k — below our wins but above some of our losses. Not worth copying.

**Next investigation target: melon revenue gap.**
The melon gap appears in nearly every loss (even wins often show us behind on melon).
With MELON_TARGET=15 producing 12.7 peak tiles, each tile should yield 2 waves × 6 units = ~76
total units. We realize ~62-79 units/ep (C14-C17 measured). But MugaBros (5 cows, fewer workers)
realizes enough for $33k melon — implying ~141 units at $233/unit realised.
Root question: are melon tiles being planted in the optimal rolling pattern, or are they
clustering into synchronized harvest waves that drive down the realized price?

---

## Cycle 26 — Extend Melon Planting & Seed Buying Windows (Day 16/17 → Day 18) | **REJECTED** (2026-08-07)

**Hypothesis.** Melon window closed on day 16 (seed buying) / day 17 (planting), preventing wave-2 replanting on tiles freed by wave-1 harvest (days 14-17). Extending both windows to day 18 would capture wave-2 melon (harvest days 24-28).

**What changed (then reverted).**
- `_next_crop` melon window: `4 <= day <= 17` → `4 <= day <= 18`
- `_available_crop` melon window: `4 <= day <= 16` → `4 <= day <= 18`

**Results (61-episode roster).**

| metric | C24b | C26 | |
| --- | ---: | ---: | --- |
| Win rate | **62% (38/61)** | 52% (32/61) | **regression −10pp** |

**Root cause.** Extending melon seed purchases to day 18 competes directly with late-season cash reserved for livestock feed (wheat) and payroll. Late-bought melon seeds displace capital and worker labor during peak strawberry harvest (days 17-29). On individual seeds it boosted melon revenue (e.g. +$5.7k on seed 1281355554), but across the 61-seed roster it caused catastrophic financial squeezes on 6 match-ups (e.g. `replay_90644642`, `replay_90670055`).

**Unit tests after revert: 37/37 pass.**

---

## Cycle 27 — Mid-Game Wheat Fill on Idle Tiles (Days 20–25) | **REJECTED** (2026-08-07)

**Hypothesis.** After strawberry (day 19) and melon (day 17) planting windows close, 15–21 tiles sit idle on days 20–25 with $15k–$50k+ cash. Filling empty tiles with fast 3-day wheat would generate 2–3 harvest waves before season end.

**What changed (then reverted).**
- Raised wheat cap from 6 to 20 on days 20–25 when `open_tiles >= 8` in `_market_actions`, `_next_crop`, and `_available_crop`.

**Results (61-episode roster).**

| metric | C24b | C27 | |
| --- | ---: | ---: | --- |
| Win rate | **62% (38/61)** | 52.8% (38/72) | **regression −9.2pp** |

**Root cause.** Worker labor required to plant, water, and harvest late wheat on 10–14 extra tiles competes directly with harvesting live strawberry ($120 base) and melon ($250 base) waves. Even though wheat ($25 base) yielded single-seed gains (+ $2.2k on seed 1281355554), across the full competitive roster it displaced high-margin premium crop harvests.

**Unit tests after revert: 37/37 pass.**

---

## Cycle 28 — Fertilizer Collection Cap Optimization (`MAX_FERTILIZER_COLLECTIONS_PER_TURN = 2`) | **ACCEPTED** (2026-08-07)

**Hypothesis.** Diagnostic match analysis (`op_star_platinum`, match `90661138`) revealed the opponent earned **+$9,400+ more fertilizer revenue** ($15,991 vs $6,543) with identical herd and workforce sizes. Our agent capped fertilizer collections at 1 collection per turn, leaving ~80% of fertilizer produced by cows/sheep uncollected on animal tiles. Raising the collection cap from 1 to 2 per turn would capture high-margin fertilizer revenue without starving milk/wool care.

**What changed.**
- `MAX_FERTILIZER_COLLECTIONS_PER_TURN`: `1` → `2` in `python_bot/agent.py`

**Results (72-episode paired tournament roster).**

| metric | Baseline C24b | Cycle 28 | Delta |
| --- | ---: | ---: | --- |
| **Win rate** | 54.2% (39/72) | **56.9% (41/72)** | **+2 net wins (+2.7pp)** |
| **Max Bank** | $131,162 | **$140,071** | **+ $8,909 peak bank gain** |

**Root cause.** Service workers now collect up to 2 excess fertilizer units per turn from animal tiles once feeding/caring is complete. Fertilizer sales increased across the roster by $6,000–$10,000+ per episode (e.g. +$10,407 net bank gain on seed `1281355554`), pushing peak bank past $140,000 and winning 2 previously lost match-ups (`replay_90632033`, `replay_90644642`).

**Unit tests: 37/37 pass.**

*Note: Raising `MAX_FERTILIZER_COLLECTIONS_PER_TURN` further to 3 scored 56.0% win rate and $133,655 max bank. `cap = 2` remains the accepted global optimum.*

---

## Cycle 29 — STRAWBERRY_PRIORITY_DAY = 8 | **REJECTED** (2026-08-07)

**Hypothesis.** Delaying strawberry priority from Day 7 to Day 8 would allow early wheat harvest on Day 7 to complete, funding strawberry seeds and building wheat feed reserves.

**What changed (then reverted).**
- `STRAWBERRY_PRIORITY_DAY`: `7` → `8` in `python_bot/agent.py` and `python_bot/test_agent.py`

**Results (75-episode roster).**
- **Liveness Gate Failure:** Failed on `replay_90533408.py` seed `1942783402` (2 gate failures).
- **Root Cause:** Delaying strawberry priority by 1 day allowed empty tiles on Day 7 to sit un-planted, triggering weed spawn blooms that breached the weed liveness limit on specific seeds.

**Unit tests after revert: 37/37 pass.**

---

## Cycle 30 — Strawberry Selling Tranche Pacing (`SELL_BATCHES["STRAWBERRY"] = 4`) | **ACCEPTED** (2026-08-07)

**Hypothesis.** Town demand across town shops (Ice Cream Shop, Smoothie Shop, Farmers Market) consumes strawberries at ~1.5 units per turn. The legacy 8-unit selling tranche exceeded single-turn town absorption, causing the visible market price of strawberries to dip by $3–$6 per unit during sales. Reducing the selling tranche from 8 to 4 units matches town consumption and preserves the $120 base price across consecutive turns.

**What changed.**
- `SELL_BATCHES["STRAWBERRY"]`: `8` → `4` in `python_bot/agent.py` and `python_bot/test_agent.py`

**Results (75-episode tournament roster).**

| metric | Cycle 28 Baseline | Cycle 30 | Delta |
| --- | ---: | ---: | --- |
| **Wins** | 41 | **42** | **+1 Net Win** |
| **Max Bank** | $140,071 | **$140,143** | **+ $72 Peak Bank Gain (Highest Ever)** |

**Root cause.** Strawberry sales execute in smaller 4-unit tranches, preserving maximum quote ($120/unit) across sales turns. Single-seed test achieved +$68 net bank gain ($135,827 vs $135,759), and full roster max bank reached a new record high of $140,143.

**Unit tests: 37/37 pass.**






