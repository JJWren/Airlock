import React from 'react';

function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'control', label: 'Control Center', icon: 'shield' },
    { id: 'logs', label: 'Active Logs', icon: 'terminal' },
    { id: 'reports', label: 'Reports', icon: 'analytics' }
  ];

  return (
    <aside className="fixed left-0 top-14 h-[calc(100vh-3.5rem)] flex flex-col p-4 bg-[#1c1b1d] w-64 border-r border-white/5 z-40">
      <div className="mb-8 px-4">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
          <h2 className="font-headline font-bold text-sm tracking-tight text-white">Control Center</h2>
        </div>
        <p className="font-mono uppercase tracking-widest text-[10px] text-secondary">Tactical Observer</p>
      </div>

      <nav className="flex-1 space-y-1">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-md transition-all active:scale-95 group ${
              activeTab === item.id 
                ? 'bg-[#2a2a2c] text-primary border-l-2 border-primary' 
                : 'text-secondary hover:bg-[#201f22] hover:text-slate-200'
            }`}
          >
            <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
            <span className="font-mono uppercase tracking-widest text-[10px] font-bold">
              {item.label}
            </span>
          </button>
        ))}
      </nav>

      {/* Persistence of the primary action */}
      <button
        className="mt-auto bg-gradient-to-br from-primary to-[#2563EB] text-neutral font-bold py-3 rounded-md font-mono uppercase tracking-widest text-[10px] transition-all active:scale-95"
        onClick={() => setActiveTab('control')}
      >
        Execute Audit
      </button>
    </aside>
  );
}

export default Sidebar;