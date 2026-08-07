# Kaggle Match Diagnostic Report

*Per-product sales are reconstructed from each turn's public money delta (exact accounting identity: money_after = money_before - buy_cost + sell_revenue), not from raw SELL order face value. Raw order quantities overstate revenue whenever an order exceeds available shed stock and silently fails. The per-turn total is exact; only the split across products sold in the same turn is approximated (weighted by that turn's SELL order notional).*

## Overall Dataset Summary
- **Total Analyzed Matches**: 79
- **Record**: 31 Wins / 48 Losses / 0 Draws (39.2% Win Rate)

## Top Opponents Leaderboard (Ranked by Max Bank Achieved)
| Opponent Name | Max Bank | Avg Bank | Matches | Opponent Wins | Our Wins |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **mohit** | $159,147.00 | $159,147.00 | 1 | 1 | 0 |
| **Ueddy** | $150,223.00 | $150,223.00 | 1 | 1 | 0 |
| **Desyat IO** | $147,599.00 | $147,599.00 | 1 | 1 | 0 |
| **Juyong** | $146,245.00 | $123,851.50 | 2 | 2 | 0 |
| **Mehdi Azouz** | $144,615.00 | $144,615.00 | 1 | 1 | 0 |
| **Dmitry Larko** | $144,116.00 | $144,116.00 | 1 | 1 | 0 |
| **MugaBros** | $141,992.00 | $141,992.00 | 1 | 1 | 0 |
| **Raggriculture** | $140,986.00 | $140,986.00 | 1 | 1 | 0 |
| **Junior Sohou** | $138,228.00 | $138,228.00 | 1 | 1 | 0 |
| **ömer kiraz** | $135,997.00 | $135,997.00 | 1 | 1 | 0 |
| **Sparsh389** | $132,351.00 | $95,677.67 | 3 | 2 | 1 |
| **Lugas024** | $130,889.00 | $130,889.00 | 1 | 0 | 1 |
| **eternitywinner** | $128,018.00 | $128,018.00 | 1 | 1 | 0 |
| **heinado** | $127,404.00 | $127,404.00 | 1 | 1 | 0 |
| **somewhere after** | $125,896.00 | $125,896.00 | 1 | 1 | 0 |
| **Emile Andrieu** | $125,735.00 | $125,735.00 | 1 | 1 | 0 |
| **Aleks Lviv** | $125,241.00 | $125,241.00 | 1 | 1 | 0 |
| **Pizzaboi** | $124,814.00 | $124,814.00 | 1 | 1 | 0 |
| **this is lsm** | $124,195.00 | $124,195.00 | 1 | 1 | 0 |
| **cobrapigeon** | $123,793.00 | $118,913.00 | 2 | 0 | 2 |
| **Leon Christians** | $123,385.00 | $123,385.00 | 1 | 1 | 0 |
| **CdeTilly** | $122,842.00 | $122,842.00 | 1 | 1 | 0 |
| **xlnt** | $122,767.00 | $122,767.00 | 1 | 1 | 0 |
| **Manifolds1** | $121,949.00 | $121,949.00 | 1 | 1 | 0 |
| **brainpick** | $121,468.00 | $121,468.00 | 1 | 1 | 0 |
| **Rahul Ray** | $120,579.00 | $120,579.00 | 1 | 1 | 0 |
| **Hira Norm** | $118,157.00 | $112,542.50 | 2 | 1 | 1 |
| **Max Manushin** | $118,099.00 | $118,099.00 | 1 | 1 | 0 |
| **D S S Kumar** | $115,388.00 | $115,388.00 | 1 | 1 | 0 |
| **KodamaSec Labs LTD** | $112,376.00 | $112,376.00 | 1 | 1 | 0 |
| **an Expired Engineer** | $110,162.00 | $110,162.00 | 1 | 0 | 1 |
| **Alpesh Kumar** | $110,156.00 | $110,156.00 | 1 | 1 | 0 |
| **Datta Dhebe** | $109,897.00 | $109,897.00 | 1 | 1 | 0 |
| **Xiaolei Lian** | $108,217.00 | $108,217.00 | 1 | 0 | 1 |
| **Quyền Thịnh** | $108,120.00 | $108,120.00 | 1 | 1 | 0 |
| **khan** | $107,743.00 | $107,743.00 | 1 | 0 | 1 |
| **Pascal** | $107,082.00 | $107,082.00 | 1 | 0 | 1 |
| **Gmmastermind** | $106,712.00 | $96,031.50 | 2 | 1 | 1 |
| **SIDHAARTH SHREE** | $106,155.00 | $94,279.00 | 2 | 0 | 2 |
| **yuto083** | $103,884.00 | $103,884.00 | 1 | 1 | 0 |
| **Kameron Green** | $103,123.00 | $101,609.50 | 2 | 0 | 2 |
| **Thomas** | $102,031.00 | $102,031.00 | 1 | 1 | 0 |
| **vlad101** | $100,262.00 | $100,262.00 | 1 | 1 | 0 |
| **Tergel Munkhbat** | $98,930.00 | $98,930.00 | 1 | 1 | 0 |
| **LGarcia10** | $98,434.00 | $98,434.00 | 1 | 1 | 0 |
| **BONPU👨‍🌾** | $98,227.00 | $98,227.00 | 1 | 1 | 0 |
| **Juan David Bolanos** | $98,198.00 | $78,362.00 | 2 | 0 | 2 |
| **Joseph Franck** | $98,057.00 | $98,057.00 | 1 | 0 | 1 |
| **yuki** | $97,872.00 | $97,872.00 | 1 | 0 | 1 |
| **sneaky6767** | $96,450.00 | $96,450.00 | 1 | 1 | 0 |
| **Abhishek Dubey** | $93,968.00 | $93,968.00 | 1 | 0 | 1 |
| **Haris Ahmed** | $93,370.00 | $93,370.00 | 1 | 1 | 0 |
| **Aman Vishwakarma** | $92,645.00 | $92,645.00 | 1 | 0 | 1 |
| **Sutee** | $92,645.00 | $92,645.00 | 1 | 1 | 0 |
| **HIDEYO CHIBA** | $92,457.00 | $92,457.00 | 1 | 1 | 0 |
| **George Byne** | $90,344.00 | $90,344.00 | 1 | 1 | 0 |
| **Tristan Peng** | $90,256.00 | $90,256.00 | 1 | 0 | 1 |
| **Roman Rozen** | $90,075.00 | $90,075.00 | 1 | 0 | 1 |
| **cameronezrajones579** | $87,013.00 | $87,013.00 | 1 | 0 | 1 |
| **m-toshi desu** | $84,682.00 | $84,682.00 | 1 | 0 | 1 |
| **Ian Kim** | $83,978.00 | $83,978.00 | 1 | 0 | 1 |
| **bhavya shah** | $78,612.00 | $78,612.00 | 1 | 1 | 0 |
| **Shuichi Fushimi** | $78,291.00 | $74,069.50 | 2 | 1 | 1 |
| **Hiroyasu Okuno** | $78,142.00 | $78,142.00 | 1 | 0 | 1 |
| **harmo-miu** | $73,091.00 | $73,091.00 | 1 | 0 | 1 |
| **Matt Motoki** | $60,890.00 | $60,890.00 | 1 | 0 | 1 |
| **Rohan Lopes** | $52,850.00 | $52,850.00 | 1 | 0 | 1 |
| **MarvelousXun** | $50,411.00 | $50,411.00 | 1 | 1 | 0 |
| **RacoonTW** | $46,087.00 | $46,087.00 | 1 | 0 | 1 |

---

## Detailed Match Diagnostics

### Match 90372802 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $107,097.00
- **Alpesh Kumar** (Opponent): $110,156.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $107,097.00 | $110,156.00 | $-3,059.00 |
| Max Workers | 13 | 13 | 0 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 9 | 0 |
| Sheep Purchased | 0 | 0 | 0 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,714.39 | $1,715.70 | $-1.31 |
| Sales: FERTILIZER | $15,842.67 | $10,541.33 | $5,301.34 |
| Sales: MELON | $24,868.75 | $25,593.10 | $-724.35 |
| Sales: MILK | $48,368.68 | $48,732.84 | $-364.16 |
| Sales: STRAWBERRY | $47,084.54 | $49,750.53 | $-2,665.99 |
| Sales: WHEAT | $7,972.96 | $6,923.50 | $1,049.46 |

**Key Loss Factors Identified:**
- Difference in general pacing or price optimization (selling at better market peaks).

---

### Match 90374109 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $132,124.00
- **RacoonTW** (Opponent): $46,087.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $132,124.00 | $46,087.00 | $86,037.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 13 | -4 |
| Sheep Purchased | 0 | 7 | -7 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,167.18 | $0.00 | $2,167.18 |
| Sales: FERTILIZER | $11,996.04 | $11,016.21 | $979.84 |
| Sales: MELON | $30,117.55 | $14,308.15 | $15,809.40 |
| Sales: MILK | $46,884.20 | $32,090.05 | $14,794.14 |
| Sales: STRAWBERRY | $67,243.19 | $7,849.64 | $59,393.56 |
| Sales: WHEAT | $11,027.83 | $51,348.24 | $-40,320.41 |
| Sales: WOOL | $0.00 | $16,356.71 | $-16,356.71 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 12), giving us labor superiority.
- We outperformed on MELON sales by $15,809.40.
- We outperformed on STRAWBERRY sales by $59,393.56.
- We outperformed on MILK sales by $14,794.14.

---

### Match 90374838 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $130,667.00
- **Rohan Lopes** (Opponent): $52,850.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $130,667.00 | $52,850.00 | $77,817.00 |
| Max Workers | 13 | 7 | 6 |
| Land Purchases | 2 | 1 | 1 |
| Cows Purchased | 9 | 3 | 6 |
| Sheep Purchased | 0 | 0 | 0 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,015.63 | $1,097.78 | $917.85 |
| Sales: FERTILIZER | $15,325.16 | $4,150.15 | $11,175.01 |
| Sales: MELON | $27,061.02 | $15,467.20 | $11,593.82 |
| Sales: MILK | $44,398.72 | $21,069.54 | $23,329.18 |
| Sales: STRAWBERRY | $73,587.07 | $20,674.28 | $52,912.79 |
| Sales: WHEAT | $6,799.40 | $781.06 | $6,018.35 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 7), giving us labor superiority.
- We invested more in Cows (9 vs 3), yielding higher Milk revenues.
- We outperformed on MELON sales by $11,593.82.
- We outperformed on STRAWBERRY sales by $52,912.79.
- We outperformed on MILK sales by $23,329.18.

---

