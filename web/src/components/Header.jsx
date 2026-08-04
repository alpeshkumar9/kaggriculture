import React from 'react';
import { Play, Pause, FastForward, RotateCcw, Award, Calendar, DollarSign, Cpu } from 'lucide-react';

export default function Header({ gameState, isRunning, speed, onToggleRun, onStep, onReset, onSpeedChange, activeTab, setActiveTab }) {
  const day = gameState.day;
  const hour = gameState.hour;
  const progressPercent = Math.min(100, Math.round((gameState.turn / gameState.maxTurns) * 100));

  return (
    <header className="glass-nav sticky top-0 z-50 px-6 py-4 border-b border-slate-700/60 bg-slate-900/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Brand & Season Badge */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-green-400 flex items-center justify-center text-xl shadow-lg shadow-emerald-500/20">
            🌾
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400">
                Kaggriculture AI Simulator
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Kaggle Season 2026
              </span>
            </div>
            <p className="text-xs text-slate-400">720-Turn Autonomous Agent & Market Simulator</p>
          </div>
        </div>

        {/* Turn & Financial Progress Stats */}
        <div className="flex items-center gap-6 bg-slate-800/80 border border-slate-700/60 rounded-xl px-5 py-2.5 shadow-inner">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-emerald-400" />
            <div>
              <div className="text-xs text-slate-400">Day {day} / 30</div>
              <div className="text-sm font-semibold text-slate-200">{hour}:00 HR (Turn {gameState.turn})</div>
            </div>
          </div>

          <div className="h-8 w-px bg-slate-700/80" />

          <div className="flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-amber-400" />
            <div>
              <div className="text-xs text-slate-400">Cash Capital</div>
              <div className="text-sm font-bold text-amber-400">${gameState.cash.toLocaleString()}</div>
            </div>
          </div>

          <div className="h-8 w-px bg-slate-700/80" />

          <div className="flex items-center gap-2">
            <Award className="w-4 h-4 text-cyan-400" />
            <div>
              <div className="text-xs text-slate-400">Net Worth</div>
              <div className="text-sm font-bold text-cyan-400">${gameState.netWorth.toLocaleString()}</div>
            </div>
          </div>
        </div>

        {/* Simulator Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={onToggleRun}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold text-sm transition-all shadow-md ${
              isRunning
                ? 'bg-amber-500 hover:bg-amber-600 text-slate-950 shadow-amber-500/20'
                : 'bg-emerald-500 hover:bg-emerald-600 text-slate-950 shadow-emerald-500/20'
            }`}
          >
            {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            {isRunning ? 'Pause' : 'Auto Play'}
          </button>

          <button
            onClick={onStep}
            disabled={isRunning || gameState.isGameOver}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 border border-slate-700 transition"
            title="Step 1 Turn"
          >
            <FastForward className="w-4 h-4" />
          </button>

          <button
            onClick={onReset}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            title="Reset Simulation"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          {/* Speed Selector */}
          <select
            value={speed}
            onChange={(e) => onSpeedChange(Number(e.target.value))}
            className="bg-slate-800 border border-slate-700 text-xs rounded-lg px-2 py-2 text-slate-300 focus:outline-none focus:border-emerald-500"
          >
            <option value={300}>1x Speed</option>
            <option value={100}>3x Speed</option>
            <option value={30}>10x Speed</option>
          </select>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="max-w-7xl mx-auto mt-3 h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-400 transition-all duration-300"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Tab Navigation */}
      <div className="max-w-7xl mx-auto mt-4 flex items-center gap-2 border-b border-slate-800">
        {[
          { id: 'farm', label: '🌾 Farm & Plots' },
          { id: 'market', label: '📈 Market & Trading' },
          { id: 'strategy', label: '🤖 Bot Strategy Builder' },
          { id: 'arena', label: '🏆 Multi-Bot Match Arena' },
          { id: 'export', label: '📦 Kaggle Export' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition border-b-2 ${
              activeTab === tab.id
                ? 'border-emerald-400 text-emerald-400 bg-slate-800/60'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/30'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </header>
  );
}
