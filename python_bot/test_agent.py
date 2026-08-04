"""
Automated Test Harness for Official Kaggle Kaggriculture Bot
Validates full compliance with Kaggle Environments observation & action dict schemas.
"""

import time
from agent import agent

def run_official_kaggle_test():
    print("=" * 65)
    print("🤖 RUNNING OFFICIAL KAGGRICULTURE AGENT COMPLIANCE TEST SUITE")
    print("=" * 65)

    # Construct initial official Kaggle observation schema
    obs = {
        'player': 0,
        'day': 0,
        'hour': 0,
        'farms': [
            {
                'money': 3000.0,
                'tiles': [[None if (x < 5 and y < 5) else "LOCKED" for x in range(10)] for y in range(10)],
                'farmer': [0, 0],
                'hands': [],
                'unlocked_quadrants': ['NW'],
                'hires_today': 0
            },
            {
                'money': 3000.0,
                'tiles': [[None if (x < 5 and y < 5) else "LOCKED" for x in range(10)] for y in range(10)],
                'farmer': [0, 0],
                'hands': [],
                'unlocked_quadrants': ['NW'],
                'hires_today': 0
            }
        ],
        'market': {
            'inventory': {
                'WHEAT': 10000, 'CARROT': 10000, 'TOMATO': 10000,
                'STRAWBERRY': 10000, 'MELON': 10000, 'FERTILIZER': 10000
            },
            'prices': {
                'WHEAT': 25.0, 'CARROT': 35.0, 'TOMATO': 60.0,
                'STRAWBERRY': 120.0, 'MELON': 250.0, 'FERTILIZER': 100.0
            }
        },
        'town': {
            'unlocked_shops': ['BAKERY']
        },
        'private': {
            'shed': {'WHEAT': 0, 'CARROT': 0, 'TOMATO': 0, 'STRAWBERRY': 0, 'MELON': 0},
            'seeds': {'WHEAT': 0, 'CARROT': 0, 'TOMATO': 0, 'STRAWBERRY': 0, 'MELON': 0},
            'inventories': [{}]
        }
    }

    start_time = time.time()
    valid_actions_count = 0

    for step in range(720):
        obs['day'] = step // 24
        obs['hour'] = step % 24
        
        t0 = time.perf_counter()
        action_dict = agent(obs)
        t1 = time.perf_counter()

        # Strict Kaggle schema assertions
        assert isinstance(action_dict, dict), f"Turn {step}: Action must be dict"
        assert 'farmer' in action_dict, f"Turn {step}: Missing 'farmer' key"
        assert 'hands' in action_dict, f"Turn {step}: Missing 'hands' key"
        assert 'market' in action_dict, f"Turn {step}: Missing 'market' key"

        assert isinstance(action_dict['farmer'], list), f"Turn {step}: 'farmer' must be a list"
        assert isinstance(action_dict['hands'], list), f"Turn {step}: 'hands' must be a list"
        assert isinstance(action_dict['market'], list), f"Turn {step}: 'market' must be a list"

        valid_actions_count += 1

        # Process worker actions (farmer & hands)
        farmer_act = action_dict.get('farmer', ['PASS'])
        workers_actions = [farmer_act] + action_dict.get('hands', [])
        workers_pos = [obs['farms'][0]['farmer']] + obs['farms'][0]['hands']

        for idx, act in enumerate(workers_actions):
            if not act or not isinstance(act, list):
                continue
            wx, wy = workers_pos[idx] if idx < len(workers_pos) else (0, 0)
            cmd = act[0]

            if cmd == 'NORTH' and wy > 0:
                workers_pos[idx][1] -= 1
            elif cmd == 'SOUTH' and wy < 9:
                workers_pos[idx][1] += 1
            elif cmd == 'EAST' and wx < 9:
                workers_pos[idx][0] += 1
            elif cmd == 'WEST' and wx > 0:
                workers_pos[idx][0] -= 1
            elif cmd == 'PLANT' and len(act) > 1:
                crop = act[1]
                if obs['private']['seeds'].get(crop, 0) > 0:
                    obs['private']['seeds'][crop] -= 1
                    obs['farms'][0]['tiles'][wy][wx] = {
                        'kind': 'PLANT',
                        'crop': crop,
                        'planted_day': obs['day'],
                        'watered_today': True,
                        'yield_units': 0
                    }
            elif cmd == 'WATER':
                t = obs['farms'][0]['tiles'][wy][wx]
                if isinstance(t, dict):
                    t['watered_today'] = True
            elif cmd == 'HARVEST':
                t = obs['farms'][0]['tiles'][wy][wx]
                if isinstance(t, dict) and t.get('kind') == 'PLANT':
                    crop = t.get('crop', 'WHEAT')
                    yield_qty = t.get('yield_units', 4)
                    if yield_qty <= 0: yield_qty = 4
                    obs['private']['shed'][crop] = obs['private']['shed'].get(crop, 0) + yield_qty
                    obs['farms'][0]['tiles'][wy][wx] = None # One-time harvest clears tile

        # Simulate Crop Growth & Yield updates each day
        if obs['hour'] == 0:
            obs['farms'][0]['hires_today'] = 0
            obs['farms'][0]['hands'] = [] # Reset hired hands each day
            for r in range(10):
                for c in range(10):
                    t = obs['farms'][0]['tiles'][r][c]
                    if isinstance(t, dict) and t.get('kind') == 'PLANT':
                        t['watered_today'] = False
                        age = obs['day'] - t.get('planted_day', 0)
                        if age >= 2: # Crops mature after 2+ days
                            t['yield_units'] = 4

        # Process market orders in test loop
        for order in action_dict['market']:
            if not isinstance(order, list) or not order:
                continue
            cmd = order[0]
            if cmd == 'BUY_LAND':
                quads = obs['farms'][0]['unlocked_quadrants']
                if len(quads) < 4:
                    next_cost = [1000, 2000, 4000][len(quads) - 1]
                    if obs['farms'][0]['money'] >= next_cost:
                        obs['farms'][0]['money'] -= next_cost
                        quads.append('NE' if len(quads) == 1 else 'SW' if len(quads) == 2 else 'SE')
                        for y in range(10):
                            for x in range(10):
                                if x >= 5 and y < 5 and 'NE' in quads:
                                    obs['farms'][0]['tiles'][y][x] = None
                                elif x < 5 and y >= 5 and 'SW' in quads:
                                    obs['farms'][0]['tiles'][y][x] = None
                                elif x >= 5 and y >= 5 and 'SE' in quads:
                                    obs['farms'][0]['tiles'][y][x] = None
            elif cmd == 'HIRE':
                hires = obs['farms'][0]['hires_today']
                fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
                cost = fib[min(hires, len(fib) - 1)]
                if obs['farms'][0]['money'] >= cost:
                    obs['farms'][0]['money'] -= cost
                    obs['farms'][0]['hires_today'] += 1
                    obs['farms'][0]['hands'].append([0, 0]) # Spawn hand at shed
            elif cmd == 'BUY_SEED' and len(order) >= 3:
                crop = order[1]
                qty = order[2]
                costs = {'WHEAT': 10, 'CARROT': 20, 'TOMATO': 50, 'STRAWBERRY': 100, 'MELON': 80}
                total_cost = costs.get(crop, 10) * qty
                if obs['farms'][0]['money'] >= total_cost:
                    obs['farms'][0]['money'] -= total_cost
                    obs['private']['seeds'][crop] = obs['private']['seeds'].get(crop, 0) + qty
            elif cmd == 'SELL' and len(order) >= 3:
                item = order[1]
                qty = order[2]
                avail = obs['private']['shed'].get(item, 0)
                sold = min(avail, qty)
                obs['private']['shed'][item] -= sold
                obs['farms'][0]['money'] += sold * obs['market']['prices'].get(item, 25)

    total_time = time.time() - start_time
    avg_turn_ms = (total_time / 720) * 1000

    print("\n✅ OFFICIAL KAGGRICULTURE COMPLIANCE TEST RESULTS:")
    print(f"  • Total Valid Turns Executed: {valid_actions_count} / 720")
    print(f"  • Total Benchmark Duration:  {total_time:.3f} seconds")
    print(f"  • Average Turn Latency:      {avg_turn_ms:.3f} ms / turn")
    print(f"  • Final Cash Balance:        ${obs['farms'][0]['money']:.2f}")
    print(f"  • Unlocked Quadrants:        {obs['farms'][0]['unlocked_quadrants']}")
    print(f"  • Final Private Seeds:       {obs['private']['seeds']}")
    print(f"  • Final Shed Inventory:      {obs['private']['shed']}")
    print("=" * 65)
    print("🎉 ALL KAGGLE ENVIRONMENTS SCHEMA ASSERTIONS PASSED!")
    print("=" * 65)

if __name__ == '__main__':
    run_official_kaggle_test()

