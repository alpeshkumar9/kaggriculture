// Official Kaggle Kaggriculture Engine Implementation (Full Rulebook Specification)

import { DynamicMarket, COMMODITIES } from './dynamicMarket.js';
import { BotStrategyRunner, PRESET_STRATEGIES } from './botStrategies.js';

export class KaggricultureEngine {
  constructor(botStrategy = PRESET_STRATEGIES.DYNAMIC_AI_OPTIMIZER) {
    this.botStrategy = botStrategy;
    this.market = new DynamicMarket();
    this.reset();
  }

  reset() {
    this.turn = 0; // 0 to 720 turns (30 days * 24 hours)
    this.maxTurns = 720;
    this.cash = 1000;
    this.initialCash = 1000;
    
    // Land Quadrants: Starts with Quadrant 1 (5x5 = 25 tiles). Up to 4 Quadrants (10x10 = 100 tiles).
    this.landQuadrants = 1;
    this.landCosts = [1000, 2000, 4000]; // Quadrants 2, 3, 4 cost $1k, $2k, $4k
    this.tiles = this.generateTiles(25);

    // Shed Inventory: Max 100 items (seeds do not consume shed space)
    this.shedCapacity = 100;
    this.shedInventory = {
      WHEAT: 0, CARROT: 0, TOMATO: 0, STRAWBERRY: 0,
      EGGS: 0, MILK: 0, WOOL: 0, FERTILIZER: 5
    };

    // Seeds Storage (separate from shed, unlimited cap)
    this.seedsInventory = {
      WHEAT: 5, CARROT: 2, TOMATO: 0, STRAWBERRY: 0
    };

    // Farmhand Hiring (Fibonacci cost resetting daily)
    this.dailyHires = 0;
    this.farmhands = 0;

    // Town Shops System (Unlocks every 3 days)
    this.unlockedShops = 0;

    this.logs = [];
    this.financialHistory = [{ turn: 0, day: 1, cash: 1000, netWorth: 1000 }];
    this.salesThisTurn = {};
    this.isGameOver = false;

    this.log(`🌾 Official Kaggriculture Season Started! Grid: 5x5 (25 tiles). Shed Cap: 100. Strategy: ${this.botStrategy.name}`);
  }

  generateTiles(count) {
    const tiles = [];
    for (let i = 1; i <= count; i++) {
      tiles.push({
        id: `tile_${i}`,
        type: 'EMPTY', // EMPTY, PLANT, COOP, PASTURE, WEED
        crop: null,
        animal: null,
        hoursPlanted: 0,
        unwateredHours: 0,
        unfedHours: 0,
        wateredToday: false,
        fedToday: false,
        caredToday: false,
        fertilized: false,
        yieldBonus: 0,
        pendingCareBonus: 0
      });
    }
    return tiles;
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
    const hour = (this.turn - 1) % 24;
    const isStartOfDay = hour === 0;

    // Reset daily counters at start of day (0:00 HR)
    if (isStartOfDay && this.turn > 1) {
      this.dailyHires = 0;
      this.farmhands = 0; // Hands disappear at start of new day after dropping inventory
      this.tiles.forEach((t) => {
        t.wateredToday = false;
        t.fedToday = false;
        t.caredToday = false;
      });

      // Town Shop Unlock check (Every 3 days = 72 turns)
      if ((this.turn - 1) % 72 === 0) {
        this.unlockedShops = Math.min(10, this.unlockedShops + 1);
        this.log(`🏪 New Town Shop Unlocked! Total Active Shops: ${this.unlockedShops}`, 'success');
      }
    }

    // 1. Update Market Prices & Town Shop Consumption
    this.market.updateTurn(this.turn, this.salesThisTurn, this.unlockedShops);
    const marketPrices = this.market.getPrices();

    // 2. Evaluate Strategy Actions
    const currentGameState = this.getState();
    const recommendedActions = BotStrategyRunner.evaluateActions(currentGameState, this.botStrategy);

    // 3. Process Turn Actions
    recommendedActions.forEach((action) => {
      this.applyAction(action, marketPrices);
    });

    // 4. Update Environmental & Animal State
    this.updateGrowthAndAnimals();

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
      this.log(`🏆 Season Finished (720 Turns)! Final Net Worth: $${Math.round(netWorth)}. Total Profit: $${Math.round(netWorth - 1000)}`, 'success');
    }

