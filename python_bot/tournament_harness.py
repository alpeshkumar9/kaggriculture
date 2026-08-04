"""
Official Tournament Validation Harness & Bradley-Terry Skill Rating Benchmark
Runs head-to-head 720-turn match episodes between competing AI agents.
"""

import time
import math
import random
from agent import agent as phase2_agent

class TournamentEngine:
    """
    Lightweight 2-Player Kaggriculture Match Simulator
    """
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)
        self.reset()

    def reset(self):
        self.turn = 0
        self.market = {
            'inventory': {
                'WHEAT': 10000, 'CARROT': 10000, 'TOMATO': 10000,
                'STRAWBERRY': 10000, 'MELON': 10000, 'FERTILIZER': 10000
            },
            'prices': {
                'WHEAT': 25.0, 'CARROT': 35.0, 'TOMATO': 60.0,
                'STRAWBERRY': 120.0, 'MELON': 250.0, 'FERTILIZER': 100.0
            }
        }
        self.farms = [
            {
                'money': 1000.0,
                'tiles': [[None if (x < 5 and y < 5) else "LOCKED" for x in range(10)] for y in range(10)],
                'farmer': [0, 0],
                'hands': [],
                'unlocked_quadrants': ['NW'],
                'hires_today': 0
            },
            {
                'money': 1000.0,
                'tiles': [[None if (x < 5 and y < 5) else "LOCKED" for x in range(10)] for y in range(10)],
                'farmer': [0, 0],
                'hands': [],
                'unlocked_quadrants': ['NW'],
                'hires_today': 0
            }
        ]
        self.privates = [
            {'shed': {'WHEAT': 0, 'CARROT': 0, 'TOMATO': 0, 'STRAWBERRY': 0, 'MELON': 0}, 'seeds': {'WHEAT': 5, 'CARROT': 2}},
            {'shed': {'WHEAT': 0, 'CARROT': 0, 'TOMATO': 0, 'STRAWBERRY': 0, 'MELON': 0}, 'seeds': {'WHEAT': 5, 'CARROT': 2}}
        ]

    def run_match(self, agent_a, agent_b):
        self.reset()
        agents = [agent_a, agent_b]

        for turn in range(720):
            day = turn // 24
            hour = turn % 24

            for pid in range(2):
                obs = {
                    'player': pid,
                    'day': day,
                    'hour': hour,
                    'farms': self.farms,
                    'market': self.market,
                    'town': {'unlocked_shops': ['BAKERY'] if day >= 3 else []},
                    'private': self.privates[pid]
                }
                
                try:
                    action = agents[pid](obs)
                except Exception as e:
                    action = {"farmer": ["PASS"], "hands": [], "market": []}

                self.apply_player_action(pid, action, day, hour)

            # Daily crop & animal growth update at start of day (0:00 HR)
            if hour == 0:
                for f in self.farms:
                    f['hires_today'] = 0
                    f['hands'] = []
                    for r in range(10):
                        for c in range(10):
                            t = f['tiles'][r][c]
                            if isinstance(t, dict):
                                if t.get('kind') == 'PLANT':
                                    t['watered_today'] = False
                                    crop = t.get('crop', 'WHEAT')
                                    age = day - t.get('planted_day', 0)
                                    if crop in ['WHEAT', 'CARROT'] and age >= 2:
                                        t['yield_units'] = 4
                                    elif crop == 'TOMATO' and age >= 7:
                                        t['yield_units'] = 4
                                    elif crop in ['STRAWBERRY', 'MELON'] and age >= 10:
                                        t['yield_units'] = 6
                                elif t.get('kind') == 'PASTURE' and t.get('animal') == 'COW':
                                    t['fed_today'] = False
                                    t['cared_today'] = False
                                    age = day - t.get('placed_day', 0)
                                    # Cows produce Milk every 2 days
                                    if age >= 2 and age % 2 == 0:
                                        bonus = t.get('pending_care_bonus', 0)
                                        t['yield_units'] = 1 + bonus
                                        t['pending_care_bonus'] = 0

        score_a = self.farms[0]['money']
        score_b = self.farms[1]['money']
        return score_a, score_b


    def apply_player_action(self, pid, action, day, hour):
        farm = self.farms[pid]
        priv = self.privates[pid]
        
        # Process worker actions (farmer & hands)
        workers_actions = [action.get('farmer', ['PASS'])] + action.get('hands', [])
        workers_pos = [farm['farmer']] + farm['hands']

        for idx, act in enumerate(workers_actions):
            if not act or not isinstance(act, list): continue
            wx, wy = workers_pos[idx] if idx < len(workers_pos) else (0, 0)
            cmd = act[0]

            if cmd == 'NORTH' and wy > 0: workers_pos[idx][1] -= 1
            elif cmd == 'SOUTH' and wy < 9: workers_pos[idx][1] += 1
            elif cmd == 'EAST' and wx < 9: workers_pos[idx][0] += 1
            elif cmd == 'WEST' and wx > 0: workers_pos[idx][0] -= 1
            elif cmd == 'BUILD_PASTURE':
                if farm['tiles'][wy][wx] is None and farm['money'] >= 150:
                    farm['money'] -= 150
                    farm['tiles'][wy][wx] = {'kind': 'PASTURE', 'animal': 'COW', 'placed_day': day, 'fed_today': True, 'cared_today': True, 'yield_units': 0, 'pending_care_bonus': 0}
            elif cmd == 'PLACE_ANIMAL' and len(act) > 1:
                animal = act[1]
                t = farm['tiles'][wy][wx]
                if isinstance(t, dict) and t.get('kind') == 'PASTURE':
                    t['animal'] = animal
                    t['placed_day'] = day
            elif cmd == 'FEED':
                t = farm['tiles'][wy][wx]
                if isinstance(t, dict) and t.get('kind') == 'PASTURE' and (priv['shed'].get('WHEAT', 0) > 0 or priv['seeds'].get('WHEAT', 0) > 0):
                    if priv['shed'].get('WHEAT', 0) > 0: priv['shed']['WHEAT'] -= 1
                    elif priv['seeds'].get('WHEAT', 0) > 0: priv['seeds']['WHEAT'] -= 1
                    t['fed_today'] = True
            elif cmd == 'CARE':
                t = farm['tiles'][wy][wx]
                if isinstance(t, dict) and t.get('kind') == 'PASTURE':
                    t['cared_today'] = True
                    if t.get('fed_today', False):
                        t['pending_care_bonus'] = t.get('pending_care_bonus', 0) + 2
            elif cmd == 'PLANT' and len(act) > 1:
                crop = act[1]
                if priv['seeds'].get(crop, 0) > 0:
                    priv['seeds'][crop] -= 1
                    farm['tiles'][wy][wx] = {'kind': 'PLANT', 'crop': crop, 'planted_day': day, 'watered_today': True, 'yield_units': 0}
            elif cmd == 'HARVEST':
                t = farm['tiles'][wy][wx]
                if isinstance(t, dict):
                    if t.get('kind') == 'PLANT':
                        crop = t.get('crop', 'WHEAT')
                        yield_qty = t.get('yield_units', 4)
                        if yield_qty <= 0: yield_qty = 4
                        priv['shed'][crop] = priv['shed'].get(crop, 0) + yield_qty
                        farm['tiles'][wy][wx] = None
                    elif t.get('kind') == 'PASTURE' and t.get('animal') == 'COW':
                        yield_qty = t.get('yield_units', 3)
                        if yield_qty <= 0: yield_qty = 3
                        priv['shed']['MILK'] = priv['shed'].get('MILK', 0) + yield_qty
                        t['yield_units'] = 0

        # Market actions
        for order in action.get('market', []):
            if not isinstance(order, list) or not order: continue
            cmd = order[0]
            if cmd == 'BUY_LAND':
                quads = farm['unlocked_quadrants']
                if len(quads) < 3: # Max 3 Quadrants
                    cost = [1000, 2000][len(quads) - 1]
                    if farm['money'] >= cost:
                        farm['money'] -= cost
                        quads.append('NE' if len(quads) == 1 else 'SW' if len(quads) == 2 else 'SE')
                        for y in range(10):
                            for x in range(10):
                                if (x >= 5 and y < 5 and 'NE' in quads) or (x < 5 and y >= 5 and 'SW' in quads):
                                    farm['tiles'][y][x] = None
            elif cmd == 'HIRE':
                cost = [1, 1, 2, 3, 5, 8, 13, 21][min(farm['hires_today'], 7)]
                if farm['money'] >= cost:
                    farm['money'] -= cost
                    farm['hires_today'] += 1
                    farm['hands'].append([0, 0])
            elif cmd == 'BUY_ANIMAL' and len(order) >= 3:
                animal = order[1]
                qty = order[2]
                cost = 400 * qty
                if farm['money'] >= cost:
                    farm['money'] -= cost
                    priv['shed'][animal] = priv['shed'].get(animal, 0) + qty
            elif cmd == 'BUY_SEED' and len(order) >= 3:
                crop, qty = order[1], order[2]
                cost = {'WHEAT': 10, 'CARROT': 20, 'TOMATO': 50, 'STRAWBERRY': 100, 'MELON': 80}.get(crop, 10) * qty
                if farm['money'] >= cost:
                    farm['money'] -= cost
                    priv['seeds'][crop] = priv['seeds'].get(crop, 0) + qty
            elif cmd == 'SELL' and len(order) >= 3:
                item, qty = order[1], order[2]
                avail = priv['shed'].get(item, 0)
                sold = min(avail, qty)
                priv['shed'][item] -= sold
                farm['money'] += sold * self.market['prices'].get(item, 25)


