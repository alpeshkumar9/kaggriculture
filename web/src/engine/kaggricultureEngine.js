// Kaggriculture 720-Turn Game Engine Simulation State Machine

import { DynamicMarket } from './dynamicMarket.js';
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
    this.landQuadrants = 1; // Starts with 1 land quadrant (up to 4)
    this.farmhands = 0;
    
    // Plots: Each quadrant has 4 plots (Total 4 to 16 plots)
    this.plots = this.generatePlots(4);

    // Livestock
    this.animals = { cows: 0, chickens: 0, sheep: 0 };

    // Inventory
    this.inventory = {
      WHEAT: 0, CORN: 0, SOY: 0,
      EGGS: 0, MILK: 0, WOOL: 0,
      FERTILIZER: 5
    };

    // Metrics & Logs
    this.logs = [];
    this.financialHistory = [{ turn: 0, day: 1, cash: 1000, netWorth: 1000 }];
    this.salesThisTurn = {};
    this.isGameOver = false;

    this.log(`🌾 Kaggriculture Simulation Started. Initial Capital: $1,000. Strategy: ${this.botStrategy.name}`);
  }

  generatePlots(count) {
    const plots = [];
    for (let i = 1; i <= count; i++) {
      plots.push({
        id: `plot_${i}`,
        state: 'EMPTY', // EMPTY, PLANTED, READY_TO_HARVEST
        crop: null,
        growth: 0, // 0 to 100%
        moisture: 80,
        fertilized: false,
        daysToGrow: 0
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

    // 2. Evaluate Bot Strategy Actions
    const currentGameState = this.getState();
    const recommendedActions = BotStrategyRunner.evaluateActions(currentGameState, this.botStrategy);

    // 3. Process Actions
    recommendedActions.forEach((action) => {
      this.applyAction(action, marketPrices);
    });

    // 4. Update Environmental & Natural Growth
    this.updateGrowthAndAnimals();

    // 5. Calculate Financial Net Worth
    const netWorth = this.calculateNetWorth(marketPrices);
    this.financialHistory.push({
      turn: this.turn,
      day: Math.floor(this.turn / 24) + 1,
      cash: Math.round(this.cash),
      netWorth: Math.round(netWorth)
    });

    // 6. Check Game Over
    if (this.turn >= this.maxTurns) {
      this.isGameOver = true;
      this.log(`🏆 Season Finished (720 Turns)! Final Net Worth: $${Math.round(netWorth)}. Net Profit: $${Math.round(netWorth - this.initialCash)}`, 'success');
    }

    return this.getState();
  }

  applyAction(action, marketPrices) {
    switch (action.type) {
      case 'BUY_LAND':
        if (this.cash >= action.cost && this.landQuadrants < 4) {
          this.cash -= action.cost;
          this.landQuadrants += 1;
          const newPlotCount = this.landQuadrants * 4;
          const currentCount = this.plots.length;
          for (let i = currentCount + 1; i <= newPlotCount; i++) {
            this.plots.push({
              id: `plot_${i}`,
              state: 'EMPTY',
              crop: null,
              growth: 0,
              moisture: 75,
              fertilized: false
            });
          }
          this.log(`🚜 Purchased Land Quadrant #${this.landQuadrants}. Total plots: ${newPlotCount}`, 'action');
        }
        break;

      case 'HIRE_FARMHAND':
        if (this.cash >= action.cost) {
          this.cash -= action.cost;
          this.farmhands += 1;
          this.log(`👩‍🌾 Hired Farmhand #${this.farmhands} for automated tasks.`, 'action');
        }
        break;

      case 'BUY_ANIMAL':
        if (this.cash >= action.cost) {
          this.cash -= action.cost;
          if (action.animal === 'COW') this.animals.cows += 1;
          else if (action.animal === 'CHICKEN') this.animals.chickens += 1;
          else if (action.animal === 'SHEEP') this.animals.sheep += 1;
          this.log(`🐄 Purchased ${action.animal} for $${action.cost}`, 'action');
        }
        break;

      case 'PLANT':
        const plot = this.plots.find(p => p.id === action.plotId);
        if (plot && plot.state === 'EMPTY' && this.cash >= 10) {
          this.cash -= 10;
          plot.state = 'PLANTED';
          plot.crop = action.crop;
          plot.growth = 0;
          plot.moisture = 80;
          this.log(`🌱 Planted ${action.crop} on ${plot.id}`, 'action');
        }
        break;

      case 'WATER':
        const waterPlot = this.plots.find(p => p.id === action.plotId);
        if (waterPlot && this.cash >= 3) {
          this.cash -= 3;
          waterPlot.moisture = Math.min(100, waterPlot.moisture + 35);
        }
        break;

      case 'FERTILIZE':
        const fertPlot = this.plots.find(p => p.id === action.plotId);
        if (fertPlot && this.cash >= 10) {
          this.cash -= 10;
          fertPlot.fertilized = true;
          this.log(`🧪 Applied fertilizer to ${fertPlot.id}`, 'action');
        }
        break;

      case 'HARVEST':
        const hPlot = this.plots.find(p => p.id === action.plotId);
        if (hPlot && hPlot.state === 'READY_TO_HARVEST') {
          const yieldQty = hPlot.fertilized ? 15 : 10;
          this.inventory[hPlot.crop] = (this.inventory[hPlot.crop] || 0) + yieldQty;
          this.log(`🌾 Harvested ${yieldQty} units of ${hPlot.crop} from ${hPlot.id}`, 'success');
          hPlot.state = 'EMPTY';
          hPlot.crop = null;
          hPlot.growth = 0;
          hPlot.fertilized = false;
        }
        break;

      case 'SELL_MARKET':
        const qty = action.quantity;
        if (this.inventory[action.item] >= qty && qty > 0) {
          const price = marketPrices[action.item] || action.price;
          const totalEarned = Math.round(qty * price);
          this.inventory[action.item] -= qty;
          this.cash += totalEarned;
          this.salesThisTurn[action.item] = (this.salesThisTurn[action.item] || 0) + qty;
          this.log(`💰 Sold ${qty} units of ${action.item} @ $${price}/unit for total $${totalEarned}`, 'success');
        }
        break;

      default:
        break;
    }
  }

  updateGrowthAndAnimals() {
    // Plots growth
    this.plots.forEach((p) => {
      if (p.state === 'PLANTED') {
        p.moisture = Math.max(0, p.moisture - 2);
        const growthRate = p.moisture > 30 ? (p.fertilized ? 8 : 5) : 2;
        p.growth += growthRate;
        if (p.growth >= 100) {
          p.growth = 100;
          p.state = 'READY_TO_HARVEST';
        }
      }
    });

    // Livestock yield every 12 turns (twice a day)
    if (this.turn > 0 && this.turn % 12 === 0) {
      if (this.animals.chickens > 0) {
        const eggs = this.animals.chickens * 3;
        this.inventory.EGGS += eggs;
        this.log(`🥚 Chickens produced ${eggs} Eggs`, 'info');
      }
      if (this.animals.cows > 0) {
        const milk = this.animals.cows * 4;
        this.inventory.MILK += milk;
        this.log(`🥛 Cows produced ${milk} Milk`, 'info');
      }
      if (this.animals.sheep > 0) {
        const wool = this.animals.sheep * 2;
        this.inventory.WOOL += wool;
        this.log(`🧶 Sheep produced ${wool} Wool`, 'info');
      }
    }

    // Farmhand automated maintenance
    if (this.farmhands > 0) {
      const dryPlots = this.plots.filter(p => p.state === 'PLANTED' && p.moisture < 40);
      for (let i = 0; i < Math.min(this.farmhands, dryPlots.length); i++) {
        dryPlots[i].moisture = Math.min(100, dryPlots[i].moisture + 30);
      }
    }
  }

  calculateNetWorth(marketPrices) {
    let inventoryVal = 0;
    Object.keys(this.inventory).forEach((k) => {
      inventoryVal += (this.inventory[k] || 0) * (marketPrices[k] || 10);
    });
    const assetVal = (this.landQuadrants * 400) + (this.farmhands * 100) +
      (this.animals.cows * 250) + (this.animals.chickens * 80) + (this.animals.sheep * 150);
    return this.cash + inventoryVal + assetVal;
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
      animals: { ...this.animals },
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
