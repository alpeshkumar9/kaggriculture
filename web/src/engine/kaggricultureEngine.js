// Official Kaggle Kaggriculture Engine Implementation

import { DynamicMarket, COMMODITIES } from './dynamicMarket.js';
import { BotStrategyRunner, PRESET_STRATEGIES } from './botStrategies.js';

export class KaggricultureEngine {
  constructor(botStrategy = PRESET_STRATEGIES.DYNAMIC_AI_OPTIMIZER) {
    this.botStrategy = botStrategy;
    this.market = new DynamicMarket();
    this.reset();
  }

  reset() {
    this.turn = 0; // 0 to 720 (30 days * 24 hours)
    this.maxTurns = 720;
    this.cash = 1000;
    this.initialCash = 1000;
    this.landQuadrants = 1; // 1 to 4
    this.farmhands = 0;
    
    // Plots: Starts with 4 plots in Quadrant 1
    this.plots = this.generatePlots(4);

    // Inventory
    this.inventory = {
      WHEAT: 0,
      CARROT: 0,
      TOMATO: 0,
      STRAWBERRY: 0
    };

    this.logs = [];
    this.financialHistory = [{ turn: 0, day: 1, cash: 1000, netWorth: 1000 }];
    this.salesThisTurn = {};
    this.isGameOver = false;

    this.log(`🌾 Kaggriculture Season Started (Official Rules). Capital: $1,000. Wheat & Carrot specs loaded. Strategy: ${this.botStrategy.name}`);
  }

  generatePlots(count) {
    const plots = [];
    for (let i = 1; i <= count; i++) {
      plots.push({
        id: `plot_${i}`,
        state: 'EMPTY', // EMPTY, PLANTED, READY_TO_HARVEST, WEED
        crop: null,
        hoursPlanted: 0,
        unwateredHours: 0,
        moisture: 100,
        fertilized: false,
        yieldAmount: 0
      });
    }
    return plots;
  }

  log(message, type = 'info') {
    this.logs.unshift({
      turn: this.turn,
      day: Math.floor(this.turn / 24) + 1,
      hour: this.turn % 24,
      message,
      type,
      time: new Date().toLocaleTimeString()
    });
  }

  executeTurn() {
    if (this.isGameOver || this.turn >= this.maxTurns) {
      this.isGameOver = true;
      return this.getState();
    }

    this.turn += 1;
    this.salesThisTurn = {};

    // 1. Update Market Prices
    this.market.updateTurn(this.turn, this.salesThisTurn);
    const marketPrices = this.market.getPrices();

    // 2. Evaluate Bot Actions
    const currentGameState = this.getState();
    const recommendedActions = BotStrategyRunner.evaluateActions(currentGameState, this.botStrategy);

    // 3. Apply Actions
    recommendedActions.forEach((action) => {
      this.applyAction(action, marketPrices);
    });

    // 4. Environmental Growth & Weed Check
    this.updateGrowth();

    // 5. Calculate Financial Net Worth
    const netWorth = this.calculateNetWorth(marketPrices);
    this.financialHistory.push({
      turn: this.turn,
      day: Math.floor(this.turn / 24) + 1,
      cash: Math.round(this.cash),
      netWorth: Math.round(netWorth)
    });

    if (this.turn >= this.maxTurns) {
      this.isGameOver = true;
      this.log(`🏆 Season Finished (720 Turns)! Final Net Worth: $${Math.round(netWorth)}. Profit: $${Math.round(netWorth - 1000)}`, 'success');
    }

    return this.getState();
  }