# Opponent Baseline Agents
def pass_agent(obs):
    return {"farmer": ["PASS"], "hands": [], "market": []}

def random_agent(obs):
    moves = ["NORTH", "SOUTH", "EAST", "WEST", "PASS"]
    return {"farmer": [random.choice(moves)], "hands": [], "market": []}

def greedy_harvester_agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    priv = obs["private"]
    fx, fy = me["farmer"]
    tile = me["tiles"][fy][fx]
    market = []

    if priv["seeds"].get("WHEAT", 0) == 0 and me["money"] >= 10:
        market.append(["BUY_SEED", "WHEAT", 1])

    for k, v in priv["shed"].items():
        if v > 0: market.append(["SELL", k, v])

    if tile is None and priv["seeds"].get("WHEAT", 0) > 0:
        return {"farmer": ["PLANT", "WHEAT"], "hands": [], "market": market}

    if isinstance(tile, dict) and tile.get("kind") == "PLANT":
        if obs["day"] - tile.get("planted_day", 0) >= 2:
            return {"farmer": ["HARVEST"], "hands": [], "market": market}
        if not tile.get("watered_today", False):
            return {"farmer": ["WATER"], "hands": [], "market": market}

    return {"farmer": ["PASS"], "hands": [], "market": market}


# Bradley-Terry Skill Rating System
class BradleyTerryRating:
    def __init__(self, k_factor=32.0, initial_rating=1200.0):
        self.k_factor = k_factor
        self.ratings = {}
        self.initial_rating = initial_rating

    def get_rating(self, agent_name):
        return self.ratings.get(agent_name, self.initial_rating)

    def expected_score(self, rating_a, rating_b):
        return 1.0 / (1.0 + math.pow(10.0, (rating_b - rating_a) / 400.0))

    def update_ratings(self, agent_a, agent_b, score_a_actual, score_b_actual):
        r_a = self.get_rating(agent_a)
        r_b = self.get_rating(agent_b)

        e_a = self.expected_score(r_a, r_b)
        e_b = self.expected_score(r_b, r_a)

        if score_a_actual > score_b_actual:
            s_a, s_b = 1.0, 0.0
        elif score_b_actual > score_a_actual:
            s_a, s_b = 0.0, 1.0
        else:
            s_a, s_b = 0.5, 0.5

        self.ratings[agent_a] = r_a + self.k_factor * (s_a - e_a)
        self.ratings[agent_b] = r_b + self.k_factor * (s_b - e_b)


