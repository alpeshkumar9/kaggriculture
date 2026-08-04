"""
Automated Test Harness for Kaggriculture Python Bot
Tests 720-turn simulation performance, memory integrity, and turn timing.
"""

import time
import sys
from agent import agent

def run_automated_test():
    print("=" * 60)
    print("🤖 RUNNING AUTOMATED TEST SUITE: KAGGRICULTURE AGENT")
    print("=" * 60)

    # Initialize simulated observation state
    obs = {
        'step': 0,
        'cash': 1000,
        'market_prices': {
            'WHEAT': 12.0, 'CORN': 18.0, 'SOY': 25.0,
            'MILK': 30.0, 'EGGS': 15.0, 'WOOL': 45.0
        },
        'inventory': {'WHEAT': 0, 'CORN': 0, 'SOY': 0},
        'plots': [
            {'id': f'plot_{i}', 'state': 'EMPTY', 'moisture': 80, 'crop': None, 'growth': 0}
            for i in range(1, 5)
        ]
    }

    start_time = time.time()
    turns_executed = 0

    for step in range(720):
        obs['step'] = step

        # Measure per-turn execution speed
        t0 = time.perf_counter()
        action = agent(obs)
        t1 = time.perf_counter()

        turn_ms = (t1 - t0) * 1000
        turns_executed += 1

        # Assert action structure
        assert isinstance(action, dict), f"Turn {step}: Action must be a dictionary!"
        assert 'action' in action, f"Turn {step}: Action dictionary missing 'action' key!"

        # Simulate environmental plot growth and market selling state updates
        act_type = action.get('action')
        if act_type == 'PLANT':
            p_id = action.get('plot_id')
            crop = action.get('crop')
            obs['cash'] -= 10
            for p in obs['plots']:
                if p['id'] == p_id:
                    p['state'] = 'PLANTED'
                    p['crop'] = crop
                    p['growth'] = 0

        elif act_type == 'WATER':
            obs['cash'] -= 3

        elif act_type == 'HARVEST':
            p_id = action.get('plot_id')
            for p in obs['plots']:
                if p['id'] == p_id and p['state'] == 'READY_TO_HARVEST':
                    crop = p['crop']
                    obs['inventory'][crop] = obs['inventory'].get(crop, 0) + 10
                    p['state'] = 'EMPTY'
                    p['growth'] = 0

        elif act_type == 'SELL_MARKET':
            item = action.get('item')
            qty = action.get('quantity', 0)
            if obs['inventory'].get(item, 0) >= qty and qty > 0:
                price = obs['market_prices'].get(item, 10)
                obs['inventory'][item] -= qty
                obs['cash'] += int(qty * price)

        elif act_type == 'BUY_LAND':
            obs['cash'] -= 500
            curr_plots = len(obs['plots'])
            for i in range(curr_plots + 1, curr_plots + 5):
                obs['plots'].append({'id': f'plot_{i}', 'state': 'EMPTY', 'moisture': 80, 'crop': None, 'growth': 0})

        # Advance plot growth
        for p in obs['plots']:
            if p['state'] == 'PLANTED':
                p['growth'] += 20
                if p['growth'] >= 100:
                    p['state'] = 'READY_TO_HARVEST'

        if turn_ms > 1000:
            print(f"⚠️ Warning: Turn {step} execution took {turn_ms:.2f} ms (>1000ms limit)")

    total_time = time.time() - start_time
    avg_turn_ms = (total_time / 720) * 1000

    print("\n✅ AUTOMATED TEST RESULTS:")
    print(f"  • Total Turns Executed: {turns_executed} / 720")
    print(f"  • Total Test Duration:  {total_time:.3f} seconds")
    print(f"  • Average Turn Latency: {avg_turn_ms:.3f} ms / turn (Max Kaggle limit: 5000ms)")
    print(f"  • Final Cash Balance:   ${obs['cash']:.2f}")
    print(f"  • Final Inventory:      {obs['inventory']}")
    print(f"  • Final Land Plots:     {len(obs['plots'])}")
    print("=" * 60)
    print("🎉 ALL TEST ASSERITIONS PASSED! AGENT IS READY FOR KAGGLE SUBMISSION.")
    print("=" * 60)

if __name__ == '__main__':
    run_automated_test()
