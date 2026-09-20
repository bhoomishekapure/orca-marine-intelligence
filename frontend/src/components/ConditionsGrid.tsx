import React from 'react';
import { MarineConditions } from '../services/types';

interface ConditionsGridProps {
  conditions: MarineConditions | null;
}

export const ConditionsGrid: React.FC<ConditionsGridProps> = ({ conditions }) => {
  if (!conditions) return null;

  const { ocean, weather, location } = conditions;

  return (
    <div className="bg-ocean-900/70 border border-ocean-700/80 rounded-xl p-3.5 space-y-2 backdrop-blur-sm">
      <div className="flex items-center justify-between text-xs">
        <span className="font-semibold text-slate-300">
          Ocean State Telemetry — <span className="text-cyan-400 font-bold">{location.name}</span>
        </span>
        <span className="text-[11px] text-slate-400 font-mono">
          Updated: {conditions.timestamp.slice(11, 16)} UTC
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        {/* Wave Height */}
        <div className="bg-ocean-850/80 border border-ocean-700/60 rounded-lg p-2.5 space-y-1">
          <div className="text-[11px] text-slate-400 font-medium">Wave Height</div>
          <div className="text-lg font-bold font-mono text-cyan-300">
            {ocean.significant_wave_height_m.toFixed(1)} <span className="text-xs font-sans text-slate-400">m</span>
          </div>
          <div className="text-[10px] text-slate-400">Max: {ocean.maximum_wave_height_m ? `${ocean.maximum_wave_height_m}m` : 'Normal'}</div>
        </div>

        {/* Wave Period */}
        <div className="bg-ocean-850/80 border border-ocean-700/60 rounded-lg p-2.5 space-y-1">
          <div className="text-[11px] text-slate-400 font-medium">Wave Period</div>
          <div className="text-lg font-bold font-mono text-cyan-300">
            {ocean.wave_period_s.toFixed(1)} <span className="text-xs font-sans text-slate-400">s</span>
          </div>
          <div className="text-[10px] text-slate-400">Dir: {ocean.wave_direction_deg.toFixed(0)}°</div>
        </div>

        {/* Wind Speed */}
        <div className="bg-ocean-850/80 border border-ocean-700/60 rounded-lg p-2.5 space-y-1">
          <div className="text-[11px] text-slate-400 font-medium">Wind Speed</div>
          <div className="text-lg font-bold font-mono text-sky-300">
            {weather.wind_speed_kmh.toFixed(1)} <span className="text-xs font-sans text-slate-400">km/h</span>
          </div>
          <div className="text-[10px] text-slate-400">From {weather.wind_direction_cardinal} ({weather.wind_direction_deg.toFixed(0)}°)</div>
        </div>

        {/* Swell Height */}
        <div className="bg-ocean-850/80 border border-ocean-700/60 rounded-lg p-2.5 space-y-1">
          <div className="text-[11px] text-slate-400 font-medium">Swell Height</div>
          <div className="text-lg font-bold font-mono text-sky-300">
            {ocean.swell_wave_height_m.toFixed(1)} <span className="text-xs font-sans text-slate-400">m</span>
          </div>
          <div className="text-[10px] text-slate-400">Period: {ocean.swell_period_s.toFixed(1)}s</div>
        </div>

        {/* Sea Surface Temp */}
        <div className="bg-ocean-850/80 border border-ocean-700/60 rounded-lg p-2.5 space-y-1">
          <div className="text-[11px] text-slate-400 font-medium">Sea Temp (SST)</div>
          <div className="text-lg font-bold font-mono text-emerald-300">
            {ocean.sea_surface_temperature_c.toFixed(1)} <span className="text-xs font-sans text-slate-400">°C</span>
          </div>
          <div className="text-[10px] text-slate-400">Thermal Front</div>
        </div>

        {/* Sky / Weather */}
        <div className="bg-ocean-850/80 border border-ocean-700/60 rounded-lg p-2.5 space-y-1">
          <div className="text-[11px] text-slate-400 font-medium">Weather</div>
          <div className="text-sm font-semibold text-slate-200 truncate" title={weather.weather_description}>
            {weather.weather_description}
          </div>
          <div className="text-[10px] text-emerald-400 font-semibold">
            {ocean.ocean_state_alert || 'Alert: Normal'}
          </div>
        </div>
      </div>
    </div>
  );
};
