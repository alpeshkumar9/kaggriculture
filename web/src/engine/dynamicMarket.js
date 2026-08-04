// Official Kaggle Kaggriculture Dynamic Market Engine
// Formula: price(inv) = base + sign * amp * f(|inv - I0|)

export const COMMODITIES = {
  WHEAT: {
    name: 'Wheat',
    type: 'One-time',
    seedCost: 10,
    basePrice: 25,
    I0: 10000,
    T: 400,
    belowFunc: 'sq',
    belowTarget: 0.80,
    aboveFunc: 'log',
    aboveTarget: 0.20,
    firstYieldDays: 2,
    maxYieldDays: 4,
    maxYield: 6,
    icon: '🌾'
  },
  CARROT: {
    name: 'Carrot',
    type: 'One-time',
    seedCost: 20,
    basePrice: 35,
    I0: 10000,
    T: 450,
    belowFunc: 'log',
    belowTarget: 0.20,
    aboveFunc: 'sqrt',
    aboveTarget: 0.70,
    firstYieldDays: 2,
    maxYieldDays: 3,
    maxYield: 4,
    icon: '🥕'
  },
  TOMATO: {
    name: 'Tomato',
    type: 'Ongoing',
    seedCost: 50,
    basePrice: 60,
    I0: 10000,
    T: 200,
    belowFunc: 'linear',
    belowTarget: 0.40,
    aboveFunc: 'sqrt',
    aboveTarget: 0.60,
    firstYieldDays: 7,
    maxYield: 4,
    icon: '🍅'
  },
  STRAWBERRY: {
    name: 'Strawberry',
    type: 'Ongoing',
    seedCost: 100,
    basePrice: 120,
    I0: 10000,
    T: 100,
    belowFunc: 'sqrt',
    belowTarget: 0.70,
    aboveFunc: 'linear',
    aboveTarget: 1.60,
    firstYieldDays: 10,
    maxYield: 4,
    icon: '🍓'
  },
  MELON: {
    name: 'Melon',
    type: 'One-time',
    seedCost: 80,
    basePrice: 250,
    I0: 10000,
    T: 300,
    belowFunc: 'log',
    belowTarget: 0.20,
    aboveFunc: 'sq',
    aboveTarget: 3.60,
    firstYieldDays: 10,
    maxYieldDays: 12,
    maxYield: 6,
    icon: '🍈'
  },
  EGGS: {
    name: 'Eggs',
    type: 'AnimalProduct',
    animalCost: 300,
    basePrice: 50,
    I0: 10000,
    T: 332,
    belowFunc: 'linear',
    belowTarget: 0.40,
    aboveFunc: 'log',
    aboveTarget: 0.20,
    firstYieldDays: 4,
    maxYield: 4,
    icon: '🥚'
  },
  MILK: {
    name: 'Milk',
    type: 'AnimalProduct',
    animalCost: 400,
    basePrice: 160,
    I0: 10000,
    T: 122,
    belowFunc: 'sqrt',
    belowTarget: 0.60,
    aboveFunc: 'linear',
    aboveTarget: 1.60,
    firstYieldDays: 8,
    maxYield: 6,
    icon: '🥛'
  },
  WOOL: {
    name: 'Wool',
    type: 'AnimalProduct',
    animalCost: 500,
    basePrice: 200,
    I0: 10000,
    T: 105,
    belowFunc: 'log',
    belowTarget: 0.20,
    aboveFunc: 'sq',
    aboveTarget: 3.20,
    firstYieldDays: 6,
    maxYield: 6,
    icon: '🧶'
  },
  FERTILIZER: {
    name: 'Fertilizer',
    type: 'Consumable',
    buyCost: 100,
    basePrice: 100,
    I0: 10000,
    T: 200,
    belowFunc: 'linear',
    belowTarget: 0.40,
    aboveFunc: 'linear',
    aboveTarget: 0.40,
    icon: '🧪'
  }
};

export class DynamicMarket {
  constructor(seed = 42) {
    this.seed = seed;
    this.inventory = {};
    this.prices = {};
    this.history = [];
    this.initMarket();
  }

  initMarket() {
    Object.keys(COMMODITIES).forEach((key) => {
      this.inventory[key] = COMMODITIES[key].I0;
      this.prices[key] = COMMODITIES[key].basePrice;
    });
    this.recordHistory(0);
  }

  evaluateShape(funcName, x) {
    if (funcName === 'sq') return x * x;
    if (funcName === 'sqrt') return Math.sqrt(x);
    if (funcName === 'log' || funcName === 'log10') return Math.log1p(x);
    return x; // linear default
  }

  calculatePrice(key) {
    const comm = COMMODITIES[key];
    if (!comm) return 25;

    const I0 = comm.I0;
    const inv = this.inventory[key] || I0;
    const diff = inv - I0;

    if (diff === 0) return comm.basePrice;

    const isScarcity = diff < 0;
    const absDiff = Math.abs(diff);
    const funcName = isScarcity ? comm.belowFunc : comm.aboveFunc;
    const target = isScarcity ? comm.belowTarget : comm.aboveTarget;
    const T = comm.T;

    const fT = this.evaluateShape(funcName, T);
    if (fT === 0) return comm.basePrice;

    const amp = (target * comm.basePrice) / fT;
    const fx = this.evaluateShape(funcName, absDiff);

    const sign = isScarcity ? 1 : -1;
    let price = comm.basePrice + sign * amp * fx;
    
    // Price floor at $1 and rounded to nearest dollar
    return Math.max(1, Math.round(price));
  }

  recordHistory(turn) {
    const entry = { turn, day: Math.floor(turn / 24) + 1, hour: turn % 24, ...this.prices };
    this.history.push(entry);
  }

  updateTurn(turn, playerSales = {}, townShopsUnlocked = 0) {
    Object.keys(COMMODITIES).forEach((key) => {
      let soldAmount = playerSales[key] || 0;
      // Town consumption drains inventory
      let townDrain = townShopsUnlocked > 0 ? townShopsUnlocked * 2 : 1;
      
      this.inventory[key] = Math.max(0, (this.inventory[key] || 10000) + soldAmount - townDrain);
      this.prices[key] = this.calculatePrice(key);
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
