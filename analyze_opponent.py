import json

def analyze(log_path):
    with open(log_path) as f:
        data = json.load(f)
    
    agent_id = 1
    
    sales = {}
    purchases = {}
    
    for step in data["steps"]:
        obs = step[0].get("observation", {})
        if "market" in obs:
            prices = obs["market"]
        
        action = step[agent_id].get("action", {})
        market = action.get("market", [])
        for act in market:
            if act[0] == "SELL":
                item = act[1]
                qty = act[2]
                sales[item] = sales.get(item, 0) + qty * prices.get(item, 0)
            elif act[0] == "BUY_PRODUCT":
                item = act[1]
                qty = act[2]
                purchases[item] = purchases.get(item, 0) + qty * prices.get(item, 0)
            elif act[0] == "BUY_SEED":
                item = act[1]
                qty = act[2]
                purchases[item + "_SEED"] = purchases.get(item + "_SEED", 0) + qty * 10
            elif act[0] == "BUY_ANIMAL":
                item = act[1]
                qty = act[2]
                purchases[item] = purchases.get(item, 0) + qty * 400
    
    print("Sales:")
    for k, v in sales.items():
        print(f"  {k}: ${v:,.0f}")
    print("Purchases:")
    for k, v in purchases.items():
        print(f"  {k}: ${v:,.0f}")

analyze("logs/90491990.json")
