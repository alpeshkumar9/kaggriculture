"""
Official Strategy Rules & Heuristics for Kaggriculture Kaggle Bot
Matches Official Kaggle "How to Play" Specifications
"""

COMMODITY_BASE_PRICES = {
    'WHEAT': 25,
    'CARROT': 35,
    'TOMATO': 45,
    'STRAWBERRY': 60
}

SEED_COSTS = {
    'WHEAT': 10,
    'CARROT': 20,
    'TOMATO': 30,
    'STRAWBERRY': 40
}

def get_base_price(item):
    return COMMODITY_BASE_PRICES.get(item, 25)

def evaluate_best_action(step, cash, inventory, market_prices, plots, land_quadrants=1):
    """
    Evaluates optimal turn action based on official Kaggle Wheat/Carrot rules.
    """
    # 1. Expand land if cash permits
    if cash >= 550 and land_quadrants < 4:
        return {"action": "BUY_LAND", "cost": 500}

    # 2. Sell inventory when price >= 1.15 * Base Price or near season end
    for item, qty in inventory.items():
        if qty > 0 and item in market_prices:
            curr_price = market_prices[item]
            base = get_base_price(item)
            if curr_price >= base * 1.15 or step >= 710:
                return {
                    "action": "SELL_MARKET",
                    "item": item,
                    "quantity": qty,
                    "price": curr_price
                }

    # 3. Handle Plot Operations (Clear Weeds > Harvest > Water > Plant)
    for plot in plots:
        plot_id = plot.get('id')
        state = plot.get('state', 'EMPTY')

        if state == 'WEED':
            return {"action": "CLEAR_WEED", "plot_id": plot_id}

        elif state == 'READY_TO_HARVEST':
            return {"action": "HARVEST", "plot_id": plot_id}

        elif state == 'PLANTED':
            if plot.get('moisture', 100) < 35 and cash >= 2:
                return {"action": "WATER", "plot_id": plot_id}

        elif state == 'EMPTY' and cash >= 15:
            # Rotate crop choices (Wheat, Carrot, Tomato)
            crops = ['WHEAT', 'CARROT', 'TOMATO']
            selected_crop = crops[step % len(crops)]
            if cash >= SEED_COSTS.get(selected_crop, 10):
                return {"action": "PLANT", "plot_id": plot_id, "crop": selected_crop}

    return {"action": "PASS"}