### Match 90375569 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $90,692.00
- **Hiroyasu Okuno** (Opponent): $78,142.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $90,692.00 | $78,142.00 | $12,550.00 |
| Max Workers | 13 | 11 | 2 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 8 | 5 | 3 |
| Sheep Purchased | 0 | 83 | -83 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,981.29 | $0.00 | $1,981.29 |
| Sales: EGG | $0.00 | $7,760.14 | $-7,760.14 |
| Sales: FERTILIZER | $8,429.08 | $27,644.00 | $-19,214.92 |
| Sales: MELON | $27,731.87 | $23,563.52 | $4,168.36 |
| Sales: MILK | $28,499.76 | $17,627.94 | $10,871.82 |
| Sales: STRAWBERRY | $48,072.23 | $14,314.48 | $33,757.75 |
| Sales: WHEAT | $10,385.76 | $3,521.00 | $6,864.76 |
| Sales: WOOL | $0.00 | $24,765.92 | $-24,765.92 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 11), giving us labor superiority.
- We invested more in Cows (8 vs 5), yielding higher Milk revenues.
- We outperformed on STRAWBERRY sales by $33,757.75.
- We outperformed on MILK sales by $10,871.82.

---

### Match 90377057 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $101,361.00
- **Ian Kim** (Opponent): $83,978.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $101,361.00 | $83,978.00 | $17,383.00 |
| Max Workers | 13 | 10 | 3 |
| Land Purchases | 2 | 1 | 1 |
| Cows Purchased | 9 | 10 | -1 |
| Sheep Purchased | 0 | 3 | -3 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,271.34 | $1,863.17 | $408.17 |
| Sales: FERTILIZER | $9,475.62 | $17,259.41 | $-7,783.78 |
| Sales: MELON | $23,270.97 | $24,126.31 | $-855.33 |
| Sales: MILK | $29,805.31 | $40,693.53 | $-10,888.21 |
| Sales: STRAWBERRY | $63,702.74 | $0.00 | $63,702.74 |
| Sales: WHEAT | $9,049.01 | $28,421.25 | $-19,372.24 |
| Sales: WOOL | $0.00 | $23,099.34 | $-23,099.34 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 10), giving us labor superiority.
- We outperformed on STRAWBERRY sales by $63,702.74.

---

### Match 90377788 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $107,911.00
- **Abhishek Dubey** (Opponent): $93,968.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $107,911.00 | $93,968.00 | $13,943.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 8 | 3 | 5 |
| Sheep Purchased | 0 | 1 | -1 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,309.70 | $363.48 | $1,946.21 |
| Sales: FERTILIZER | $16,170.77 | $8,166.64 | $8,004.13 |
| Sales: MELON | $11,974.15 | $32,683.10 | $-20,708.95 |
| Sales: MILK | $53,994.23 | $22,801.74 | $31,192.49 |
| Sales: STRAWBERRY | $52,743.71 | $36,429.97 | $16,313.75 |
| Sales: WHEAT | $10,733.43 | $7,018.70 | $3,714.73 |
| Sales: WOOL | $0.00 | $7,619.36 | $-7,619.36 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 12), giving us labor superiority.
- We invested more in Cows (8 vs 3), yielding higher Milk revenues.
- We outperformed on STRAWBERRY sales by $16,313.75.
- We outperformed on MILK sales by $31,192.49.

---

### Match 90378554 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $101,230.00
- **Mehdi Azouz** (Opponent): $144,615.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $101,230.00 | $144,615.00 | $-43,385.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 9 | 0 |
| Sheep Purchased | 0 | 8 | -8 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,088.13 | $0.00 | $2,088.13 |
| Sales: FERTILIZER | $8,868.65 | $14,281.61 | $-5,412.96 |
| Sales: MELON | $20,597.24 | $27,964.04 | $-7,366.80 |
| Sales: MILK | $38,988.89 | $33,425.88 | $5,563.02 |
| Sales: STRAWBERRY | $52,309.31 | $64,109.53 | $-11,800.22 |
| Sales: WHEAT | $10,394.78 | $2,300.62 | $8,094.16 |
| Sales: WOOL | $0.00 | $33,623.32 | $-33,623.32 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (8 vs 0), yielding higher Wool revenues.
- Opponent outperformed on MELON sales by $7,366.80.
- Opponent outperformed on STRAWBERRY sales by $11,800.22.
- Opponent outperformed on WOOL sales by $33,623.32.

---

### Match 90378529 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $99,167.00
- **Manifolds1** (Opponent): $121,949.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $99,167.00 | $121,949.00 | $-22,782.00 |
| Max Workers | 13 | 11 | 2 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 8 | 1 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,623.61 | $151.44 | $2,472.17 |
| Sales: FERTILIZER | $9,710.82 | $15,157.58 | $-5,446.76 |
| Sales: MELON | $27,288.00 | $22,280.24 | $5,007.76 |
| Sales: MILK | $38,382.60 | $36,840.08 | $1,542.52 |
| Sales: STRAWBERRY | $44,853.03 | $41,809.50 | $3,043.53 |
| Sales: WHEAT | $9,495.94 | $23,768.69 | $-14,272.75 |
| Sales: WOOL | $0.00 | $30,329.47 | $-30,329.47 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (6 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $30,329.47.

---

### Match 90378575 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $101,640.00
- **Juyong** (Opponent): $146,245.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $101,640.00 | $146,245.00 | $-44,605.00 |
| Max Workers | 13 | 14 | -1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 6 | 3 |
| Sheep Purchased | 0 | 11 | -11 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,088.26 | $0.00 | $2,088.26 |
| Sales: FERTILIZER | $16,584.76 | $14,821.24 | $1,763.53 |
| Sales: MELON | $19,290.49 | $25,676.50 | $-6,386.02 |
| Sales: MILK | $43,495.07 | $34,978.55 | $8,516.52 |
| Sales: STRAWBERRY | $51,086.16 | $51,360.16 | $-274.00 |
| Sales: WHEAT | $9,457.26 | $40,484.04 | $-31,026.78 |
| Sales: WOOL | $0.00 | $50,988.51 | $-50,988.51 |

**Key Loss Factors Identified:**
- Opponent hired more workers, indicating we might be under-hiring or expanding too slowly.
- Opponent bought more Sheep (11 vs 0), yielding higher Wool revenues.
- Opponent outperformed on MELON sales by $6,386.02.
- Opponent outperformed on WOOL sales by $50,988.51.

---

### Match 90379336 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $108,366.00
- **khan** (Opponent): $107,743.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $108,366.00 | $107,743.00 | $623.00 |
| Max Workers | 13 | 13 | 0 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 9 | 0 |
| Sheep Purchased | 0 | 4 | -4 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,990.11 | $0.00 | $1,990.11 |
| Sales: EGG | $0.00 | $3,381.30 | $-3,381.30 |
| Sales: FERTILIZER | $13,516.94 | $14,415.22 | $-898.28 |
| Sales: MELON | $22,428.17 | $28,260.39 | $-5,832.22 |
| Sales: MILK | $43,386.79 | $33,495.38 | $9,891.41 |
| Sales: STRAWBERRY | $58,443.29 | $42,713.86 | $15,729.44 |
| Sales: WHEAT | $6,624.69 | $1,342.41 | $5,282.28 |
| Sales: WOOL | $0.00 | $19,372.44 | $-19,372.44 |

**Key Win Factors Identified:**
- We outperformed on STRAWBERRY sales by $15,729.44.
- We outperformed on MILK sales by $9,891.41.

---

### Match 90380092 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $101,953.00
- **Rahul Ray** (Opponent): $120,579.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $101,953.00 | $120,579.00 | $-18,626.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 8 | 10 | -2 |
| Sheep Purchased | 0 | 8 | -8 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,085.74 | $0.00 | $2,085.74 |
| Sales: FERTILIZER | $16,955.95 | $15,738.85 | $1,217.09 |
| Sales: MELON | $26,287.53 | $20,347.43 | $5,940.10 |
| Sales: MILK | $31,965.29 | $34,218.01 | $-2,252.73 |
| Sales: STRAWBERRY | $54,705.40 | $42,648.80 | $12,056.59 |
| Sales: WHEAT | $9,751.10 | $26,291.70 | $-16,540.60 |
| Sales: WOOL | $0.00 | $37,597.20 | $-37,597.20 |

**Key Loss Factors Identified:**
- Opponent invested more in Cows (10 vs 8), yielding higher Milk revenues.
- Opponent bought more Sheep (8 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $37,597.20.

---

### Match 90380861 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $109,589.00
- **cameronezrajones579** (Opponent): $87,013.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $109,589.00 | $87,013.00 | $22,576.00 |
| Max Workers | 13 | 9 | 4 |
| Land Purchases | 2 | 1 | 1 |
| Cows Purchased | 9 | 51 | -42 |
| Sheep Purchased | 0 | 231 | -231 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,850.53 | $0.00 | $1,850.53 |
| Sales: FERTILIZER | $10,589.63 | $15,777.66 | $-5,188.03 |
| Sales: MELON | $23,272.21 | $29,432.76 | $-6,160.55 |
| Sales: MILK | $41,309.01 | $34,268.55 | $7,040.47 |
| Sales: STRAWBERRY | $62,161.66 | $0.00 | $62,161.66 |
| Sales: WHEAT | $5,410.97 | $1,344.00 | $4,066.97 |
| Sales: WOOL | $0.00 | $28,518.03 | $-28,518.03 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 9), giving us labor superiority.
- We outperformed on STRAWBERRY sales by $62,161.66.
- We outperformed on MILK sales by $7,040.47.

---

### Match 90381619 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $98,930.00
- **SIDHAARTH SHREE** (Opponent): $82,403.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $98,930.00 | $82,403.00 | $16,527.00 |
| Max Workers | 13 | 10 | 3 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 7 | 2 |
| Sheep Purchased | 0 | 8 | -8 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,124.80 | $0.00 | $2,124.80 |
| Sales: FERTILIZER | $10,615.36 | $13,628.90 | $-3,013.54 |
| Sales: MELON | $29,415.51 | $20,718.79 | $8,696.72 |
| Sales: MILK | $27,562.67 | $26,590.54 | $972.13 |
| Sales: STRAWBERRY | $54,423.62 | $13,845.95 | $40,577.67 |
| Sales: WHEAT | $8,228.05 | $1,899.00 | $6,329.05 |
| Sales: WOOL | $0.00 | $36,385.82 | $-36,385.82 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 10), giving us labor superiority.
- We invested more in Cows (9 vs 7), yielding higher Milk revenues.
- We outperformed on MELON sales by $8,696.72.
- We outperformed on STRAWBERRY sales by $40,577.67.

---

### Match 90383119 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $97,251.00
- **Tristan Peng** (Opponent): $90,256.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $97,251.00 | $90,256.00 | $6,995.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 3 | -1 |
| Cows Purchased | 8 | 10 | -2 |
| Sheep Purchased | 0 | 10 | -10 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,161.05 | $5,705.73 | $-3,544.68 |
| Sales: FERTILIZER | $12,569.92 | $16,959.19 | $-4,389.28 |
| Sales: MELON | $25,761.97 | $21,422.35 | $4,339.62 |
| Sales: MILK | $27,193.30 | $25,053.31 | $2,139.99 |
| Sales: STRAWBERRY | $56,761.52 | $17,514.09 | $39,247.42 |
| Sales: WHEAT | $9,206.25 | $18,826.58 | $-9,620.34 |
| Sales: WOOL | $0.00 | $38,762.74 | $-38,762.74 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 12), giving us labor superiority.
- We outperformed on STRAWBERRY sales by $39,247.42.

---

