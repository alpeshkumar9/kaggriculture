#!/usr/bin/env python3
"""Automated script to fetch new Kaggle replays, deduplicate logs, analyze match results,

and rebuild the local tournament opponent roster.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict

try:
    import requests
except ImportError:
    print("Error: 'requests' package not installed. Run 'pip install requests' in your environment.")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_replay_opponents import BASE_PRICES, KNOWN_PLAYER_NAMES, _opponent_seat, ensure_opponents_synced


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
    steps = replay.get("steps", [])
    if not steps or len(names) < 2:
        return None

    # Reuse the same seat-identification logic build_replay_opponents.py uses to
    # generate benchmark opponents, so "who is the opponent" can never drift
    # between the diagnostic report and the roster it feeds.
    opponent_seat, _selection = _opponent_seat(replay)
    our_seat = 1 - opponent_seat

    last_step = steps[-1]
    our_score = last_step[our_seat].get("reward", 0) if our_seat < len(last_step) else 0
    opponent_score = last_step[opponent_seat].get("reward", 0) if opponent_seat < len(last_step) else 0

    outcome = "DRAW"
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
    def process_step(step_data, seat_key, seat):
        observation = step_data.get("observation", {})
        action = step_data.get("action", {}) or {}

        # Prices
        prices = (observation.get("market") or {}).get("prices", {})

        # Track active hands and weeds
        farms = observation.get("farms") or []
        if seat < len(farms):
            farm = farms[seat]
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
            process_step(step[our_seat], "our", our_seat)
        if opponent_seat < len(step):
            process_step(step[opponent_seat], "opp", opponent_seat)

    return {
        "episode_id": log_path.stem,
        "our_name": names[our_seat] if our_seat < len(names) else "Us",
        "opp_name": names[opponent_seat] if opponent_seat < len(names) else "Opponent",
        "our_score": our_score,
        "opp_score": opponent_score,
        "outcome": outcome,
        "metrics": metrics
    }

def print_diagnostic_report(analyses):
    """Print and save a clean diagnostic markdown report summarizing the replays."""
    if not analyses:
        print("No new analyses to report.")
        return

    report = []
    report.append("# Kaggle Match Diagnostic Report\n")

    # Calculate overall leaderboard and stats
    opp_stats = defaultdict(lambda: {"max_score": 0.0, "scores": [], "opp_wins": 0, "our_wins": 0, "draws": 0})
    total_wins = 0
    total_losses = 0
    total_draws = 0

    for analysis in analyses:
        opp_name = analysis['opp_name']
        opp_score = float(analysis['opp_score'])
        our_score = float(analysis['our_score'])
        outcome = analysis['outcome']

        st = opp_stats[opp_name]
        st['scores'].append(opp_score)
        st['max_score'] = max(st['max_score'], opp_score)

        if outcome == "LOSS":
            st['opp_wins'] += 1
            total_losses += 1
        elif outcome == "WIN":
            st['our_wins'] += 1
            total_wins += 1
        else:
            st['draws'] += 1
            total_draws += 1

    total_matches = len(analyses)
    win_rate = (total_wins / total_matches * 100) if total_matches > 0 else 0

    report.append("## Overall Dataset Summary")
    report.append(f"- **Total Analyzed Matches**: {total_matches}")
    report.append(f"- **Record**: {total_wins} Wins / {total_losses} Losses / {total_draws} Draws ({win_rate:.1f}% Win Rate)\n")

    report.append("## Top Opponents Leaderboard (Ranked by Max Bank Achieved)")
    report.append("| Opponent Name | Max Bank | Avg Bank | Matches | Opponent Wins | Our Wins |")
    report.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

    ranked_opps = sorted(opp_stats.items(), key=lambda x: x[1]['max_score'], reverse=True)
    for name, st in ranked_opps:
        avg_score = sum(st['scores']) / len(st['scores'])
        report.append(f"| **{name}** | ${st['max_score']:,.2f} | ${avg_score:,.2f} | {len(st['scores'])} | {st['opp_wins']} | {st['our_wins']} |")

    report.append("\n" + "---" + "\n")
    report.append("## Detailed Match Diagnostics\n")

    for analysis in analyses:
        report.append(f"### Match {analysis['episode_id']} | Outcome: **{analysis['outcome']}**")
        report.append(f"- **{analysis['our_name']}** (Us): ${analysis['our_score']:,.2f}")
        report.append(f"- **{analysis['opp_name']}** (Opponent): ${analysis['opp_score']:,.2f}\n")

        our_met = analysis['metrics']['our']
        opp_met = analysis['metrics']['opp']

        report.append("| Metric | Us | Opponent | Difference |")
        report.append("| :--- | :--- | :--- | :--- |")
        report.append(f"| Final Bank | ${analysis['our_score']:,.2f} | ${analysis['opp_score']:,.2f} | ${analysis['our_score'] - analysis['opp_score']:,.2f} |")
        report.append(f"| Max Workers | {our_met['hands']} | {opp_met['hands']} | {our_met['hands'] - opp_met['hands']} |")
        report.append(f"| Land Purchases | {our_met['land']} | {opp_met['land']} | {our_met['land'] - opp_met['land']} |")
        report.append(f"| Cows Purchased | {our_met['cows']} | {opp_met['cows']} | {our_met['cows'] - opp_met['cows']} |")
        report.append(f"| Sheep Purchased | {our_met['sheep']} | {opp_met['sheep']} | {our_met['sheep'] - opp_met['sheep']} |")
        report.append(f"| Max Weeds Count | {our_met['max_weeds']} | {opp_met['max_weeds']} | {our_met['max_weeds'] - opp_met['max_weeds']} |")

        # Product sales revenue
        all_products = set(our_met['sales'].keys()) | set(opp_met['sales'].keys())
        for prod in sorted(all_products):
            our_val = our_met['sales'].get(prod, 0)
            opp_val = opp_met['sales'].get(prod, 0)
            report.append(f"| Sales: {prod} | ${our_val:,.2f} | ${opp_val:,.2f} | ${our_val - opp_val:,.2f} |")

        # Explain why we won/lost
        reasons = []
        if analysis['outcome'] == "LOSS":
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

            report.append("\n**Key Loss Factors Identified:**")
            for r in reasons:
                report.append(f"- {r}")
        elif analysis['outcome'] == "WIN":
            if our_met['hands'] > opp_met['hands']:
                reasons.append(f"We hired more workers ({our_met['hands']} vs {opp_met['hands']}), giving us labor superiority.")
            if our_met['cows'] > opp_met['cows']:
                reasons.append(f"We invested more in Cows ({our_met['cows']} vs {opp_met['cows']}), yielding higher Milk revenues.")
            if our_met['sheep'] > opp_met['sheep']:
                reasons.append(f"We bought more Sheep ({our_met['sheep']} vs {opp_met['sheep']}), yielding higher Wool revenues.")

            # Compare premium sales
            for premium in ["MELON", "STRAWBERRY", "MILK", "WOOL"]:
                our_val = our_met['sales'].get(premium, 0)
                opp_val = opp_met['sales'].get(premium, 0)
                if our_val > opp_val + 5000:
                    reasons.append(f"We outperformed on {premium} sales by ${our_val - opp_val:,.2f}.")

            if opp_met['max_weeds'] > 12:
                reasons.append(f"Opponent hit a peak of {opp_met['max_weeds']} weeds, suggesting their care loop was overwhelmed.")

            if not reasons:
                reasons.append("Superior general pacing or price optimization (selling at better market peaks).")

            report.append("\n**Key Win Factors Identified:**")
            for r in reasons:
                report.append(f"- {r}")

        report.append("\n" + "---" + "\n")

    full_report = "\n".join(report)
    print(full_report)

    # Save report
    project_root = Path(__file__).resolve().parents[1]
    report_file = project_root / "match_diagnostic_report.md"
    try:
        report_file.write_text(full_report, encoding="utf-8")
        print(f"Saved diagnostic report to: {report_file}")
    except Exception as e:
        print(f"Warning: Failed to save diagnostic report to file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Fetch and analyze new Kaggle replays.")
    parser.add_argument("--submission-id", type=int, help="Fetch episodes specifically for this submission ID.")
    parser.add_argument("--max-episodes", type=int, default=5, help="Maximum number of new episodes to download. Set to -1 for unlimited.")
    parser.add_argument("--dry-run", action="store_true", help="Only run analysis on existing logs, don't download anything.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    def existing_full_logs():
        return sorted(
            (path for path in logs_dir.glob("*.json") if "-" not in path.stem),
            key=os.path.getmtime, reverse=True,
        )

    if args.dry_run:
        print("Dry run: Analyzing existing logs in logs/...")
        analyses = []
        for file in existing_full_logs()[:args.max_episodes]:
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

    config_path = Path(__file__).resolve().parent / "config_submissions.json"
    submission_ids = []
    if args.submission_id:
        submission_ids = [args.submission_id]
    elif config_path.exists():
        try:
            config_data = json.loads(config_path.read_text(encoding="utf-8"))
            submission_ids = config_data.get("submission_ids", [])
            if submission_ids:
                print(f"Loaded submission IDs from config: {submission_ids}")
        except Exception as e:
            print(f"Warning: Failed to load {config_path.name}: {e}")

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

    for sub_id in submission_ids:
        episodes = fetch_episodes_for_submission(username, key, sub_id)
        print(f"Found {len(episodes)} episodes total for submission {sub_id}")

        # Replays live flat under logs/<episode_id>.json, matching the layout
        # build_replay_opponents.py and test_replay_opponents.py assume.
        existing_stems = {path.stem for path in logs_dir.glob("*.json")}
        new_episodes = [ep.get("id") for ep in episodes if str(ep.get("id")) not in existing_stems]

        print(f"{len(new_episodes)} of these are new (not present in logs/).")

        # Limit the number of episodes we fetch to prevent rate limits
        to_download = new_episodes if args.max_episodes < 0 else new_episodes[:args.max_episodes]
        if to_download:
            print(f"Downloading {len(to_download)} new episode(s)...")
            for ep_id in to_download:
                dest = logs_dir / f"{ep_id}.json"
                success = download_replay(username, key, ep_id, dest)
                if success:
                    print(f"Downloaded episode {ep_id} to logs/")
                    downloaded_episodes.append(dest)
        else:
            print("No new episodes to download.")

    print("\nAnalyzing all logs in logs/...")
    all_analyses = []
    for file in existing_full_logs():
        analysis = analyze_replay(file)
        if analysis:
            all_analyses.append(analysis)

    if all_analyses:
        print_diagnostic_report(all_analyses)

        # Rebuild the replay opponent roster in-process (profiles.json,
        # ghost_actions.json, and the replay_*.py/profile_*.py stub agents).
        print("\nRebuilding replay opponents roster...")
        try:
            ensure_opponents_synced(force=True)
            print("Successfully rebuilt replay opponents roster!")
        except Exception as e:
            print(f"Error rebuilding replay opponents: {e}")
    else:
        print("No logs found to analyze.")

if __name__ == "__main__":
    main()
