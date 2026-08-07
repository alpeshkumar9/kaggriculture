import json

def analyze(log_path):
    with open(log_path) as f:
        data = json.load(f)
    
    for agent_id in [0, 1]:
        print(f"Agent {agent_id}:")
        wheat_plants_by_day = {}
        for i, step in enumerate(data["steps"]):
            if len(step) <= agent_id: continue
            action = step[agent_id].get("action", {})
            if action is None: continue
            workers = action.get("hands", []) + [action.get("farmer", ["PASS"])]
            day = i // 24
            wheat_plants_by_day.setdefault(day, 0)
            for worker in workers:
                if worker and len(worker) > 1 and worker[0] == "PLANT" and worker[1] == "WHEAT":
                    wheat_plants_by_day[day] += 1
        
        for day in sorted(wheat_plants_by_day.keys()):
            if wheat_plants_by_day[day] > 0:
                print(f"  Day {day}: {wheat_plants_by_day[day]}")

analyze("logs/90491990.json")