  applyAction(action, marketPrices) {
    switch (action.type) {
      case 'BUY_LAND':
        if (this.cash >= action.cost && this.landQuadrants < 4) {
          this.cash -= action.cost;
          this.landQuadrants += 1;
          const newTotal = this.landQuadrants * 4;
          for (let i = this.plots.length + 1; i <= newTotal; i++) {
            this.plots.push({
              id: `plot_${i}`,
              state: 'EMPTY',
              crop: null,
              hoursPlanted: 0,
              unwateredHours: 0,
              moisture: 100,
              fertilized: false,
              yieldAmount: 0
            });
          }
          this.log(`🚜 Purchased Land Quadrant #${this.landQuadrants}. Total plots: ${newTotal}`, 'action');
        }
        break;

      case 'HIRE_FARMHAND':
        if (this.cash >= action.cost) {
          this.cash -= action.cost;
          this.farmhands += 1;
          this.log(`👩‍🌾 Hired Farmhand #${this.farmhands} for auto-watering.`, 'action');
        }
        break;

      case 'PLANT':
        const plot = this.plots.find(p => p.id === action.plotId);
        const spec = COMMODITIES[action.crop] || COMMODITIES.WHEAT;
        if (plot && plot.state === 'EMPTY' && this.cash >= spec.seedCost) {
          this.cash -= spec.seedCost;
          plot.state = 'PLANTED';
          plot.crop = action.crop;
          plot.hoursPlanted = 0;
          plot.unwateredHours = 0;
          plot.moisture = 100;
          plot.fertilized = false;
          plot.yieldAmount = spec.maxYield;
          this.log(`🌱 Planted ${spec.name} on ${plot.id} (Seed Cost: $${spec.seedCost})`, 'action');
        }
        break;

      case 'WATER':
        const wPlot = this.plots.find(p => p.id === action.plotId);
        if (wPlot && wPlot.state === 'PLANTED' && this.cash >= 2) {
          this.cash -= 2;
          wPlot.moisture = 100;
          wPlot.unwateredHours = 0;
        }
        break;

      case 'HARVEST':
        const hPlot = this.plots.find(p => p.id === action.plotId);
        if (hPlot && hPlot.state === 'READY_TO_HARVEST') {
          const qty = hPlot.yieldAmount || 6;
          this.inventory[hPlot.crop] = (this.inventory[hPlot.crop] || 0) + qty;
          this.log(`🌾 Harvested ${qty} units of ${hPlot.crop} from ${hPlot.id}`, 'success');
          hPlot.state = 'EMPTY';
          hPlot.crop = null;
          hPlot.hoursPlanted = 0;
        }
        break;

      case 'CLEAR_WEED':
        const cPlot = this.plots.find(p => p.id === action.plotId);
        if (cPlot && cPlot.state === 'WEED') {
          cPlot.state = 'EMPTY';
          cPlot.crop = null;
          cPlot.hoursPlanted = 0;
          this.log(`🧹 Cleared weeds from ${cPlot.id}`, 'action');
        }
        break;

      case 'SELL_MARKET':
        const qty = action.quantity;
        if (this.inventory[action.item] >= qty && qty > 0) {
          const price = marketPrices[action.item] || COMMODITIES[action.item]?.basePrice || 25;
          const totalEarned = Math.round(qty * price);
          this.inventory[action.item] -= qty;
          this.cash += totalEarned;
          this.salesThisTurn[action.item] = (this.salesThisTurn[action.item] || 0) + qty;
          this.log(`💰 Sold ${qty} units of ${action.item} @ $${price}/unit ($${totalEarned})`, 'success');
        }
        break;

      default:
        break;
    }
  }

  updateGrowth() {
    this.plots.forEach((p) => {
      if (p.state === 'PLANTED') {
        p.hoursPlanted += 1;
        p.moisture = Math.max(0, p.moisture - 3);

        if (p.moisture < 20) {
          p.unwateredHours += 1;
        } else {
          p.unwateredHours = 0;
        }

        // Penalty: If unwatered for 48 consecutive hours (2 days), turns into WEED
        if (p.unwateredHours >= 48) {
          p.state = 'WEED';
          this.log(`⚠️ ${p.id} dried out and turned into WEEDS!`, 'warning');
          return;
        }

        const spec = COMMODITIES[p.crop] || COMMODITIES.WHEAT;
        if (p.hoursPlanted >= spec.timeToFirstYieldHours) {
          p.state = 'READY_TO_HARVEST';
        }
      }
    });

    // Farmhand auto-watering
    if (this.farmhands > 0) {
      const thirsty = this.plots.filter(p => p.state === 'PLANTED' && p.moisture < 40);
      for (let i = 0; i < Math.min(this.farmhands, thirsty.length); i++) {
        thirsty[i].moisture = 100;
        thirsty[i].unwateredHours = 0;
      }
    }
  }

  calculateNetWorth(marketPrices) {
    let invVal = 0;
    Object.keys(this.inventory).forEach((k) => {
      const price = marketPrices[k] || COMMODITIES[k]?.basePrice || 25;
      invVal += (this.inventory[k] || 0) * price;
    });
    const landVal = this.landQuadrants * 400;
    const workerVal = this.farmhands * 100;
    return this.cash + invVal + landVal + workerVal;
  }

  getState() {
    const marketPrices = this.market.getPrices();
    return {
      turn: this.turn,
      day: Math.floor(this.turn / 24) + 1,
      hour: this.turn % 24,
      maxTurns: this.maxTurns,
      cash: Math.round(this.cash),
      netWorth: Math.round(this.calculateNetWorth(marketPrices)),
      landQuadrants: this.landQuadrants,
      farmhands: this.farmhands,
      plots: [...this.plots],
      inventory: { ...this.inventory },
      marketPrices,
      marketHistory: this.market.getHistory(),
      financialHistory: [...this.financialHistory],
      logs: [...this.logs],
      isGameOver: this.isGameOver,
      botStrategy: this.botStrategy
    };
  }
}
