import { useState, useEffect } from 'react';
import Terminal from '../components/Terminal.jsx';

function ActiveLogs({ logs, onStop, elapsed }) {
  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-black text-white uppercase italic tracking-tighter">System Vulnerability Scan</h2>
          <p className="text-[10px] text-secondary font-mono tracking-widest mt-1 uppercase">Node: DC-04 // Mode: Tactical Analysis</p>
        </div>
        <div className="text-right">
          <p className="text-[9px] text-secondary font-black uppercase tracking-widest mb-1">Elapsed Time</p>
          <p className="text-2xl font-mono font-medium text-primary tracking-tighter">{elapsed}</p>
        </div>
      </div>

      <div className="h-[600px]">
        {/* Full-screen terminal consumes master log state */}
        <Terminal height="h-full" logs={logs} onStop={onStop} />
      </div>
    </div>
  );
}

export default ActiveLogs;