/**
 * API Service for Spotter HOS & ELD Planner.
 */

const API_BASE = '/api';

export async function planTrip(tripData) {
  const response = await fetch(`${API_BASE}/plan-trip/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(tripData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || errorData.details || `Server responded with status ${response.status}`);
  }

  return response.json();
}

export async function exportPdf(logSheets, tripSummary) {
  const response = await fetch(`${API_BASE}/export-pdf/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      log_sheets: logSheets,
      trip_summary: tripSummary || {},
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to generate PDF. Status: ${response.status}`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `drivers_daily_log_${new Date().toISOString().slice(0, 10)}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

export async function getGeocodeSuggestions(query) {
  if (!query || query.trim().length < 2) return [];
  try {
    const response = await fetch(`${API_BASE}/geocode/?q=${encodeURIComponent(query.trim())}`);
    if (!response.ok) return [];
    const data = await response.json();
    return data.results || [];
  } catch {
    return [];
  }
}

export async function getSampleTrips() {
  const response = await fetch(`${API_BASE}/sample-trips/`);
  if (!response.ok) throw new Error('Failed to load sample trips');
  const data = await response.json();
  return data.samples || [];
}