### Match 90384632 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $79,481.00
- **Matt Motoki** (Opponent): $60,890.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $79,481.00 | $60,890.00 | $18,591.00 |
| Max Workers | 13 | 14 | -1 |
| Land Purchases | 2 | 3 | -1 |
| Cows Purchased | 8 | 14 | -6 |
| Sheep Purchased | 0 | 14 | -14 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,985.08 | $0.00 | $1,985.08 |
| Sales: FERTILIZER | $11,346.24 | $14,332.35 | $-2,986.12 |
| Sales: MELON | $22,196.88 | $22,226.78 | $-29.91 |
| Sales: MILK | $20,901.32 | $20,157.02 | $744.30 |
| Sales: STRAWBERRY | $46,509.57 | $20,502.61 | $26,006.96 |
| Sales: WHEAT | $10,832.92 | $22,501.59 | $-11,668.67 |
| Sales: WOOL | $0.00 | $43,789.65 | $-43,789.65 |

**Key Win Factors Identified:**
- We outperformed on STRAWBERRY sales by $26,006.96.

---

### Match 90410835 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $114,374.00
- **an Expired Engineer** (Opponent): $110,162.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $114,374.00 | $110,162.00 | $4,212.00 |
| Max Workers | 13 | 10 | 3 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 12 | -3 |
| Sheep Purchased | 0 | 0 | 0 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,010.67 | $0.00 | $2,010.67 |
| Sales: FERTILIZER | $12,688.27 | $11,818.38 | $869.90 |
| Sales: MELON | $21,701.75 | $26,651.30 | $-4,949.55 |
| Sales: MILK | $41,191.46 | $58,518.76 | $-17,327.30 |
| Sales: STRAWBERRY | $66,451.18 | $27,274.81 | $39,176.37 |
| Sales: WHEAT | $8,871.67 | $6,985.76 | $1,885.92 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 10), giving us labor superiority.
- We outperformed on STRAWBERRY sales by $39,176.37.

---

### Match 90420469 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $92,911.00
- **Thomas** (Opponent): $102,031.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $92,911.00 | $102,031.00 | $-9,120.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 3 | -1 |
| Cows Purchased | 8 | 11 | -3 |
| Sheep Purchased | 0 | 7 | -7 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,983.50 | $0.00 | $1,983.50 |
| Sales: EGG | $0.00 | $4,124.38 | $-4,124.38 |
| Sales: FERTILIZER | $10,464.19 | $17,137.47 | $-6,673.28 |
| Sales: MELON | $28,961.48 | $22,112.41 | $6,849.08 |
| Sales: MILK | $25,610.65 | $24,476.79 | $1,133.86 |
| Sales: STRAWBERRY | $57,143.02 | $25,038.86 | $32,104.16 |
| Sales: TOMATO | $0.00 | $2,439.49 | $-2,439.49 |
| Sales: WHEAT | $6,882.16 | $18,830.29 | $-11,948.13 |
| Sales: WOOL | $0.00 | $39,528.32 | $-39,528.32 |

