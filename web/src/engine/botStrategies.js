// Preset Strategies for Official Kaggle Rules (Wheat, Carrot, Tomato, Strawberry)

export const PRESET_STRATEGIES = {
  GREEDY_HARVESTER: {
    id: 'GREEDY_HARVESTER',
    name: 'Wheat & Carrot Fast Cycle',
    description: 'Focuses on 2-day fast-cycle Wheat (Seed $10, Base $25) and Carrots (Seed $20, Base $35).',
    icon: '⚡',
    rules: {
      targetCrops: ['WHEAT', 'CARROT'],
      sellThresholdMultiplier: 0.95,
      reinvestInLand: false,
      maxFarmhands: 1
    }
  },
  MARKET_ARBITRAGE: {
    id: 'MARKET_ARBITRAGE',
    name: 'Market Arbitrageur',
    description: 'Stores inventory until market prices surge > 120% of base price.',
    icon: '📈',
    rules: {
      targetCrops: ['CARROT', 'TOMATO'],
      sellThresholdMultiplier: 1.20,
      reinvestInLand: true,
      landBuyThreshold: 600,
      maxFarmhands: 2
    }
  },
  HIGH_YIELD_TYCOON: {
    id: 'HIGH_YIELD_TYCOON',
    name: 'High Yield Strawberry Tycoon',
    description: 'Aggressively scales high-value Strawberry (Base $60, Yield 10) and buys land quadrants.',
    icon: '🍓',
    rules: {
      targetCrops: ['STRAWBERRY', 'TOMATO'],
      sellThresholdMultiplier: 1.05,
      reinvestInLand: true,
      landBuyThreshold: 500,
      maxFarmhands: 3
    }
  },
  DYNAMIC_AI_OPTIMIZER: {
    id: 'DYNAMIC_AI_OPTIMIZER',
    name: 'Official AI Optimizer (Recommended)',
    description: 'Adaptive algorithm balancing Wheat, Carrot, Tomato, and Strawberry yields according to real-time ROI.',
    icon: '🤖',
    rules: {
      targetCrops: ['WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY'],
      sellThresholdMultiplier: 1.15,
      reinvestInLand: true,
      landBuyThreshold: 550,
      maxFarmhands: 2
    }
  }
};

export class BotStrategyRunner {
  static evaluateActions(gameState, strategyConfig) {
    const { turn, cash, plots, inventory, marketPrices, landQuadrants, farmhands } = gameState;
    const actions = [];
    const rules = strategyConfig.rules;

    // 1. Expand land if cash permits
    if (rules.reinvestInLand && cash >= (rules.landBuyThreshold || 550) && landQuadrants < 4) {
      actions.push({ type: 'BUY_LAND', cost: 500 });
    }

    // 2. Hire Farmhand for auto-watering
    if (farmhands < (rules.maxFarmhands || 2) && cash >= 250) {
      actions.push({ type: 'HIRE_FARMHAND', cost: 150 });
    }

    // 3. Clear Weeds or Harvest / Water / Plant
    plots.forEach((plot) => {
      if (plot.state === 'WEED') {
        actions.push({ type: 'CLEAR_WEED', plotId: plot.id });
      } else if (plot.state === 'READY_TO_HARVEST') {
        actions.push({ type: 'HARVEST', plotId: plot.id });
      } else if (plot.state === 'PLANTED') {
        if (plot.moisture < 35 && cash >= 2) {
          actions.push({ type: 'WATER', plotId: plot.id });
        }
      } else if (plot.state === 'EMPTY' && cash >= 15) {
        const cropChoice = rules.targetCrops[turn % rules.targetCrops.length] || 'WHEAT';
        actions.push({ type: 'PLANT', plotId: plot.id, crop: cropChoice });
      }
    });

    // 4. Market Trading
    Object.keys(inventory).forEach((itemKey) => {
      const quantity = inventory[itemKey];
      if (quantity > 0) {
        const currentPrice = marketPrices[itemKey] || getBasePrice(itemKey);
        const basePrice = getBasePrice(itemKey);
        const threshold = basePrice * (rules.sellThresholdMultiplier || 1.0);

        if (currentPrice >= threshold || turn > 700) {
          actions.push({ type: 'SELL_MARKET', item: itemKey, quantity, price: currentPrice });
        }
      }
    });

    return actions;
  }
}

function getBasePrice(itemKey) {
  const basePrices = { WHEAT: 25, CARROT: 35, TOMATO: 45, STRAWBERRY: 60 };
  return basePrices[itemKey] || 25;
}
