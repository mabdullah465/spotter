import React, { useState } from 'react';
import {
  FileDown,
  Printer,
  ChevronLeft,
  ChevronRight,
  FileCheck,
  CheckCircle2
} from 'lucide-react';
import LogGridCanvas from './LogGridCanvas';
import { exportPdf } from '../services/api';

export default function DailyLogSheet({ logSheets, tripSummary }) {
  const [activeDayIndex, setActiveDayIndex] = useState(0);
  const [isExporting, setIsExporting] = useState(false);

  if (!logSheets || logSheets.length === 0) return null;

  const currentSheet = logSheets[activeDayIndex] || logSheets[0];

  const handleExportPdf = async () => {
    setIsExporting(true);
    try {
      await exportPdf(logSheets, tripSummary);
    } catch (err) {
      alert(`Export PDF failed: ${err.message}`);
    } finally {
      setIsExporting(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-7 shadow-sm space-y-6">
      {/* Top Header & Export Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-semibold text-slate-900 flex items-center gap-2">
              <FileCheck className="w-5 h-5 text-slate-700" />
              <span>Driver's Daily Log (RODS)</span>
            </h2>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-medium border border-slate-200">
              {logSheets.length} {logSheets.length === 1 ? 'Day' : 'Days'} Total
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            24-hour midnight-to-midnight Record of Duty Status conforming to 49 CFR §395.8.
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleExportPdf}
            disabled={isExporting}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs shadow-sm transition-colors disabled:opacity-50"
          >
            <FileDown className="w-4 h-4" />
            <span>{isExporting ? 'Generating...' : 'Download PDF'}</span>
          </button>
          <button
            onClick={handlePrint}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium border border-slate-200 transition-colors"
          >
            <Printer className="w-4 h-4" />
            <span className="hidden sm:inline">Print</span>
          </button>
        </div>
      </div>

      {/* Day Selector Tabs */}
      <div className="flex items-center justify-between bg-slate-50 p-2 rounded-lg border border-slate-200">
        <button
          onClick={() => setActiveDayIndex(Math.max(0, activeDayIndex - 1))}
          disabled={activeDayIndex === 0}
          className="p-1.5 rounded bg-white hover:bg-slate-100 text-slate-700 disabled:opacity-30 disabled:cursor-not-allowed border border-slate-200 transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-2 overflow-x-auto px-2 py-1">
          {logSheets.map((s, idx) => (
            <button
              key={idx}
              onClick={() => setActiveDayIndex(idx)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all flex items-center gap-2 whitespace-nowrap ${
                activeDayIndex === idx
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200'
              }`}
            >
              <span>Day {s.day_number}</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${activeDayIndex === idx ? 'bg-slate-800 text-slate-200' : 'bg-slate-100 text-slate-500'}`}>
                {s.date}
              </span>
            </button>
          ))}
        </div>

        <button
          onClick={() => setActiveDayIndex(Math.min(logSheets.length - 1, activeDayIndex + 1))}
          disabled={activeDayIndex === logSheets.length - 1}
          className="p-1.5 rounded bg-white hover:bg-slate-100 text-slate-700 disabled:opacity-30 disabled:cursor-not-allowed border border-slate-200 transition-colors"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Official Log Sheet Container */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 sm:p-6 space-y-5">
        {/* Header Information Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pb-4 border-b border-slate-200 text-xs">
          <div>
            <h3 className="text-base font-bold text-slate-900 font-sans uppercase tracking-tight">
              Driver's Daily Log
            </h3>
            <div className="text-slate-500 mt-0.5">
              (24 hours) • Day {currentSheet.day_number} of {logSheets.length}
            </div>
            <div className="font-mono font-semibold text-slate-900 mt-1">
              Date: {currentSheet.date_display || currentSheet.date}
            </div>
          </div>

          <div className="space-y-1 text-slate-600">
            <div><span className="text-slate-400 font-medium">From:</span> {currentSheet.from_location}</div>
            <div><span className="text-slate-400 font-medium">To:</span> {currentSheet.to_location}</div>
            <div><span className="text-slate-400 font-medium">Driver:</span> <strong className="text-slate-900">{currentSheet.driver_name}</strong></div>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
              <div className="text-[10px] text-slate-500">Miles Driven Today</div>
              <div className="text-sm font-bold text-slate-900 font-mono mt-0.5">{currentSheet.miles_today} mi</div>
            </div>
            <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
              <div className="text-[10px] text-slate-500">Truck / Trailer</div>
              <div className="text-[11px] font-semibold text-slate-800 font-mono mt-0.5 truncate">
                {currentSheet.truck_tractor_number} / {currentSheet.trailer_number}
              </div>
            </div>
          </div>
        </div>

        {/* Carrier Info */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs bg-slate-50 p-3 rounded border border-slate-200 text-slate-700">
          <div>
            <span className="text-slate-500">Carrier:</span>{' '}
            <span className="font-medium text-slate-900">{currentSheet.carrier_name}</span>
          </div>
          <div>
            <span className="text-slate-500">Main Office:</span>{' '}
            <span className="font-medium text-slate-900">{currentSheet.main_office_address}</span>
          </div>
        </div>

        {/* 24-Hour SVG Graph */}
        <div>
          <LogGridCanvas sheet={currentSheet} />
        </div>

        {/* Line Totals */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
          <div className="p-2.5 rounded bg-slate-50 border border-slate-200 flex items-center justify-between">
            <span className="text-slate-600 font-medium">1. Off Duty:</span>
            <strong className="text-slate-900 font-mono">{currentSheet.line_totals?.line_1_off_duty?.toFixed(2)} hrs</strong>
          </div>
          <div className="p-2.5 rounded bg-slate-50 border border-slate-200 flex items-center justify-between">
            <span className="text-slate-600 font-medium">2. Sleeper Berth:</span>
            <strong className="text-slate-900 font-mono">{currentSheet.line_totals?.line_2_sleeper_berth?.toFixed(2)} hrs</strong>
          </div>
          <div className="p-2.5 rounded bg-slate-50 border border-slate-200 flex items-center justify-between">
            <span className="text-slate-600 font-medium">3. Driving:</span>
            <strong className="text-slate-900 font-mono">{currentSheet.line_totals?.line_3_driving?.toFixed(2)} hrs</strong>
          </div>
          <div className="p-2.5 rounded bg-slate-50 border border-slate-200 flex items-center justify-between">
            <span className="text-slate-600 font-medium">4. On Duty (Not Drv):</span>
            <strong className="text-slate-900 font-mono">{currentSheet.line_totals?.line_4_on_duty_not_driving?.toFixed(2)} hrs</strong>
          </div>
        </div>

        {/* Remarks Section */}
        <div className="space-y-3 pt-2">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 pb-2">
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Remarks & Change of Duty Status
            </h4>
            <div className="text-xs text-slate-500 font-mono">
              BOL / Manifest: <strong className="text-slate-700">{currentSheet.shipping_documents}</strong>
            </div>
          </div>

          <div className="overflow-x-auto rounded border border-slate-200">
            <table className="w-full text-left text-xs divide-y divide-slate-200">
              <thead className="bg-slate-50 text-slate-600 font-semibold">
                <tr>
                  <th className="px-3 py-2 w-24">Time</th>
                  <th className="px-3 py-2 w-32">Status</th>
                  <th className="px-3 py-2 w-48">Location</th>
                  <th className="px-3 py-2">Activity Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white font-mono text-slate-700">
                {currentSheet.remarks && currentSheet.remarks.length > 0 ? (
                  currentSheet.remarks.map((rem, rIdx) => (
                    <tr key={rIdx} className="hover:bg-slate-50 transition-colors">
                      <td className="px-3 py-2 text-slate-900 font-bold whitespace-nowrap">
                        {rem.time_12h || rem.time}
                      </td>
                      <td className="px-3 py-2 whitespace-nowrap">
                        <span className="text-[10px] px-2 py-0.5 rounded font-sans font-medium bg-slate-100 text-slate-700 border border-slate-200">
                          {rem.status?.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="px-3 py-2 text-slate-800 font-sans font-medium">
                        {rem.location}
                      </td>
                      <td className="px-3 py-2 text-slate-600 font-sans">
                        {rem.remark}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="4" className="px-3 py-4 text-center text-slate-400 font-sans">
                      All hours for this day were spent in continuous off-duty status.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* 70-Hour / 8-Day Recap Box */}
        {currentSheet.recap && (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-800">
              <span>Recap: 70 Hour / 8 Day Drivers (49 CFR §395.8)</span>
              <span className="text-slate-500 font-mono text-[11px]">End of Day Calculations</span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              <div className="bg-white p-3 rounded border border-slate-200">
                <div className="text-[11px] text-slate-500">On Duty Today (3 & 4)</div>
                <div className="text-base font-bold text-slate-900 font-mono mt-1">
                  {currentSheet.recap.today_on_duty?.toFixed(2)} hrs
                </div>
              </div>

              <div className="bg-white p-3 rounded border border-slate-200">
                <div className="text-[11px] text-slate-500">A. Last 7 Days (incl. today)</div>
                <div className="text-base font-bold text-slate-900 font-mono mt-1">
                  {currentSheet.recap.recap_a_total_last_7_days?.toFixed(2)} hrs
                </div>
              </div>

              <div className="bg-white p-3 rounded border border-slate-200">
                <div className="text-[11px] text-slate-500">B. Available Tomorrow (70 - A)</div>
                <div className="text-base font-bold text-slate-900 font-mono mt-1">
                  {currentSheet.recap.recap_b_available_tomorrow?.toFixed(2)} hrs
                </div>
              </div>

              <div className="bg-white p-3 rounded border border-slate-200">
                <div className="text-[11px] text-slate-500">C. Last 8 Days (incl. today)</div>
                <div className="text-base font-bold text-slate-900 font-mono mt-1">
                  {currentSheet.recap.recap_c_total_last_8_days?.toFixed(2)} hrs
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Signature */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-slate-200 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span className="font-medium text-slate-700">Driver Signature:</span>
            <span className="font-serif italic text-slate-900 border-b border-slate-300 pb-0.5 px-2">
              {currentSheet.driver_name}
            </span>
          </div>
          <div className="flex items-center justify-end gap-2 text-right">
            <CheckCircle2 className="w-4 h-4 text-slate-700" />
            <span>Certified true and correct (FMCSA §395.8)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