**Key Loss Factors Identified:**
- Opponent invested more in Cows (11 vs 8), yielding higher Milk revenues.
- Opponent bought more Sheep (7 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $39,528.32.

---

### Match 90444753 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $71,604.00
- **eternitywinner** (Opponent): $128,018.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $71,604.00 | $128,018.00 | $-56,414.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 8 | 6 | 2 |
| Sheep Purchased | 0 | 10 | -10 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,946.95 | $0.00 | $1,946.95 |
| Sales: FERTILIZER | $8,834.43 | $14,478.55 | $-5,644.13 |
| Sales: MELON | $19,776.00 | $24,098.69 | $-4,322.69 |
| Sales: MILK | $16,587.89 | $17,073.58 | $-485.69 |
| Sales: STRAWBERRY | $46,215.79 | $57,385.12 | $-11,169.34 |
| Sales: WHEAT | $7,917.94 | $10,003.76 | $-2,085.82 |
| Sales: WOOL | $0.00 | $38,857.29 | $-38,857.29 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (10 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $11,169.34.
- Opponent outperformed on WOOL sales by $38,857.29.

---

### Match 90445447 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $101,945.00
- **xlnt** (Opponent): $122,767.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $101,945.00 | $122,767.00 | $-20,822.00 |
| Max Workers | 13 | 13 | 0 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 3 | 6 |
| Sheep Purchased | 0 | 12 | -12 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,568.63 | $573.41 | $995.22 |
| Sales: FERTILIZER | $10,316.09 | $15,708.51 | $-5,392.42 |
| Sales: MELON | $23,052.61 | $21,910.91 | $1,141.70 |
| Sales: MILK | $44,432.52 | $20,461.62 | $23,970.90 |
| Sales: STRAWBERRY | $47,168.33 | $58,692.91 | $-11,524.58 |
| Sales: WHEAT | $7,278.82 | $59,522.37 | $-52,243.55 |
| Sales: WOOL | $0.00 | $38,722.27 | $-38,722.27 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (12 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $11,524.58.
- Opponent outperformed on WOOL sales by $38,722.27.

---

### Match 90448504 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $138,598.00
- **Lugas024** (Opponent): $130,889.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $138,598.00 | $130,889.00 | $7,709.00 |
| Max Workers | 13 | 10 | 3 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 6 | 3 |
| Sheep Purchased | 0 | 9 | -9 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,812.24 | $2,070.11 | $-257.87 |
| Sales: FERTILIZER | $13,071.94 | $12,810.62 | $261.32 |
| Sales: MELON | $26,770.64 | $20,885.39 | $5,885.25 |
| Sales: MILK | $55,085.04 | $35,857.49 | $19,227.55 |
| Sales: STRAWBERRY | $72,276.15 | $44,066.19 | $28,209.96 |
| Sales: WHEAT | $9,057.99 | $3,427.18 | $5,630.81 |
| Sales: WOOL | $0.00 | $43,596.02 | $-43,596.02 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 10), giving us labor superiority.
- We invested more in Cows (9 vs 6), yielding higher Milk revenues.
- We outperformed on MELON sales by $5,885.25.
- We outperformed on STRAWBERRY sales by $28,209.96.
- We outperformed on MILK sales by $19,227.55.

---

### Match 90468587 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $74,249.00
- **Sparsh389** (Opponent): $72,007.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $74,249.00 | $72,007.00 | $2,242.00 |
| Max Workers | 13 | 14 | -1 |
| Land Purchases | 2 | 3 | -1 |
| Cows Purchased | 9 | 8 | 1 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,697.20 | $1,363.39 | $333.81 |
| Sales: FERTILIZER | $15,119.10 | $13,324.59 | $1,794.50 |
| Sales: MELON | $20,447.78 | $24,900.37 | $-4,452.59 |
| Sales: MILK | $11,947.12 | $15,592.74 | $-3,645.61 |
| Sales: STRAWBERRY | $50,309.14 | $30,710.04 | $19,599.10 |
| Sales: WHEAT | $10,386.67 | $2,393.32 | $7,993.36 |
| Sales: WOOL | $0.00 | $26,718.56 | $-26,718.56 |

**Key Win Factors Identified:**
- We invested more in Cows (9 vs 8), yielding higher Milk revenues.
- We outperformed on STRAWBERRY sales by $19,599.10.

---

### Match 90481425 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $127,942.00
- **Aman Vishwakarma** (Opponent): $92,645.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $127,942.00 | $92,645.00 | $35,297.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 8 | 8 | 0 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,806.54 | $0.00 | $1,806.54 |
| Sales: FERTILIZER | $10,548.15 | $12,970.98 | $-2,422.83 |
| Sales: MELON | $32,330.63 | $15,435.01 | $16,895.63 |
| Sales: MILK | $55,327.84 | $40,604.89 | $14,722.96 |
| Sales: STRAWBERRY | $52,845.61 | $21,817.03 | $31,028.58 |
| Sales: TOMATO | $0.00 | $26.01 | $-26.01 |
| Sales: WHEAT | $7,716.22 | $29,610.70 | $-21,894.48 |
| Sales: WOOL | $0.00 | $31,577.39 | $-31,577.39 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 12), giving us labor superiority.
- We outperformed on MELON sales by $16,895.63.
- We outperformed on STRAWBERRY sales by $31,028.58.
- We outperformed on MILK sales by $14,722.96.

---

### Match 90502078 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $89,887.00
- **Haris Ahmed** (Opponent): $93,370.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $89,887.00 | $93,370.00 | $-3,483.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 5 | 4 |
| Sheep Purchased | 0 | 3 | -3 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,370.52 | $0.00 | $2,370.52 |
| Sales: EGG | $0.00 | $2,177.02 | $-2,177.02 |
| Sales: FERTILIZER | $8,974.47 | $9,809.71 | $-835.24 |
| Sales: MELON | $26,668.19 | $20,405.60 | $6,262.58 |
| Sales: MILK | $23,050.39 | $17,555.65 | $5,494.74 |
| Sales: STRAWBERRY | $53,669.67 | $46,101.07 | $7,568.60 |
| Sales: WHEAT | $7,115.76 | $77,922.21 | $-70,806.45 |
| Sales: WOOL | $0.00 | $19,021.74 | $-19,021.74 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (3 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $19,021.74.

---

### Match 90532809 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $75,010.00
- **Shuichi Fushimi** (Opponent): $78,291.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $75,010.00 | $78,291.00 | $-3,281.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 11 | -2 |
| Sheep Purchased | 0 | 2 | -2 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,124.90 | $0.00 | $2,124.90 |
| Sales: FERTILIZER | $8,703.31 | $9,824.39 | $-1,121.08 |
| Sales: MELON | $25,987.88 | $21,712.01 | $4,275.87 |
| Sales: MILK | $13,664.62 | $13,180.67 | $483.95 |
| Sales: STRAWBERRY | $47,993.58 | $44,164.29 | $3,829.29 |
| Sales: WHEAT | $5,825.71 | $6,874.23 | $-1,048.52 |
| Sales: WOOL | $0.00 | $14,362.41 | $-14,362.41 |

**Key Loss Factors Identified:**
- Opponent invested more in Cows (11 vs 9), yielding higher Milk revenues.
- Opponent bought more Sheep (2 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $14,362.41.

---

### Match 90541328 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $108,064.00
- **Hira Norm** (Opponent): $106,928.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $108,064.00 | $106,928.00 | $1,136.00 |
| Max Workers | 13 | 11 | 2 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 6 | 4 |
| Sheep Purchased | 0 | 5 | -5 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,027.99 | $505.75 | $1,522.24 |
| Sales: FERTILIZER | $14,562.47 | $10,260.02 | $4,302.45 |
| Sales: MELON | $30,270.62 | $18,330.33 | $11,940.30 |
| Sales: MILK | $47,869.76 | $35,426.06 | $12,443.71 |
| Sales: STRAWBERRY | $41,588.12 | $44,269.07 | $-2,680.95 |
| Sales: WHEAT | $8,006.04 | $3,311.23 | $4,694.81 |
| Sales: WOOL | $0.00 | $21,013.55 | $-21,013.55 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 11), giving us labor superiority.
- We invested more in Cows (10 vs 6), yielding higher Milk revenues.
- We outperformed on MELON sales by $11,940.30.
- We outperformed on MILK sales by $12,443.71.

---

### Match 90564673 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $94,063.00
- **mohit** (Opponent): $159,147.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $94,063.00 | $159,147.00 | $-65,084.00 |
| Max Workers | 13 | 14 | -1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 8 | 8 | 0 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,324.69 | $0.00 | $2,324.69 |
| Sales: FERTILIZER | $16,024.62 | $11,074.66 | $4,949.96 |
| Sales: MELON | $21,639.28 | $25,365.09 | $-3,725.81 |
| Sales: MILK | $51,259.79 | $57,188.70 | $-5,928.90 |
| Sales: STRAWBERRY | $34,893.90 | $49,780.56 | $-14,886.66 |
| Sales: WHEAT | $3,213.72 | $32,839.54 | $-29,625.83 |
| Sales: WOOL | $0.00 | $40,554.45 | $-40,554.45 |

**Key Loss Factors Identified:**
- Opponent hired more workers, indicating we might be under-hiring or expanding too slowly.
- Opponent bought more Sheep (6 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $14,886.66.
- Opponent outperformed on MILK sales by $5,928.90.
- Opponent outperformed on WOOL sales by $40,554.45.

---

### Match 90568623 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $114,095.00
- **Kameron Green** (Opponent): $100,096.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $114,095.00 | $100,096.00 | $13,999.00 |
| Max Workers | 13 | 14 | -1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 8 | 1 |
| Sheep Purchased | 0 | 7 | -7 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,386.84 | $0.00 | $2,386.84 |
| Sales: FERTILIZER | $8,371.93 | $11,161.05 | $-2,789.13 |
| Sales: MELON | $25,740.59 | $20,887.89 | $4,852.70 |
| Sales: MILK | $38,701.52 | $38,251.72 | $449.79 |
| Sales: STRAWBERRY | $60,821.28 | $47,232.19 | $13,589.10 |
| Sales: WHEAT | $9,372.84 | $4,233.20 | $5,139.64 |
| Sales: WOOL | $0.00 | $23,177.95 | $-23,177.95 |

**Key Win Factors Identified:**
- We invested more in Cows (9 vs 8), yielding higher Milk revenues.
- We outperformed on STRAWBERRY sales by $13,589.10.

---

### Match 90575592 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $94,340.00
- **Leon Christians** (Opponent): $123,385.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $94,340.00 | $123,385.00 | $-29,045.00 |
| Max Workers | 13 | 10 | 3 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 6 | 3 |
| Sheep Purchased | 0 | 10 | -10 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,793.56 | $207.00 | $1,586.56 |
| Sales: FERTILIZER | $8,726.32 | $16,505.44 | $-7,779.13 |
| Sales: MELON | $32,526.62 | $8,137.03 | $24,389.59 |
| Sales: MILK | $24,000.40 | $18,866.79 | $5,133.60 |
| Sales: STRAWBERRY | $52,743.23 | $53,206.87 | $-463.64 |
| Sales: WHEAT | $4,846.87 | $1,227.06 | $3,619.81 |
| Sales: WOOL | $0.00 | $58,203.80 | $-58,203.80 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (10 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $58,203.80.

---

### Match 90575599 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $126,512.00
- **cobrapigeon** (Opponent): $123,793.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $126,512.00 | $123,793.00 | $2,719.00 |
| Max Workers | 13 | 10 | 3 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 5 | 4 |
| Sheep Purchased | 0 | 4 | -4 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,186.64 | $0.00 | $2,186.64 |
| Sales: FERTILIZER | $11,364.53 | $15,281.92 | $-3,917.40 |
| Sales: MELON | $26,402.03 | $23,779.49 | $2,622.54 |
| Sales: MILK | $51,175.15 | $34,846.10 | $16,329.05 |
| Sales: STRAWBERRY | $61,566.16 | $41,123.37 | $20,442.79 |
| Sales: WHEAT | $3,033.48 | $14,546.11 | $-11,512.63 |
| Sales: WOOL | $0.00 | $20,030.99 | $-20,030.99 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 10), giving us labor superiority.
- We invested more in Cows (9 vs 5), yielding higher Milk revenues.
- We outperformed on STRAWBERRY sales by $20,442.79.
- We outperformed on MILK sales by $16,329.05.

---

### Match 90581743 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $78,846.00
- **Juan David Bolanos** (Opponent): $58,526.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $78,846.00 | $58,526.00 | $20,320.00 |
| Max Workers | 13 | 9 | 4 |
| Land Purchases | 2 | 3 | -1 |
| Cows Purchased | 9 | 9 | 0 |
| Sheep Purchased | 0 | 3 | -3 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,099.31 | $1,847.41 | $251.90 |
| Sales: EGG | $0.00 | $5,469.84 | $-5,469.84 |
| Sales: FERTILIZER | $10,994.92 | $11,530.36 | $-535.44 |
| Sales: MELON | $24,884.55 | $18,916.45 | $5,968.10 |
| Sales: MILK | $18,517.00 | $18,886.85 | $-369.85 |
| Sales: STRAWBERRY | $46,129.62 | $0.00 | $46,129.62 |
| Sales: WHEAT | $6,563.59 | $16,180.74 | $-9,617.15 |
| Sales: WOOL | $0.00 | $5,351.34 | $-5,351.34 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 9), giving us labor superiority.
- We outperformed on MELON sales by $5,968.10.
- We outperformed on STRAWBERRY sales by $46,129.62.

---

### Match 90588952 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $134,252.00
- **Kameron Green** (Opponent): $103,123.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $134,252.00 | $103,123.00 | $31,129.00 |
| Max Workers | 13 | 14 | -1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 8 | 5 | 3 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,114.54 | $0.00 | $2,114.54 |
| Sales: FERTILIZER | $13,195.96 | $10,210.85 | $2,985.11 |
| Sales: MELON | $26,695.08 | $23,345.41 | $3,349.67 |
| Sales: MILK | $50,661.49 | $34,936.07 | $15,725.42 |
| Sales: STRAWBERRY | $69,978.98 | $39,518.18 | $30,460.80 |
| Sales: WHEAT | $4,176.95 | $6,285.07 | $-2,108.13 |
| Sales: WOOL | $0.00 | $30,232.42 | $-30,232.42 |

**Key Win Factors Identified:**
- We invested more in Cows (8 vs 5), yielding higher Milk revenues.
- We outperformed on STRAWBERRY sales by $30,460.80.
- We outperformed on MILK sales by $15,725.42.

---

### Match 90592039 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $80,053.00
- **Gmmastermind** (Opponent): $85,351.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $80,053.00 | $85,351.00 | $-5,298.00 |
| Max Workers | 13 | 9 | 4 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 8 | 1 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,188.01 | $0.00 | $2,188.01 |
| Sales: FERTILIZER | $8,365.08 | $13,999.43 | $-5,634.35 |
| Sales: MELON | $24,075.20 | $17,312.00 | $6,763.19 |
| Sales: MILK | $19,214.79 | $14,190.02 | $5,024.77 |
| Sales: STRAWBERRY | $47,957.89 | $32,879.62 | $15,078.26 |
| Sales: WHEAT | $4,220.04 | $6,131.23 | $-1,911.19 |
| Sales: WOOL | $0.00 | $35,313.70 | $-35,313.70 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (6 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $35,313.70.

---

### Match 90631265 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $114,820.00
- **Gmmastermind** (Opponent): $106,712.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $114,820.00 | $106,712.00 | $8,108.00 |
| Max Workers | 13 | 9 | 4 |
| Land Purchases | 2 | 3 | -1 |
| Cows Purchased | 9 | 8 | 1 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,137.40 | $0.00 | $2,137.40 |
| Sales: FERTILIZER | $8,714.67 | $16,887.75 | $-8,173.08 |
| Sales: MELON | $23,509.96 | $20,988.27 | $2,521.69 |
| Sales: MILK | $47,334.44 | $41,254.01 | $6,080.43 |
| Sales: STRAWBERRY | $56,967.75 | $22,626.79 | $34,340.96 |
| Sales: WHEAT | $3,934.77 | $2,118.12 | $1,816.66 |
| Sales: WOOL | $0.00 | $33,981.07 | $-33,981.07 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 9), giving us labor superiority.
- We invested more in Cows (9 vs 8), yielding higher Milk revenues.
- We outperformed on STRAWBERRY sales by $34,340.96.
- We outperformed on MILK sales by $6,080.43.

---

### Match 90638196 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $132,799.00
- **Juan David Bolanos** (Opponent): $98,198.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $132,799.00 | $98,198.00 | $34,601.00 |
| Max Workers | 13 | 9 | 4 |
| Land Purchases | 2 | 1 | 1 |
| Cows Purchased | 9 | 11 | -2 |
| Sheep Purchased | 0 | 0 | 0 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,086.91 | $961.53 | $1,125.38 |
| Sales: EGG | $0.00 | $3,818.40 | $-3,818.40 |
| Sales: FERTILIZER | $11,770.32 | $13,586.90 | $-1,816.57 |
| Sales: MELON | $24,595.34 | $21,047.01 | $3,548.33 |
| Sales: MILK | $48,937.49 | $57,827.46 | $-8,889.97 |
| Sales: STRAWBERRY | $72,063.35 | $0.00 | $72,063.35 |
| Sales: WHEAT | $7,043.59 | $12,971.70 | $-5,928.11 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 9), giving us labor superiority.
- We outperformed on STRAWBERRY sales by $72,063.35.

---

### Match 90638389 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $122,507.00
- **cobrapigeon** (Opponent): $114,033.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $122,507.00 | $114,033.00 | $8,474.00 |
| Max Workers | 13 | 13 | 0 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 5 | 4 |
| Sheep Purchased | 0 | 3 | -3 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,248.17 | $0.00 | $2,248.17 |
| Sales: FERTILIZER | $10,501.14 | $7,133.82 | $3,367.32 |
| Sales: MELON | $29,522.53 | $22,661.37 | $6,861.16 |
| Sales: MILK | $54,010.38 | $38,415.78 | $15,594.60 |
| Sales: STRAWBERRY | $49,781.32 | $37,185.17 | $12,596.15 |
| Sales: WHEAT | $4,776.45 | $24,432.37 | $-19,655.92 |
| Sales: WOOL | $0.00 | $21,312.49 | $-21,312.49 |

**Key Win Factors Identified:**
- We invested more in Cows (9 vs 5), yielding higher Milk revenues.
- We outperformed on MELON sales by $6,861.16.
- We outperformed on STRAWBERRY sales by $12,596.15.
- We outperformed on MILK sales by $15,594.60.

---

### Match 90638985 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $92,488.00
- **Quyền Thịnh** (Opponent): $108,120.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $92,488.00 | $108,120.00 | $-15,632.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 9 | 0 |
| Sheep Purchased | 0 | 7 | -7 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,947.95 | $727.40 | $1,220.55 |
| Sales: FERTILIZER | $9,243.73 | $13,189.36 | $-3,945.63 |
| Sales: MELON | $23,130.24 | $28,683.69 | $-5,553.45 |
| Sales: MILK | $34,173.67 | $35,708.74 | $-1,535.06 |
| Sales: STRAWBERRY | $43,938.93 | $30,685.10 | $13,253.82 |
| Sales: TOMATO | $0.00 | $898.76 | $-898.76 |
| Sales: WHEAT | $6,293.48 | $3,959.96 | $2,333.52 |
| Sales: WOOL | $0.00 | $31,570.00 | $-31,570.00 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (7 vs 0), yielding higher Wool revenues.
- Opponent outperformed on MELON sales by $5,553.45.
- Opponent outperformed on WOOL sales by $31,570.00.

---

### Match 90650178 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $122,481.00
- **Pizzaboi** (Opponent): $124,814.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $122,481.00 | $124,814.00 | $-2,333.00 |
| Max Workers | 13 | 13 | 0 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 10 | -1 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,824.70 | $2,925.52 | $-1,100.82 |
| Sales: FERTILIZER | $8,271.85 | $17,550.07 | $-9,278.22 |
| Sales: MELON | $24,400.65 | $19,457.65 | $4,943.00 |
| Sales: MILK | $47,202.25 | $55,132.20 | $-7,929.95 |
| Sales: STRAWBERRY | $64,883.04 | $40,252.51 | $24,630.53 |
| Sales: WHEAT | $7,295.51 | $52.96 | $7,242.55 |
| Sales: WOOL | $0.00 | $25,607.09 | $-25,607.09 |

**Key Loss Factors Identified:**
- Opponent invested more in Cows (10 vs 9), yielding higher Milk revenues.
- Opponent bought more Sheep (6 vs 0), yielding higher Wool revenues.
- Opponent outperformed on MILK sales by $7,929.95.
- Opponent outperformed on WOOL sales by $25,607.09.

---

### Match 90651731 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $108,868.00
- **Joseph Franck** (Opponent): $98,057.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $108,868.00 | $98,057.00 | $10,811.00 |
| Max Workers | 13 | 11 | 2 |
| Land Purchases | 2 | 1 | 1 |
| Cows Purchased | 9 | 11 | -2 |
| Sheep Purchased | 0 | 3 | -3 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,940.04 | $0.00 | $1,940.04 |
| Sales: FERTILIZER | $8,780.34 | $15,118.11 | $-6,337.78 |
| Sales: MELON | $24,044.43 | $24,130.31 | $-85.88 |
| Sales: MILK | $38,619.01 | $42,857.19 | $-4,238.19 |
| Sales: STRAWBERRY | $60,849.36 | $0.00 | $60,849.36 |
| Sales: WHEAT | $4,876.83 | $10,178.35 | $-5,301.51 |
| Sales: WOOL | $0.00 | $21,689.04 | $-21,689.04 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 11), giving us labor superiority.
- We outperformed on STRAWBERRY sales by $60,849.36.