    return this.getState();
  }

  applyAction(action, marketPrices) {
    switch (action.type) {
      case 'BUY_LAND':
        const nextCost = this.landCosts[this.landQuadrants - 1];
        if (nextCost && this.cash >= nextCost && this.landQuadrants < 4) {
          this.cash -= nextCost;
          this.landQuadrants += 1;
          const newTileTotal = this.landQuadrants * 25; // 25, 50, 75, 100 tiles
          for (let i = this.tiles.length + 1; i <= newTileTotal; i++) {
            this.tiles.push({
              id: `tile_${i}`,
              type: 'EMPTY',
              crop: null,
              animal: null,
              hoursPlanted: 0,
              unwateredHours: 0,
              unfedHours: 0,
              wateredToday: false,
              fedToday: false,
              caredToday: false,
              fertilized: false,
              yieldBonus: 0,
              pendingCareBonus: 0
            });
          }
          this.log(`🚜 Unlocked 5x5 Land Quadrant #${this.landQuadrants} for $${nextCost}. Total Tiles: ${newTileTotal}`, 'action');
        }
        break;

      case 'HIRE_FARMHAND':
        // Fibonacci Hiring Cost: 1, 1, 2, 3, 5, 8...
        const fibCost = this.getFibonacciCost(this.dailyHires);
        if (this.cash >= fibCost) {
          this.cash -= fibCost;
          this.dailyHires += 1;
          this.farmhands += 1;
          this.log(`👩‍🌾 Hired Farmhand #${this.farmhands} for today (Cost: $${fibCost})`, 'action');
        }
        break;

      case 'BUY_SEED':
        const seedSpec = COMMODITIES[action.crop] || COMMODITIES.WHEAT;
        const seedQty = action.quantity || 1;
        const seedCost = seedSpec.seedCost * seedQty;
        if (this.cash >= seedCost) {
          this.cash -= seedCost;
          this.seedsInventory[action.crop] = (this.seedsInventory[action.crop] || 0) + seedQty;
          this.log(`🛒 Purchased ${seedQty} ${seedSpec.name} Seed(s) for $${seedCost}`, 'action');
        }
        break;

      case 'PLANT':
        const pTile = this.tiles.find(t => t.id === action.tileId);
        if (pTile && pTile.type === 'EMPTY' && (this.seedsInventory[action.crop] || 0) > 0) {
          this.seedsInventory[action.crop] -= 1;
          pTile.type = 'PLANT';
          pTile.crop = action.crop;
          pTile.hoursPlanted = 0;
          pTile.unwateredHours = 0;
          pTile.wateredToday = false;
          pTile.fertilized = false;
          this.log(`🌱 Planted ${action.crop} on ${pTile.id}`, 'action');
        }
        break;

      case 'WATER':
        const wTile = this.tiles.find(t => t.id === action.tileId);
        if (wTile && wTile.type === 'PLANT' && !wTile.wateredToday) {
          wTile.wateredToday = true;
          wTile.unwateredHours = 0;
        }
        break;

      case 'FERTILIZE':
        const fTile = this.tiles.find(t => t.id === action.tileId);
        if (fTile && fTile.type === 'PLANT' && !fTile.fertilized && (this.shedInventory.FERTILIZER || 0) > 0) {
          this.shedInventory.FERTILIZER -= 1;
          fTile.fertilized = true;
          this.log(`🧪 Fertilized plant on ${fTile.id} (Doubles bonus yield for 3 days)`, 'action');
        }
        break;

      case 'HARVEST_PLANT':
        const hTile = this.tiles.find(t => t.id === action.tileId);
        if (hTile && hTile.type === 'PLANT') {
          const spec = COMMODITIES[hTile.crop] || COMMODITIES.WHEAT;
          let yieldQty = spec.maxYield;
          if (hTile.fertilized) yieldQty += 4;
          
          if (this.addShedItem(hTile.crop, yieldQty)) {
            this.log(`🌾 Harvested ${yieldQty} units of ${hTile.crop} from ${hTile.id}`, 'success');
            hTile.type = 'EMPTY';
            hTile.crop = null;
          }
        }
        break;

      case 'BUILD_COOP':
        const cTile = this.tiles.find(t => t.id === action.tileId);
        if (cTile && cTile.type === 'EMPTY' && this.cash >= 100) {
          this.cash -= 100;
          cTile.type = 'COOP';
          this.log(`🏠 Built Goose Coop on ${cTile.id}`, 'action');
        }
        break;

      case 'BUILD_PASTURE':
        const pasTile = this.tiles.find(t => t.id === action.tileId);
        if (pasTile && pasTile.type === 'EMPTY' && this.cash >= 150) {
          this.cash -= 150;
          pasTile.type = 'PASTURE';
          this.log(`🏡 Built Livestock Pasture on ${pasTile.id}`, 'action');
        }
        break;

      case 'PLACE_ANIMAL':
        const aTile = this.tiles.find(t => t.id === action.tileId);
        if (aTile && !aTile.animal) {
          if (action.animal === 'GOOSE' && aTile.type === 'COOP' && this.cash >= 80) {
            this.cash -= 80;
            aTile.animal = 'GOOSE';
            this.log(`🪿 Placed Goose on Coop ${aTile.id}`, 'action');
          } else if ((action.animal === 'COW' || action.animal === 'SHEEP') && aTile.type === 'PASTURE') {
            const cost = action.animal === 'COW' ? 250 : 150;
            if (this.cash >= cost) {
              this.cash -= cost;
              aTile.animal = action.animal;
              this.log(`🐄 Placed ${action.animal} on Pasture ${aTile.id}`, 'action');
            }
          }
        }
        break;

      case 'FEED_ANIMAL':
        const feedTile = this.tiles.find(t => t.id === action.tileId);
        if (feedTile && feedTile.animal && !feedTile.fedToday && (this.shedInventory.WHEAT || 0) > 0) {
          this.shedInventory.WHEAT -= 1;
          feedTile.fedToday = true;
          feedTile.unfedHours = 0;
        }
        break;

      case 'CARE_ANIMAL':
        const careTile = this.tiles.find(t => t.id === action.tileId);
        if (careTile && careTile.animal && !careTile.caredToday) {
          careTile.caredToday = true;
          if (careTile.fedToday) {
            careTile.pendingCareBonus += 2;
          }
        }
        break;

      case 'HARVEST_ANIMAL':
        const haTile = this.tiles.find(t => t.id === action.tileId);
        if (haTile && haTile.animal && haTile.fedToday) {
          const product = haTile.animal === 'COW' ? 'MILK' : haTile.animal === 'GOOSE' ? 'EGGS' : 'WOOL';
          const qty = 1 + haTile.pendingCareBonus;
          haTile.pendingCareBonus = 0;
          if (this.addShedItem(product, qty)) {
            this.log(`🥛 Collected ${qty} ${product} from ${haTile.animal} on ${haTile.id}`, 'success');
          }
        }
        break;

      case 'DIG':
        const digTile = this.tiles.find(t => t.id === action.tileId);
        if (digTile && digTile.type !== 'EMPTY') {
          this.log(`🧹 Cleared ${digTile.type} on ${digTile.id}`, 'action');
          digTile.type = 'EMPTY';
          digTile.crop = null;
          digTile.animal = null;
        }
        break;

      case 'SELL':
        const qty = action.quantity || 1;
        if ((this.shedInventory[action.item] || 0) >= qty && qty > 0) {
          const price = marketPrices[action.item] || COMMODITIES[action.item]?.basePrice || 25;
          const total = Math.round(qty * price);
          this.shedInventory[action.item] -= qty;
          this.cash += total;
          this.salesThisTurn[action.item] = (this.salesThisTurn[action.item] || 0) + qty;
          this.log(`💰 Sold ${qty} ${action.item} to Market @ $${price}/unit ($${total})`, 'success');
        }
        break;

      default:
        break;
    }
  }

  updateGrowthAndAnimals() {
    this.tiles.forEach((t) => {
      // Crop Growth & Weed Check
      if (t.type === 'PLANT') {
        t.hoursPlanted += 1;
        if (!t.wateredToday) {
          t.unwateredHours += 1;
        }
        // Weed Rule: 48 consecutive unwatered hours = WEED
        if (t.unwateredHours >= 48) {
          t.type = 'WEED';
          t.crop = null;
          this.log(`⚠️ Plant on ${t.id} dried out and turned into a WEED!`, 'warning');
        }
      }

      // Animal Escape Check
      if (t.animal) {
        if (!t.fedToday) {
          t.unfedHours += 1;
        }
        // Escape Rule: 48 consecutive unfed hours = Animal escapes (unrecoverable)
        if (t.unfedHours >= 48) {
          this.log(`⚠️ ${t.animal} on ${t.id} escaped due to 2 days without Wheat feed!`, 'warning');
          t.animal = null;
        }
      }
    });

    // Farmhand Auto Maintenance
    if (this.farmhands > 0) {
      const thirsty = this.tiles.filter(t => t.type === 'PLANT' && !t.wateredToday);
      for (let i = 0; i < Math.min(this.farmhands, thirsty.length); i++) {
        thirsty[i].wateredToday = true;
        thirsty[i].unwateredHours = 0;
      }
    }
  }

  addShedItem(item, qty) {
    const currentTotal = Object.values(this.shedInventory).reduce((a, b) => a + b, 0);
    const spaceLeft = Math.max(0, this.shedCapacity - currentTotal);
    if (spaceLeft <= 0) {
      this.log(`⚠️ Shed is FULL (100 items cap)! Overflow ${item} discarded.`, 'warning');
      return false;
    }
    const added = Math.min(spaceLeft, qty);
    this.shedInventory[item] = (this.shedInventory[item] || 0) + added;
    return true;
  }

  getFibonacciCost(n) {
    const fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55];
    return (fib[n] || (n * 10)) * 10; // Scaled fib hiring cost
  }

  calculateNetWorth(marketPrices) {
    let shedVal = 0;
    Object.keys(this.shedInventory).forEach((k) => {
      const price = marketPrices[k] || COMMODITIES[k]?.basePrice || 25;
      shedVal += (this.shedInventory[k] || 0) * price;
    });

    const landVal = this.landQuadrants * 1000;
    return this.cash + shedVal + landVal;
  }

  getState() {
    const marketPrices = this.market.getPrices();
    return {
      turn: this.turn,
      day: Math.floor((this.turn - 1) / 24) + 1,
      hour: (this.turn - 1) % 24,
      maxTurns: this.maxTurns,
      cash: Math.round(this.cash),
      netWorth: Math.round(this.calculateNetWorth(marketPrices)),
      landQuadrants: this.landQuadrants,
      farmhands: this.farmhands,
      tiles: [...this.tiles],
      shedInventory: { ...this.shedInventory },
      seedsInventory: { ...this.seedsInventory },
      shedCapacity: this.shedCapacity,
      shedUsed: Object.values(this.shedInventory).reduce((a, b) => a + b, 0),
      marketPrices,
      marketHistory: this.market.getHistory(),
      financialHistory: [...this.financialHistory],
      logs: [...this.logs],
      isGameOver: this.isGameOver,
      botStrategy: this.botStrategy
    };
  }
}
