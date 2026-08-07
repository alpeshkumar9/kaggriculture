import json

def analyze(log_path):
    with open(log_path) as f:
        data = json.load(f)
    
    agent_id = 0
    plants_by_day = {}
    
    for i, step in enumerate(data["steps"]):
        if len(step) <= agent_id: continue
        action = step[agent_id].get("action", {})
        if action is None: continue
        workers = action.get("hands", []) + [action.get("farmer", ["PASS"])]
        day = i // 24
        plants_by_day.setdefault(day, {})
        for worker in workers:
            if worker and len(worker) > 1 and worker[0] == "PLANT":
                crop = worker[1]
                plants_by_day[day][crop] = plants_by_day[day].get(crop, 0) + 1
    
    print("Opponent Ghost (Agent 0) Plants:")
    for day in sorted(plants_by_day.keys()):
        if plants_by_day[day]:
            print(f"  Day {day}: {plants_by_day[day]}")

analyze("logs/90491990.json")