---

### Match 90655663 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $87,645.00
- **sneaky6767** (Opponent): $96,450.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $87,645.00 | $96,450.00 | $-8,805.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 8 | 1 |
| Sheep Purchased | 0 | 5 | -5 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,197.65 | $336.00 | $1,861.65 |
| Sales: FERTILIZER | $7,736.38 | $16,280.06 | $-8,543.68 |
| Sales: MELON | $23,688.24 | $22,929.95 | $758.28 |
| Sales: MILK | $20,432.45 | $15,465.25 | $4,967.20 |
| Sales: STRAWBERRY | $54,302.62 | $37,731.73 | $16,570.89 |
| Sales: WHEAT | $4,598.67 | $14,320.40 | $-9,721.73 |
| Sales: WOOL | $0.00 | $34,883.60 | $-34,883.60 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (5 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $34,883.60.

---

### Match 90656372 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $80,652.00
- **Junior Sohou** (Opponent): $138,228.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $80,652.00 | $138,228.00 | $-57,576.00 |
| Max Workers | 13 | 15 | -2 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 8 | 8 | 0 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,915.26 | $0.00 | $1,915.26 |
| Sales: FERTILIZER | $8,969.55 | $15,119.56 | $-6,150.00 |
| Sales: MELON | $24,870.11 | $26,193.96 | $-1,323.85 |
| Sales: MILK | $40,735.20 | $43,800.57 | $-3,065.37 |
| Sales: STRAWBERRY | $29,414.66 | $42,846.22 | $-13,431.55 |
| Sales: WHEAT | $5,012.22 | $9,400.43 | $-4,388.21 |
| Sales: WOOL | $0.00 | $35,186.27 | $-35,186.27 |

**Key Loss Factors Identified:**
- Opponent hired more workers, indicating we might be under-hiring or expanding too slowly.
- Opponent bought more Sheep (6 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $13,431.55.
- Opponent outperformed on WOOL sales by $35,186.27.

---

### Match 90538852 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $127,732.00
- **MugaBros** (Opponent): $141,992.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $127,732.00 | $141,992.00 | $-14,260.00 |
| Max Workers | 13 | 10 | 3 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 8 | 5 | 3 |
| Sheep Purchased | 6 | 5 | 1 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: FERTILIZER | $10,875.58 | $13,592.34 | $-2,716.76 |
| Sales: MELON | $22,322.06 | $34,135.68 | $-11,813.62 |
| Sales: MILK | $52,879.66 | $44,081.52 | $8,798.14 |
| Sales: STRAWBERRY | $51,595.09 | $49,845.68 | $1,749.42 |
| Sales: WHEAT | $3,454.29 | $2,082.15 | $1,372.14 |
| Sales: WOOL | $22,924.32 | $26,862.63 | $-3,938.32 |

**Key Loss Factors Identified:**
- Opponent outperformed on MELON sales by $11,813.62.

---

### Match 90537299 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $115,496.00
- **yuki** (Opponent): $97,872.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $115,496.00 | $97,872.00 | $17,624.00 |
| Max Workers | 13 | 10 | 3 |
| Land Purchases | 2 | 3 | -1 |
| Cows Purchased | 8 | 0 | 8 |
| Sheep Purchased | 6 | 8 | -2 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: FERTILIZER | $14,231.18 | $10,523.96 | $3,707.21 |
| Sales: MELON | $15,856.24 | $32,820.65 | $-16,964.41 |
| Sales: MILK | $46,462.32 | $0.00 | $46,462.32 |
| Sales: STRAWBERRY | $53,743.92 | $28,990.65 | $24,753.27 |
| Sales: WHEAT | $2,349.34 | $12,048.59 | $-9,699.25 |
| Sales: WOOL | $22,364.01 | $35,909.15 | $-13,545.14 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 10), giving us labor superiority.
- We invested more in Cows (8 vs 0), yielding higher Milk revenues.
- We outperformed on STRAWBERRY sales by $24,753.27.
- We outperformed on MILK sales by $46,462.32.

---

### Match 90536517 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $83,132.00
- **BONPU👨‍🌾** (Opponent): $98,227.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $83,132.00 | $98,227.00 | $-15,095.00 |
| Max Workers | 13 | 13 | 0 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 8 | 6 | 2 |
| Sheep Purchased | 4 | 26 | -22 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: FERTILIZER | $9,132.13 | $20,191.79 | $-11,059.66 |
| Sales: MELON | $20,068.37 | $29,333.27 | $-9,264.90 |
| Sales: MILK | $15,681.82 | $16,655.06 | $-973.24 |
| Sales: STRAWBERRY | $48,943.44 | $7,648.19 | $41,295.25 |
| Sales: WHEAT | $2,242.18 | $9,788.73 | $-7,546.55 |
| Sales: WOOL | $19,411.05 | $62,701.96 | $-43,290.90 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (26 vs 4), yielding higher Wool revenues.
- Opponent outperformed on MELON sales by $9,264.90.
- Opponent outperformed on WOOL sales by $43,290.90.

---

### Match 90535815 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $77,924.00
- **George Byne** (Opponent): $90,344.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $77,924.00 | $90,344.00 | $-12,420.00 |
| Max Workers | 13 | 14 | -1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 8 | 8 | 0 |
| Sheep Purchased | 6 | 6 | 0 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: FERTILIZER | $16,261.84 | $13,408.06 | $2,853.78 |
| Sales: MELON | $20,929.50 | $27,157.08 | $-6,227.58 |
| Sales: MILK | $9,209.18 | $15,354.74 | $-6,145.56 |
| Sales: STRAWBERRY | $46,342.75 | $33,470.11 | $12,872.64 |
| Sales: WHEAT | $1,548.51 | $4,528.14 | $-2,979.63 |
| Sales: WOOL | $24,678.23 | $35,530.87 | $-10,852.64 |

**Key Loss Factors Identified:**
- Opponent hired more workers, indicating we might be under-hiring or expanding too slowly.
- Opponent outperformed on MELON sales by $6,227.58.
- Opponent outperformed on MILK sales by $6,145.56.
- Opponent outperformed on WOOL sales by $10,852.64.

---

### Match 90491990 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $77,131.00
- **Dmitry Larko** (Opponent): $144,116.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $77,131.00 | $144,116.00 | $-66,985.00 |
| Max Workers | 13 | 14 | -1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 8 | 1 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,865.38 | $0.00 | $2,865.38 |
| Sales: FERTILIZER | $9,014.58 | $12,128.63 | $-3,114.06 |
| Sales: MELON | $22,000.00 | $23,988.82 | $-1,988.82 |
| Sales: MILK | $20,189.41 | $22,727.19 | $-2,537.78 |
| Sales: STRAWBERRY | $43,356.93 | $71,846.14 | $-28,489.21 |
| Sales: WHEAT | $10,415.70 | $32,606.28 | $-22,190.58 |
| Sales: WOOL | $0.00 | $35,927.94 | $-35,927.94 |

**Key Loss Factors Identified:**
- Opponent hired more workers, indicating we might be under-hiring or expanding too slowly.
- Opponent bought more Sheep (6 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $28,489.21.
- Opponent outperformed on WOOL sales by $35,927.94.

---

### Match 90468429 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $86,677.00
- **Desyat IO** (Opponent): $147,599.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $86,677.00 | $147,599.00 | $-60,922.00 |
| Max Workers | 13 | 15 | -2 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 8 | 1 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,086.88 | $0.00 | $2,086.88 |
| Sales: FERTILIZER | $8,324.12 | $15,079.49 | $-6,755.37 |
| Sales: MELON | $21,640.98 | $27,733.48 | $-6,092.50 |
| Sales: MILK | $27,067.78 | $29,958.63 | $-2,890.85 |
| Sales: STRAWBERRY | $47,285.63 | $63,454.06 | $-16,168.43 |
| Sales: WHEAT | $11,374.60 | $9,186.19 | $2,188.41 |
| Sales: WOOL | $0.00 | $36,452.14 | $-36,452.14 |

**Key Loss Factors Identified:**
- Opponent hired more workers, indicating we might be under-hiring or expanding too slowly.
- Opponent bought more Sheep (6 vs 0), yielding higher Wool revenues.
- Opponent outperformed on MELON sales by $6,092.50.
- Opponent outperformed on STRAWBERRY sales by $16,168.43.
- Opponent outperformed on WOOL sales by $36,452.14.

---

### Match 90462373 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $111,866.00
- **brainpick** (Opponent): $121,468.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $111,866.00 | $121,468.00 | $-9,602.00 |
| Max Workers | 13 | 10 | 3 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 8 | 8 | 0 |
| Sheep Purchased | 0 | 4 | -4 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,010.76 | $0.00 | $2,010.76 |
| Sales: FERTILIZER | $10,615.06 | $13,226.15 | $-2,611.09 |
| Sales: MELON | $22,893.60 | $20,250.93 | $2,642.67 |
| Sales: MILK | $47,727.02 | $49,847.49 | $-2,120.48 |
| Sales: STRAWBERRY | $54,052.74 | $38,675.35 | $15,377.38 |
| Sales: WHEAT | $10,417.83 | $1,225.51 | $9,192.31 |
| Sales: WOOL | $0.00 | $25,561.57 | $-25,561.57 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (4 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $25,561.57.

---

### Match 90459285 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $125,452.00
- **Sparsh389** (Opponent): $132,351.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $125,452.00 | $132,351.00 | $-6,899.00 |
| Max Workers | 13 | 14 | -1 |
| Land Purchases | 2 | 3 | -1 |
| Cows Purchased | 8 | 10 | -2 |
| Sheep Purchased | 0 | 8 | -8 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,673.44 | $1,329.73 | $343.71 |
| Sales: FERTILIZER | $11,473.35 | $15,440.63 | $-3,967.28 |
| Sales: MELON | $21,040.35 | $26,741.23 | $-5,700.88 |
| Sales: MILK | $55,457.82 | $64,499.57 | $-9,041.74 |
| Sales: STRAWBERRY | $62,336.89 | $41,600.95 | $20,735.94 |
| Sales: WHEAT | $9,257.15 | $840.78 | $8,416.38 |
| Sales: WOOL | $0.00 | $28,136.12 | $-28,136.12 |

**Key Loss Factors Identified:**
- Opponent hired more workers, indicating we might be under-hiring or expanding too slowly.
- Opponent invested more in Cows (10 vs 8), yielding higher Milk revenues.
- Opponent bought more Sheep (8 vs 0), yielding higher Wool revenues.
- Opponent outperformed on MELON sales by $5,700.88.
- Opponent outperformed on MILK sales by $9,041.74.
- Opponent outperformed on WOOL sales by $28,136.12.

---

### Match 90415948 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $75,825.00
- **Raggriculture** (Opponent): $140,986.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $75,825.00 | $140,986.00 | $-65,161.00 |
| Max Workers | 13 | 14 | -1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 8 | 8 | 0 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,978.89 | $0.00 | $1,978.89 |
| Sales: FERTILIZER | $11,254.35 | $11,568.87 | $-314.52 |
| Sales: MELON | $23,934.44 | $22,254.51 | $1,679.93 |
| Sales: MILK | $33,097.96 | $33,842.77 | $-744.81 |
| Sales: STRAWBERRY | $30,536.16 | $56,658.32 | $-26,122.16 |
| Sales: WHEAT | $8,707.20 | $37,121.34 | $-28,414.14 |
| Sales: WOOL | $0.00 | $39,124.19 | $-39,124.19 |

**Key Loss Factors Identified:**
- Opponent hired more workers, indicating we might be under-hiring or expanding too slowly.
- Opponent bought more Sheep (6 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $26,122.16.
- Opponent outperformed on WOOL sales by $39,124.19.

---

### Match 90386123 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $102,898.00
- **D S S Kumar** (Opponent): $115,388.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $102,898.00 | $115,388.00 | $-12,490.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 3 | 6 |
| Sheep Purchased | 0 | 12 | -12 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,492.85 | $84.00 | $1,408.85 |
| Sales: FERTILIZER | $9,820.41 | $12,031.70 | $-2,211.29 |
| Sales: MELON | $27,346.32 | $19,211.20 | $8,135.12 |
| Sales: MILK | $36,239.60 | $14,642.76 | $21,596.83 |
| Sales: STRAWBERRY | $50,866.97 | $55,195.50 | $-4,328.53 |
| Sales: WHEAT | $10,031.85 | $108,470.47 | $-98,438.62 |
| Sales: WOOL | $0.00 | $37,642.37 | $-37,642.37 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (12 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $37,642.37.

---

### Match 90385366 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $116,609.00
- **Pascal** (Opponent): $107,082.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $116,609.00 | $107,082.00 | $9,527.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 8 | 2 | 6 |
| Sheep Purchased | 0 | 10 | -10 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,259.03 | $1,192.87 | $1,066.16 |
| Sales: FERTILIZER | $15,308.27 | $13,506.16 | $1,802.11 |
| Sales: MELON | $25,599.68 | $18,370.45 | $7,229.23 |
| Sales: MILK | $54,614.99 | $16,546.13 | $38,068.86 |
| Sales: STRAWBERRY | $47,468.73 | $47,756.16 | $-287.43 |
| Sales: WHEAT | $10,803.29 | $33,501.74 | $-22,698.44 |
| Sales: WOOL | $0.00 | $36,249.49 | $-36,249.49 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 12), giving us labor superiority.
- We invested more in Cows (8 vs 2), yielding higher Milk revenues.
- We outperformed on MELON sales by $7,229.23.
- We outperformed on MILK sales by $38,068.86.

---

### Match 90383874 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $120,213.00
- **this is lsm** (Opponent): $124,195.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $120,213.00 | $124,195.00 | $-3,982.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 8 | 3 | 5 |
| Sheep Purchased | 0 | 12 | -12 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,065.53 | $732.34 | $1,333.19 |
| Sales: FERTILIZER | $14,347.79 | $17,422.41 | $-3,074.62 |
| Sales: MELON | $25,799.85 | $20,368.56 | $5,431.30 |
| Sales: MILK | $49,959.87 | $19,637.72 | $30,322.15 |
| Sales: STRAWBERRY | $57,120.08 | $30,443.08 | $26,677.00 |
| Sales: WHEAT | $10,099.87 | $28,217.86 | $-18,117.99 |
| Sales: WOOL | $0.00 | $64,990.03 | $-64,990.03 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (12 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $64,990.03.

---

### Match 90382371 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $85,188.00
- **Tergel Munkhbat** (Opponent): $98,930.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $85,188.00 | $98,930.00 | $-13,742.00 |
| Max Workers | 13 | 15 | -2 |
| Land Purchases | 2 | 3 | -1 |
| Cows Purchased | 9 | 4 | 5 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,267.26 | $671.17 | $1,596.09 |
| Sales: FERTILIZER | $10,927.07 | $11,657.76 | $-730.68 |
| Sales: MELON | $12,133.00 | $28,882.43 | $-16,749.43 |
| Sales: MILK | $33,662.57 | $19,567.31 | $14,095.26 |
| Sales: STRAWBERRY | $44,274.85 | $52,527.03 | $-8,252.18 |
| Sales: WHEAT | $12,823.25 | $8,875.65 | $3,947.60 |
| Sales: WOOL | $0.00 | $25,989.64 | $-25,989.64 |

**Key Loss Factors Identified:**
- Opponent hired more workers, indicating we might be under-hiring or expanding too slowly.
- Opponent bought more Sheep (6 vs 0), yielding higher Wool revenues.
- Opponent outperformed on MELON sales by $16,749.43.
- Opponent outperformed on STRAWBERRY sales by $8,252.18.
- Opponent outperformed on WOOL sales by $25,989.64.

---

### Match 90376288 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $96,432.00
- **CdeTilly** (Opponent): $122,842.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $96,432.00 | $122,842.00 | $-26,410.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 9 | 3 | 6 |
| Sheep Purchased | 0 | 12 | -12 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,081.87 | $561.31 | $1,520.56 |
| Sales: FERTILIZER | $9,847.14 | $15,701.00 | $-5,853.86 |
| Sales: MELON | $21,633.28 | $21,548.88 | $84.40 |
| Sales: MILK | $27,363.63 | $12,869.28 | $14,494.35 |
| Sales: STRAWBERRY | $55,696.27 | $42,012.14 | $13,684.13 |
| Sales: WHEAT | $10,164.81 | $58,516.09 | $-48,351.29 |
| Sales: WOOL | $0.00 | $60,009.30 | $-60,009.30 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (12 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $60,009.30.

---

### Match 90223428 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $75,016.00
- **HIDEYO CHIBA** (Opponent): $92,457.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $75,016.00 | $92,457.00 | $-17,441.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 1 | 1 |
| Cows Purchased | 10 | 12 | -2 |
| Sheep Purchased | 0 | 10 | -10 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,090.69 | $0.00 | $2,090.69 |
| Sales: FERTILIZER | $12,619.96 | $15,147.88 | $-2,527.92 |
| Sales: MELON | $22,275.90 | $23,642.84 | $-1,366.94 |
| Sales: MILK | $37,596.75 | $35,430.25 | $2,166.50 |
| Sales: STRAWBERRY | $28,382.87 | $22,015.88 | $6,366.99 |
| Sales: WHEAT | $8,454.84 | $1,642.78 | $6,812.05 |
| Sales: WOOL | $0.00 | $27,547.37 | $-27,547.37 |

**Key Loss Factors Identified:**
- Opponent invested more in Cows (12 vs 10), yielding higher Milk revenues.
- Opponent bought more Sheep (10 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $27,547.37.

---

### Match 90222692 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $67,474.00
- **Sparsh389** (Opponent): $82,675.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $67,474.00 | $82,675.00 | $-15,201.00 |
| Max Workers | 13 | 14 | -1 |
| Land Purchases | 2 | 3 | -1 |
| Cows Purchased | 10 | 10 | 0 |
| Sheep Purchased | 0 | 8 | -8 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,780.70 | $1,205.94 | $574.77 |
| Sales: FERTILIZER | $11,664.84 | $11,473.52 | $191.32 |
| Sales: MELON | $28,636.81 | $20,239.70 | $8,397.11 |
| Sales: MILK | $21,460.79 | $19,719.07 | $1,741.72 |
| Sales: STRAWBERRY | $30,969.40 | $44,011.03 | $-13,041.63 |
| Sales: WHEAT | $5,375.46 | $4,755.40 | $620.07 |
| Sales: WOOL | $0.00 | $25,781.35 | $-25,781.35 |

**Key Loss Factors Identified:**
- Opponent hired more workers, indicating we might be under-hiring or expanding too slowly.
- Opponent bought more Sheep (8 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $13,041.63.
- Opponent outperformed on WOOL sales by $25,781.35.

---

### Match 90221964 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $98,066.00
- **Datta Dhebe** (Opponent): $109,897.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $98,066.00 | $109,897.00 | $-11,831.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 6 | 4 |
| Sheep Purchased | 0 | 4 | -4 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,005.01 | $0.00 | $2,005.01 |
| Sales: FERTILIZER | $15,180.33 | $8,138.60 | $7,041.73 |
| Sales: MELON | $27,302.89 | $19,712.09 | $7,590.80 |
| Sales: MILK | $43,195.67 | $29,268.99 | $13,926.68 |
| Sales: STRAWBERRY | $39,754.45 | $51,559.33 | $-11,804.89 |
| Sales: WHEAT | $8,543.65 | $4,288.32 | $4,255.33 |
| Sales: WOOL | $0.00 | $24,458.66 | $-24,458.66 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (4 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $11,804.89.
- Opponent outperformed on WOOL sales by $24,458.66.

---

### Match 90221241 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $90,015.00
- **yuto083** (Opponent): $103,884.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $90,015.00 | $103,884.00 | $-13,869.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 8 | 2 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,716.16 | $0.00 | $1,716.16 |
| Sales: FERTILIZER | $14,895.37 | $10,615.96 | $4,279.41 |
| Sales: MELON | $26,343.62 | $20,248.61 | $6,095.02 |
| Sales: MILK | $44,172.12 | $27,698.43 | $16,473.69 |
| Sales: STRAWBERRY | $28,859.10 | $44,023.21 | $-15,164.12 |
| Sales: WHEAT | $7,266.63 | $2,015.22 | $5,251.40 |
| Sales: WOOL | $0.00 | $34,457.56 | $-34,457.56 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (6 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $15,164.12.
- Opponent outperformed on WOOL sales by $34,457.56.

---

### Match 90220515 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $59,367.00
- **bhavya shah** (Opponent): $78,612.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $59,367.00 | $78,612.00 | $-19,245.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 8 | 2 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,972.76 | $0.00 | $1,972.76 |
| Sales: FERTILIZER | $10,582.09 | $12,899.12 | $-2,317.03 |
| Sales: MELON | $36,994.48 | $9,648.48 | $27,346.00 |
| Sales: MILK | $15,834.47 | $14,174.24 | $1,660.23 |
| Sales: STRAWBERRY | $13,584.06 | $32,474.26 | $-18,890.20 |
| Sales: WHEAT | $10,461.14 | $1,658.98 | $8,802.15 |
| Sales: WOOL | $0.00 | $41,129.91 | $-41,129.91 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (6 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $18,890.20.
- Opponent outperformed on WOOL sales by $41,129.91.

---

### Match 90219050 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $116,159.00
- **SIDHAARTH SHREE** (Opponent): $106,155.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $116,159.00 | $106,155.00 | $10,004.00 |
| Max Workers | 13 | 10 | 3 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 9 | 1 |
| Sheep Purchased | 0 | 8 | -8 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,728.53 | $0.00 | $1,728.53 |
| Sales: FERTILIZER | $12,704.31 | $14,160.77 | $-1,456.46 |
| Sales: MELON | $31,766.01 | $20,671.81 | $11,094.21 |
| Sales: MILK | $52,421.85 | $34,374.42 | $18,047.44 |
| Sales: STRAWBERRY | $43,174.73 | $25,499.84 | $17,674.89 |
| Sales: WHEAT | $8,929.57 | $1,589.94 | $7,339.63 |
| Sales: WOOL | $0.00 | $42,710.23 | $-42,710.23 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 10), giving us labor superiority.
- We invested more in Cows (10 vs 9), yielding higher Milk revenues.
- We outperformed on MELON sales by $11,094.21.
- We outperformed on STRAWBERRY sales by $17,674.89.
- We outperformed on MILK sales by $18,047.44.

---

### Match 90218314 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $101,926.00
- **Emile Andrieu** (Opponent): $125,735.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $101,926.00 | $125,735.00 | $-23,809.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 11 | 8 | 3 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,637.64 | $0.00 | $1,637.64 |
| Sales: FERTILIZER | $14,048.99 | $10,209.18 | $3,839.82 |
| Sales: MELON | $29,665.50 | $25,403.22 | $4,262.28 |
| Sales: MILK | $46,346.80 | $37,351.29 | $8,995.51 |
| Sales: STRAWBERRY | $40,708.58 | $51,166.91 | $-10,458.33 |
| Sales: WHEAT | $5,522.50 | $7,174.73 | $-1,652.23 |
| Sales: WOOL | $0.00 | $33,499.68 | $-33,499.68 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (6 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $10,458.33.
- Opponent outperformed on WOOL sales by $33,499.68.

---

### Match 90217572 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $119,792.00
- **Roman Rozen** (Opponent): $90,075.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $119,792.00 | $90,075.00 | $29,717.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 11 | 6 | 5 |
| Sheep Purchased | 0 | 7 | -7 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,947.59 | $0.00 | $1,947.59 |
| Sales: FERTILIZER | $13,346.63 | $7,195.21 | $6,151.42 |
| Sales: MELON | $29,462.84 | $21,897.59 | $7,565.25 |
| Sales: MILK | $57,014.02 | $23,981.96 | $33,032.06 |
| Sales: STRAWBERRY | $46,882.28 | $29,961.63 | $16,920.64 |
| Sales: WHEAT | $7,439.64 | $32,552.05 | $-25,112.40 |
| Sales: WOOL | $0.00 | $33,121.55 | $-33,121.55 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 12), giving us labor superiority.
- We invested more in Cows (11 vs 6), yielding higher Milk revenues.
- We outperformed on MELON sales by $7,565.25.
- We outperformed on STRAWBERRY sales by $16,920.64.
- We outperformed on MILK sales by $33,032.06.

---

### Match 90157524 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $131,590.00
- **Xiaolei Lian** (Opponent): $108,217.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $131,590.00 | $108,217.00 | $23,373.00 |
| Max Workers | 13 | 10 | 3 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 8 | 2 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,955.77 | $0.00 | $1,955.77 |
| Sales: FERTILIZER | $12,623.86 | $16,767.09 | $-4,143.23 |
| Sales: MELON | $36,968.48 | $6,005.67 | $30,962.81 |
| Sales: MILK | $63,656.06 | $44,394.73 | $19,261.32 |
| Sales: STRAWBERRY | $46,220.11 | $28,764.95 | $17,455.17 |
| Sales: WHEAT | $17,116.71 | $10,628.17 | $6,488.54 |
| Sales: WOOL | $0.00 | $31,549.39 | $-31,549.39 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 10), giving us labor superiority.
- We invested more in Cows (10 vs 8), yielding higher Milk revenues.
- We outperformed on MELON sales by $30,962.81.
- We outperformed on STRAWBERRY sales by $17,455.17.
- We outperformed on MILK sales by $19,261.32.

---

### Match 90147946 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $58,324.00
- **Juyong** (Opponent): $101,458.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $58,324.00 | $101,458.00 | $-43,134.00 |
| Max Workers | 13 | 10 | 3 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 18 | 8 | 10 |
| Sheep Purchased | 0 | 2 | -2 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,636.65 | $0.00 | $1,636.65 |
| Sales: FERTILIZER | $7,265.82 | $13,213.60 | $-5,947.77 |
| Sales: MELON | $32,643.06 | $19,756.24 | $12,886.82 |
| Sales: MILK | $21,302.72 | $40,007.41 | $-18,704.69 |
| Sales: STRAWBERRY | $20,562.85 | $33,963.79 | $-13,400.94 |
| Sales: WHEAT | $14,744.90 | $7,661.93 | $7,082.96 |
| Sales: WOOL | $0.00 | $15,327.03 | $-15,327.03 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (2 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $13,400.94.
- Opponent outperformed on MILK sales by $18,704.69.
- Opponent outperformed on WOOL sales by $15,327.03.

---

### Match 90120436 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $92,884.00
- **Ueddy** (Opponent): $150,223.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $92,884.00 | $150,223.00 | $-57,339.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 8 | 2 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,267.64 | $116.23 | $2,151.42 |
| Sales: FERTILIZER | $10,282.59 | $14,608.35 | $-4,325.76 |
| Sales: MELON | $28,168.00 | $16,420.81 | $11,747.19 |
| Sales: MILK | $52,410.23 | $47,398.96 | $5,011.27 |
| Sales: STRAWBERRY | $24,573.41 | $68,452.68 | $-43,879.27 |
| Sales: TOMATO | $0.00 | $20.54 | $-20.54 |
| Sales: WHEAT | $16,929.13 | $30,638.56 | $-13,709.43 |
| Sales: WOOL | $0.00 | $33,884.87 | $-33,884.87 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (6 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $43,879.27.
- Opponent outperformed on WOOL sales by $33,884.87.

---

### Match 90115034 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $95,814.00
- **Hira Norm** (Opponent): $118,157.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $95,814.00 | $118,157.00 | $-22,343.00 |
| Max Workers | 13 | 11 | 2 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 3 | 7 |
| Sheep Purchased | 0 | 8 | -8 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,050.61 | $645.63 | $1,404.98 |
| Sales: FERTILIZER | $11,085.01 | $8,420.23 | $2,664.79 |
| Sales: MELON | $26,317.39 | $22,300.50 | $4,016.88 |
| Sales: MILK | $59,113.66 | $22,881.23 | $36,232.44 |
| Sales: STRAWBERRY | $22,501.21 | $57,246.65 | $-34,745.44 |
| Sales: WHEAT | $12,888.12 | $2,582.26 | $10,305.86 |
| Sales: WOOL | $0.00 | $29,932.51 | $-29,932.51 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (8 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $34,745.44.
- Opponent outperformed on WOOL sales by $29,932.51.

---

### Match 90112980 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $69,172.00
- **ömer kiraz** (Opponent): $135,997.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $69,172.00 | $135,997.00 | $-66,825.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 8 | 2 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,998.78 | $0.00 | $1,998.78 |
| Sales: EGG | $0.00 | $293.28 | $-293.28 |
| Sales: FERTILIZER | $10,672.58 | $14,583.87 | $-3,911.29 |
| Sales: MELON | $28,386.94 | $15,228.49 | $13,158.45 |
| Sales: MILK | $31,564.03 | $32,216.24 | $-652.21 |
| Sales: STRAWBERRY | $21,901.30 | $64,433.64 | $-42,532.34 |
| Sales: TOMATO | $0.00 | $23.84 | $-23.84 |
| Sales: WHEAT | $16,933.37 | $30,747.22 | $-13,813.85 |
| Sales: WOOL | $0.00 | $39,288.41 | $-39,288.41 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (6 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $42,532.34.
- Opponent outperformed on WOOL sales by $39,288.41.

---

### Match 90108226 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $52,685.00
- **heinado** (Opponent): $127,404.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $52,685.00 | $127,404.00 | $-74,719.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 8 | 2 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,267.52 | $215.99 | $2,051.53 |
| Sales: FERTILIZER | $10,375.94 | $14,561.74 | $-4,185.80 |
| Sales: MELON | $27,301.20 | $15,519.76 | $11,781.43 |
| Sales: MILK | $17,735.58 | $18,684.58 | $-949.01 |
| Sales: STRAWBERRY | $15,785.08 | $66,358.90 | $-50,573.82 |
| Sales: TOMATO | $0.00 | $24.83 | $-24.83 |
| Sales: WHEAT | $18,546.69 | $35,398.00 | $-16,851.31 |
| Sales: WOOL | $0.00 | $38,456.19 | $-38,456.19 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (6 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $50,573.82.
- Opponent outperformed on WOOL sales by $38,456.19.

---

### Match 90091984 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $81,963.00
- **harmo-miu** (Opponent): $73,091.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $81,963.00 | $73,091.00 | $8,872.00 |
| Max Workers | 13 | 9 | 4 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 3 | 7 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,008.88 | $0.00 | $2,008.88 |
| Sales: EGG | $0.00 | $5,680.35 | $-5,680.35 |
| Sales: FERTILIZER | $11,599.13 | $9,911.23 | $1,687.90 |
| Sales: MELON | $24,482.63 | $19,545.29 | $4,937.33 |
| Sales: MILK | $47,007.44 | $8,629.37 | $38,378.07 |
| Sales: STRAWBERRY | $20,671.52 | $43,469.42 | $-22,797.90 |
| Sales: WHEAT | $19,914.41 | $15,540.41 | $4,374.01 |
| Sales: WOOL | $0.00 | $5,553.93 | $-5,553.93 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 9), giving us labor superiority.
- We invested more in Cows (10 vs 3), yielding higher Milk revenues.
- We outperformed on MILK sales by $38,378.07.

---

### Match 90062890 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $77,694.00
- **LGarcia10** (Opponent): $98,434.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $77,694.00 | $98,434.00 | $-20,740.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 3 | -1 |
| Cows Purchased | 10 | 6 | 4 |
| Sheep Purchased | 0 | 3 | -3 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,641.86 | $6,926.88 | $-5,285.02 |
| Sales: FERTILIZER | $11,318.71 | $24,604.23 | $-13,285.52 |
| Sales: MELON | $23,489.03 | $23,853.76 | $-364.73 |
| Sales: MILK | $44,205.11 | $33,784.03 | $10,421.08 |
| Sales: STRAWBERRY | $21,036.81 | $14,506.78 | $6,530.02 |
| Sales: TOMATO | $0.00 | $5,247.66 | $-5,247.66 |
| Sales: WHEAT | $12,850.48 | $16,934.82 | $-4,084.34 |
| Sales: WOOL | $0.00 | $16,790.84 | $-16,790.84 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (3 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $16,790.84.

---

### Match 90060119 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $74,741.00
- **Shuichi Fushimi** (Opponent): $69,848.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $74,741.00 | $69,848.00 | $4,893.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 13 | -3 |
| Sheep Purchased | 0 | 2 | -2 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,868.29 | $924.07 | $944.22 |
| Sales: FERTILIZER | $9,367.82 | $15,228.56 | $-5,860.74 |
| Sales: MELON | $29,173.15 | $20,055.56 | $9,117.59 |
| Sales: MILK | $26,565.58 | $29,138.00 | $-2,572.42 |
| Sales: STRAWBERRY | $34,110.21 | $18,816.51 | $15,293.70 |
| Sales: WHEAT | $11,154.96 | $3,283.48 | $7,871.48 |
| Sales: WOOL | $0.00 | $15,395.82 | $-15,395.82 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 12), giving us labor superiority.
- We outperformed on MELON sales by $9,117.59.
- We outperformed on STRAWBERRY sales by $15,293.70.

---

### Match 90006347 | Outcome: **LOSS**
- **CARLOS CAADA ROSTRO** (Us): $118,008.00
- **somewhere after** (Opponent): $125,896.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $118,008.00 | $125,896.00 | $-7,888.00 |
| Max Workers | 12 | 12 | 0 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 8 | 8 | 0 |
| Sheep Purchased | 6 | 6 | 0 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $361.21 | $22.78 | $338.44 |
| Sales: FERTILIZER | $13,458.10 | $13,345.46 | $112.64 |
| Sales: MELON | $24,837.84 | $27,187.28 | $-2,349.44 |
| Sales: MILK | $45,524.31 | $42,131.61 | $3,392.70 |
| Sales: STRAWBERRY | $30,798.04 | $35,578.58 | $-4,780.54 |
| Sales: TOMATO | $114.49 | $97.31 | $17.18 |
| Sales: WHEAT | $34,261.20 | $31,038.71 | $3,222.49 |
| Sales: WOOL | $31,306.80 | $38,900.27 | $-7,593.47 |

**Key Loss Factors Identified:**
- Opponent outperformed on WOOL sales by $7,593.47.

---

### Match 89989543 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $88,842.00
- **Sutee** (Opponent): $92,645.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $88,842.00 | $92,645.00 | $-3,803.00 |
| Max Workers | 13 | 9 | 4 |
| Land Purchases | 2 | 1 | 1 |
| Cows Purchased | 10 | 5 | 5 |
| Sheep Purchased | 0 | 6 | -6 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,647.99 | $0.00 | $1,647.99 |
| Sales: FERTILIZER | $10,064.45 | $14,864.09 | $-4,799.64 |
| Sales: MELON | $28,958.85 | $18,942.48 | $10,016.38 |
| Sales: MILK | $41,748.26 | $28,428.96 | $13,319.30 |
| Sales: STRAWBERRY | $34,386.98 | $854.18 | $33,532.80 |
| Sales: WHEAT | $13,805.46 | $46,975.43 | $-33,169.97 |
| Sales: WOOL | $0.00 | $36,241.86 | $-36,241.86 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (6 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $36,241.86.

---

### Match 89985050 | Outcome: **WIN**
- **Alpesh Kumar** (Us): $97,925.00
- **m-toshi desu** (Opponent): $84,682.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $97,925.00 | $84,682.00 | $13,243.00 |
| Max Workers | 13 | 10 | 3 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 4 | 6 |
| Sheep Purchased | 0 | 8 | -8 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $2,212.93 | $2,015.84 | $197.09 |
| Sales: FERTILIZER | $10,257.65 | $14,050.93 | $-3,793.27 |
| Sales: MELON | $26,754.00 | $17,772.01 | $8,981.99 |
| Sales: MILK | $54,730.20 | $25,672.32 | $29,057.88 |
| Sales: STRAWBERRY | $27,745.23 | $14,783.95 | $12,961.28 |
| Sales: WHEAT | $16,957.99 | $6,575.44 | $10,382.55 |
| Sales: WOOL | $0.00 | $33,248.51 | $-33,248.51 |

**Key Win Factors Identified:**
- We hired more workers (13 vs 10), giving us labor superiority.
- We invested more in Cows (10 vs 4), yielding higher Milk revenues.
- We outperformed on MELON sales by $8,981.99.
- We outperformed on STRAWBERRY sales by $12,961.28.
- We outperformed on MILK sales by $29,057.88.

---

### Match 89984407 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $94,617.00
- **KodamaSec Labs LTD** (Opponent): $112,376.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $94,617.00 | $112,376.00 | $-17,759.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 4 | 6 |
| Sheep Purchased | 0 | 11 | -11 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,650.04 | $732.20 | $917.84 |
| Sales: FERTILIZER | $8,851.97 | $16,251.78 | $-7,399.81 |
| Sales: MELON | $22,996.24 | $21,669.97 | $1,326.27 |
| Sales: MILK | $52,891.64 | $22,788.34 | $30,103.30 |
| Sales: STRAWBERRY | $33,041.94 | $35,009.31 | $-1,967.37 |
| Sales: WHEAT | $17,864.16 | $61,426.23 | $-43,562.07 |
| Sales: WOOL | $0.00 | $46,971.17 | $-46,971.17 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (11 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $46,971.17.

---

### Match 89983749 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $105,111.00
- **Max Manushin** (Opponent): $118,099.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $105,111.00 | $118,099.00 | $-12,988.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 8 | 2 |
| Sheep Purchased | 0 | 8 | -8 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,616.03 | $149.00 | $1,467.03 |
| Sales: FERTILIZER | $11,490.74 | $13,953.02 | $-2,462.28 |
| Sales: MELON | $25,829.85 | $18,119.94 | $7,709.92 |
| Sales: MILK | $55,594.63 | $43,506.69 | $12,087.93 |
| Sales: STRAWBERRY | $35,477.17 | $36,122.60 | $-645.43 |
| Sales: WHEAT | $16,964.57 | $2,938.59 | $14,025.98 |
| Sales: WOOL | $0.00 | $38,862.16 | $-38,862.16 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (8 vs 0), yielding higher Wool revenues.
- Opponent outperformed on WOOL sales by $38,862.16.

---

### Match 89983092 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $110,825.00
- **Aleks Lviv** (Opponent): $125,241.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $110,825.00 | $125,241.00 | $-14,416.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 8 | 2 |
| Sheep Purchased | 0 | 37 | -37 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,981.89 | $0.00 | $1,981.89 |
| Sales: FERTILIZER | $10,982.03 | $14,257.25 | $-3,275.21 |
| Sales: MELON | $37,576.95 | $10,230.36 | $27,346.59 |
| Sales: MILK | $51,363.97 | $48,099.34 | $3,264.63 |
| Sales: STRAWBERRY | $38,179.68 | $48,469.69 | $-10,290.00 |
| Sales: WHEAT | $14,816.48 | $3,813.30 | $11,003.18 |
| Sales: WOOL | $0.00 | $37,447.07 | $-37,447.07 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (37 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $10,290.00.
- Opponent outperformed on WOOL sales by $37,447.07.

---

### Match 89980458 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $56,611.00
- **vlad101** (Opponent): $100,262.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $56,611.00 | $100,262.00 | $-43,651.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 3 | -1 |
| Cows Purchased | 20 | 8 | 12 |
| Sheep Purchased | 0 | 7 | -7 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,947.06 | $81.71 | $1,865.36 |
| Sales: FERTILIZER | $8,445.41 | $0.00 | $8,445.41 |
| Sales: MELON | $21,809.51 | $26,617.76 | $-4,808.25 |
| Sales: MILK | $21,178.21 | $42,596.62 | $-21,418.41 |
| Sales: STRAWBERRY | $20,901.56 | $32,371.23 | $-11,469.67 |
| Sales: TOMATO | $0.00 | $1,317.56 | $-1,317.56 |
| Sales: WHEAT | $20,932.24 | $2,837.00 | $18,095.24 |
| Sales: WOOL | $0.00 | $28,212.12 | $-28,212.12 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (7 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $11,469.67.
- Opponent outperformed on MILK sales by $21,418.41.
- Opponent outperformed on WOOL sales by $28,212.12.

---

### Match 89978502 | Outcome: **LOSS**
- **Alpesh Kumar** (Us): $47,674.00
- **MarvelousXun** (Opponent): $50,411.00

| Metric | Us | Opponent | Difference |
| :--- | :--- | :--- | :--- |
| Final Bank | $47,674.00 | $50,411.00 | $-2,737.00 |
| Max Workers | 13 | 12 | 1 |
| Land Purchases | 2 | 2 | 0 |
| Cows Purchased | 10 | 9 | 1 |
| Sheep Purchased | 0 | 9 | -9 |
| Max Weeds Count | 0 | 0 | 0 |
| Sales: CARROT | $1,995.95 | $0.00 | $1,995.95 |
| Sales: FERTILIZER | $11,836.09 | $10,847.18 | $988.91 |
| Sales: MELON | $35,630.60 | $9,840.48 | $25,790.12 |
| Sales: MILK | $10,946.97 | $12,215.04 | $-1,268.07 |
| Sales: STRAWBERRY | $10,023.21 | $24,516.72 | $-14,493.51 |
| Sales: WHEAT | $17,908.18 | $3,336.75 | $14,571.43 |
| Sales: WOOL | $0.00 | $25,615.83 | $-25,615.83 |

**Key Loss Factors Identified:**
- Opponent bought more Sheep (9 vs 0), yielding higher Wool revenues.
- Opponent outperformed on STRAWBERRY sales by $14,493.51.
- Opponent outperformed on WOOL sales by $25,615.83.

---
