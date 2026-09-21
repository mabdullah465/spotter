import React from 'react';
import {
  Truck,
  Clock,
  Fuel,
  Moon,
  ShieldCheck,
  FileCheck
} from 'lucide-react';
import { formatDuration, formatMiles } from '../utils/formatters';

export default function TripSummary({ summary, routeData, logSheetsCount }) {
  if (!summary) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-900 mb-4 pb-3 border-b border-slate-100 flex items-center justify-between">
        <span>Trip Performance Metrics</span>
        <span className="text-xs text-slate-500 font-normal">Calculated across all scheduled legs</span>
      </h3>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* Total Distance */}
        <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200 flex flex-col justify-between">
          <div className="text-[11px] text-slate-500 flex items-center gap-1">
            <Truck className="w-3.5 h-3.5 text-slate-400" />
            <span>Total Distance</span>
          </div>
          <div className="text-lg font-bold text-slate-900 font-mono mt-1">
            {formatMiles(summary.total_miles)}
          </div>
        </div>

        {/* Total Driving Time */}
        <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200 flex flex-col justify-between">
          <div className="text-[11px] text-slate-500 flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>Driving Time</span>
          </div>
          <div className="text-lg font-bold text-slate-900 font-mono mt-1">
            {formatDuration(summary.total_driving_hours)}
          </div>
        </div>

        {/* Total Duty Time */}
        <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200 flex flex-col justify-between">
          <div className="text-[11px] text-slate-500 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-slate-400" />
            <span>Total On Duty</span>
          </div>
          <div className="text-lg font-bold text-slate-900 font-mono mt-1">
            {formatDuration(summary.total_duty_hours)}
          </div>
        </div>

        {/* Fuel Stops */}
        <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200 flex flex-col justify-between">
          <div className="text-[11px] text-slate-500 flex items-center gap-1">
            <Fuel className="w-3.5 h-3.5 text-slate-400" />
            <span>Fuel Stops</span>
          </div>
          <div className="text-lg font-bold text-slate-900 font-mono mt-1">
            {summary.fuel_stops_count} <span className="text-xs font-normal text-slate-500">stops</span>
          </div>
        </div>

        {/* 10h Layovers */}
        <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200 flex flex-col justify-between">
          <div className="text-[11px] text-slate-500 flex items-center gap-1">
            <Moon className="w-3.5 h-3.5 text-slate-400" />
            <span>10h Resets</span>
          </div>
          <div className="text-lg font-bold text-slate-900 font-mono mt-1">
            {summary.layovers_10h_count} <span className="text-xs font-normal text-slate-500">layovers</span>
          </div>
        </div>

        {/* Log Sheets */}
        <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200 flex flex-col justify-between">
          <div className="text-[11px] text-slate-500 flex items-center gap-1">
            <FileCheck className="w-3.5 h-3.5 text-slate-400" />
            <span>Daily Sheets</span>
          </div>
          <div className="text-lg font-bold text-slate-900 font-mono mt-1">
            {logSheetsCount} <span className="text-xs font-normal text-slate-500">sheets</span>
          </div>
        </div>
      </div>
    </div>
  );
}
