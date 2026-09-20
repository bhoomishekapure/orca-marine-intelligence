import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { MarineMap } from './components/MarineMap';
import { ConditionsGrid } from './components/ConditionsGrid';
import { ChatPanel, ChatMessage } from './components/ChatPanel';
import { AgentTracker } from './components/AgentTracker';
import { RiskCard } from './components/RiskCard';
import { EvidenceDrawer } from './components/EvidenceDrawer';
import {
  LandingCentre,
  MapLayers,
  MarineConditions,
  RiskAssessment,
  AgentTimelineItem,
  EvidenceRecord,
} from './services/types';
import {
  fetchLocations,
  fetchMapLayers,
  fetchConditions,
  submitQuery,
} from './services/api';

export const App: React.FC = () => {
  // State
  const [locations, setLocations] = useState<LandingCentre[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<string>('Ratnagiri');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('auto');
  const [isDemoMode, setIsDemoMode] = useState<boolean>(false);

  const [mapLayers, setMapLayers] = useState<MapLayers | null>(null);
  const [queryFeatures, setQueryFeatures] = useState<any>(null);
  const [conditions, setConditions] = useState<MarineConditions | null>(null);

  const [assessment, setAssessment] = useState<RiskAssessment | null>(null);
  const [timeline, setTimeline] = useState<AgentTimelineItem[]>([]);
  const [evidence, setEvidence] = useState<EvidenceRecord[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'orca',
      text: 'Welcome to ORCA (Marine Ecosystem Reasoning with Collaborative Agents). Ask any query regarding sea safety, Potential Fishing Zones (PFZ), or marine conditions in English, Marathi (मराठी), or Hindi (हिन्दी).',
      timestamp: 'Ready'
    }
  ]);

  // Initial Data Fetching
  useEffect(() => {
    const initData = async () => {
      try {
        const [locs, layers, conds] = await Promise.all([
          fetchLocations().catch(() => []),
          fetchMapLayers().catch(() => null),
          fetchConditions('Ratnagiri', 16.99, 73.30).catch(() => null)
        ]);

        setLocations(locs);
        setMapLayers(layers);
        setConditions(conds);
      } catch (err) {
        console.error('Error initializing ORCA data:', err);
      }
    };
    initData();
  }, []);

  // Handle Location Change
  const handleLocationChange = async (newLocName: string) => {
    setSelectedLocation(newLocName);
    const locObj = locations.find((l) => l.location_name === newLocName);
    const lat = locObj?.latitude || 16.99;
    const lon = locObj?.longitude || 73.30;
    try {
      const conds = await fetchConditions(newLocName, lat, lon);
      setConditions(conds);
    } catch (e) {
      console.warn('Could not refresh conditions for location:', e);
    }
  };

  // Handle Query Submission
  const handleSendMessage = async (queryText: string) => {
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const resp = await submitQuery(
        queryText,
        'orca-sih-session',
        selectedLocation,
        selectedLanguage,
        isDemoMode
      );

      const orcaMsg: ChatMessage = {
        id: `orca-${Date.now()}`,
        sender: 'orca',
        text: resp.answer,
        intent: resp.intent,
        language: resp.query_language,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        executionMs: resp.execution_time_ms
      };

      setMessages((prev) => [...prev, orcaMsg]);
      setAssessment(resp.risk_assessment);
      setTimeline(resp.agent_timeline);
      setEvidence(resp.evidence);
      setQueryFeatures(resp.map_features);

      // Refresh conditions for coordinates
      const locObj = locations.find((l) => l.location_name === selectedLocation);
      const lat = locObj?.latitude || 16.99;
      const lon = locObj?.longitude || 73.30;
      fetchConditions(selectedLocation, lat, lon).then(setConditions).catch(() => {});
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `error-${Date.now()}`,
        sender: 'orca',
        text: `Error processing query: ${err.message || 'System unavailable'}. Please verify backend connection.`,
        timestamp: 'Error'
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-ocean-950 overflow-hidden select-none">
      {/* Top Header */}
      <Header
        locations={locations}
        selectedLocation={selectedLocation}
        onSelectLocation={handleLocationChange}
        selectedLanguage={selectedLanguage}
        onSelectLanguage={setSelectedLanguage}
        isDemoMode={isDemoMode}
        onToggleDemoMode={() => setIsDemoMode(!isDemoMode)}
      />

      {/* Main Dual Workspace */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 p-4 overflow-hidden">
        {/* Left Column: Telemetry + Interactive Marine Map + Evidence (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-3 h-full overflow-y-auto pr-1">
          {/* Live Oceanic Telemetry Grid */}
          <ConditionsGrid conditions={conditions} />

          {/* Interactive MapLibre GL Map */}
          <div className="flex-1 min-h-[380px]">
            <MarineMap
              layers={mapLayers}
              queryFeatures={queryFeatures}
            />
          </div>

          {/* Evidence Provenance Audit Drawer */}
          <EvidenceDrawer evidence={evidence} />
        </div>

        {/* Right Column: Chat Dialogue + Agent Pipeline + Decision Risk Card (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-3 h-full overflow-hidden">
          {/* Agent Pipeline Activity Indicator */}
          {timeline.length > 0 && (
            <AgentTracker timeline={timeline} isLoading={isLoading} />
          )}

          {/* Deterministic Decision Risk Card */}
          {assessment && (
            <RiskCard assessment={assessment} />
          )}

          {/* Conversational Assistant */}
          <div className="flex-1 min-h-[300px]">
            <ChatPanel
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          </div>
        </div>
      </main>
    </div>
  );
};
