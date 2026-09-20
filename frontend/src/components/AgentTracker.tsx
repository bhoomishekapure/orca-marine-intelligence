import React from 'react';
import { AgentTimelineItem } from '../services/types';

interface AgentTrackerProps {
  timeline: AgentTimelineItem[];
  isLoading: boolean;
}

export const AgentTracker: React.FC<AgentTrackerProps> = ({ timeline, isLoading }) => {
  return (
    <div className="bg-ocean-900/70 border border-ocean-700/80 rounded-xl p-3.5 space-y-2.5 backdrop-blur-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Collaborative Agent Pipeline
          </h4>
        </div>
        {isLoading && (
          <span className="text-[11px] text-cyan-400 font-mono flex items-center gap-1.5">
            <svg className="animate-spin h-3.5 w-3.5 text-cyan-400" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Orchestrating...
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
        {timeline.map((item, idx) => (
          <div
            key={idx}
            className="bg-ocean-850/90 border border-ocean-700/60 rounded-lg p-2 flex flex-col justify-between text-xs transition-all hover:border-ocean-500/50"
          >
            <div className="flex items-center justify-between mb-1">
              <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                <span className="text-emerald-400 text-xs">✓</span>
                {item.label}
              </span>
              <span className="font-mono text-[10px] text-ocean-400 px-1.5 py-0.2 rounded bg-ocean-950 border border-ocean-800">
                {item.duration_ms} ms
              </span>
            </div>
            <div className="text-[11px] text-slate-400 truncate" title={item.summary}>
              {item.summary}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
