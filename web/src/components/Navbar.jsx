import React from 'react';

function Navbar() {
  const placeholderAction = (e) => {
    e.preventDefault();
    window.location.reload();
  };

  return (
    <header className="fixed top-0 w-full z-50 flex justify-between items-center px-6 h-14 bg-[#131315] border-b border-white/5 shadow-none">
      {/* Far Left: Branding */}
      <div className="flex items-center">
        <span className="text-xl font-black tracking-tighter text-primary uppercase font-headline">
          Airlock
        </span>
      </div>

      {/* Far Right: Placeholders */}
      <div className="flex items-center gap-4 text-secondary">
        <button onClick={placeholderAction} className="hover:text-white transition-colors p-2 rounded">
          <span className="material-symbols-outlined">notifications</span>
        </button>
        <button onClick={placeholderAction} className="hover:text-white transition-colors p-2 rounded">
          <span className="material-symbols-outlined">settings</span>
        </button>
        <div className="w-8 h-8 rounded-full overflow-hidden border border-white/10 ml-2 cursor-pointer" onClick={placeholderAction}>
          <img
            alt="Profile"
            src="https://api.dicebear.com/7.x/avataaars/svg?seed=Airlock"
            className="bg-surface"
          />
        </div>
      </div>
    </header>
  );
}

export default Navbar;