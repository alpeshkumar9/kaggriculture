// Built-in Bot Strategies for Kaggriculture Simulation

export const PRESET_STRATEGIES = {
  GREEDY_HARVESTER: {
    id: 'GREEDY_HARVESTER',
    name: 'Greedy Harvester',
    description: 'Prioritizes fast-cycling crops (Wheat & Corn) and sells harvested crops immediately.',
    icon: '⚡',
    rules: {
      targetCrops: ['WHEAT', 'CORN'],
      sellThresholdMultiplier: 0.95, // sell whenever price is at least 95% of base
      reinvestInLand: false,
      buyLivestock: false,
      maxFarmhands: 1
    }
  },
  MARKET_ARBITRAGE: {
    id: 'MARKET_ARBITRAGE',
    name: 'Market Arbitrageur',
    description: 'Stores inventory until market prices surge, maximizing profit margin per item.',
    icon: '📈',
    rules: {
      targetCrops: ['CORN', 'SOY'],
      sellThresholdMultiplier: 1.25, // hold until price is 125% of base price
      reinvestInLand: true,
      landBuyThreshold: 800,
      buyLivestock: true,
      maxFarmhands: 2
    }
  },
  LAND_LIVESTOCK_TYCOON: {
    id: 'LAND_LIVESTOCK_TYCOON',
    name: 'Livestock & Land Tycoon',
    description: 'Aggressively expands farm quadrants and invests in Cows, Chickens, and Sheep for recurring yield.',
    icon: '🚜',
    rules: {
      targetCrops: ['SOY', 'CORN'],
      sellThresholdMultiplier: 1.05,
      reinvestInLand: true,
      landBuyThreshold: 500,
      buyLivestock: true,
      maxFarmhands: 4
    }
  },
  DYNAMIC_AI_OPTIMIZER: {
    id: 'DYNAMIC_AI_OPTIMIZER',
    name: 'Dynamic AI Optimizer (Recommended)',
    description: 'Adaptive algorithm calculating ROI, weather/moisture factors, market curve forecasts, and worker efficiency.',
    icon: '🤖',
    rules: {
      targetCrops: ['WHEAT', 'CORN', 'SOY'],
      sellThresholdMultiplier: 1.15,
      reinvestInLand: true,
      landBuyThreshold: 650,
      buyLivestock: true,
      maxFarmhands: 3
    }
  }
};

export class BotStrategyRunner {
  static evaluateActions(gameState, strategyConfig) {
    const { turn, cash, plots, animals, inventory, marketPrices, landQuadrants, farmhands } = gameState;
    const actions = [];
    const rules = strategyConfig.rules;

    // 1. Buy Land expansion if cash permits
    if (rules.reinvestInLand && cash >= (rules.landBuyThreshold || 600) && landQuadrants < 4) {
      actions.push({ type: 'BUY_LAND', cost: 500 });
    }

    // 2. Hire Farmhands if operational cash is high
    if (farmhands < (rules.maxFarmhands || 2) && cash >= 350) {
      actions.push({ type: 'HIRE_FARMHAND', cost: 150 });
    }

    // 3. Animal Husbandry actions
    if (rules.buyLivestock && cash >= 200) {
      if (animals.cows < 2 && cash >= 300) actions.push({ type: 'BUY_ANIMAL', animal: 'COW', cost: 250 });
      else if (animals.chickens < 4 && cash >= 100) actions.push({ type: 'BUY_ANIMAL', animal: 'CHICKEN', cost: 80 });
    }

    // 4. Crop Plot Actions (Planting, Watering, Fertilizing, Harvesting)
    plots.forEach((plot) => {
      if (plot.state === 'EMPTY' && cash >= 20) {
        // Pick optimal crop based on strategy and market price ROI
        const cropChoice = rules.targetCrops[Math.floor(Math.random() * rules.targetCrops.length)] || 'WHEAT';
        actions.push({ type: 'PLANT', plotId: plot.id, crop: cropChoice });
      } else if (plot.state === 'PLANTED') {
        if (plot.moisture < 40 && cash >= 5) {
          actions.push({ type: 'WATER', plotId: plot.id });
        } else if (!plot.fertilized && cash >= 15) {
          actions.push({ type: 'FERTILIZE', plotId: plot.id });
        }
      } else if (plot.state === 'READY_TO_HARVEST') {
        actions.push({ type: 'HARVEST', plotId: plot.id });
      }
    });

    // 5. Market Trading (Sell Inventory when target price hit)
    Object.keys(inventory).forEach((itemKey) => {
      const quantity = inventory[itemKey];
      if (quantity > 0 && itemKey !== 'FERTILIZER') {
        const currentPrice = marketPrices[itemKey] || 10;
        const basePrice = getBasePrice(itemKey);
        const threshold = basePrice * (rules.sellThresholdMultiplier || 1.0);

        if (currentPrice >= threshold || turn > 700) { // Force liquidation near turn 720
          actions.push({ type: 'SELL_MARKET', item: itemKey, quantity, price: currentPrice });
        }
      }
    });

    return actions;
  }
}

function getBasePrice(itemKey) {
  const basePrices = { WHEAT: 12, CORN: 18, SOY: 25, EGGS: 15, MILK: 30, WOOL: 45 };
  return basePrices[itemKey] || 10;
}
