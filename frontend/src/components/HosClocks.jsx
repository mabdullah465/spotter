import React from 'react';
import { Clock, ShieldAlert, CheckCircle2, AlertTriangle, Gauge } from 'lucide-react';
import { formatDuration } from '../utils/formatters';

export default function HosClocks({ clocks, summary }) {
  if (!summary) return null;

  const cycleUsed = summary.final_cycle_used || summary.initial_cycle_used || 0;
  const cycleRemaining = Math.max(0, 70.0 - cycleUsed);
  const cyclePercent = Math.min(100, (cycleUsed / 70.0) * 100);

  return (
    <div className="space-y-4">
      {/* Alert if Cycle Exceeded or Near Limit */}
      {summary.cycle_warning && (
        <div className={`p-4 rounded-xl border flex items-start gap-3 ${summary.final_cycle_used > 70 ? 'bg-red-50 border-red-200 text-red-900' : 'bg-amber-50 border-amber-200 text-amber-900'} animate-fade-in`}>
          <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5 text-amber-700" />
          <div className="text-xs">
            <strong className="font-semibold block text-sm mb-0.5">FMCSA 70-Hour Cycle Alert</strong>
            {summary.cycle_warning}
          </div>
        </div>
      )}

      {/* The 4 Clean Compliance Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 1. 11-Hour Driving Limit */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
            <span>11-Hour Drive Limit</span>
            <Gauge className="w-4 h-4 text-slate-400" />
          </div>
          <div className="my-3">
            <div className="text-2xl font-bold text-slate-900 font-mono">
              11.0 <span className="text-xs font-normal text-slate-500">hrs max</span>
            </div>
            <div className="text-[11px] text-slate-600 flex items-center gap-1 mt-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-slate-700" />
              <span>Reset after 10h rest</span>
            </div>
          </div>
          <div className="text-[11px] text-slate-500 border-t border-slate-100 pt-2 font-mono">
            Trip Drive: <strong className="text-slate-900">{summary.total_driving_hours} hrs</strong>
          </div>
        </div>

        {/* 2. 14-Hour Shift Window */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
            <span>14-Hour Shift Window</span>
            <Clock className="w-4 h-4 text-slate-400" />
          </div>
          <div className="my-3">
            <div className="text-2xl font-bold text-slate-900 font-mono">
              14.0 <span className="text-xs font-normal text-slate-500">hrs max</span>
            </div>
            <div className="text-[11px] text-slate-600 flex items-center gap-1 mt-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-slate-700" />
              <span>Consecutive duty clock</span>
            </div>
          </div>
          <div className="text-[11px] text-slate-500 border-t border-slate-100 pt-2 font-mono">
            10h Resets: <strong className="text-slate-900">{summary.layovers_10h_count} scheduled</strong>
          </div>
        </div>

        {/* 3. 30-Minute Rest Break */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
            <span>30-Min Rest Break</span>
            <Clock className="w-4 h-4 text-slate-400" />
          </div>
          <div className="my-3">
            <div className="text-2xl font-bold text-slate-900 font-mono">
              30 <span className="text-xs font-normal text-slate-500">min break</span>
            </div>
            <div className="text-[11px] text-slate-600 flex items-center gap-1 mt-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-slate-700" />
              <span>Every 8h cumulative drive</span>
            </div>
          </div>
          <div className="text-[11px] text-slate-500 border-t border-slate-100 pt-2 font-mono">
            Breaks: <strong className="text-slate-900">{summary.rest_breaks_count} scheduled</strong>
          </div>
        </div>

        {/* 4. 70-Hour / 8-Day Cycle */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
            <span>70-Hour / 8-Day Cycle</span>
            <ShieldAlert className="w-4 h-4 text-slate-400" />
          </div>
          <div className="my-2.5">
            <div className="text-2xl font-bold text-slate-900 font-mono">
              {cycleUsed.toFixed(1)} <span className="text-xs font-normal text-slate-500">/ 70.0 hrs</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-1.5 mt-2 overflow-hidden">
              <div
                className={`h-full rounded-full ${cycleUsed > 70 ? 'bg-red-600' : 'bg-slate-900'}`}
                style={{ width: `${Math.min(100, cyclePercent)}%` }}
              ></div>
            </div>
          </div>
          <div className="text-[11px] text-slate-500 border-t border-slate-100 pt-2 flex items-center justify-between font-mono">
            <span>Remaining: <strong className="text-slate-900">{cycleRemaining.toFixed(1)} hrs</strong></span>
            <span>{cyclePercent.toFixed(0)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
