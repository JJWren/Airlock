import { useEffect, useState, useRef } from 'react';

/**
 * AIRLOCK Terminal Component
 * Purely presentational log viewer driven by parent state.
 */
function Terminal({ height = "h-64", logs = [], onStop }) {
  const [isMinimized, setIsMinimized] = useState(false);
  const scrollRef = useRef(null);

  // Auto-scroll to latest log entries
  useEffect(() => {
    if (scrollRef.current && !isMinimized) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, isMinimized]);

  const handleExport = () => {
    const blob = new Blob([logs.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `airlock_audit_${new Date().toISOString()}.log`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div
      className={`flex flex-col rounded-lg border border-white/10 bg-black shadow-2xl overflow-hidden transition-all duration-300 ${
        isMinimized ? 'h-10' : height
      }`}
    >
      {/* Header: Minimize Toggle */}
      <div
        className="bg-[#1c1b1d] px-4 py-2 flex items-center justify-between border-b border-white/5 cursor-pointer hover:bg-[#252427]"
        onClick={() => setIsMinimized(!isMinimized)}
      >
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${isMinimized ? 'bg-secondary' : 'bg-primary animate-pulse'}`}></span>
          <span className="font-mono text-[10px] uppercase font-bold text-slate-400">Global Terminal</span>
        </div>
        <span className="material-symbols-outlined text-secondary text-sm">
          {isMinimized ? 'unfold_more' : 'unfold_less'}
        </span>
      </div>

      {!isMinimized && (
        <>
          <div
            ref={scrollRef}
            className="flex-1 p-4 font-mono text-[11px] leading-relaxed overflow-y-auto space-y-1 text-slate-300 scroll-smooth"
          >
            {logs.length === 0 && (
              <p className="text-secondary italic">📡 Standing by for telemetry...</p>
            )}
            {logs.map((log, i) => (
              <p key={i} className="border-l border-white/5 pl-2 break-all font-mono">
                {log}
              </p>
            ))}
          </div>

          {/* Action Bar */}
          <div className="p-2 bg-[#1c1b1d] border-t border-white/5 flex justify-between items-center px-4">
            <button
              onClick={handleExport}
              className="text-[9px] uppercase font-black text-secondary hover:text-white flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-[14px]">download</span> Export Logs
            </button>
            <button
              onClick={() => { if(window.confirm("CRITICAL: Terminate process group?")) onStop(); }}
              className="text-[9px] uppercase font-black text-tertiary hover:text-white flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-[14px]">cancel</span> Emergency Stop
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default Terminal;