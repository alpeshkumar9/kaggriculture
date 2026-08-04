"""
Kaggriculture Submission Bot for Kaggle Environments (Official Rules Compliant)
Author: Antigravity AI Agent
Competition: Kaggriculture (Kaggle)
"""

import math
import random
try:
    from strategy_rules import evaluate_best_action, get_base_price
except ImportError:
    COMMODITY_BASE_PRICES = {'WHEAT': 25, 'CARROT': 35, 'TOMATO': 45, 'STRAWBERRY': 60}
    SEED_COSTS = {'WHEAT': 10, 'CARROT': 20, 'TOMATO': 30, 'STRAWBERRY': 40}

    def get_base_price(item):
        return COMMODITY_BASE_PRICES.get(item, 25)

    def evaluate_best_action(step, cash, inventory, market_prices, plots, land_quadrants=1):
        if cash >= 550 and land_quadrants < 4:
            return {"action": "BUY_LAND", "cost": 500}

        for item, qty in inventory.items():
            if qty > 0 and item in market_prices:
                if market_prices[item] >= get_base_price(item) * 1.15 or step >= 710:
                    return {"action": "SELL_MARKET", "item": item, "quantity": qty, "price": market_prices[item]}

        for plot in plots:
            p_id = plot.get('id')
            state = plot.get('state', 'EMPTY')
            if state == 'WEED':
                return {"action": "CLEAR_WEED", "plot_id": p_id}
            elif state == 'READY_TO_HARVEST':
                return {"action": "HARVEST", "plot_id": p_id}
            elif state == 'PLANTED' and plot.get('moisture', 100) < 35 and cash >= 2:
                return {"action": "WATER", "plot_id": p_id}
            elif state == 'EMPTY' and cash >= 15:
                crops = ['WHEAT', 'CARROT', 'TOMATO']
                choice = crops[step % len(crops)]
                if cash >= SEED_COSTS.get(choice, 10):
                    return {"action": "PLANT", "plot_id": p_id, "crop": choice}

        return {"action": "PASS"}

bot_memory = {
    'turn': 0,
    'land_quadrants': 1
}

def agent(observation, configuration=None):
    global bot_memory

    obs_dict = observation if isinstance(observation, dict) else getattr(observation, '__dict__', {})

    step = obs_dict.get('step', bot_memory['turn'])
    cash = obs_dict.get('cash', 1000)
    market_prices = obs_dict.get('market_prices', {
        'WHEAT': 25, 'CARROT': 35, 'TOMATO': 45, 'STRAWBERRY': 60
    })
    inventory = obs_dict.get('inventory', {})
    plots = obs_dict.get('plots', [
        {'id': 'plot_1', 'state': 'EMPTY', 'moisture': 100},
        {'id': 'plot_2', 'state': 'EMPTY', 'moisture': 100},
        {'id': 'plot_3', 'state': 'EMPTY', 'moisture': 100},
        {'id': 'plot_4', 'state': 'EMPTY', 'moisture': 100}
    ])

    bot_memory['turn'] = step

    action_dict = evaluate_best_action(
        step=step,
        cash=cash,
        inventory=inventory,
        market_prices=market_prices,
        plots=plots,
        land_quadrants=bot_memory['land_quadrants']
    )

    if action_dict.get('action') == 'BUY_LAND':
        bot_memory['land_quadrants'] += 1

    return action_dict

def my_agent(observation, configuration=None):
    return agent(observation, configuration)
