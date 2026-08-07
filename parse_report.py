import json

with open("replays/report.json") as f:
    report = json.load(f)

for ep in report["episodes"]:
    if "90491990" in ep["agents"][1]:
        print("Opponent 90491990 Stats:")
        stats = ep["stats"][1]
        print(f"  Bank: ${stats['bank']}")
        for k, v in stats.items():
            if isinstance(v, dict) and "revenue" in v:
                print(f"  {k}: {v['units']} units, ${v['revenue']}")
        print(f"  Purchases:")
        for k, v in stats.items():
            if isinstance(v, dict) and "purchases" in v:
                print(f"    {k}: ${v['purchases']}")
        print(f"  Peak Tiles: {stats.get('peak_tiles')}")
        break
