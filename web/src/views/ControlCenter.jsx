import React, { useRef } from 'react';
import ConnectionStatus from '../components/ConnectionStatus.jsx';
import Terminal from '../components/Terminal.jsx';

function ControlCenter({ onExecute, isScanning, path, setPath, selectedFiles, setSelectedFiles, logs, onStop, elapsed }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
    }
  };

  const removeFile = (index, e) => {
    e.stopPropagation();
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="relative min-h-[calc(100vh-7rem)] flex flex-col items-center pt-12">
      <div className="max-w-4xl w-full flex flex-col items-center text-center space-y-12">
        <ConnectionStatus />
        <div className="space-y-4">
          <h1 className="text-5xl font-extrabold tracking-tighter text-white uppercase italic">Control Center</h1>
          <p className="text-secondary text-lg">Prepare your assets for deep analysis. Select a path or upload manifest files.</p>
        </div>

        <div className="w-full grid md:grid-cols-2 gap-6 items-stretch text-left">
          {/* Path Input (Controlled via App.jsx) */}
          <div className="bg-surface rounded-xl p-8 border border-white/5 relative group">
            <div className="absolute top-0 left-0 w-1 h-full bg-primary"></div>
            <h3 className="font-mono uppercase text-xs text-white mb-2">Local Directory Path</h3>
            <input
              className="w-full bg-neutral rounded-lg px-4 py-3 text-primary font-mono text-xs focus:ring-1 focus:ring-primary outline-none"
              value={path}
              onChange={(e) => setPath(e.target.value)}
            />
          </div>

          {/* File Staging (Controlled via App.jsx) */}
          <div
            onClick={() => fileInputRef.current.click()}
            className={`bg-surface rounded-xl p-8 border-2 border-dashed cursor-pointer ${
              selectedFiles.length > 0 ? 'border-primary bg-primary/5' : 'border-white/10'
            }`}
          >
            <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileChange} multiple accept=".txt,.json" />
            {selectedFiles.length > 0 ? (
              <div className="space-y-2">
                <p className="text-[10px] text-primary font-black uppercase">{selectedFiles.length} File(s) Staged</p>
                <div className="max-h-32 overflow-y-auto space-y-1">
                  {selectedFiles.map((file, idx) => (
                    <div key={idx} className="flex justify-between bg-neutral/50 p-2 rounded border border-white/5">
                      <span className="text-[10px] font-mono truncate">{file.name}</span>
                      <button onClick={(e) => removeFile(idx, e)} className="text-tertiary">✕</button>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-4">
                <span className="material-symbols-outlined text-secondary text-3xl mb-2">upload_file</span>
                <h3 className="font-mono uppercase text-xs text-white">Manifest Upload</h3>
              </div>
            )}
          </div>
        </div>

        <div className="flex flex-col items-center space-y-4">
          <button
            onClick={() => onExecute(path, selectedFiles)}
            disabled={isScanning}
            className="px-12 py-5 bg-primary text-neutral rounded-xl font-black text-lg uppercase italic shadow-lg"
          >
            {isScanning ? "Vetting Sequence Active..." : "Execute Security Audit"}
          </button>
          
          <div className="text-center">
            <p className="text-[9px] text-secondary font-black uppercase tracking-widest mb-1">Elapsed Time</p>
            <p className="text-2xl font-mono font-medium text-primary tracking-tighter">{elapsed}</p>
          </div>
        </div>
      </div>

      <div className="fixed bottom-12 right-8 w-80 z-20">
        <Terminal height="h-40" logs={logs} onStop={onStop} />
      </div>
    </div>
  );
}

export default ControlCenter;