import React, { useState } from 'react';
import { Trophy, Play, RefreshCw, Award, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { PRESET_STRATEGIES } from '../engine/botStrategies.js';
import { KaggricultureEngine } from '../engine/kaggricultureEngine.js';

export default function MatchArena() {
  const [isSimulatingMatch, setIsSimulatingMatch] = useState(false);
  const [matchResults, setMatchResults] = useState(null);

  const runTournament = () => {
    setIsSimulatingMatch(true);
    setTimeout(() => {
      const results = Object.values(PRESET_STRATEGIES).map((strat) => {
        const engine = new KaggricultureEngine(strat);
        for (let turn = 0; turn < 720; turn++) {
          engine.executeTurn();
        }
        const state = engine.getState();
        return {
          id: strat.id,
          name: strat.name,
          icon: strat.icon,
          finalNetWorth: state.netWorth,
          finalCash: state.cash,
          totalProfit: state.netWorth - 1000,
          landQuadrants: state.landQuadrants,
          farmhands: state.farmhands
        };
      });

      // Sort by final Net Worth descending
      results.sort((a, b) => b.finalNetWorth - a.finalNetWorth);
      setMatchResults(results);
      setIsSimulatingMatch(false);
    }, 500);
  };

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-700/60 bg-slate-900/60 backdrop-blur-md space-y-6">
      
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            🏆 Multi-Bot 720-Turn Match Arena
          </h2>
          <p className="text-xs text-slate-400">Run parallel 30-day season tournament matches between all agent strategy presets</p>
        </div>

        <button
          onClick={runTournament}
          disabled={isSimulatingMatch}
          className="px-5 py-2.5 rounded-xl font-bold text-sm bg-gradient-to-r from-amber-500 via-orange-500 to-yellow-500 text-slate-950 hover:from-amber-400 hover:to-yellow-400 shadow-lg shadow-amber-500/20 transition flex items-center gap-2 disabled:opacity-50"
        >
          {isSimulatingMatch ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          {isSimulatingMatch ? 'Simulating 720-Turn Season...' : 'Run Tournament Match'}
        </button>
      </div>

      {/* Leaderboard Results */}
      {matchResults ? (
        <div className="space-y-4">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Tournament Final Standings (30 Days / 720 Turns)
          </div>

          <div className="space-y-3">
            {matchResults.map((res, index) => {
              const isWinner = index === 0;
              const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '🏅';

              return (
                <div
                  key={res.id}
                  className={`p-4 rounded-xl border transition flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
                    isWinner
                      ? 'border-amber-500/80 bg-gradient-to-r from-amber-950/30 via-slate-900 to-slate-900 shadow-lg shadow-amber-500/10'
                      : 'border-slate-800 bg-slate-950/50'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <span className="text-2xl font-bold">{medal}</span>
                    <span className="text-3xl p-2 rounded-xl bg-slate-900 border border-slate-800">{res.icon}</span>
                    <div>
                      <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                        {res.name}
                        {isWinner && <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 font-semibold">1ST PLACE</span>}
                      </h3>
                      <p className="text-xs text-slate-400">
                        Expansion: {res.landQuadrants} Quadrants | {res.farmhands} Farmhands
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-6 text-right w-full md:w-auto justify-between md:justify-end">
                    <div>
                      <div className="text-[10px] text-slate-400">Net Profit</div>
                      <div className={`text-xs font-bold ${res.totalProfit >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {res.totalProfit >= 0 ? '+' : ''}${res.totalProfit.toLocaleString()}
                      </div>
                    </div>

                    <div className="h-8 w-px bg-slate-800" />

                    <div>
                      <div className="text-[10px] text-slate-400">Final Net Worth</div>
                      <div className="text-lg font-extrabold text-amber-400">${res.finalNetWorth.toLocaleString()}</div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="p-12 text-center rounded-xl border border-dashed border-slate-800 bg-slate-950/40">
          <Trophy className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-sm font-bold text-slate-300">No Tournament Match Simulated Yet</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
            Click "Run Tournament Match" to simulate all 4 strategy bots head-to-head across a complete 720-turn season.
          </p>
        </div>
      )}

    </div>
  );
}
