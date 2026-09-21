/**
 * Formatting utilities for dates, times, durations, and distances.
 */

export function formatDuration(hoursDecimal) {
  if (hoursDecimal === undefined || hoursDecimal === null) return '0h 00m';
  const hours = Math.floor(hoursDecimal);
  const minutes = Math.round((hoursDecimal - hours) * 60);
  return `${hours}h ${minutes.toString().padStart(2, '0')}m`;
}

export function formatMiles(miles) {
  if (miles === undefined || miles === null) return '0 mi';
  return `${Number(miles).toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })} mi`;
}

export function formatHourDecToTime(hoursDecimal) {
  const totalMinutes = Math.round(hoursDecimal * 60);
  const hours = Math.floor(totalMinutes / 60) % 24;
  const minutes = totalMinutes % 60;
  const period = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 === 0 ? 12 : hours % 12;
  return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`;
}

export function getStatusColor(status) {
  switch (status) {
    case 'OFF_DUTY':
      return {
        bg: 'bg-slate-700',
        text: 'text-slate-300',
        border: 'border-slate-600',
        badge: 'bg-slate-800 text-slate-300 border-slate-700',
        line: '#64748b'
      };
    case 'SLEEPER_BERTH':
      return {
        bg: 'bg-purple-900/60',
        text: 'text-purple-300',
        border: 'border-purple-600',
        badge: 'bg-purple-950/80 text-purple-300 border-purple-800',
        line: '#a855f7'
      };
    case 'DRIVING':
      return {
        bg: 'bg-emerald-950/60',
        text: 'text-emerald-300',
        border: 'border-emerald-600',
        badge: 'bg-emerald-950/80 text-emerald-300 border-emerald-800',
        line: '#10b981'
      };
    case 'ON_DUTY_NOT_DRIVING':
      return {
        bg: 'bg-amber-950/60',
        text: 'text-amber-300',
        border: 'border-amber-600',
        badge: 'bg-amber-950/80 text-amber-300 border-amber-800',
        line: '#f59e0b'
      };
    default:
      return {
        bg: 'bg-slate-800',
        text: 'text-slate-300',
        border: 'border-slate-700',
        badge: 'bg-slate-800 text-slate-300',
        line: '#94a3b8'
      };
  }
}
