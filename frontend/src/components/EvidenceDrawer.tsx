import React, { useState } from 'react';
import { EvidenceRecord } from '../services/types';

interface EvidenceDrawerProps {
  evidence: EvidenceRecord[];
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({ evidence }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!evidence || evidence.length === 0) return null;

  return (
    <div className="bg-ocean-900/60 border border-ocean-700/80 rounded-xl overflow-hidden backdrop-blur-sm">
      {/* Accordion Toggle Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-2.5 flex items-center justify-between text-xs font-semibold text-slate-200 hover:bg-ocean-850 transition-colors"
      >
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-cyan-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10 9 9 9 8 9" />
          </svg>
          <span>Evidence Provenance & Verification Audit Trail ({evidence.length} items)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-slate-400 font-normal hidden sm:inline">Zero Hallucination Proof</span>
          <span className="text-slate-400 transform transition-transform duration-200">
            {isOpen ? '▲' : '▼'}
          </span>
        </div>
      </button>

      {/* Expanded Table */}
      {isOpen && (
        <div className="p-3 border-t border-ocean-800 overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-ocean-700/80 text-slate-400 font-medium text-[11px] uppercase tracking-wider">
                <th className="py-2 px-2.5">ID</th>
                <th className="py-2 px-2.5">Parameter</th>
                <th className="py-2 px-2.5">Observed Value</th>
                <th className="py-2 px-2.5">Authoritative Source</th>
                <th className="py-2 px-2.5">Type</th>
                <th className="py-2 px-2.5">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ocean-800/60 font-mono">
              {evidence.map((e) => (
                <tr key={e.evidence_id} className="hover:bg-ocean-850/50 transition-colors text-slate-300 text-[11px]">
                  <td className="py-2 px-2.5 font-bold text-cyan-400">{e.evidence_id}</td>
                  <td className="py-2 px-2.5 font-sans font-medium text-slate-200">{e.parameter}</td>
                  <td className="py-2 px-2.5 font-bold text-white">{String(e.value)} {e.unit}</td>
                  <td className="py-2 px-2.5 font-sans text-slate-300">{e.source}</td>
                  <td className="py-2 px-2.5">
                    <span className={`inline-block px-1.5 py-0.2 rounded text-[10px] uppercase font-sans font-semibold ${
                      e.source_type.includes('LIVE')
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                        : e.source_type.includes('CACHE')
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                    }`}>
                      {e.source_type}
                    </span>
                  </td>
                  <td className="py-2 px-2.5 text-slate-400">{e.source_timestamp.slice(0, 16)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
