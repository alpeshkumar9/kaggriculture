"""
Strategy Rules & Heuristics for Kaggriculture Bot
"""

COMMODITY_BASE_PRICES = {
    'WHEAT': 12,
    'CORN': 18,
    'SOY': 25,
    'MILK': 30,
    'EGGS': 15,
    'WOOL': 45,
    'FERTILIZER': 10
}

def get_base_price(item):
    return COMMODITY_BASE_PRICES.get(item, 10)

def evaluate_best_action(step, cash, inventory, market_prices, plots, land_quadrants=1):
    """
    Evaluates optimal action for the current turn based on ROI, market prices, and soil moisture.
    """
    # 1. Land Expansion: If cash >= 500 and land < 4, buy land quadrant
    if cash >= 600 and land_quadrants < 4:
        return {"action": "BUY_LAND", "cost": 500}

    # 2. Market Sales: Dump inventory when price is above base price * 1.15 or end of season
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

    # 3. Plot Operations: Harvest > Water > Plant
    for plot in plots:
        plot_id = plot.get('id')
        state = plot.get('state', 'EMPTY')

        if state == 'READY_TO_HARVEST':
            return {"action": "HARVEST", "plot_id": plot_id}
            
        elif state == 'PLANTED':
            if plot.get('moisture', 100) < 40 and cash >= 5:
                return {"action": "WATER", "plot_id": plot_id}
                
        elif state == 'EMPTY' and cash >= 15:
            # Rotate crop choice based on turn step
            crops = ['SOY', 'CORN', 'WHEAT']
            selected_crop = crops[step % len(crops)]
            return {"action": "PLANT", "plot_id": plot_id, "crop": selected_crop}

    # 4. Fallback Action
    return {"action": "PASS"}
