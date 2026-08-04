import React from 'react';
import { Cpu, Check, Sliders, Shield, Zap, Sparkles, TrendingUp } from 'lucide-react';
import { PRESET_STRATEGIES } from '../engine/botStrategies.js';

export default function StrategyEditor({ currentStrategy, onSelectStrategy }) {
  return (
    <div className="space-y-6">
      
      <div className="glass-card p-6 rounded-2xl border border-slate-700/60 bg-slate-900/60 backdrop-blur-md">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              🤖 Autonomous Agent Strategy Presets
            </h2>
            <p className="text-xs text-slate-400">Choose or configure the algorithmic decision policy for the 720-turn simulation</p>
          </div>
          <span className="text-xs px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">
            Active: {currentStrategy.name}
          </span>
        </div>

        {/* Strategy Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.values(PRESET_STRATEGIES).map((strat) => {
            const isSelected = currentStrategy.id === strat.id;

            return (
              <div
                key={strat.id}
                onClick={() => onSelectStrategy(strat)}
                className={`p-5 rounded-xl border transition cursor-pointer flex flex-col justify-between space-y-4 ${
                  isSelected
                    ? 'border-emerald-500/80 bg-gradient-to-br from-emerald-950/40 via-slate-900 to-slate-950 shadow-lg shadow-emerald-500/10'
                    : 'border-slate-800 bg-slate-950/50 hover:border-slate-700 hover:bg-slate-900/40'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl p-2 rounded-xl bg-slate-900 border border-slate-800">{strat.icon}</span>
                    <div>
                      <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                        {strat.name}
                        {isSelected && <Check className="w-4 h-4 text-emerald-400" />}
                      </h3>
                      <p className="text-xs text-slate-400 mt-1">{strat.description}</p>
                    </div>
                  </div>
                </div>

                {/* Strategy Rules Breakdown */}
                <div className="grid grid-cols-2 gap-2 pt-3 border-t border-slate-800/80 text-[11px]">
                  <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                    <span className="text-slate-400 block">Target Crops</span>
                    <span className="font-semibold text-slate-200">{strat.rules.targetCrops.join(', ')}</span>
                  </div>

                  <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                    <span className="text-slate-400 block">Sell Price Trigger</span>
                    <span className="font-semibold text-emerald-400">{Math.round(strat.rules.sellThresholdMultiplier * 100)}% of Base</span>
                  </div>

                  <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                    <span className="text-slate-400 block">Land Expansion</span>
                    <span className="font-semibold text-slate-200">{strat.rules.reinvestInLand ? `Yes ($${strat.rules.landBuyThreshold})` : 'Disabled'}</span>
                  </div>

                  <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                    <span className="text-slate-400 block">Livestock Farming</span>
                    <span className="font-semibold text-slate-200">{strat.rules.buyLivestock ? 'Enabled' : 'Disabled'}</span>
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