def run_tournament(episodes_per_pair=15):
    print("=" * 70)
    print("🏆 RUNNING OFFICIAL KAGGRICULTURE BRADLEY-TERRY TOURNAMENT HARNESS")
    print("=" * 70)

    agents = {
        "Phase2_Winning_Bot": phase2_agent,
        "Greedy_Harvester_Bot": greedy_harvester_agent,
        "Random_Baseline_Bot": random_agent,
        "Pass_Baseline_Bot": pass_agent
    }

    bt_system = BradleyTerryRating()
    engine = TournamentEngine()

    agent_names = list(agents.keys())
    total_matches = 0
    start_time = time.time()

    stats = {name: {'wins': 0, 'losses': 0, 'ties': 0, 'total_cash': 0.0, 'matches': 0} for name in agent_names}

    for i in range(len(agent_names)):
        for j in range(i + 1, len(agent_names)):
            name_a = agent_names[i]
            name_b = agent_names[j]

            print(f"⚔️ Matchup: {name_a} vs {name_b} ({episodes_per_pair} Episodes)...")

            for ep in range(episodes_per_pair):
                score_a, score_b = engine.run_match(agents[name_a], agents[name_b])
                total_matches += 1

                stats[name_a]['total_cash'] += score_a
                stats[name_b]['total_cash'] += score_b
                stats[name_a]['matches'] += 1
                stats[name_b]['matches'] += 1

                if score_a > score_b:
                    stats[name_a]['wins'] += 1
                    stats[name_b]['losses'] += 1
                elif score_b > score_a:
                    stats[name_b]['wins'] += 1
                    stats[name_a]['losses'] += 1
                else:
                    stats[name_a]['ties'] += 1
                    stats[name_b]['ties'] += 1

                bt_system.update_ratings(name_a, name_b, score_a, score_b)

    duration = time.time() - start_time

    print("\n" + "=" * 70)
    print("📊 BRADLEY-TERRY LEADERBOARD STANDINGS & SKILL RATINGS")
    print("=" * 70)
    print(f"{'Rank':<5} | {'Agent Name':<25} | {'Elo Rating':<12} | {'Win Rate':<10} | {'Avg Cash':<12}")
    print("-" * 70)

    sorted_agents = sorted(agent_names, key=lambda name: bt_system.get_rating(name), reverse=True)

    for rank, name in enumerate(sorted_agents, 1):
        st = stats[name]
        rating = bt_system.get_rating(name)
        win_rate = (st['wins'] / st['matches'] * 100) if st['matches'] > 0 else 0.0
        avg_cash = (st['total_cash'] / st['matches']) if st['matches'] > 0 else 0.0
        print(f"#{rank:<4} | {name:<25} | {rating:<12.1f} | {win_rate:<9.1f}% | ${avg_cash:<11.2f}")

    print("=" * 70)
    print(f"🎉 TOURNAMENT COMPLETED! Total Matches: {total_matches} | Duration: {duration:.2f}s")
    print("=" * 70)

if __name__ == '__main__':
    run_tournament()

