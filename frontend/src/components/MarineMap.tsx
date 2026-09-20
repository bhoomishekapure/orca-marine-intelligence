import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import { MapLayers } from '../services/types';

interface MarineMapProps {
  layers: MapLayers | null;
  queryFeatures: any;
  selectedCoordinates?: [number, number];
}

export const MarineMap: React.FC<MarineMapProps> = ({
  layers,
  queryFeatures,
  selectedCoordinates,
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const marker = useRef<maplibregl.Marker | null>(null);

  // Initialize Map
  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    // Carto Dark Matter style for dark maritime look
    const style: maplibregl.StyleSpecification = {
      version: 8,
      sources: {
        'osm-tiles': {
          type: 'raster',
          tiles: [
            'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
            'https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
            'https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png'
          ],
          tileSize: 256,
          attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
        }
      },
      layers: [
        {
          id: 'osm-tiles-layer',
          type: 'raster',
          source: 'osm-tiles',
          minzoom: 0,
          maxzoom: 19
        }
      ]
    };

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: style,
      center: [73.28, 16.99], // Ratnagiri coastal center
      zoom: 9.8,
      attributionControl: false
    });

    map.current.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-left');

    map.current.on('load', () => {
      // Setup dynamic sources and layers
      setupMapLayers();
    });

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  // Function to setup GeoJSON layers
  const setupMapLayers = () => {
    if (!map.current || !layers) return;

    // 1. Restricted Zones Layer (Red outline & fill)
    if (layers.restricted_zones && !map.current.getSource('restricted-zones-source')) {
      map.current.addSource('restricted-zones-source', {
        type: 'geojson',
        data: layers.restricted_zones
      });

      map.current.addLayer({
        id: 'restricted-zones-fill',
        type: 'fill',
        source: 'restricted-zones-source',
        paint: {
          'fill-color': '#ef4444',
          'fill-opacity': 0.25
        }
      });

      map.current.addLayer({
        id: 'restricted-zones-line',
        type: 'line',
        source: 'restricted-zones-source',
        paint: {
          'line-color': '#ef4444',
          'line-width': 2,
          'line-dasharray': [3, 2]
        }
      });

      // Popup on restricted zone click
      map.current.on('click', 'restricted-zones-fill', (e) => {
        if (!e.features || !e.features[0]) return;
        const props = e.features[0].properties;
        new maplibregl.Popup()
          .setLngLat(e.lngLat)
          .setHTML(`
            <div class="space-y-1">
              <span class="inline-block px-1.5 py-0.5 rounded text-[10px] font-bold bg-red-500/20 text-red-400 border border-red-500/30">
                RESTRICTED ZONE
              </span>
              <h4 class="font-bold text-sm text-white">${props.name}</h4>
              <p class="text-xs text-slate-300">${props.description}</p>
              <p class="text-[11px] text-slate-400"><strong>Authority:</strong> ${props.authority}</p>
            </div>
          `)
          .addTo(map.current!);
      });
    }

    // 2. Potential Fishing Zones (PFZ) Layer (Cyan outline & fill)
    if (layers.pfz_polygons && !map.current.getSource('pfz-source')) {
      map.current.addSource('pfz-source', {
        type: 'geojson',
        data: layers.pfz_polygons
      });

      map.current.addLayer({
        id: 'pfz-fill',
        type: 'fill',
        source: 'pfz-source',
        paint: {
          'fill-color': '#06b6d4',
          'fill-opacity': 0.25
        }
      });

      map.current.addLayer({
        id: 'pfz-line',
        type: 'line',
        source: 'pfz-source',
        paint: {
          'line-color': '#22d3ee',
          'line-width': 2
        }
      });

      map.current.on('click', 'pfz-fill', (e) => {
        if (!e.features || !e.features[0]) return;
        const props = e.features[0].properties;
        new maplibregl.Popup()
          .setLngLat(e.lngLat)
          .setHTML(`
            <div class="space-y-1">
              <span class="inline-block px-1.5 py-0.5 rounded text-[10px] font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                INCOIS PFZ ADVISORY
              </span>
              <h4 class="font-bold text-sm text-cyan-300">${props.name}</h4>
              <div class="grid grid-cols-2 gap-x-2 text-xs text-slate-200 mt-1">
                <div><strong>Distance:</strong> ${props.distance_km} km (${props.direction})</div>
                <div><strong>Water Depth:</strong> ${props.depth_range_m}</div>
                <div><strong>SST:</strong> ${props.sst_celsius}°C</div>
                <div><strong>Chlorophyll:</strong> ${props.chlorophyll_mg_m3} mg/m³</div>
              </div>
              <p class="text-[11px] text-slate-300 pt-1 border-t border-ocean-700"><strong>Target Species:</strong> ${props.target_species}</p>
            </div>
          `)
          .addTo(map.current!);
      });
    }

    // 3. Landing Centres (Harbours) Layer (Markers)
    if (layers.landing_centres && !map.current.getSource('landing-centres-source')) {
      map.current.addSource('landing-centres-source', {
        type: 'geojson',
        data: layers.landing_centres
      });

      map.current.addLayer({
        id: 'landing-centres-circle',
        type: 'circle',
        source: 'landing-centres-source',
        paint: {
          'circle-radius': 6,
          'circle-color': '#38bdf8',
          'circle-stroke-width': 2,
          'circle-stroke-color': '#ffffff'
        }
      });

      map.current.on('click', 'landing-centres-circle', (e) => {
        if (!e.features || !e.features[0]) return;
        const props = e.features[0].properties;
        new maplibregl.Popup()
          .setLngLat(e.lngLat)
          .setHTML(`
            <div class="space-y-1">
              <span class="inline-block px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                FISHING HARBOUR
              </span>
              <h4 class="font-bold text-sm text-white">${props.name}</h4>
              <p class="text-xs text-slate-300">${props.category} — ${props.district} District</p>
              <p class="text-xs text-slate-400">Active Crafts: ${props.active_vessels || 'N/A'}</p>
            </div>
          `)
          .addTo(map.current!);
      });
    }

    // 4. Query Dynamic Features (Navigation Line)
    if (!map.current.getSource('query-features-source')) {
      map.current.addSource('query-features-source', {
        type: 'geojson',
        data: queryFeatures || { type: 'FeatureCollection', features: [] }
      });

      map.current.addLayer({
        id: 'query-features-line',
        type: 'line',
        source: 'query-features-source',
        filter: ['==', '$type', 'LineString'],
        paint: {
          'line-color': '#38bdf8',
          'line-width': 3,
          'line-dasharray': [2, 2]
        }
      });
    }
  };

  // Update dynamic layers when layers or queryFeatures change
  useEffect(() => {
    if (!map.current || !map.current.isStyleLoaded()) return;
    setupMapLayers();

    const qSource = map.current.getSource('query-features-source') as maplibregl.GeoJSONSource;
    if (qSource && queryFeatures) {
      qSource.setData(queryFeatures);

      // If navigation vector exists, fly smoothly to encompass it
      const lineFeat = queryFeatures.features?.find((f: any) => f.geometry.type === 'LineString');
      if (lineFeat) {
        const coords = lineFeat.geometry.coordinates;
        const bounds = coords.reduce(
          (b: maplibregl.LngLatBounds, c: [number, number]) => b.extend(c),
          new maplibregl.LngLatBounds(coords[0], coords[0])
        );
        map.current.fitBounds(bounds, { padding: 60, duration: 1200 });
      }
    }
  }, [layers, queryFeatures]);

  return (
    <div className="relative w-full h-full min-h-[420px] rounded-xl overflow-hidden border border-ocean-700 shadow-xl">
      <div ref={mapContainer} className="w-full h-full" />
      
      {/* Map Legend Overlay */}
      <div className="absolute bottom-4 left-4 bg-ocean-900/90 backdrop-blur-md border border-ocean-700/80 rounded-lg p-3 text-xs space-y-2 shadow-xl pointer-events-none select-none">
        <div className="font-semibold text-slate-200 tracking-wider text-[11px] uppercase border-b border-ocean-700/60 pb-1">
          Marine Map Layers
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-sky-400 border border-white" />
          <span className="text-slate-300">Fish Landing Centre / Harbour</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-2.5 rounded bg-cyan-500/40 border border-cyan-400" />
          <span className="text-slate-300">INCOIS PFZ (Potential Fishing Zone)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-2.5 rounded bg-red-500/40 border border-red-500" />
          <span className="text-slate-300">Restricted Marine Sanctuary (No Fishing)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-0.5 border-t-2 border-dashed border-sky-400" />
          <span className="text-slate-300">Calculated PFZ Bearing Vector</span>
        </div>
      </div>
    </div>
  );
};
