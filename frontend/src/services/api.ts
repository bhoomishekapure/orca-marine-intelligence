import { QueryResponse, LandingCentre, MapLayers, MarineConditions, HealthStatus } from './types';

const API_BASE = '/api';

export async function submitQuery(
  query: string,
  sessionId: string = 'orca-default-session',
  locationOverride?: string,
  languageOverride?: string,
  forceDemoMode?: boolean
): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      session_id: sessionId,
      location_override: locationOverride || null,
      language_override: languageOverride || 'auto',
      force_demo_mode: forceDemoMode ?? false
    })
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Network request failed' }));
    throw new Error(err.detail || 'Failed to submit query to ORCA');
  }

  return response.json();
}

export async function fetchLocations(): Promise<LandingCentre[]> {
  const response = await fetch(`${API_BASE}/locations`);
  if (!response.ok) throw new Error('Failed to fetch coastal locations');
  return response.json();
}

export async function fetchMapLayers(): Promise<MapLayers> {
  const response = await fetch(`${API_BASE}/map/layers`);
  if (!response.ok) throw new Error('Failed to fetch map layers');
  return response.json();
}

export async function fetchConditions(name: string, lat: number, lon: number): Promise<MarineConditions> {
  const params = new URLSearchParams({ name, lat: lat.toString(), lon: lon.toString() });
  const response = await fetch(`${API_BASE}/marine-conditions?${params.toString()}`);
  if (!response.ok) throw new Error('Failed to fetch marine conditions');
  return response.json();
}

export async function fetchHealth(): Promise<HealthStatus> {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) throw new Error('Failed to fetch system health');
  return response.json();
}
