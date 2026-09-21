import React, { useState } from 'react';

/**
 * Authentic 24-Hour FMCSA Driver's Daily Log Graph.
 * Visualizes the 4 standard duty lines on clean paper background with crisp black ink lines.
 */
export default function LogGridCanvas({ sheet }) {
  const [hoveredSegment, setHoveredSegment] = useState(null);

  if (!sheet) return null;

  const width = 860;
  const height = 210;
  const leftMargin = 175;
  const rightMargin = 75;
  const topMargin = 28;
  const gridWidth = width - leftMargin - rightMargin;
  const gridHeight = height - topMargin - 15;
  const rowHeight = gridHeight / 4.0;

  const rows = [
    { num: 1, label: '1. OFF DUTY' },
    { num: 2, label: '2. SLEEPER BERTH' },
    { num: 3, label: '3. DRIVING' },
    { num: 4, label: '4. ON DUTY (NOT DRIVING)' }
  ];

  const hourLabels = [
    'Mid', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
    'Noon', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', 'Mid'
  ];

  const getX = (hour) => leftMargin + (Math.min(24.0, Math.max(0.0, hour)) / 24.0) * gridWidth;
  const getY = (lineNum) => topMargin + (lineNum - 0.5) * rowHeight;

  const polylinePoints = (sheet.grid_polyline || [])
    .map(pt => `${getX(pt.x).toFixed(1)},${getY(pt.y).toFixed(1)}`)
    .join(' ');

  const totals = sheet.line_totals || {};
  const lineValues = {
    1: totals.line_1_off_duty || 0,
    2: totals.line_2_sleeper_berth || 0,
    3: totals.line_3_driving || 0,
    4: totals.line_4_on_duty_not_driving || 0,
  };

  return (
    <div className="w-full bg-white p-3 sm:p-5 rounded-lg border border-slate-300 select-none overflow-x-auto shadow-sm">
      <div className="min-w-[800px]">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto font-sans"
          style={{ shapeRendering: 'geometricPrecision' }}
        >
          {/* Top Hour Bar Background */}
          <rect
            x={leftMargin}
            y={topMargin - 20}
            width={gridWidth}
            height={18}
            fill="#0f172a"
            stroke="#0f172a"
            strokeWidth="1"
          />

          {/* Hour labels */}
          {hourLabels.map((lbl, idx) => (
            <text
              key={idx}
              x={getX(idx)}
              y={topMargin - 7}
              textAnchor="middle"
              fill="#ffffff"
              fontSize="8.5"
              fontWeight="700"
              fontFamily="JetBrains Mono, monospace"
            >
              {lbl}
            </text>
          ))}

          {/* Total Hours Header */}
          <rect
            x={leftMargin + gridWidth + 6}
            y={topMargin - 20}
            width={62}
            height={18}
            fill="#0f172a"
            stroke="#0f172a"
            strokeWidth="1"
          />
          <text
            x={leftMargin + gridWidth + 37}
            y={topMargin - 7}
            textAnchor="middle"
            fill="#ffffff"
            fontSize="8"
            fontWeight="700"
          >
            Total Hrs
          </text>

          {/* Main Grid Frame */}
          <rect
            x={leftMargin}
            y={topMargin}
            width={gridWidth}
            height={gridHeight}
            fill="#ffffff"
            stroke="#0f172a"
            strokeWidth="1.2"
          />

          {/* Rows & Labels */}
          {rows.map((row, idx) => {
            const rowTop = topMargin + idx * rowHeight;
            const rowMid = rowTop + rowHeight / 2;

            return (
              <g key={row.num}>
                <text
                  x={leftMargin - 12}
                  y={rowMid + 3.5}
                  textAnchor="end"
                  fill="#0f172a"
                  fontSize="9.5"
                  fontWeight="700"
                >
                  {row.label}
                </text>

                {idx > 0 && (
                  <line
                    x1={leftMargin}
                    y1={rowTop}
                    x2={leftMargin + gridWidth}
                    y2={rowTop}
                    stroke="#94a3b8"
                    strokeWidth="0.8"
                  />
                )}

                {/* Right Total Box */}
                <rect
                  x={leftMargin + gridWidth + 6}
                  y={rowTop + 2}
                  width={62}
                  height={rowHeight - 4}
                  fill="#f8fafc"
                  stroke="#cbd5e1"
                  strokeWidth="0.8"
                  rx="2"
                />
                <text
                  x={leftMargin + gridWidth + 37}
                  y={rowMid + 4}
                  textAnchor="middle"
                  fill="#0f172a"
                  fontSize="10.5"
                  fontWeight="700"
                  fontFamily="JetBrains Mono, monospace"
                >
                  {lineValues[row.num].toFixed(2)}
                </text>
              </g>
            );
          })}

          {/* 15-Minute Grid Subdivisions */}
          {Array.from({ length: 25 }).map((_, h) => {
            const hx = getX(h);
            return (
              <g key={h}>
                <line
                  x1={hx}
                  y1={topMargin}
                  x2={hx}
                  y2={topMargin + gridHeight}
                  stroke="#94a3b8"
                  strokeWidth="0.8"
                  strokeDasharray={h % 6 === 0 ? 'none' : '2 2'}
                />

                {h < 24 && rows.map((_, rIdx) => {
                  const rTop = topMargin + rIdx * rowHeight;
                  const rBot = rTop + rowHeight;
                  const x15 = getX(h + 0.25);
                  const x30 = getX(h + 0.50);
                  const x45 = getX(h + 0.75);

                  return (
                    <g key={rIdx}>
                      <line x1={x15} y1={rTop} x2={x15} y2={rTop + 3} stroke="#94a3b8" strokeWidth="0.6" />
                      <line x1={x15} y1={rBot - 3} x2={x15} y2={rBot} stroke="#94a3b8" strokeWidth="0.6" />
                      <line x1={x30} y1={rTop} x2={x30} y2={rTop + 6} stroke="#64748b" strokeWidth="0.9" />
                      <line x1={x30} y1={rBot - 6} x2={x30} y2={rBot} stroke="#64748b" strokeWidth="0.9" />
                      <line x1={x45} y1={rTop} x2={x45} y2={rTop + 3} stroke="#94a3b8" strokeWidth="0.6" />
                      <line x1={x45} y1={rBot - 3} x2={x45} y2={rBot} stroke="#94a3b8" strokeWidth="0.6" />
                    </g>
                  );
                })}
              </g>
            );
          })}

          {/* Interactive Hover Area */}
          {sheet.segments && sheet.segments.map((seg, sIdx) => {
            const sx1 = getX(seg.start_hour);
            const sx2 = getX(seg.end_hour);
            const sw = Math.max(2, sx2 - sx1);
            const sy = topMargin + (seg.status_line - 1) * rowHeight;

            return (
              <rect
                key={sIdx}
                x={sx1}
                y={sy + 1}
                width={sw}
                height={rowHeight - 2}
                fill="transparent"
                className="cursor-pointer hover:fill-blue-500/10 transition-colors"
                onMouseEnter={() => setHoveredSegment(seg)}
                onMouseLeave={() => setHoveredSegment(null)}
              />
            );
          })}

          {/* Bold Continuous Stepped Duty Line */}
          {polylinePoints && (
            <polyline
              points={polylinePoints}
              fill="none"
              stroke="#1e3a8a"
              strokeWidth="2.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}

          {/* Hover Tooltip */}
          {hoveredSegment && (
            <g>
              <rect
                x={Math.min(width - 230, Math.max(leftMargin, getX(hoveredSegment.start_hour) - 15))}
                y={topMargin + 8}
                width="210"
                height="40"
                fill="#0f172a"
                rx="4"
              />
              <text
                x={Math.min(width - 230, Math.max(leftMargin, getX(hoveredSegment.start_hour) - 15)) + 10}
                y={topMargin + 22}
                fill="#38bdf8"
                fontSize="9.5"
                fontWeight="700"
              >
                {hoveredSegment.time_display} • {hoveredSegment.duration_hours.toFixed(2)} hrs
              </text>
              <text
                x={Math.min(width - 230, Math.max(leftMargin, getX(hoveredSegment.start_hour) - 15)) + 10}
                y={topMargin + 37}
                fill="#ffffff"
                fontSize="9"
                fontWeight="500"
              >
                {hoveredSegment.remark ? (hoveredSegment.remark.length > 32 ? hoveredSegment.remark.slice(0, 30) + '...' : hoveredSegment.remark) : 'Duty Status'}
              </text>
            </g>
          )}
        </svg>
      </div>
    </div>
  );
}
