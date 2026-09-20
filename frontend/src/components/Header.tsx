import React from 'react';
import { LandingCentre } from '../services/types';

interface HeaderProps {
  locations: LandingCentre[];
  selectedLocation: string;
  onSelectLocation: (locName: string) => void;
  selectedLanguage: string;
  onSelectLanguage: (lang: string) => void;
  isDemoMode: boolean;
  onToggleDemoMode: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  locations,
  selectedLocation,
  onSelectLocation,
  selectedLanguage,
  onSelectLanguage,
  isDemoMode,
  onToggleDemoMode,
}) => {
  return (
    <header className="bg-ocean-900 border-b border-ocean-700 px-6 py-3 flex flex-wrap items-center justify-between gap-4 select-none">
      {/* Brand & Identity */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-ocean-500 to-ocean-700 p-2 shadow-lg shadow-ocean-500/20 flex items-center justify-center">
          <svg className="w-full h-full text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M2 12h2a8 8 0 0 1 8 8v2" />
            <path d="M2 20h2a8 8 0 0 0 8-8V2" />
            <path d="M14 2h2a8 8 0 0 1 8 8v2" />
            <path d="M14 22h2a8 8 0 0 0 8-8v-2" />
            <circle cx="12" cy="12" r="3" />
          </svg>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-wider text-white font-mono">ORCA</h1>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-ocean-500/20 text-ocean-400 border border-ocean-500/30">
              SIH 2026
            </span>
          </div>
          <p className="text-xs text-slate-400 hidden sm:block">
            Marine Ecosystem Reasoning with Collaborative Agents
          </p>
        </div>
      </div>

      {/* Controls: Location, Language, Demo Mode */}
      <div className="flex items-center flex-wrap gap-3">
        {/* Landing Centre Selector */}
        <div className="flex items-center gap-1.5 bg-ocean-850 px-3 py-1.5 rounded-lg border border-ocean-700 text-xs">
          <svg className="w-3.5 h-3.5 text-ocean-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z" />
            <circle cx="12" cy="10" r="3" />
          </svg>
          <span className="text-slate-400 hidden md:inline">Harbour:</span>
          <select
            value={selectedLocation}
            onChange={(e) => onSelectLocation(e.target.value)}
            className="bg-transparent text-slate-200 focus:outline-none cursor-pointer font-medium"
          >
            {locations.length > 0 ? (
              locations.map((loc) => (
                <option key={loc.id} value={loc.location_name} className="bg-ocean-900 text-slate-200">
                  {loc.name} ({loc.district})
                </option>
              ))
            ) : (
              <option value="Ratnagiri" className="bg-ocean-900 text-slate-200">
                Mirkarwada, Ratnagiri
              </option>
            )}
          </select>
        </div>

        {/* Language Selector */}
        <div className="flex items-center gap-1.5 bg-ocean-850 px-3 py-1.5 rounded-lg border border-ocean-700 text-xs">
          <svg className="w-3.5 h-3.5 text-ocean-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="2" y1="12" x2="22" y2="12" />
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
          </svg>
          <select
            value={selectedLanguage}
            onChange={(e) => onSelectLanguage(e.target.value)}
            className="bg-transparent text-slate-200 focus:outline-none cursor-pointer font-medium"
          >
            <option value="auto" className="bg-ocean-900 text-slate-200">Auto (Detect)</option>
            <option value="en" className="bg-ocean-900 text-slate-200">English</option>
            <option value="mr" className="bg-ocean-900 text-slate-200">मराठी (Marathi)</option>
            <option value="hi" className="bg-ocean-900 text-slate-200">हिन्दी (Hindi)</option>
          </select>
        </div>

        {/* Demo Mode Toggle */}
        <button
          onClick={onToggleDemoMode}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all border ${
            isDemoMode
              ? 'bg-amber-500/20 text-amber-300 border-amber-500/50 shadow-sm shadow-amber-500/20'
              : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50'
          }`}
          title="Toggle between Live Multi-source APIs and Verified Cache Demo Mode"
        >
          <span className={`w-2 h-2 rounded-full ${isDemoMode ? 'bg-amber-400 animate-pulse' : 'bg-emerald-400'}`} />
          {isDemoMode ? 'Demo / Cached Data' : 'Live Marine Feed'}
        </button>
      </div>
    </header>
  );
};
