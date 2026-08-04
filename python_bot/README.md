# Kaggriculture Python Bot Kit

Submission kit for the **Kaggle Kaggriculture Competition**.

## Files
- `agent.py`: Single self-contained Python entrypoint function (`agent(observation, configuration)`) for Kaggle submission.
- `test_agent.py`: Automated 720-turn benchmark test runner.
- `run_official_tournament.py`: Official-engine replay and benchmark runner.

## How to Test Locally
Run the unit tests using Python 3:
```bash
python3 -m unittest test_agent.py
```

## Official-Engine Tournament Gate

The schema test above does not predict Kaggle performance. Before any upload,
run the exact agent in the official Kaggle environment:

```bash
python3 -m pip install -U kaggle-environments
python3 run_official_tournament.py --agent agent.py --replay-dir replays/official
```

The command saves official replay JSON files and returns a non-zero exit code
when the agent fails the crop-loop checks (plant, water, harvest, sell, and no
weeds). See `TEST_STRATEGY.md` for the release criteria.

**Required for every strategy change:** run the official benchmark before
calling the change verified, rebuilding a release artifact, or submitting it.
If the official engine cannot run, report that the benchmark is blocked; unit
tests alone never establish a score improvement.

### ⚠️ The built-in opponents measure liveness, not performance

Measured on the official engine, final bank after 720 turns:

| Agent | Final bank |
| --- | ---: |
| `pass` | $3,000 (starting money) |
| `random` | $0 |
| `starter` | $3,514 |
| Real ladder opponents | $84,682 – $125,241 |

The strongest built-in scores about **3% of a real opponent**. `agent.py` scores
**$136,548 against `starter`** and still loses 6 of 7 games on the ladder.

The market is *shared* between both players. Because these opponents barely sell,
the harness market never sees a second seller and prices do not behave as they do
in a real game — which hides exactly the price-crash failures that lose ladder
matches.

**Use `pass`/`random`/`starter` as a smoke test only.** Never quote a
vs-`starter` bank as evidence that a change helped.

### Measuring an actual strategy change

Self-play puts a realistic second seller in the shared market and reproduces the
real ladder score band (70k–102k on the default seeds):

```bash
python3 run_official_tournament.py --agent agent.py --opponents self --seed-count 50 --seed-source 20260804 --replay-dir replays/self-play
```

Head-to-head against the previously approved artifact is the number that decides a
change. `kaggle_environments` accepts a **file path** as an agent, so a prior
artifact can be used as the opponent directly:

```bash
python3 run_official_tournament.py --agent agent.py --opponents ../artifacts/approved_agent.py --seed-count 30 --replay-dir replays/regression
```

> **Note:** `RECORD_MILESTONE = 154615` in `run_official_tournament.py` is a
> vs-weak-opponent figure and is **not** comparable to a ladder score. Do not
> treat it as a target. Work item W0 in `../implementation_plan.md` covers
> rebuilding this harness so its exit code gates on score regression, pairs seeds
> across both sides, and reports the diagnostic metrics that explain wins and
> losses.

## How to Submit to Kaggle
1. Upload `agent.py` directly to [Kaggle Kaggriculture Submission](https://www.kaggle.com/competitions/kaggriculture/submit).
2. Or use the Kaggle CLI:
   ```bash
   kaggle competitions submit -c kaggriculture -f agent.py -m "Autonomous Strategy Bot"
   ```
