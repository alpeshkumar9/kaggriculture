import React, { useState } from 'react';
import { TrendingUp, TrendingDown, DollarSign, ShoppingCart, RefreshCw } from 'lucide-react';
import { COMMODITIES } from '../engine/dynamicMarket.js';

export default function MarketChart({ gameState }) {
  const { marketPrices, marketHistory, inventory, cash } = gameState;
  const [selectedCommodity, setSelectedCommodity] = useState('WHEAT');

  // Generate SVG sparkline points for market history
  const historyData = marketHistory.slice(-30);
  const maxVal = Math.max(...historyData.map(d => d[selectedCommodity] || 10), 50);
  const minVal = Math.min(...historyData.map(d => d[selectedCommodity] || 10), 1);
  const range = maxVal - minVal || 1;

  const points = historyData.map((d, idx) => {
    const x = (idx / (historyData.length - 1 || 1)) * 500;
    const val = d[selectedCommodity] || 10;
    const y = 180 - ((val - minVal) / range) * 150;
    return `${x},${y}`;
  }).join(' ');

  const currentPrice = marketPrices[selectedCommodity] || COMMODITIES[selectedCommodity]?.basePrice || 10;
  const basePrice = COMMODITIES[selectedCommodity]?.basePrice || 10;
  const priceDiff = currentPrice - basePrice;
  const isUp = priceDiff >= 0;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      {/* Dynamic Market SVG Price Trend Chart (2 Columns) */}
      <div className="lg:col-span-2 glass-card p-6 rounded-2xl border border-slate-700/60 bg-slate-900/60 backdrop-blur-md">
        
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              📈 Price-Reactive Commodity Exchange
            </h2>
            <p className="text-xs text-slate-400">Live prices react dynamically to supply, demand, and player trade dumps</p>
          </div>

          {/* Commodity Selector Pills */}
          <div className="flex flex-wrap items-center gap-1.5 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
            {Object.keys(COMMODITIES).map((key) => {
              const comm = COMMODITIES[key];
              const isSelected = selectedCommodity === key;
              return (
                <button
                  key={key}
                  onClick={() => setSelectedCommodity(key)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
                    isSelected
                      ? 'bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <span>{comm.icon}</span>
                  <span>{comm.name}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected Commodity Header */}
        <div className="flex items-center justify-between p-4 mb-4 rounded-xl border border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="text-3xl p-2 rounded-xl bg-slate-900 border border-slate-800">
              {COMMODITIES[selectedCommodity]?.icon}
            </div>
            <div>
              <div className="text-sm font-bold text-slate-200">{COMMODITIES[selectedCommodity]?.name} Market Index</div>
              <div className="text-xs text-slate-400">Base Price: ${basePrice} / unit</div>
            </div>
          </div>

          <div className="text-right">
            <div className="text-2xl font-black text-slate-100">${currentPrice}</div>
            <div className={`text-xs font-semibold flex items-center justify-end gap-1 ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
              {isUp ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
              {isUp ? '+' : ''}{priceDiff.toFixed(2)} ({((priceDiff / basePrice) * 100).toFixed(1)}%)
            </div>
          </div>
        </div>

        {/* SVG Sparkline Graph */}
        <div className="relative w-full h-52 bg-slate-950/80 rounded-xl border border-slate-800/80 p-4 flex flex-col justify-between overflow-hidden">
          {/* Background Grid Lines */}
          <div className="absolute inset-0 flex flex-col justify-between p-4 opacity-10 pointer-events-none">
            <div className="border-b border-slate-400 w-full" />
            <div className="border-b border-slate-400 w-full" />
            <div className="border-b border-slate-400 w-full" />
            <div className="border-b border-slate-400 w-full" />
          </div>

          {points.length > 0 ? (
            <svg viewBox="0 0 500 200" className="w-full h-full overflow-visible">
              {/* Gradient Area Fill */}
              <defs>
                <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity="0.35" />
                  <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
                </linearGradient>
              </defs>
              
              <polygon
                points={`0,200 ${points} 500,200`}
                fill="url(#chartGradient)"
              />

              {/* Smooth Path Line */}
              <polyline
                fill="none"
                stroke={isUp ? '#10b981' : '#f43f5e'}
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
                points={points}
              />
            </svg>
          ) : (
            <div className="flex items-center justify-center h-full text-xs text-slate-500">
              Gathering market trend data...
            </div>
          )}

          <div className="flex justify-between text-[10px] text-slate-500 mt-2 font-mono">
            <span>Turn {Math.max(0, gameState.turn - 30)}</span>
            <span>Turn {gameState.turn}</span>
          </div>
        </div>

      </div>

      {/* Commodity Ticker Grid & Inventory Valuation */}
      <div className="glass-card p-6 rounded-2xl border border-slate-700/60 bg-slate-900/60 backdrop-blur-md space-y-4">
        <h3 className="text-md font-bold text-slate-100 flex items-center gap-2">
          🏪 Live Market Ticker
        </h3>

        <div className="space-y-2.5 max-h-[380px] overflow-y-auto pr-1">
          {Object.keys(COMMODITIES).map((key) => {
            const comm = COMMODITIES[key];
            const price = marketPrices[key] || comm.basePrice;
            const diff = price - comm.basePrice;
            const up = diff >= 0;
            const userQty = inventory[key] || 0;

            return (
              <div
                key={key}
                onClick={() => setSelectedCommodity(key)}
                className={`p-3 rounded-xl border transition cursor-pointer flex items-center justify-between ${
                  selectedCommodity === key
                    ? 'border-emerald-500/60 bg-emerald-950/20'
                    : 'border-slate-800 bg-slate-950/40 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <span className="text-xl">{comm.icon}</span>
                  <div>
                    <div className="text-xs font-bold text-slate-200">{comm.name}</div>
                    <div className="text-[10px] text-slate-400">Stock: {userQty} units</div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-sm font-bold text-slate-100">${price}</div>
                  <div className={`text-[10px] font-semibold ${up ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {up ? '▲' : '▼'} ${Math.abs(diff).toFixed(1)}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

      </div>

    </div>
  );
}
