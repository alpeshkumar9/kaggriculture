// Official Kaggle Kaggriculture Commodity Specification & Dynamic Market Engine

export const COMMODITIES = {
  WHEAT: {
    name: 'Wheat',
    type: 'One-time',
    seedCost: 10,
    basePrice: 25,
    minPrice: 10,
    maxPrice: 60,
    timeToFirstYieldHours: 48, // 2 days
    timeToMaxYieldHours: 96,   // 4 days
    maxYield: 6,
    actionCost: 1,
    icon: '🌾'
  },
  CARROT: {
    name: 'Carrot',
    type: 'One-time',
    seedCost: 20,
    basePrice: 35,
    minPrice: 15,
    maxPrice: 85,
    timeToFirstYieldHours: 48, // 2 days
    timeToMaxYieldHours: 72,   // 3 days
    maxYield: 4,
    actionCost: 1,
    icon: '🥕'
  },
  TOMATO: {
    name: 'Tomato',
    type: 'Ongoing',
    seedCost: 30,
    basePrice: 45,
    minPrice: 20,
    maxPrice: 110,
    timeToFirstYieldHours: 72, // 3 days
    timeToMaxYieldHours: 120,  // 5 days
    maxYield: 8,
    actionCost: 1,
    icon: '🍅'
  },
  STRAWBERRY: {
    name: 'Strawberry',
    type: 'Ongoing',
    seedCost: 40,
    basePrice: 60,
    minPrice: 25,
    maxPrice: 140,
    timeToFirstYieldHours: 96, // 4 days
    timeToMaxYieldHours: 144,  // 6 days
    maxYield: 10,
    actionCost: 1,
    icon: '🍓'
  }
};

export class DynamicMarket {
  constructor(seed = 42) {
    this.seed = seed;
    this.prices = {};
    this.history = [];
    this.initMarket();
  }

  initMarket() {
    Object.keys(COMMODITIES).forEach((key) => {
      this.prices[key] = COMMODITIES[key].basePrice;
    });
    this.recordHistory(0);
  }

  recordHistory(turn) {
    const entry = { turn, day: Math.floor(turn / 24) + 1, hour: turn % 24, ...this.prices };
    this.history.push(entry);
  }

  updateTurn(turn, playerSales = {}) {
    Object.keys(COMMODITIES).forEach((key) => {
      const comm = COMMODITIES[key];
      let currentPrice = this.prices[key];

      // Cyclic demand curve (peaks twice daily)
      const hour = turn % 24;
      const cycleBonus = Math.sin((hour / 24) * Math.PI * 2) * 0.025;
      const noise = (Math.random() - 0.49) * 0.05;

      // Price decay when selling
      const soldAmount = playerSales[key] || 0;
      const priceImpact = soldAmount > 0 ? -Math.log1p(soldAmount) * 0.02 : 0.008;

      let nextPrice = currentPrice * (1 + noise + cycleBonus + priceImpact);
      nextPrice = Math.max(comm.minPrice, Math.min(comm.maxPrice, nextPrice));
      
      this.prices[key] = Number(nextPrice.toFixed(2));
    });

    this.recordHistory(turn);
  }

  getPrices() {
    return { ...this.prices };
  }

  getHistory() {
    return [...this.history];
  }
}
