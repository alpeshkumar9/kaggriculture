# Kaggriculture Python Bot Kit

Submission kit for the **Kaggle Kaggriculture Competition**.

## Files
- `agent.py`: Single self-contained Python entrypoint function (`agent(observation, configuration)`) for Kaggle submission.
- `strategy_rules.py`: Modular heuristic & dynamic pricing rules.
- `test_agent.py`: Automated 720-turn benchmark test runner.

## How to Test Locally
Run the test runner using Python 3:
```bash
python3 test_agent.py
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

## How to Submit to Kaggle
1. Upload `agent.py` directly to [Kaggle Kaggriculture Submission](https://www.kaggle.com/competitions/kaggriculture/submit).
2. Or use the Kaggle CLI:
   ```bash
   kaggle competitions submit -c kaggriculture -f agent.py -m "Autonomous Strategy Bot"
   ```
