import { useState, useEffect } from 'react';

function ConnectionStatus() {
  const [status, setStatus] = useState("LOADING"); // ONLINE, OFFLINE, LOADING
  const baseUrl = import.meta.env.VITE_API_BASE_URL;

  const checkHealth = async () => {
    try {
      // Pings the system health endpoint defined in your system.py router
      const response = await fetch(`${baseUrl}/system/health`);
      if (response.ok) {
        setStatus("ONLINE");
      } else {
        setStatus("OFFLINE");
      }
    } catch (err) {
      setStatus("OFFLINE");
    }
  };

  useEffect(() => {
    checkHealth()
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, [baseUrl]);

  const statusColors = {
    ONLINE: "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]",
    OFFLINE: "bg-tertiary shadow-[0_0_8px_rgba(239,68,68,0.6)]",
    LOADING: "bg-secondary animate-pulse"
  };

  return (
    <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-surface border border-white/5">
      <span className={`w-2.5 h-2.5 rounded-full ${statusColors[status]}`}></span>
      <span className="font-mono text-[10px] font-black uppercase tracking-[0.2em] text-white">
        System Status: <span className={status === 'OFFLINE' ? 'text-tertiary' : 'text-primary'}>{status}</span>
      </span>
    </div>
  );
}

export default ConnectionStatus;