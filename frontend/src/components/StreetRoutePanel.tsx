import React, { useState } from 'react';
import { Navigation, ChevronDown, ChevronUp, AlertTriangle, CheckCircle, Truck, User } from 'lucide-react';

// ─── Interfaces ──────────────────────────────────────────────

interface OsrmStep {
  name: string;
  distance: number;   // metres
  duration: number;   // seconds
  maneuver: { type: string; modifier?: string };
}

interface StreetRoute {
  coords: [number, number][];
  steps: OsrmStep[];
  totalDistanceM: number;
  totalDurationS: number;
  snapped: boolean;
}

interface RouteData {
  route_id?: number;
  truck_id: string;
  driver: string;
  distance_km: number;
  fuel_liters: number;
  duration_hours: number;
  path: { bin_id: string; latitude: number; longitude: number; load_at_node: number }[];
}

interface StreetRoutePanelProps {
  routes: RouteData[];
  streetRoutes: Record<string, StreetRoute>;
  fetchingRoutes: boolean;
}

// ─── Utilities ───────────────────────────────────────────────

const ROUTE_COLORS = ['#06b6d4', '#a855f7', '#f97316', '#ec4899', '#10b981'];

const formatDuration = (s: number): string => {
  if (s < 60) return `${Math.round(s)}s`;
  if (s < 3600) return `${Math.round(s / 60)} min`;
  const h = Math.floor(s / 3600);
  const m = Math.round((s % 3600) / 60);
  return `${h}h ${m}m`;
};

const formatDistance = (m: number): string => {
  if (m < 1000) return `${Math.round(m)} m`;
  return `${(m / 1000).toFixed(2)} km`;
};

const maneuverIcon = (step: OsrmStep): string => {
  const { type, modifier } = step.maneuver;
  if (type === 'depart') return '🚀';
  if (type === 'arrive') return '🏁';
  if (type === 'turn') {
    if (modifier === 'left' || modifier === 'sharp left') return '↰';
    if (modifier === 'right' || modifier === 'sharp right') return '↱';
    if (modifier === 'slight left') return '↖';
    if (modifier === 'slight right') return '↗';
    return '⬆';
  }
  if (type === 'new name' || type === 'continue') return '⬆';
  if (type === 'merge') return '⤵';
  if (type === 'roundabout' || type === 'rotary') return '🔄';
  if (type === 'fork') return '⑂';
  if (type === 'end of road') return '⬆';
  return '⬆';
};

// ─── Single Route Card ────────────────────────────────────────

interface RouteCardProps {
  route: RouteData;
  sr: StreetRoute | undefined;
  color: string;
}

