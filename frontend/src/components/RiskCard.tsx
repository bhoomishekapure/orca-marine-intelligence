import React from 'react';
import { RiskAssessment } from '../services/types';

interface RiskCardProps {
  assessment: RiskAssessment | null;
}

export const RiskCard: React.FC<RiskCardProps> = ({ assessment }) => {
  if (!assessment) return null;

  const colorStyles = {
    green: {
      border: 'border-emerald-500/40',
      bg: 'bg-emerald-950/20',
      badge: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      meter: 'bg-emerald-500',
      icon: '✓'
    },
    yellow: {
      border: 'border-amber-500/40',
      bg: 'bg-amber-950/20',
      badge: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      meter: 'bg-amber-500',
      icon: '⚠'
    },
    red: {
      border: 'border-red-500/40',
      bg: 'bg-red-950/20',
      badge: 'bg-red-500/20 text-red-400 border-red-500/30',
      meter: 'bg-red-500',
      icon: '✕'
    },
    gray: {
      border: 'border-slate-700',
      bg: 'bg-slate-900/40',
      badge: 'bg-slate-700/40 text-slate-400 border-slate-600',
      meter: 'bg-slate-500',
      icon: '?'
    }
  };

  const currentTheme = colorStyles[assessment.status_color as keyof typeof colorStyles] || colorStyles.gray;

  return (
    <div className={`rounded-xl border ${currentTheme.border} ${currentTheme.bg} p-4 space-y-3.5 backdrop-blur-sm shadow-lg`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs ${currentTheme.badge}`}>
            {currentTheme.icon}
          </span>
          <h3 className="font-semibold text-sm text-slate-100">
            Deterministic Marine Decision Assessment
          </h3>
        </div>
        <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider border ${currentTheme.badge}`}>
          {assessment.risk_level}
        </span>
      </div>

      {/* Headline */}
      <div className="text-sm font-medium text-slate-200">
        {assessment.headline}
      </div>

      {/* Risk Score Progress */}
      <div className="space-y-1">
        <div className="flex justify-between text-xs text-slate-400">
          <span>Evaluated Risk Score</span>
          <span className="font-mono font-bold text-slate-200">{assessment.risk_score} / 100</span>
        </div>
        <div className="w-full bg-ocean-950 rounded-full h-2 overflow-hidden border border-ocean-800">
          <div
            className={`h-full transition-all duration-500 ${currentTheme.meter}`}
            style={{ width: `${assessment.risk_score}%` }}
          />
        </div>
      </div>

      {/* Contributing Factors Table */}
      <div className="space-y-1.5">
        <h4 className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
          Evaluated Threshold Factors
        </h4>
        <div className="bg-ocean-900/80 rounded-lg border border-ocean-700/60 divide-y divide-ocean-800/80 overflow-hidden text-xs">
          {assessment.factors.map((f, i) => (
            <div key={i} className="p-2 flex items-center justify-between">
              <div className="space-y-0.5">
                <div className="font-medium text-slate-200">{f.parameter}</div>
                <div className="text-[11px] text-slate-400">Threshold: {f.threshold}</div>
              </div>
              <div className="text-right space-y-0.5">
                <div className="font-mono font-bold text-slate-100">{f.value}</div>
                <span className={`inline-block px-1.5 py-0.2 rounded text-[10px] font-semibold uppercase ${
                  f.status === 'SAFE' || f.status === 'CLEAR'
                    ? 'text-emerald-400 bg-emerald-500/10'
                    : f.status === 'CAUTION'
                    ? 'text-amber-400 bg-amber-500/10'
                    : 'text-red-400 bg-red-500/10'
                }`}>
                  {f.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      {assessment.recommendations.length > 0 && (
        <div className="space-y-1 text-xs">
          <h4 className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
            Actionable Recommendations
          </h4>
          <ul className="list-disc list-inside space-y-1 text-slate-300">
            {assessment.recommendations.map((rec, idx) => (
              <li key={idx} className="leading-relaxed">{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
