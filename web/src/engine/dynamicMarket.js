// Dynamic Market Pricing Engine for Kaggriculture Simulation

export const COMMODITIES = {
  WHEAT: { name: 'Wheat', basePrice: 12, minPrice: 5, maxPrice: 35, category: 'crop', icon: '🌾' },
  CORN: { name: 'Corn', basePrice: 18, minPrice: 8, maxPrice: 48, category: 'crop', icon: '🌽' },
  SOY: { name: 'Soybeans', basePrice: 25, minPrice: 12, maxPrice: 65, category: 'crop', icon: '🫘' },
  EGGS: { name: 'Eggs', basePrice: 15, minPrice: 7, maxPrice: 40, category: 'livestock', icon: '🥚' },
  MILK: { name: 'Fresh Milk', basePrice: 30, minPrice: 14, maxPrice: 75, category: 'livestock', icon: '🥛' },
  WOOL: { name: 'Fine Wool', basePrice: 45, minPrice: 20, maxPrice: 110, category: 'livestock', icon: '🧶' },
  FERTILIZER: { name: 'Organic Fertilizer', basePrice: 10, minPrice: 6, maxPrice: 28, category: 'input', icon: '🧪' }
};

export class DynamicMarket {
  constructor(seed = 42) {
    this.seed = seed;
    this.prices = {};
    this.history = [];
    this.demandIndex = {};
    this.supplyPool = {};
    this.initMarket();
  }

  initMarket() {
    Object.keys(COMMODITIES).forEach((key) => {
      this.prices[key] = COMMODITIES[key].basePrice;
      this.demandIndex[key] = 1.0;
      this.supplyPool[key] = 100;
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

      // Random market drift (-3% to +3%)
      const noise = (Math.random() - 0.49) * 0.06;
      
      // Cyclic demand curve (e.g. higher demand every morning hour 8 and evening hour 18)
      const hour = turn % 24;
      const cycleBonus = Math.sin((hour / 24) * Math.PI * 2) * 0.02;

      // Player market impact (dumping items lowers price)
      const soldAmount = playerSales[key] || 0;
      const priceImpact = soldAmount > 0 ? -Math.log1p(soldAmount) * 0.015 : 0.005;

      // Price update formula
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