const RouteCard: React.FC<RouteCardProps> = ({ route, sr, color }) => {
  const [expanded, setExpanded] = useState(false);

  const displayedSteps = sr?.steps.filter(s => s.name && s.name !== '') ?? [];
  const totalM = sr?.totalDistanceM ?? route.distance_km * 1000;
  const totalS = sr?.totalDurationS ?? route.duration_hours * 3600;

  return (
    <div style={{
      background: 'var(--bg-primary)',
      border: `1px solid ${expanded ? color + '88' : 'var(--border-glass)'}`,
      borderRadius: '12px',
      overflow: 'hidden',
      transition: 'all 0.25s ease',
      boxShadow: expanded ? `0 0 20px ${color}20` : 'var(--shadow-sm)',
    }}>
      {/* Header */}
      <button
        onClick={() => setExpanded(p => !p)}
        style={{
          width: '100%', background: 'none', border: 'none', cursor: 'pointer',
          padding: '16px', display: 'flex', alignItems: 'center', gap: '12px',
          borderBottom: expanded ? `1px solid var(--border-glass)` : 'none',
        }}
      >
        {/* Colour dot */}
        <div style={{
          width: 12, height: 12, borderRadius: '50%',
          background: color, boxShadow: `0 0 12px ${color}`, flexShrink: 0,
        }} />

        {/* Truck info */}
        <div style={{ flex: 1, textAlign: 'left' }}>
          <div style={{ fontFamily: 'Outfit', fontWeight: 800, fontSize: '15px', color: 'var(--text-primary)' }}>
            {route.truck_id}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <User size={12} color="var(--accent-cyan)" /> {route.driver} · <strong style={{ color: 'var(--text-primary)' }}>{route.path.length - 2}</strong> stops
          </div>
        </div>

        {/* Stats */}
        <div style={{ textAlign: 'right', marginRight: '8px' }}>
          <div style={{ fontSize: '13px', fontWeight: 800, color: color, fontFamily: 'JetBrains Mono, monospace' }}>
            {formatDistance(totalM)}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '1px' }}>
            {formatDuration(totalS)}
          </div>
        </div>

        {/* Snapped badge */}
        <div style={{ flexShrink: 0 }}>
          {sr?.snapped ? (
            <CheckCircle size={16} color="var(--color-success)" />
          ) : (
            <AlertTriangle size={16} color="var(--color-warning)" />
          )}
        </div>

        {expanded ? <ChevronUp size={16} color="var(--text-muted)" /> : <ChevronDown size={16} color="var(--text-muted)" />}
      </button>

      {/* Expanded turn-by-turn */}
      {expanded && (
        <div style={{ padding: '0 16px 16px 16px', background: 'var(--bg-secondary)' }}>
          {/* Route quality note */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            padding: '8px 12px', borderRadius: '8px', margin: '12px 0',
            background: sr?.snapped ? 'var(--color-success-dim)' : 'var(--color-warning-dim)',
            border: `1px solid ${sr?.snapped ? 'rgba(16,185,129,0.3)' : 'rgba(245,158,11,0.3)'}`,
          }}>
            {sr?.snapped ? (
              <>
                <CheckCircle size={13} color="var(--color-success)" />
                <span style={{ fontSize: '11.5px', color: 'var(--color-success)', fontWeight: 700 }}>Street-snapped via OSRM (real road network)</span>
              </>
            ) : (
              <>
                <AlertTriangle size={13} color="var(--color-warning)" />
                <span style={{ fontSize: '11.5px', color: 'var(--color-warning)', fontWeight: 700 }}>Straight-line estimate (OSRM unavailable)</span>
              </>
            )}
          </div>

          {/* Turn-by-turn list */}
          {displayedSteps.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', maxHeight: '300px', overflowY: 'auto' }}>
              {displayedSteps.map((step, i) => (
                <div key={i} style={{
                  display: 'flex', alignItems: 'center', gap: '10px',
                  padding: '7px 10px', borderRadius: '8px',
                  background: i % 2 === 0 ? 'rgba(255,255,255,0.03)' : 'transparent',
                  border: '1px solid rgba(255,255,255,0.03)',
                }}>
                  {/* Maneuver icon */}
                  <span style={{ fontSize: '14px', width: '20px', textAlign: 'center', flexShrink: 0 }}>
                    {maneuverIcon(step)}
                  </span>

                  {/* Street name */}
                  <div style={{ flex: 1, overflow: 'hidden' }}>
                    <div style={{
                      fontSize: '12.5px', fontWeight: 700, color: 'var(--text-primary)',
                      overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                    }}>
                      {step.name || '(unnamed road)'}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '1px' }}>
                      {step.maneuver.type}{step.maneuver.modifier ? ` ${step.maneuver.modifier}` : ''}
                    </div>
                  </div>

                  {/* Distance + duration */}
                  <div style={{ textAlign: 'right', flexShrink: 0 }}>
                    <div style={{ fontSize: '12px', fontWeight: 700, color: color, fontFamily: 'JetBrains Mono, monospace' }}>
                      {formatDistance(step.distance)}
                    </div>
                    <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                      {formatDuration(step.duration)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px', padding: '20px' }}>
              No turn-by-turn data available.<br />
              <span style={{ fontSize: '11px', color: 'var(--accent-cyan)' }}>Click "Optimize Routes" to generate street-snapped routes.</span>
            </div>
          )}

          {/* Fuel summary */}
          <div style={{
            display: 'flex', gap: '10px', marginTop: '12px',
          }}>
            {[
              { label: 'Fuel Consumed', value: `${route.fuel_liters} L` },
              { label: 'Bin Stops', value: `${route.path.length - 2}` },
              { label: 'Road Segments', value: `${displayedSteps.length}` },
            ].map(stat => (
              <div key={stat.label} style={{
                flex: 1, background: 'var(--bg-primary)',
                border: '1px solid var(--border-glass)',
                borderRadius: '8px', padding: '8px 10px', textAlign: 'center',
              }}>
                <div style={{ fontSize: '14px', fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'JetBrains Mono, monospace' }}>
                  {stat.value}
                </div>
                <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px', fontWeight: 600 }}>{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// ─── Main Panel ───────────────────────────────────────────────

const StreetRoutePanel: React.FC<StreetRoutePanelProps> = ({ routes, streetRoutes, fetchingRoutes }) => {
  const snappedCount = Object.values(streetRoutes).filter(r => r.snapped).length;
  const totalDistanceM = Object.values(streetRoutes).reduce((sum, r) => sum + r.totalDistanceM, 0);
  const totalDurationS = Object.values(streetRoutes).reduce((sum, r) => sum + r.totalDurationS, 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: 'var(--bg-base)' }}>
      {/* Panel header */}
      <div style={{
        padding: '20px 24px',
        borderBottom: '1px solid var(--border-glass)',
        display: 'flex', alignItems: 'center', gap: '12px',
        background: 'var(--bg-primary)',
      }}>
        <Navigation size={20} color="var(--accent-cyan)" />
        <div>
          <div style={{ fontFamily: 'Outfit', fontWeight: 800, fontSize: '17px', color: 'var(--text-primary)' }}>
            Street Route Details
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Real road distances calculated via OSRM Engine
          </div>
        </div>
        {fetchingRoutes && (
          <div style={{
            marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '8px',
            fontSize: '12px', color: 'var(--accent-cyan)', fontWeight: 600,
          }}>
            <div style={{
              width: 10, height: 10, border: '2px solid var(--accent-cyan)',
              borderTopColor: 'transparent', borderRadius: '50%',
              animation: 'spin 0.7s linear infinite',
            }} />
            Calculating Routes...
          </div>
        )}
      </div>

      {/* Summary bar */}
      {routes.length > 0 && (
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '12px', padding: '16px 20px',
          borderBottom: '1px solid var(--border-glass)',
          background: 'var(--bg-secondary)',
        }}>
          {[
            { label: 'Total Distance', value: formatDistance(totalDistanceM), color: 'var(--accent-cyan)' },
            { label: 'Est. Total Time', value: formatDuration(totalDurationS), color: 'var(--accent-purple)' },
            { label: 'Street-Snapped', value: `${snappedCount}/${routes.length}`, color: snappedCount === routes.length ? 'var(--color-success)' : 'var(--color-warning)' },
          ].map(stat => (
            <div key={stat.label} style={{
              background: 'var(--bg-primary)',
              border: '1px solid var(--border-glass)',
              borderRadius: '12px', padding: '12px 14px', textAlign: 'center',
              boxShadow: 'var(--shadow-sm)',
            }}>
              <div style={{ fontSize: '18px', fontWeight: 800, color: stat.color, fontFamily: 'Outfit' }}>
                {stat.value}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px', fontWeight: 600 }}>{stat.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Route cards */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {routes.length === 0 ? (
          <div style={{
            flex: 1, display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
            color: 'var(--text-muted)', textAlign: 'center', gap: '14px', padding: '40px',
          }}>
            <Navigation size={40} style={{ strokeWidth: 1.2, color: 'var(--accent-cyan)' }} />
            <div>
              <p style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>
                No active routes generated yet
              </p>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', maxWidth: '380px' }}>
                Click <strong style={{ color: 'var(--accent-cyan)' }}>Optimize Routes</strong> in the left sidebar to trigger AI-optimized truck routing.
              </p>
            </div>
          </div>
        ) : (
          routes.map((route, idx) => (
            <RouteCard
              key={route.truck_id}
              route={route}
              sr={streetRoutes[route.truck_id]}
              color={ROUTE_COLORS[idx % ROUTE_COLORS.length]}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default StreetRoutePanel;
