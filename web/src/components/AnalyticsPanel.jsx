import React from 'react';
import { ScrollText, DollarSign, Activity, ChevronRight } from 'lucide-react';

export default function AnalyticsPanel({ gameState }) {
  const { logs, financialHistory } = gameState;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      {/* Turn Activity Logs (2 Columns) */}
      <div className="lg:col-span-2 glass-card p-6 rounded-2xl border border-slate-700/60 bg-slate-900/60 backdrop-blur-md">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            📜 Real-Time Agent Action Log
          </h2>
          <span className="text-xs text-slate-400 font-mono">{logs.length} events logged</span>
        </div>

        <div className="space-y-2 max-h-[380px] overflow-y-auto pr-2">
          {logs.length > 0 ? (
            logs.map((log, index) => {
              const isAction = log.type === 'action';
              const isSuccess = log.type === 'success';

              return (
                <div
                  key={index}
                  className={`p-3 rounded-xl border text-xs flex items-center justify-between transition ${
                    isSuccess
                      ? 'border-emerald-500/30 bg-emerald-950/20 text-emerald-300'
                      : isAction
                      ? 'border-cyan-500/30 bg-cyan-950/20 text-cyan-300'
                      : 'border-slate-800 bg-slate-950/50 text-slate-300'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                      D{log.day} {log.hour}:00
                    </span>
                    <span>{log.message}</span>
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">{log.time}</span>
                </div>
              );
            })
          ) : (
            <div className="p-8 text-center text-xs text-slate-500 italic">
              No turn logs recorded yet. Start simulation to view actions.
            </div>
          )}
        </div>
      </div>

      {/* P&L Financial History Summary */}
      <div className="glass-card p-6 rounded-2xl border border-slate-700/60 bg-slate-900/60 backdrop-blur-md space-y-4">
        <h3 className="text-md font-bold text-slate-100 flex items-center gap-2">
          📊 Capital Growth Trajectory
        </h3>

        <div className="space-y-3">
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60">
            <div className="text-xs text-slate-400">Starting Capital</div>
            <div className="text-lg font-bold text-slate-200">$1,000</div>
          </div>

          <div className="p-4 rounded-xl border border-emerald-500/40 bg-emerald-950/20">
            <div className="text-xs text-emerald-400 font-medium">Current Net Worth</div>
            <div className="text-2xl font-black text-emerald-400">${gameState.netWorth.toLocaleString()}</div>
          </div>

          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60">
            <div className="text-xs text-slate-400">Net Return (ROI)</div>
            <div className={`text-lg font-bold ${gameState.netWorth >= 1000 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {(((gameState.netWorth - 1000) / 1000) * 100).toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
