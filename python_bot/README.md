# Kaggriculture Python Bot Kit

Submission kit for the **Kaggle Kaggriculture Competition**.

## Files
- `agent.py`: Single self-contained Python entrypoint function (`agent(observation, configuration)`) for Kaggle submission.
- `agent_allocator.py`: Experimental marginal-revenue allocator. **Rejected** (23% head-to-head); kept as a reference, not shipped.
- `test_agent.py` / `test_agent_allocator.py`: Schema and engine-model unit tests.
- `run_official_tournament.py`: Official-engine benchmark runner and release gate.
- `measure_market_ceiling.py`: Town-demand and market-ceiling measurement.

## How to Submit
`agent.py` is stdlib-only and self-contained, so it is uploaded as a single file — renamed
to `main.py`, which is the entry-point name Kaggle requires:

```bash
cp agent.py main.py
python3 -c "from main import agent; assert callable(agent)"
kaggle competitions submit kaggriculture -f main.py -m "v1"
```

## How to Test Locally
Run the unit tests from the repository root:
```bash
python3 -m unittest python_bot.test_agent python_bot.test_agent_allocator python_bot.test_replay_opponents
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

### Replay-derived opponent roster

The default tournament uses one opponent for every full Kaggle replay in `logs/`.
Each replay ghost issues the real opponent's submitted actions on the original
competition seed and original seat. This preserves genuine crop, livestock,
expansion and market decisions, including opponents from games we won and lost.

```bash
python3 build_replay_opponents.py
python3 run_official_tournament.py --agent agent.py --report ../replays/replay-ghost-roster-report.json
```

The builder also creates `profile_<episode>.py` cross-seed approximations. These
are useful for fuzzing unfamiliar seeds, but the exact replay ghosts are the
primary fidelity test. Add new full replay JSON files to `logs/` and rerun the
builder to extend both sets.

The current 25-opponent exact roster is deliberately difficult: `agent.py` wins
15/25 source matches (60%). Opponent
final banks remain in the real-log range, so failures are now visible instead of
being hidden by non-competitive fixtures.

By default each tournament removes old raw replay directories under the
repository's `replays/` directory. Compact JSON summary reports are always
retained because they preserve benchmark history cheaply. Pass
`--keep-old-replays` when an experiment's full state/action trace is needed for
diagnosis.

### Measuring an actual strategy change

The replay roster is the primary competitive measurement. The candidate is
reported separately against every source opponent and must also clear the
aggregate win-rate gate.

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

Previous-artifact matches are paired across both seats. Replay ghosts remain on
their source seat because their recorded worker path is seed- and seat-specific.

## How to Submit to Kaggle
1. Upload `agent.py` directly to [Kaggle Kaggriculture Submission](https://www.kaggle.com/competitions/kaggriculture/submit).
2. Or use the Kaggle CLI:
   ```bash
   kaggle competitions submit -c kaggriculture -f agent.py -m "Autonomous Strategy Bot"
   ```
