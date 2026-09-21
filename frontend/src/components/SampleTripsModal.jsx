import React, { useEffect, useState } from 'react';
import { X, Sparkles, ArrowRight } from 'lucide-react';
import { getSampleTrips } from '../services/api';

export default function SampleTripsModal({ isOpen, onClose, onSelectSample }) {
  const [samples, setSamples] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && samples.length === 0) {
      setLoading(true);
      getSampleTrips()
        .then(data => setSamples(data))
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fade-in">
      <div className="bg-white border border-slate-200 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-xl p-6 relative text-slate-800 space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-slate-100 text-slate-700">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">Pre-Configured Sample Trips</h2>
              <p className="text-xs text-slate-500">Select a trip to test routing, HOS clocks, and multi-day log sheets</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* List of Samples */}
        <div className="space-y-2.5">
          {samples.map((s, idx) => (
            <div
              key={idx}
              onClick={() => {
                onSelectSample(s);
                onClose();
              }}
              className="p-4 rounded-lg bg-slate-50 border border-slate-200 hover:border-slate-400 hover:bg-white cursor-pointer transition-all space-y-1.5"
            >
              <div className="flex items-center justify-between">
                <h4 className="font-semibold text-slate-900 text-sm">
                  {s.title}
                </h4>
                <div className="flex items-center gap-1 text-xs text-slate-700 font-medium">
                  <span>Load</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </div>

              <p className="text-xs text-slate-600">
                {s.description}
              </p>

              <div className="flex items-center flex-wrap gap-2 text-[11px] text-slate-500 pt-1 font-mono">
                <span>Start: <strong>{s.current_location}</strong></span>
                <span>→</span>
                <span>Pickup: <strong>{s.pickup_location}</strong></span>
                <span>→</span>
                <span>Dropoff: <strong>{s.dropoff_location}</strong></span>
                <span>•</span>
                <span>Cycle Used: <strong>{s.current_cycle_used} hrs</strong></span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
