# Winning Strategy Roadmap & Implementation Plan for Kaggle Kaggriculture ($50,000 Prize Pool)

To build a **#1 Leaderboard Winning Agent** for Kaggriculture, we are following a 3-phase execution roadmap moving from foundation compatibility to advanced economic optimization, price prediction, and head-to-head validation.

---

## 🏆 Progress Status

```
Phase 1: Standard Compliance & Foundation Fix [COMPLETED ✅]
   ├── Fix Python Bot Observation & Action Schemas (Kaggle Environments) [DONE]
   ├── Implement 2D Grid Pathfinding & Spatial Inventory Manager (BFS/A*) [DONE]
   └── Align Web Simulator Engine & Exporter with 100% Official Specs [DONE]
        │
Phase 2: Winning Economic Engine & Advanced Bot [NEXT UP 🚀]
   ├── Dynamic ROI & Seasonal Crop Scheduler (720-Turn Horizon)
   ├── Town Demand Front-Running & Dynamic Market Arbitrage (Avoid Gluts)
   ├── Optimal Livestock CARE Bank & Fertilizer Bonus Cycles
   └── Aggressive Land Expansion ($1k/$2k/$4k) & Farmhand Scaling
        │
Phase 3: Tournament Validation Harness & Opponent Modeling [PLANNED ⏳]
   ├── Local 1,000-Episode Self-Play & Match Arena Simulation
   ├── Bradley-Terry Skill Rating Leaderboard Benchmark
   └── Kaggle Submission Package Packaging (<100 MiB)
```

---

## 🎯 Phase 2 Execution Plan

### 1. Dynamic ROI & 720-Turn Seasonal Crop Scheduler (`python_bot/strategy_rules.py`)
- **Early Season (Turns 1–240 / Days 1–10):** Plant 2-day fast turnover Wheat & Carrots to generate rapid capital for Land Quadrant #2 ($1,000) and Quadrant #3 ($2,000).
- **Mid Season (Turns 241–550 / Days 11–23):** Transition to ongoing high-yield crops (Tomatoes, Strawberries) and premium Melons ($250 base price). Unlock Land Quadrant #4 ($4,000) to max out at 100 tiles.
- **Late Season (Turns 551–720 / Days 24–30):** Stop planting long-gestation crops. Pivot back to fast 2-day Wheat & Carrots to ensure 100% of planted produce is harvested and sold before Turn 720.

### 2. Town Demand Front-Running & Market Arbitrage (`python_bot/agent.py`)
- Track town shop unlocks (every 3 days) and town center consumption schedule.
- Hold harvested items in shed during low price periods; liquidate when town demand drains market inventory ($I_0 < 10,000$), driving prices above base.
- Implement tiered sell limits to avoid dumping large quantities at once, preventing steep price crashes to the $1 price floor on premium items.

### 3. Livestock Care & Fertilizer Yield Doubling (`python_bot/strategy_rules.py`)
- Automated daily `CARE` execution on fed livestock (Goose, Cow, Sheep) to bank +2 yield bonuses paid out on scheduled production days.
- Strategic `FERTILIZE` application on ongoing crops (Tomato, Strawberry) on watered days to double yield.

### 4. Fibonacci Farmhand ROI Calculator (`python_bot/agent.py`)
- Dynamically calculate whether hiring an additional farmhand (`farmHandCostMult * fib(n)`) yields net positive ROI based on unwatered/unfed tile count.

---

## ❓ User Review & Approval Required

> [!IMPORTANT]  
> Phase 1 is complete and verified! Should we proceed immediately to execute **Phase 2** (Winning Economic Engine, Seasonal Crop Scheduler, Town Shop Arbitrage, and Livestock CARE Optimization)?
