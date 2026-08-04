import React from 'react';
import { Droplet, Sparkles, PlusCircle, Users, CheckCircle, Clock } from 'lucide-react';

export default function FarmGrid({ gameState }) {
  const { plots, landQuadrants, farmhands, animals, inventory } = gameState;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      {/* Visual Farm Map (2 Columns) */}
      <div className="lg:col-span-2 space-y-6">
        <div className="glass-card p-6 rounded-2xl border border-slate-700/60 bg-slate-900/60 backdrop-blur-md">
          
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                🌾 Interactive Farm Plots ({plots.length} Plots across {landQuadrants} Quadrant{landQuadrants > 1 ? 's' : ''})
              </h2>
              <p className="text-xs text-slate-400">Live moisture levels, crop growth cycles & fertilizer application</p>
            </div>
            
            <div className="flex items-center gap-3">
              <span className="text-xs px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-300 flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5 text-cyan-400" />
                {farmhands} Farmhands Active
              </span>
            </div>
          </div>

          {/* Plot Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {plots.map((plot) => {
              const isPlanted = plot.state === 'PLANTED';
              const isReady = plot.state === 'READY_TO_HARVEST';
              const isDry = isPlanted && plot.moisture < 35;

              return (
                <div
                  key={plot.id}
                  className={`relative p-4 rounded-xl border transition-all duration-300 flex flex-col justify-between h-44 ${
                    isReady
                      ? 'border-emerald-500/80 bg-gradient-to-b from-emerald-950/40 to-slate-900 shadow-lg shadow-emerald-500/10 animate-pulse'
                      : isPlanted
                      ? 'border-amber-500/40 bg-gradient-to-b from-slate-900 via-slate-900 to-amber-950/20'
                      : 'border-slate-800 bg-slate-950/60 hover:border-slate-700'
                  }`}
                >
                  {/* Status Badge */}
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-medium text-slate-400">{plot.id}</span>
                    {plot.fertilized && (
                      <span className="text-xs px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30 flex items-center gap-1" title="Fertilized (+50% yield)">
                        <Sparkles className="w-3 h-3 text-purple-400" />
                      </span>
                    )}
                  </div>

                  {/* Center Crop Visual */}
                  <div className="flex flex-col items-center justify-center my-2">
                    {isReady ? (
                      <div className="text-3xl animate-bounce">
                        {getCropIcon(plot.crop)}
                      </div>
                    ) : isPlanted ? (
                      <div className="text-2xl opacity-90">
                        {getCropIcon(plot.crop)}
                      </div>
                    ) : (
                      <div className="text-2xl opacity-20">🌱</div>
                    )}
                    
                    <span className="text-xs font-semibold mt-1 text-slate-200">
                      {isReady ? `HARVEST ${plot.crop}` : isPlanted ? plot.crop : 'EMPTY PLOT'}
                    </span>
                  </div>

                  {/* Growth & Moisture Indicators */}
                  {isPlanted || isReady ? (
                    <div className="space-y-1.5">
                      {/* Growth Bar */}
                      <div>
                        <div className="flex justify-between text-[10px] text-slate-400 mb-0.5">
                          <span>Growth</span>
                          <span>{plot.growth}%</span>
                        </div>
                        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-emerald-400 rounded-full transition-all duration-300"
                            style={{ width: `${plot.growth}%` }}
                          />
                        </div>
                      </div>

                      {/* Moisture Indicator */}
                      <div className="flex items-center justify-between text-[10px]">
                        <span className="flex items-center gap-1 text-slate-400">
                          <Droplet className={`w-3 h-3 ${isDry ? 'text-amber-400 animate-ping' : 'text-cyan-400'}`} />
                          Soil Moisture
                        </span>
                        <span className={isDry ? 'text-amber-400 font-bold' : 'text-slate-300'}>
                          {plot.moisture}%
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="text-[11px] text-slate-500 text-center italic">
                      Ready for planting
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Land Quadrant Expansion Info */}
          {landQuadrants < 4 && (
            <div className="mt-6 p-4 rounded-xl border border-dashed border-emerald-500/30 bg-emerald-950/10 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <PlusCircle className="w-5 h-5 text-emerald-400" />
                <div>
                  <div className="text-xs font-bold text-slate-200">Expand Farm Quadrant ({landQuadrants}/4 Unlocked)</div>
                  <div className="text-[11px] text-slate-400">Unlocks +4 additional plot slots for crop scaling</div>
                </div>
              </div>
              <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-lg border border-emerald-500/20">
                Cost: $500
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Side Panel: Livestock & Harvested Inventory */}
      <div className="space-y-6">
        
        {/* Livestock Pens */}
        <div className="glass-card p-6 rounded-2xl border border-slate-700/60 bg-slate-900/60 backdrop-blur-md">
          <h3 className="text-md font-bold text-slate-100 mb-4 flex items-center gap-2">
            🐄 Animal Husbandry Pens
          </h3>

          <div className="space-y-3">
            <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-950/50 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">🥛</span>
                <div>
                  <div className="text-xs font-bold text-slate-200">Dairy Cows</div>
                  <div className="text-[10px] text-slate-400">Produces Milk every 12 turns</div>
                </div>
              </div>
              <span className="text-sm font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
                {animals.cows} Head
              </span>
            </div>

            <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-950/50 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">🥚</span>
                <div>
                  <div className="text-xs font-bold text-slate-200">Poultry Chickens</div>
                  <div className="text-[10px] text-slate-400">Produces Eggs every 12 turns</div>
                </div>
              </div>
              <span className="text-sm font-bold text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-lg border border-amber-500/20">
                {animals.chickens} Head
              </span>
            </div>

            <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-950/50 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">🧶</span>
                <div>
                  <div className="text-xs font-bold text-slate-200">Wool Sheep</div>
                  <div className="text-[10px] text-slate-400">Produces Wool every 12 turns</div>
                </div>
              </div>
              <span className="text-sm font-bold text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded-lg border border-cyan-500/20">
                {animals.sheep} Head
              </span>
            </div>
          </div>
        </div>

        {/* Harvested Stock Storage */}
        <div className="glass-card p-6 rounded-2xl border border-slate-700/60 bg-slate-900/60 backdrop-blur-md">
          <h3 className="text-md font-bold text-slate-100 mb-4 flex items-center gap-2">
            📦 Granary & Storage Vault
          </h3>

          <div className="grid grid-cols-2 gap-3">
            {Object.keys(inventory).map((key) => (
              <div key={key} className="p-3 rounded-xl border border-slate-800 bg-slate-950/50">
                <div className="text-[11px] text-slate-400 font-medium">{key}</div>
                <div className="text-lg font-bold text-slate-100">{inventory[key]} <span className="text-xs font-normal text-slate-400">units</span></div>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}

function getCropIcon(crop) {
  switch (crop) {
    case 'WHEAT': return '🌾';
    case 'CORN': return '🌽';
    case 'SOY': return '🫘';
    default: return '🌱';
  }
}
