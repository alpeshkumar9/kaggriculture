| **Pet Cafe** | carrots (2x) |
| **Smoothie Shop** | strawberries, milk |
| **Farmers Market** | wheat, carrots, tomatoes, strawberries |

---

## Market Mechanics

The market has an unlimited supply of seeds and animals at fixed prices. Sell prices, however, move dynamically per resource and persist across days.

Every product (and fertilizer) starts the game with a market inventory of $I_0 = 10,000$ units, far above any single game's realistic production volume so that inventory is essentially guaranteed to stay positive. The sell price for a product is `base` at $I_0$, rises as inventory falls (players buying or town consumption draining supply), and falls as inventory grows (players selling).

### Selling inventory to the market
Players can queue any number of sell or buy orders (for any quantity) in the market action list. Orders are processed concurrently across players, one unit at a time. For example, when both players issue `SELL CARROT 10` first, we take the current carrot price, give both players that price for their first carrot, then add 2 carrots to the market (1 from each player) — which may shift the price — and repeat until both orders complete.

If the sell price has been driven down to $1 (the price floor), the unit is still purchased but is not added to market inventory, so the floor remains responsive to subsequent buys.

### Buying inventory from the market
Only WHEAT and FERTILIZER can be bought from the market via `BUY_PRODUCT` (other products are sold at the market but not bought back). Two things drain market inventory: town buildings (town center and shops, which consume products for free) and player `BUY_PRODUCT` orders. Buy orders follow the same one-unit-at-a-time concurrent procedure as sell orders. If a player runs out of money mid-order, the order is stopped.

The buy price is quoted at the post-buy inventory and the sell price is quoted at the pre-sell inventory, so an immediate buy followed by a sell of the same item against an otherwise-unchanged market nets exactly zero.

### The Price Function

For each resource the curve is defined by a base price, an anchor throughput $T$, and an independent shape function + target move for each side of the equilibrium:

$$\text{price}(\text{inv}) = \text{base} + \text{sign} \cdot \text{amp} \cdot f(|\text{inv} - I_0|)$$

* $\text{sign} = +1$ if $\text{inv} < I_0$ (scarcity $\rightarrow$ price up)
* $\text{sign} = -1$ if $\text{inv} > I_0$ (glut $\rightarrow$ price down)
* $\text{amp} = \frac{\text{target} \cdot \text{base}}{f(T)}$ (derived; not stored)
* $f \in \{ \text{linear}, \text{sq}, \text{sqrt}, \text{log}, \text{log10} \}$ ($\text{log}$ uses $\ln(1+x)$, so $f(0)=0$)

*Floored at $1 and rounded to the nearest dollar.*

$T$ is the production capacity of a single 5x5 field over a 24-day game at optimal watering with no fertilizer (animal totals are pre-discounted by 30% to account for wheat-feed overhead). `target` says "moving $T$ units past $I_0$ shifts the price by $\text{target} \times \text{base}$." Picking different $f$ and `target` on each side lets resources with similar production profiles play very differently strategically — wheat panics on scarcity but absorbs gluts, carrot is the opposite; melon barely reacts to scarcity but crashes hard on overproduction; wool mirrors melon at a smaller scale. Premium resources ($\text{base} > \$100$: strawberry, melon, milk, wool) use $\text{above\_target} > 1$, so even modest gluts drive them straight to the $1 floor — bundling and timing sales matters more for these than for staples.

| Resource | Base | $I_0$ | $T$ | Below func | Below target | Above func | Above target | $P(I_0 - T)$ | $P(I_0 + T)$ | $P(I_0 + 2T)$ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Wheat** | 25 | 10,000 | 400 | sq | 0.80 | log | 0.20 | $45 | $20 | $17 |
| **Carrot** | 35 | 10,000 | 450 | log | 0.20 | sqrt | 0.70 | $42 | $10 | $1 |
| **Tomato** | 60 | 10,000 | 200 | linear | 0.40 | sqrt | 0.60 | $84 | $24 | $9 |
| **Strawberry** | 120 | 10,000 | 100 | sqrt | 0.70 | linear | 1.60 | $204 | $1 | $1 |
| **Melon** | 250 | 10,000 | 300 | log | 0.20 | sq | 3.60 | $300 | $1 | $1 |
| **Egg** | 50 | 10,000 | 332 | linear | 0.40 | log | 0.20 | $70 | $40 | $34 |
| **Milk** | 160 | 10,000 | 122 | sqrt | 0.60 | linear | 1.60 | $256 | $1 | $1 |
| **Wool** | 200 | 10,000 | 105 | log | 0.20 | sq | 3.20 | $240 | $1 | $1 |
| **Fertilizer** | 100 | 10,000 | 200 | linear | 0.40 | linear | 0.40 | $140 | $60 | $20 |

The defaults live in `MARKET_PARAMS` in `kaggriculture.py`. Per-resource overrides (sparse: any subset of base, $I_0$, $T$, `below_func`, `below_target`, `above_func`, `above_target`) can be supplied at episode creation via `env.configuration["marketParams"]` without touching code, e.g. `{"WOOL": {"above_target": 0.95}}`.

---

## Turn Processing Order

1. **Action validation** — verify action legality
2. **Player actions** — record the actions taken by each player (happening simultaneously)
3. **Market actions** — process market queue in order by player (described above)
4. **Town buy actions** — town center and shops reduce inventory
5. **Update observations:**
   * **Day refresh** — if applicable, update the condition of plants and animals for a new day, and reset their fed/watered condition to false
   * **Market refresh** — modify the price of items on the market based on sells from previous turn
   * **Income update** — update the player's bank based on any buys or sells
   * **Farm update** — clear plants that have been harvested, items from the inventory that have been used or sold, add new plants/animals to the farm, etc.

---

## Win Conditions & Reward

* **Win Condition:** Whoever has the greatest number of coins at the end of the season (720 turns) is the winner. It is also possible that the two players will tie.
* **Reward:** The player who has the most money in the bank at the end of the game wins. Unsold items in the inventory do not count towards that total.
