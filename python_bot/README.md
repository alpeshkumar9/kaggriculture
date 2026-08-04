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
run the exact agent against the built-in opponents in the official Kaggle
environment:

```bash
python3 -m pip install -U kaggle-environments
python3 run_official_tournament.py --agent agent.py --replay-dir replays/official
```

The command saves official replay JSON files and returns a non-zero exit code
when the agent fails the crop-loop checks (plant, water, harvest, sell, and no
weeds). See `TEST_STRATEGY.md` for the release criteria.

**Required for every strategy change:** run the official benchmark before
calling the change verified, rebuilding a release artifact, or submitting it.
Benchmark candidate versus `pass`, `random`, `starter`, and the prior approved
artifact. If the official engine cannot run, report that the benchmark is
blocked; unit tests alone never establish a score improvement.

To measure a candidate against the $154,615 record on fresh scenarios, run a
reproducible batch of self-play episodes:

```bash
python3 run_official_tournament.py --agent agent.py --opponents self --seed-count 50 --seed-source 20260804 --replay-dir replays/self-play
```

## How to Submit to Kaggle
1. Upload `agent.py` directly to [Kaggle Kaggriculture Submission](https://www.kaggle.com/competitions/kaggriculture/submit).
2. Or use the Kaggle CLI:
   ```bash
   kaggle competitions submit -c kaggriculture -f agent.py -m "Autonomous Strategy Bot"
   ```
