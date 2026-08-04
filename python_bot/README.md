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

## How to Submit to Kaggle
1. Upload `agent.py` directly to [Kaggle Kaggriculture Submission](https://www.kaggle.com/competitions/kaggriculture/submit).
2. Or use the Kaggle CLI:
   ```bash
   kaggle competitions submit -c kaggriculture -f agent.py -m "Autonomous Strategy Bot"
   ```
