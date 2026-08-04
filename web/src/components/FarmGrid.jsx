import React from 'react';
import { Droplet, Sparkles, PlusCircle, Users, Box, Home, ShieldAlert } from 'lucide-react';

export default function FarmGrid({ gameState }) {
  const { tiles, landQuadrants, farmhands, shedInventory, seedsInventory, shedCapacity, shedUsed } = gameState;
  const landCosts = [1000, 2000, 4000];
  const nextLandCost = landCosts[landQuadrants - 1];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      {/* 5x5 Quadrant Farm Grid (2 Columns) */}
      <div className="lg:col-span-2 space-y-6">
        <div className="glass-card p-6 rounded-2xl border border-slate-700/60 bg-slate-900/60 backdrop-blur-md">
          
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                🌾 Official 10x10 Farm Grid ({tiles.length} Tiles across {landQuadrants} Quadrant{landQuadrants > 1 ? 's' : ''})
              </h2>
              <p className="text-xs text-slate-400">5x5 segments • 24 turns/day • 48h unwatered weed penalty</p>
            </div>
            
            <div className="flex items-center gap-3">
              <span className="text-xs px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-300 flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5 text-cyan-400" />
                {farmhands} Farmhands Hired Today
              </span>
            </div>
          </div>

          {/* Grid Render (5 columns per quadrant) */}
          <div className="grid grid-cols-5 gap-2.5 max-h-[500px] overflow-y-auto pr-1">
            {tiles.map((tile) => {
              const isPlant = tile.type === 'PLANT';
              const isWeed = tile.type === 'WEED';
              const isCoop = tile.type === 'COOP';
              const isPasture = tile.type === 'PASTURE';

              return (
                <div
                  key={tile.id}
                  className={`p-2.5 rounded-xl border text-center transition-all flex flex-col justify-between h-28 ${
                    isWeed
                      ? 'border-amber-700/60 bg-amber-950/30'
                      : isPlant
                      ? 'border-emerald-500/40 bg-slate-900/80'
                      : isCoop || isPasture
                      ? 'border-cyan-500/40 bg-cyan-950/20'
                      : 'border-slate-800 bg-slate-950/60'
                  }`}
                >
                  <div className="flex items-center justify-between text-[9px] text-slate-500 font-mono">
                    <span>{tile.id.replace('tile_', '#')}</span>
                    {tile.wateredToday && <span className="text-cyan-400 font-bold">W</span>}
                  </div>

                  <div className="my-1">
                    {isWeed ? (
                      <div className="text-xl">🌿</div>
                    ) : isPlant ? (
                      <div className="text-xl">{getCropIcon(tile.crop)}</div>
                    ) : tile.animal ? (
                      <div className="text-xl">{getAnimalIcon(tile.animal)}</div>
                    ) : isCoop ? (
                      <div className="text-lg opacity-70">🪿</div>
                    ) : isPasture ? (
                      <div className="text-lg opacity-70">🏡</div>
                    ) : (
                      <div className="text-lg opacity-20">🌱</div>
                    )}

                    <div className="text-[10px] font-semibold text-slate-200 mt-1 truncate">
                      {isWeed ? 'WEED' : isPlant ? tile.crop : tile.animal ? tile.animal : tile.type}
                    </div>
                  </div>

                  <div className="text-[9px] text-slate-400 font-mono">
                    {isPlant ? (
                      <span>{tile.hoursPlanted}h / {tile.wateredToday ? 'Watered' : 'Dry'}</span>
                    ) : tile.animal ? (
                      <span>{tile.fedToday ? 'Fed' : 'Needs Wheat'}</span>
                    ) : (
                      <span>Empty</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Land Quadrant Expansion */}
          {landQuadrants < 4 && nextLandCost && (
            <div className="mt-5 p-4 rounded-xl border border-dashed border-emerald-500/40 bg-emerald-950/10 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <PlusCircle className="w-5 h-5 text-emerald-400" />
                <div>
                  <div className="text-xs font-bold text-slate-200">Unlock Quadrant #{landQuadrants + 1} (+25 Tiles)</div>
                  <div className="text-[11px] text-slate-400">Expands farm to {(landQuadrants + 1) * 25} total squares</div>
                </div>
              </div>
              <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-lg border border-emerald-500/30">
                Cost: ${nextLandCost.toLocaleString()}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Shed Inventory & Seeds Vault (1 Column) */}
      <div className="space-y-6">
        
        {/* Shed Capacity Meter */}
        <div className="glass-card p-6 rounded-2xl border border-slate-700/60 bg-slate-900/60 backdrop-blur-md">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-md font-bold text-slate-100 flex items-center gap-2">
              📦 Shed Vault ({shedUsed}/{shedCapacity})
            </h3>
            <span className={`text-xs font-bold ${shedUsed >= shedCapacity ? 'text-rose-400' : 'text-emerald-400'}`}>
              {shedCapacity - shedUsed} free
            </span>
          </div>

          {/* Shed Progress Gauge */}
          <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden mb-4">
            <div
              className={`h-full transition-all duration-300 ${
                shedUsed >= shedCapacity ? 'bg-rose-500' : 'bg-emerald-400'
              }`}
              style={{ width: `${(shedUsed / shedCapacity) * 100}%` }}
            />
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            {Object.keys(shedInventory).map((key) => (
              <div key={key} className="p-2.5 rounded-xl border border-slate-800 bg-slate-950/50 flex justify-between">
                <span className="text-slate-400">{key}</span>
                <span className="font-bold text-slate-200">{shedInventory[key]}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Seeds Storage (Unlimited Cap) */}
        <div className="glass-card p-6 rounded-2xl border border-slate-700/60 bg-slate-900/60 backdrop-blur-md">
          <h3 className="text-md font-bold text-slate-100 mb-3 flex items-center gap-2">
            🌱 Purchased Seeds Storage
          </h3>
          <div className="grid grid-cols-2 gap-2 text-xs">
            {Object.keys(seedsInventory).map((key) => (
              <div key={key} className="p-2.5 rounded-xl border border-slate-800 bg-slate-950/50 flex justify-between">
                <span className="text-slate-400">{key}</span>
                <span className="font-bold text-emerald-400">{seedsInventory[key]}</span>
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
    case 'CARROT': return '🥕';
    case 'TOMATO': return '🍅';
    case 'STRAWBERRY': return '🍓';
    default: return '🌱';
  }
}

function getAnimalIcon(animal) {
  switch (animal) {
    case 'COW': return '🐄';
    case 'GOOSE': return '🪿';
    case 'SHEEP': return '🧶';
    default: return '🐾';
  }
}
