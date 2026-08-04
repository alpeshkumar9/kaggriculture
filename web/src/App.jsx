import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import FarmGrid from './components/FarmGrid';
import MarketChart from './components/MarketChart';
import StrategyEditor from './components/StrategyEditor';
import MatchArena from './components/MatchArena';
import AnalyticsPanel from './components/AnalyticsPanel';
import BotExporter from './components/BotExporter';
import { KaggricultureEngine } from './engine/kaggricultureEngine';
import { PRESET_STRATEGIES } from './engine/botStrategies';

export default function App() {
  const [strategy, setStrategy] = useState(PRESET_STRATEGIES.DYNAMIC_AI_OPTIMIZER);
  const engineRef = useRef(new KaggricultureEngine(strategy));
  const [gameState, setGameState] = useState(engineRef.current.getState());
  const [isRunning, setIsRunning] = useState(false);
  const [speed, setSpeed] = useState(100); // ms per turn
  const [activeTab, setActiveTab] = useState('farm');

  // Simulation Loop Timer
  useEffect(() => {
    let timer = null;
    if (isRunning && !gameState.isGameOver) {
      timer = setInterval(() => {
        const nextState = engineRef.current.executeTurn();
        setGameState(nextState);
        if (nextState.isGameOver) {
          setIsRunning(false);
        }
      }, speed);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isRunning, speed, gameState.isGameOver]);

  const handleToggleRun = () => {
    if (gameState.isGameOver) {
      handleReset();
    }
    setIsRunning(!isRunning);
  };

  const handleStep = () => {
    if (!gameState.isGameOver) {
      const nextState = engineRef.current.executeTurn();
      setGameState(nextState);
    }
  };

  const handleReset = () => {
    setIsRunning(false);
    engineRef.current = new KaggricultureEngine(strategy);
    setGameState(engineRef.current.getState());
  };

  const handleSelectStrategy = (newStrategy) => {
    setStrategy(newStrategy);
    engineRef.current = new KaggricultureEngine(newStrategy);
    setGameState(engineRef.current.getState());
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-emerald-500 selection:text-slate-950">
      
      {/* Header Controls & Stats */}
      <Header
        gameState={gameState}
        isRunning={isRunning}
        speed={speed}
        onToggleRun={handleToggleRun}
        onStep={handleStep}
        onReset={handleReset}
        onSpeedChange={setSpeed}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {/* Main View Area */}
      <main className="max-w-7xl mx-auto p-6 space-y-6">
        
        {activeTab === 'farm' && (
          <>
            <FarmGrid gameState={gameState} />
            <AnalyticsPanel gameState={gameState} />
          </>
        )}

        {activeTab === 'market' && (
          <MarketChart gameState={gameState} />
        )}

        {activeTab === 'strategy' && (
          <StrategyEditor
            currentStrategy={strategy}
            onSelectStrategy={handleSelectStrategy}
          />
        )}

        {activeTab === 'arena' && (
          <MatchArena />
        )}

        {activeTab === 'export' && (
          <BotExporter currentStrategy={strategy} />
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        <p>Kaggriculture Simulation Suite • Kaggle AI Competition Sandbox • Built with React & Vite</p>
      </footer>
    </div>
  );
}
