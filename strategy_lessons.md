# Kaggriculture Strategy Lessons & Findings

During our recent cycles (15 and 16), we ran several experiments that initially seemed logical but ended up hurting the agent's performance. By analyzing the tournament data and reverting our mistakes, we uncovered crucial game mechanics that pushed our win rate to 43% ($102k median bank). 

Documenting these failed experiments ensures we don't repeat the same mistakes in future iterations.

## 1. The WHEAT Over-Planting Trap
**The Experiment:** 
We noticed the agent was spending a lot of money buying WHEAT grain to feed its Cows and Sheep. To save capital, we modified the agent to aggressively plant WHEAT whenever it had empty tiles, effectively using open space to grow free feed.

**Why it Failed (Win rate dropped to 9%):** 
While the agent saved about $4,000 on WHEAT feed purchases, it lost over $20,000 in STRAWBERRY and MELON revenue. WHEAT takes 4 days to harvest. By continuously planting WHEAT on empty tiles, the agent ended up occupying crucial farm space right before the "premium crop windows" (e.g., Day 7 for Strawberries). When the priority days arrived, the fields were full of growing WHEAT, and the agent couldn't plant the high-margin crops.

**The Fix:** 
We restricted WHEAT planting to a strict maximum of **7 WHEAT plants on the ground at any given time**, and only allowed it to be planted before Day 4 or after Day 17. This ensures we grow just enough WHEAT to kickstart our feed supply without ever blocking the fields during the critical STRAWBERRY/MELON seasons.

## 2. The Fertilizer Panic-Selling Mistake
**The Experiment:** 
In earlier iterations, the agent was programmed to immediately sell FERTILIZER to the town market to generate quick cash liquidity.

**Why it Failed:** 
Fertilizer sells for a decent price, but its true value is as a **yield multiplier** for STRAWBERRY and MELON. By selling the fertilizer, we got a tiny cash bump but sacrificed massive crop yields. In one test run, selling fertilizer generated ~$1,200 in revenue, but our STRAWBERRY revenue plummeted.

**The Fix:** 
We implemented a strict **hoarding rule**: the agent now refuses to sell FERTILIZER unless it has more than 40 units in the shed. By keeping the fertilizer and applying it to our premium crops, our STRAWBERRY revenue skyrocketed from ~$32k to over ~$46k per episode. The Cows and Sheep essentially act as free fertilizer factories.

## 3. The CARROT "Snowball" Illusion
**The Experiment:** 
After analyzing a top-performing $190k opponent ghost, we noticed it planted massive amounts of CARROTs on Days 0-3. We assumed this was a brilliant strategy to generate fast early-game liquidity (since Carrots harvest in just 3 days). We changed our agent to fill the fields with CARROT on Days 0-3.

**Why it Failed (Win rate dropped to 34%):** 
Our agent spent $500 on CARROT seeds and generated $1,500 in revenue (a $1,000 net profit). However, WHEAT seeds only cost $10 and sell for $25 (yielding 3 units), which is actually a much higher profit margin than CARROT. Furthermore, the CARROT harvest distracted our workers, leading to inefficiencies. The opponent ghost was likely using CARROTs for a specific, highly-timed land expansion strategy that our agent wasn't equipped to replicate perfectly.

**The Fix:** 
We immediately reverted the CARROT logic and went back to the timed WHEAT strategy, which proved to be significantly more stable and profitable for our specific worker allocation model.

## Summary for Future Development
- **Space > Feed:** Never sacrifice premium crop tiles to grow cheap animal feed. It is always better to pay the market price for WHEAT grain than to block a tile that could be growing a $230 STRAWBERRY.
- **Hoard Multipliers:** Items that boost the yield of high-margin products (like FERTILIZER) are almost always worth more when used than when sold.
- **Micro-manage the Early Game:** The decisions made on Days 0-5 dictate the capital available for the Day 7 STRAWBERRY window. Any changes to the early game must be strictly benchmarked against the Day 7 cash balance.
