import React, { useState, useMemo } from 'react';
import VulnerabilityRow from '../components/VulnerabilityRow.jsx';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

/**
 * Post-Scan Analysis Phase
 * restored with original SummaryCards, detailed sidebar, and new memoized filtering.
 */
function Reports({ result, isScanning, time, onRescan }) {
  const [selectedPkg, setSelectedPkg] = useState(null);
  const [filterQuery, setFilterQuery] = useState("");

  // 1. Reactive Filtering Logic
  const filteredFindings = useMemo(() => {
    if (!result?.findings) return [];

    return result.findings.filter((pkg) => {
      const matchesPackage = pkg.package_name.toLowerCase().includes(filterQuery.toLowerCase());
      // Allows searching by CVE ID as well
      const matchesCVE = pkg.vulnerabilities.some(v =>
        v.id.toLowerCase().includes(filterQuery.toLowerCase())
      );
      return matchesPackage || matchesCVE;
    });
  }, [result, filterQuery]);

  const handleExportJSON = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    // Format date nicely for the filename
    const dateStr = new Date().toISOString().replace(/[:.]/g, '-');
    link.download = `airlock_audit_${dateStr}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleExportPDF = () => {
    if (!result) return;
    
    try {
      const doc = new jsPDF();
      const dateStr = new Date().toLocaleString();
      
      // Title
      doc.setFontSize(18);
      doc.text(`Airlock Audit: ${dateStr}`, 14, 22);
      
      // Summary Headers
      doc.setFontSize(12);
      doc.text('Summary', 14, 32);
      
      const summaryData = [
        ['Total Packages', 'Critical Risks', 'High Risks', 'Clean Packages'],
        [
          result.summary.total_packages.toString(),
          result.summary.critical_count.toString(),
          result.summary.high_count.toString(),
          (result.summary.total_packages - result.summary.vulnerable_packages).toString()
        ]
      ];
      
      // Pass the doc instance as the first argument, or use doc.autoTable if using the plugin
      doc.autoTable({
        startY: 36,
        head: [summaryData[0]],
        body: [summaryData[1]],
        theme: 'grid',
        headStyles: { fillColor: [59, 130, 246] } // primary blue
      });
      
      // Findings Table
      let finalY = doc.lastAutoTable?.finalY || 50;
      doc.text('Findings', 14, finalY + 14);
      
      const findingsBody = result.findings.map(pkg => {
        // Format vulnerabilities as a readable string or a nested-like structure
        const vulnsText = pkg.vulnerabilities.map(v => 
          `ID: ${v.id}\nBase Score: ${v.base_score} (${v.severity})\nURL: ${v.source_url}\nDesc: ${v.description}`
        ).join('\n\n---\n\n');
        
        return [
          pkg.package_name,
          pkg.installed_version,
          pkg.cpe,
          vulnsText || 'None'
        ];
      });
      
      doc.autoTable({
        startY: finalY + 18,
        head: [['Package Name', 'Installed Version', 'CPE', 'Vulnerabilities']],
        body: findingsBody,
        theme: 'grid',
        headStyles: { fillColor: [59, 130, 246] },
        styles: { cellWidth: 'wrap' },
        columnStyles: {
          0: { cellWidth: 30 },
          1: { cellWidth: 30 },
          2: { cellWidth: 40 },
          3: { cellWidth: 'auto' } // Allow vulnerabilities to take remaining space
        }
      });
      
      doc.save(`airlock_audit_${new Date().toISOString().replace(/[:.]/g, '-')}.pdf`);
    } catch (err) {
      console.error("Failed to generate PDF:", err);
      alert("Error generating PDF. Check console for details.");
    }
  };

  // 2. Loading State
  if (isScanning) {
    return (
      <div className="h-full flex flex-col items-center justify-center gap-6 mt-32">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin shadow-[0_0_20px_rgba(59,130,246,0.3)]"></div>
        <div className="text-center">
          <h2 className="text-2xl font-black tracking-widest uppercase italic animate-pulse text-white">Vetting In Progress</h2>
          <p className="text-secondary text-[10px] uppercase tracking-widest mt-2 font-mono">Building Security Matrix...</p>
        </div>
      </div>
    );
  }

  if (!result) return (
    <p className="text-secondary text-center mt-20 italic uppercase tracking-widest">
      No audit data available. Execute a scan to begin.
    </p>
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header Section */}
      <header className="flex justify-between items-end border-b border-white/5 pb-6">
        <div>
          <h1 className="text-3xl font-black uppercase italic tracking-tighter text-white">Post-Scan Analysis</h1>
          <p className="text-[11px] text-secondary uppercase font-mono mt-1">
            {new Date().toLocaleString()} // SCAN TIME: {time?.toFixed(2) || "0.00"}S
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={handleExportJSON} className="bg-surface px-4 py-2 text-[10px] font-bold uppercase tracking-widest border border-white/10 rounded hover:bg-white/5 transition-colors">Export JSON</button>
          <button onClick={handleExportPDF} className="bg-surface px-4 py-2 text-[10px] font-bold uppercase tracking-widest border border-white/10 rounded hover:bg-white/5 transition-colors">Export PDF</button>
          <button onClick={() => onRescan()} className="bg-primary/10 text-primary px-4 py-2 text-[10px] font-bold uppercase tracking-widest border border-primary/20 rounded hover:bg-primary/20 transition-all">Rescan Project</button>
        </div>
      </header>

      {/* Restored Summary Metrics */}
      <section className="grid grid-cols-4 gap-4">
        <SummaryCard label="Total Packages" value={result.summary.total_packages} color="border-primary" />
        <SummaryCard label="Critical Risks" value={result.summary.critical_count} color="border-tertiary" pulse={result.summary.critical_count > 0} />
        <SummaryCard label="High Risks" value={result.summary.high_count} color="border-orange-500" />
        <SummaryCard label="Clean Packages" value={result.summary.total_packages - result.summary.vulnerable_packages} color="border-emerald-500" />
      </section>

      {/* Table + Detail Split Pane */}
      <div className="flex gap-6 items-start h-[calc(100vh-25rem)]">
        {/* Left: Filterable Inventory Table */}
        <div className="flex-1 bg-surface rounded border border-white/5 overflow-hidden flex flex-col h-full shadow-2xl">
          <div className="p-4 border-b border-white/5 bg-neutral flex justify-between items-center">
            <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-400">Inventory Matrix</h4>
            <input
              type="text"
              placeholder="FILTER BY PACKAGE OR CVE..."
              value={filterQuery}
              onChange={(e) => setFilterQuery(e.target.value)}
              className="bg-neutral border border-white/10 rounded px-3 py-1 text-[10px] font-mono text-primary outline-none focus:border-primary w-64 uppercase tracking-widest"
            />
          </div>
          <div className="overflow-y-auto flex-1">
            <table className="w-full text-left">
              <thead className="sticky top-0 bg-neutral text-[9px] font-black text-secondary uppercase tracking-[0.2em] border-b border-white/5 z-10">
                <tr>
                  <th className="px-6 py-4">Risk</th>
                  <th className="px-6 py-4">Package Name</th>
                  <th className="px-6 py-4">Version</th>
                  <th className="px-6 py-4">Method</th>
                  <th className="px-6 py-4 text-right">Findings</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {filteredFindings.map((pkg, i) => (
                  <VulnerabilityRow
                    key={`${pkg.package_name}-${i}`}
                    pkg={pkg}
                    isSelected={selectedPkg?.package_name === pkg.package_name}
                    onSelect={setSelectedPkg}
                  />
                ))}
              </tbody>
            </table>
            {filteredFindings.length === 0 && (
              <div className="p-12 text-center text-secondary italic text-sm font-mono">
                No matching assets found in project inventory.
              </div>
            )}
          </div>
        </div>

        {/* Right: Detail Sidebar (Conditional) */}
        {selectedPkg && (
          <aside className="w-[450px] bg-surface rounded border border-primary/20 shadow-2xl p-6 overflow-y-auto h-full animate-in slide-in-from-right duration-300 relative">
            <button onClick={() => setSelectedPkg(null)} className="absolute right-4 top-4 text-secondary hover:text-white transition-colors">✕</button>
            <h3 className="text-xl font-black text-white uppercase italic tracking-tighter">Vulnerability Details</h3>
            <p className="text-[9px] text-primary tracking-widest font-black uppercase mb-8">Active Analysis: {selectedPkg.package_name}</p>

            <div className="space-y-10">
              {selectedPkg.vulnerabilities.map((v, i) => (
                <div key={`${v.id}-${i}`} className="space-y-4">
                  <div className="flex justify-between items-center">
                    <a
                      href={v.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary font-mono text-sm font-bold hover:underline"
                    >
                      {v.id}
                    </a>
                    <button
                      onClick={() => navigator.clipboard.writeText(v.description)}
                      className="text-[10px] font-bold text-secondary flex items-center gap-1 hover:text-white transition-colors"
                    >
                      <span className="material-symbols-outlined text-[14px]">content_copy</span> COPY
                    </button>
                  </div>

                  {/* CVSS Scoring Module */}
                  <div>
                    <div className="flex justify-between items-end mb-2">
                      <span className="text-[9px] font-bold text-secondary uppercase tracking-widest">CVSS v3.1 Score</span>
                      <span className="text-lg font-black text-tertiary">{v.base_score} <span className="text-[10px] font-normal opacity-50 ml-1 uppercase">{v.severity}</span></span>
                    </div>
                    <div className="h-1.5 w-full bg-neutral rounded-full overflow-hidden">
                      <div className="h-full bg-tertiary transition-all duration-700" style={{ width: `${v.base_score * 10}%` }}></div>
                    </div>
                  </div>

                  <p className="bg-neutral p-4 rounded text-[12px] text-slate-300 italic leading-relaxed border border-white/5">
                    "{v.description}"
                  </p>
                </div>
              ))}
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}

/** * Re-included SummaryCard component
 */
function SummaryCard({ label, value, color, pulse }) {
  return (
    <div className={`bg-surface p-6 rounded relative overflow-hidden border border-white/5 shadow-lg`}>
      <div className={`absolute left-0 top-0 w-1 h-full ${color.replace('border-', 'bg-')}`}></div>
      <p className="text-[9px] uppercase font-black tracking-widest text-secondary mb-2">{label}</p>
      <div className="flex items-center gap-3">
        <h3 className="text-4xl font-black text-white font-mono leading-none">{value}</h3>
        {pulse && <span className="w-2 h-2 rounded-full bg-tertiary animate-ping"></span>}
      </div>
    </div>
  );
}

export default Reports;