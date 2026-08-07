#!/usr/bin/env python3
"""Automated script to fetch new Kaggle replays, deduplicate logs, analyze match results,

and rebuild the local tournament opponent roster.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from collections import Counter, defaultdict

# Import or reuse requests
try:
    import requests
except ImportError:
    print("Error: 'requests' package not installed. Run 'pip install requests' in your environment.")
    sys.exit(1)

KNOWN_PLAYER_NAMES = {"Alpesh Kumar"}
BASE_PRICES = {
    "WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120,
    "MELON": 250, "EGG": 50, "MILK": 160, "WOOL": 200,
    "FERTILIZER": 100,
}

def load_kaggle_credentials():
    """Load username and key from ~/.kaggle/kaggle.json or environment variables."""
    creds_path = Path.home() / ".kaggle" / "kaggle.json"
    if creds_path.exists():
        try:
            with open(creds_path, 'r', encoding='utf-8') as f:
                creds = json.load(f)
                username = creds.get("username")
                key = creds.get("key")
                if username and key:
                    return username, key
        except Exception as e:
            print(f"Warning: Failed to parse {creds_path}: {e}")
            
    username = os.environ.get("KAGGLE_USERNAME")
    key = os.environ.get("KAGGLE_KEY")
    if username and key:
        return username, key
        
    return None, None

def fetch_submissions(username, key):
    """Retrieve submissions for the kaggriculture competition."""
    url = "https://www.kaggle.com/api/v1/competitions/submissions/list/kaggriculture"
    print(f"Fetching submissions from Kaggle API...")
    response = requests.get(url, auth=(username, key))
    if response.status_code != 200:
        print(f"Error fetching submissions: HTTP {response.status_code}")
        print(response.text)
        return []
    return response.json()

def fetch_episodes_for_submission(username, key, submission_id):
    """Fetch episode list for a specific submission ID using the internal API."""
    url = "https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes"
    payload = {"submissionId": int(submission_id)}
    print(f"Fetching episodes list for submission {submission_id}...")
    response = requests.post(url, auth=(username, key), json=payload, headers={"Content-Type": "application/json"})
    if response.status_code != 200:
        print(f"Error fetching episodes: HTTP {response.status_code}")
        print(response.text)
        return []
    data = response.json()
    return data.get("episodes", [])

def download_replay(username, key, episode_id, output_path):
    """Download replay file for a specific episode ID."""
    url = f"https://www.kaggle.com/api/v1/competitions/episodes/{episode_id}/replay"
    response = requests.get(url, auth=(username, key))
    if response.status_code != 200:
        print(f"Error downloading episode {episode_id}: HTTP {response.status_code}")
        return False
    output_path.write_bytes(response.content)
    return True

def analyze_replay(log_path):
    """Analyze a single replay file to understand win/loss reasons."""
    try:
        replay = json.loads(log_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error reading {log_path}: {e}")
        return None

    agents = replay.get("info", {}).get("Agents", [])
    names = [agent.get("Name", "unknown") for agent in agents]
    
    # Identify our seat vs opponent seat
    our_seat = None
    opponent_seat = None
    
    for idx, name in enumerate(names):
        if name in KNOWN_PLAYER_NAMES:
            our_seat = idx
        else:
            opponent_seat = idx
            
    if our_seat is None:
        # Default fallback: assume seat 0 is ours if we can't find Alpesh Kumar
        our_seat = 0
        opponent_seat = 1 if len(names) > 1 else None

    # Get final rewards (bank/score)
    steps = replay.get("steps", [])
    if not steps:
        return None
        
    last_step = steps[-1]
    our_score = last_step[our_seat].get("reward", 0) if our_seat < len(last_step) else 0
    opponent_score = last_step[opponent_seat].get("reward", 0) if (opponent_seat is not None and opponent_seat < len(last_step)) else 0
    
    outcome = "DRAW"
    if opponent_seat is not None:
        if our_score > opponent_score:
            outcome = "WIN"
        elif our_score < opponent_score:
            outcome = "LOSS"

    # Analyze sales, purchases, and other metrics
    metrics = {
        "our": {"sales": Counter(), "purchases": Counter(), "hands": 0, "cows": 0, "sheep": 0, "land": 0, "max_weeds": 0},
        "opp": {"sales": Counter(), "purchases": Counter(), "hands": 0, "cows": 0, "sheep": 0, "land": 0, "max_weeds": 0}
    }

    # Helper function to process seat actions/states
    def process_step(step_data, seat_key):
        observation = step_data.get("observation", {})
        action = step_data.get("action", {}) or {}
        
        # Prices
        prices = (observation.get("market") or {}).get("prices", {})
        
        # Track active hands and weeds
        farms = observation.get("farms") or []
        if our_seat < len(farms):
            farm = farms[our_seat if seat_key == "our" else opponent_seat]
            metrics[seat_key]["hands"] = max(metrics[seat_key]["hands"], len(farm.get("hands", [])))
            
            # Count weeds on tiles
            weeds_count = 0
            for row in farm.get("tiles", []):
                for tile in row:
                    if isinstance(tile, dict) and tile.get("weed"):
                        weeds_count += 1
            metrics[seat_key]["max_weeds"] = max(metrics[seat_key]["max_weeds"], weeds_count)

        # Track purchases & sales
        for order in action.get("market", []):
            if not order:
                continue
            op = order[0]
            if op == "BUY_LAND":
                metrics[seat_key]["land"] += 1
            elif op == "BUY_ANIMAL" and len(order) >= 2:
                animal = order[1]
                if animal == "COW":
                    metrics[seat_key]["cows"] += int(order[2]) if len(order) >= 3 else 1
                elif animal == "SHEEP":
                    metrics[seat_key]["sheep"] += int(order[2]) if len(order) >= 3 else 1
            elif op == "SELL" and len(order) >= 3:
                item, qty = order[1], int(order[2])
                price = prices.get(item, BASE_PRICES.get(item, 0))
                metrics[seat_key]["sales"][item] += qty * price
            elif op.startswith("BUY_") and len(order) >= 3:
                item, qty = order[1], int(order[2])
                # Estimate purchase cost
                price = prices.get(item, BASE_PRICES.get(item, 0))
                metrics[seat_key]["purchases"][item] += qty * price

    for step in steps:
        if our_seat < len(step):
            process_step(step[our_seat], "our")
        if opponent_seat is not None and opponent_seat < len(step):
            process_step(step[opponent_seat], "opp")

    return {
        "episode_id": log_path.stem,
        "our_name": names[our_seat] if our_seat < len(names) else "Us",
        "opp_name": names[opponent_seat] if (opponent_seat is not None and opponent_seat < len(names)) else "Opponent",
        "our_score": our_score,
        "opp_score": opponent_score,
        "outcome": outcome,
        "metrics": metrics
    }

def print_diagnostic_report(analyses):
    """Print a clean diagnostic markdown report summarizing the new replays."""
    if not analyses:
        print("No new analyses to report.")
        return
        
    print("\n" + "="*50)
    print(" KAGGRICULTURE MATCH DIAGNOSTIC REPORT")
    print("="*50)
    
    for analysis in analyses:
        print(f"\n### Match {analysis['episode_id']} | Outcome: **{analysis['outcome']}**")
        print(f"- **{analysis['our_name']}** (Us): ${analysis['our_score']:,.2f}")
        print(f"- **{analysis['opp_name']}** (Opponent): ${analysis['opp_score']:,.2f}")
        
        our_met = analysis['metrics']['our']
        opp_met = analysis['metrics']['opp']
        
        print("\n| Metric | Us | Opponent | Difference |")
        print("| :--- | :--- | :--- | :--- |")
        print(f"| Final Bank | ${analysis['our_score']:,.2f} | ${analysis['opp_score']:,.2f} | ${analysis['our_score'] - analysis['opp_score']:,.2f} |")
        print(f"| Max Workers | {our_met['hands']} | {opp_met['hands']} | {our_met['hands'] - opp_met['hands']} |")
        print(f"| Land Purchases | {our_met['land']} | {opp_met['land']} | {our_met['land'] - opp_met['land']} |")
        print(f"| Cows Purchased | {our_met['cows']} | {opp_met['cows']} | {our_met['cows'] - opp_met['cows']} |")
        print(f"| Sheep Purchased | {our_met['sheep']} | {opp_met['sheep']} | {our_met['sheep'] - opp_met['sheep']} |")
        print(f"| Max Weeds Count | {our_met['max_weeds']} | {opp_met['max_weeds']} | {our_met['max_weeds'] - opp_met['max_weeds']} |")
        
        # Product sales revenue
        all_products = set(our_met['sales'].keys()) | set(opp_met['sales'].keys())
        for prod in sorted(all_products):
            our_val = our_met['sales'].get(prod, 0)
            opp_val = opp_met['sales'].get(prod, 0)
            print(f"| Sales: {prod} | ${our_val:,.2f} | ${opp_val:,.2f} | ${our_val - opp_val:,.2f} |")

        # Explain why we lost if it was a loss
        if analysis['outcome'] == "LOSS":
            reasons = []
            if opp_met['hands'] > our_met['hands']:
                reasons.append("Opponent hired more workers, indicating we might be under-hiring or expanding too slowly.")
            if opp_met['cows'] > our_met['cows']:
                reasons.append(f"Opponent invested more in Cows ({opp_met['cows']} vs {our_met['cows']}), yielding higher Milk revenues.")
            if opp_met['sheep'] > our_met['sheep']:
                reasons.append(f"Opponent bought more Sheep ({opp_met['sheep']} vs {our_met['sheep']}), yielding higher Wool revenues.")
            
            # Compare premium sales
            for premium in ["MELON", "STRAWBERRY", "MILK", "WOOL"]:
                our_val = our_met['sales'].get(premium, 0)
                opp_val = opp_met['sales'].get(premium, 0)
                if opp_val > our_val + 5000:
                    reasons.append(f"Opponent outperformed on {premium} sales by ${opp_val - our_val:,.2f}.")
            
            if our_met['max_weeds'] > 12:
                reasons.append(f"We hit a peak of {our_met['max_weeds']} weeds, suggesting our care loop was overwhelmed.")
                
            if not reasons:
                reasons.append("Difference in general pacing or price optimization (selling at better market peaks).")
                
            print("\n**Key Loss Factors Identified:**")
            for r in reasons:
                print(f"- {r}")

def main():
    parser = argparse.ArgumentParser(description="Fetch and analyze new Kaggle replays.")
    parser.add_argument("--submission-id", type=int, help="Fetch episodes specifically for this submission ID.")
    parser.add_argument("--max-episodes", type=int, default=5, help="Maximum number of new episodes to download. Set to -1 for unlimited.")
    parser.add_argument("--dry-run", action="store_true", help="Only run analysis on existing logs, don't download anything.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    if args.dry_run:
        print("Dry run: Analyzing existing logs in logs/...")
        analyses = []
        for file in sorted(logs_dir.glob("**/*.json"), key=os.path.getmtime, reverse=True)[:args.max_episodes]:
            analysis = analyze_replay(file)
            if analysis:
                analyses.append(analysis)
        print_diagnostic_report(analyses)
        return

    # Check credentials
    username, key = load_kaggle_credentials()
    if not username or not key:
        print("Error: Could not load Kaggle credentials.")
        print("Please ensure your kaggle.json is placed in ~/.kaggle/kaggle.json or set KAGGLE_USERNAME and KAGGLE_KEY.")
        sys.exit(1)

    submission_ids = []
    config_path = project_root / "python_bot" / "config_submissions.json"
    if args.submission_id:
        submission_ids = [args.submission_id]
    elif config_path.exists():
        try:
            config_data = json.loads(config_path.read_text(encoding="utf-8"))
            submission_ids = config_data.get("submission_ids", [])
            if submission_ids:
                print(f"Loaded submission IDs from config: {submission_ids}")
        except Exception as e:
            print(f"Warning: Failed to load config_submissions.json: {e}")
            
    if not submission_ids:
        # Fetch submissions to find the latest
        subs = fetch_submissions(username, key)
        if not subs:
            print("No submissions found.")
            sys.exit(1)
        
        # Pick the latest submission
        latest_sub = subs[0]
        sub_id = latest_sub.get("ref")
        desc = latest_sub.get("description", "No description")
        date = latest_sub.get("date", "Unknown date")
        print(f"Latest submission found: ID {sub_id} ({desc}) submitted on {date}")
        submission_ids = [sub_id]

    downloaded_episodes = []
    analyses = []

    for sub_id in submission_ids:
        episodes = fetch_episodes_for_submission(username, key, sub_id)
        print(f"Found {len(episodes)} episodes total for submission {sub_id}")
        
        new_episodes = []
        for ep in episodes:
            ep_id = ep.get("id")
            # Skip if we already have it anywhere in logs/
            existing_files = list(logs_dir.glob(f"**/{ep_id}.json"))
            if not existing_files:
                new_episodes.append(ep_id)
                
        print(f"{len(new_episodes)} of these are new (not present in logs/).")
        
        # Limit the number of episodes we fetch to prevent rate limits
        to_download = new_episodes if args.max_episodes < 0 else new_episodes[:args.max_episodes]
        if to_download:
            print(f"Downloading {len(to_download)} new episode(s)...")
            sub_dir = logs_dir / str(sub_id)
            sub_dir.mkdir(exist_ok=True)
            for ep_id in to_download:
                dest = sub_dir / f"{ep_id}.json"
                success = download_replay(username, key, ep_id, dest)
                if success:
                    print(f"Downloaded episode {ep_id} to logs/{sub_id}/")
                    downloaded_episodes.append(dest)
                    # Run diagnostic analysis
                    analysis = analyze_replay(dest)
                    if analysis:
                        analyses.append(analysis)
        else:
            print("No new episodes to download.")

    if analyses:
        print_diagnostic_report(analyses)
        
        # Trigger rebuild of replay opponents
        print("\nRebuilding replay opponents roster...")
        build_script = project_root / "python_bot" / "build_replay_opponents.py"
        if build_script.exists():
            res = subprocess.run([sys.executable, str(build_script)], capture_output=True, text=True)
            if res.returncode == 0:
                print("Successfully rebuilt replay opponents roster!")
            else:
                print("Error rebuilding replay opponents:")
                print(res.stderr)
        else:
            print("Warning: build_replay_opponents.py not found.")
    else:
        print("No new analysis produced.")

if __name__ == "__main__":
    main()
