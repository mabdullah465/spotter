import React from 'react';
import { Truck, BookOpen, Sparkles } from 'lucide-react';

export default function Header({ onOpenGuide, onOpenSamples }) {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Title */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center text-white">
              <Truck className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-base font-semibold tracking-tight text-slate-900 font-sans">
                  Spotter
                </span>
                <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-medium border border-slate-200">
                  HOS Logbook
                </span>
              </div>
              <p className="text-[11px] text-slate-500 hidden sm:block">
                FMCSA 49 CFR Part 395 Trip Planner & 24-Hour Daily Log Sheets
              </p>
            </div>
          </div>

          {/* Minimalist Action Buttons */}
          <div className="flex items-center space-x-2">
            <button
              onClick={onOpenSamples}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200/80 transition-colors border border-slate-200"
            >
              <Sparkles className="w-3.5 h-3.5 text-slate-500" />
              <span>Sample Trips</span>
            </button>

            <button
              onClick={onOpenGuide}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-100 transition-colors border border-slate-200"
            >
              <BookOpen className="w-3.5 h-3.5 text-slate-500" />
              <span className="hidden sm:inline">HOS Rules</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
