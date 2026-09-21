import React from 'react';
import { Clock } from 'lucide-react';
import { formatDuration, formatMiles } from '../utils/formatters';

export default function ItineraryTimeline({ timeline }) {
  if (!timeline || timeline.length === 0) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-7 shadow-sm space-y-5">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div>
          <h3 className="text-base font-semibold text-slate-900">
            Trip Itinerary & Schedule
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Chronological breakdown of driving legs, mandatory rest breaks, fueling, and layovers.
          </p>
        </div>
        <span className="text-xs px-2.5 py-1 rounded bg-slate-100 text-slate-700 font-mono">
          {timeline.length} Events
        </span>
      </div>

      <div className="relative pl-6 space-y-3 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-px before:bg-slate-200">
        {timeline.map((event, idx) => (
          <div key={idx} className="relative">
            {/* Minimal Dot */}
            <div className="absolute -left-6 top-2.5 w-2 h-2 rounded-full bg-slate-400"></div>

            {/* Event Item */}
            <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-lg text-xs space-y-1.5 hover:bg-slate-100/70 transition-colors">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-white font-mono font-medium text-slate-700 border border-slate-200">
                    Line {event.status_line} • {event.status.replace(/_/g, ' ')}
                  </span>
                  <span className="font-semibold text-slate-900">
                    {event.remark}
                  </span>
                </div>
                <div className="text-xs text-slate-600 font-mono">
                  {event.start_formatted} → {event.end_formatted}
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] text-slate-500 pt-1 border-t border-slate-200/60 font-mono">
                <div>Location: <strong className="text-slate-800 font-sans">{event.location_name}</strong></div>
                <div>Duration: <strong className="text-slate-800">{formatDuration(event.duration_hours)}</strong></div>
                <div>Distance: <strong className="text-slate-800">{event.miles > 0 ? formatMiles(event.miles) : 'Stationary'}</strong></div>
                <div>Odometer: <strong className="text-slate-800">{event.odometer_end} mi</strong></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
