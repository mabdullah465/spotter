import React from 'react';
import { X, BookOpen } from 'lucide-react';

export default function HosRulesGuideModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fade-in">
      <div className="bg-white border border-slate-200 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-xl p-6 relative text-slate-800 space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-slate-100 text-slate-700">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">FMCSA Hours of Service (HOS) Rules</h2>
              <p className="text-xs text-slate-500">49 CFR Part 395 Property-Carrying Driver Standards</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Rules Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 text-xs">
          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-1">
            <strong className="text-slate-900 font-semibold block text-sm">11-Hour Driving Limit</strong>
            <p className="text-slate-600 leading-relaxed">
              May drive a maximum of 11 hours after 10 consecutive hours off duty or sleeper berth.
            </p>
          </div>

          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-1">
            <strong className="text-slate-900 font-semibold block text-sm">14-Hour Duty Window</strong>
            <p className="text-slate-600 leading-relaxed">
              May not drive beyond the 14th consecutive hour after coming on duty, following 10 hours off duty.
            </p>
          </div>

          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-1">
            <strong className="text-slate-900 font-semibold block text-sm">30-Minute Rest Break</strong>
            <p className="text-slate-600 leading-relaxed">
              Driving is not permitted if more than 8 cumulative hours have passed without at least a 30-minute interruption.
            </p>
          </div>

          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-1">
            <strong className="text-slate-900 font-semibold block text-sm">70-Hour / 8-Day Limit</strong>
            <p className="text-slate-600 leading-relaxed">
              May not drive after 70 hours on duty in 8 consecutive days. May restart after 34 consecutive hours off duty.
            </p>
          </div>

          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-1">
            <strong className="text-slate-900 font-semibold block text-sm">10-Hour Shift Reset</strong>
            <p className="text-slate-600 leading-relaxed">
              Must take 10 consecutive hours off duty / sleeper berth to reset the 11h and 14h shift clocks.
            </p>
          </div>

          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-1">
            <strong className="text-slate-900 font-semibold block text-sm">Fueling & Cargo Handling</strong>
            <p className="text-slate-600 leading-relaxed">
              Fuel stop required at least once every 1,000 miles (~30 min on duty). Loading and unloading simulated at 1 hour each.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end pt-2 border-t border-slate-100">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs transition-colors"
          >
            Close Guide
          </button>
        </div>
      </div>
    </div>
  );
}
