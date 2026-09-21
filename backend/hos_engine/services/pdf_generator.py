"""
FMCSA Paper Log PDF Generator.
Generates official, print-ready 24-hour Driver's Daily Log PDF sheets using ReportLab.
"""

import io
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def generate_hos_log_pdf(log_sheets: List[Dict[str, Any]], trip_summary: Dict[str, Any] = None) -> bytes:
    """
    Generates a multi-page PDF where each page is a completed Driver's Daily Log sheet.
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    page_w, page_h = letter # 612 x 792 points

    for idx, sheet in enumerate(log_sheets):
        # 1. Page Margin Setup
        margin_x = 36
        margin_top = page_h - 36
        content_w = page_w - (margin_x * 2)

        # 2. Header Title
        p.setFont("Helvetica-Bold", 14)
        p.drawString(margin_x, margin_top, "DRIVER'S DAILY LOG")
        p.setFont("Helvetica", 8)
        p.drawString(margin_x + 160, margin_top + 2, "(24 Hours)")

        p.setFont("Helvetica-Bold", 9)
        p.drawString(page_w - 200, margin_top, f"DATE: {sheet.get('date', '')}")
        p.setFont("Helvetica", 7)
        p.drawRightString(page_w - margin_x, margin_top - 10, f"Day {sheet.get('day_number', idx+1)} of {len(log_sheets)}")

        # 3. Carrier & Route Metadata Table
        y = margin_top - 25
        p.setStrokeColor(colors.black)
        p.setLineWidth(0.7)

        # Row 1: From & To
        p.setFont("Helvetica-Bold", 8)
        p.drawString(margin_x, y, "From:")
        p.setFont("Helvetica", 8)
        p.drawString(margin_x + 30, y, str(sheet.get("from_location", "Origin")))
        p.line(margin_x + 28, y - 2, margin_x + 240, y - 2)

        p.setFont("Helvetica-Bold", 8)
        p.drawString(margin_x + 260, y, "To:")
        p.setFont("Helvetica", 8)
        p.drawString(margin_x + 280, y, str(sheet.get("to_location", "Destination")))
        p.line(margin_x + 278, y - 2, page_w - margin_x, y - 2)

        # Row 2: Mileage & Carrier Info
        y -= 22
        # Mileage Box
        p.rect(margin_x, y - 12, 110, 20)
        p.setFont("Helvetica", 6)
        p.drawString(margin_x + 4, y + 1, "Total Miles Driving Today")
        p.setFont("Helvetica-Bold", 9)
        p.drawRightString(margin_x + 104, y - 9, f"{sheet.get('miles_today', 0.0)} mi")

        p.rect(margin_x + 115, y - 12, 110, 20)
        p.setFont("Helvetica", 6)
        p.drawString(margin_x + 119, y + 1, "Total Mileage Today")
        p.setFont("Helvetica-Bold", 9)
        p.drawRightString(margin_x + 219, y - 9, f"{sheet.get('total_mileage_today', 0.0)} mi")

        # Carrier info lines
        p.setFont("Helvetica-Bold", 7)
        p.drawString(margin_x + 240, y + 2, "Carrier Name:")
        p.setFont("Helvetica", 7.5)
        p.drawString(margin_x + 300, y + 2, str(sheet.get("carrier_name", "")))
        p.line(margin_x + 300, y - 1, page_w - margin_x, y - 1)

        y -= 16
        p.setFont("Helvetica-Bold", 7)
        p.drawString(margin_x + 240, y + 2, "Main Office:")
        p.setFont("Helvetica", 7.5)
        p.drawString(margin_x + 300, y + 2, str(sheet.get("main_office_address", "")))
        p.line(margin_x + 300, y - 1, page_w - margin_x, y - 1)

        y -= 16
        # Truck/Trailer box
        p.rect(margin_x, y - 12, 225, 20)
        p.setFont("Helvetica", 6)
        p.drawString(margin_x + 4, y + 1, "Truck / Tractor & Trailer Numbers:")
        p.setFont("Helvetica-Bold", 8)
        p.drawString(margin_x + 6, y - 9, f"Tractor: {sheet.get('truck_tractor_number', 'TRK-101')}  |  Trailer: {sheet.get('trailer_number', 'TRL-501')}")

        p.setFont("Helvetica-Bold", 7)
        p.drawString(margin_x + 240, y + 2, "Home Terminal:")
        p.setFont("Helvetica", 7.5)
        p.drawString(margin_x + 300, y + 2, str(sheet.get("home_terminal_address", "")))
        p.line(margin_x + 300, y - 1, page_w - margin_x, y - 1)

        # 4. Official 24-Hour Graph Grid
        grid_top_y = y - 35
        grid_left_x = margin_x + 105
        grid_w = 370
        grid_h = 100
        row_h = grid_h / 4.0 # 25 points per row
        grid_bottom_y = grid_top_y - grid_h
        totals_col_x = grid_left_x + grid_w

        # Black Top Header Bar for Grid Hours
        p.setFillColor(colors.black)
        p.rect(grid_left_x, grid_top_y, grid_w + 55, 14, fill=True, stroke=False)
        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 6.5)

        # Draw Hour Labels in Header (Midnight, 1..11, Noon, 1..11, Midnight)
        hour_labels = ["Mid-", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "Noon", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "Mid-"]
        for h_idx in range(25):
            hx = grid_left_x + (h_idx / 24.0) * grid_w
            lbl = hour_labels[h_idx]
            p.drawCentredString(hx, grid_top_y + 4, lbl)

        p.drawString(totals_col_x + 8, grid_top_y + 4, "Total Hours")

        # Row Labels on Left
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", 7)
        row_labels = [
            "1. Off Duty",
            "2. Sleeper Berth",
            "3. Driving",
            "4. On Duty (not driving)"
        ]
        for r_idx, r_name in enumerate(row_labels):
            ry = grid_top_y - (r_idx * row_h) - 15
            p.drawString(margin_x, ry, r_name)

        # Draw Grid Outer Borders and Row Separators
        p.setStrokeColor(colors.black)
        p.setLineWidth(1.0)
        p.rect(grid_left_x, grid_bottom_y, grid_w, grid_h, fill=False, stroke=True)

        # Row divider lines
        for r_idx in range(1, 4):
            ry = grid_top_y - (r_idx * row_h)
            p.setLineWidth(0.8)
            p.line(grid_left_x, ry, grid_left_x + grid_w, ry)

        # 15-Minute Grid Ticks and Hour Columns
        for h_idx in range(25):
            hx = grid_left_x + (h_idx / 24.0) * grid_w
            # Full vertical hour lines
            p.setLineWidth(0.5)
            p.setStrokeColor(colors.Color(0.2, 0.2, 0.2))
            p.line(hx, grid_top_y, hx, grid_bottom_y)

            if h_idx < 24:
                # 15m, 30m, 45m ticks for each row
                for r_idx in range(4):
                    ry_top = grid_top_y - (r_idx * row_h)
                    ry_bot = ry_top - row_h

                    # 15 min tick
                    p.setStrokeColor(colors.Color(0.5, 0.5, 0.5))
                    p.setLineWidth(0.3)
                    p.line(hx + (0.25 / 24.0) * grid_w, ry_top, hx + (0.25 / 24.0) * grid_w, ry_top - 4)
                    p.line(hx + (0.25 / 24.0) * grid_w, ry_bot, hx + (0.25 / 24.0) * grid_w, ry_bot + 4)

                    # 30 min tick (half hour)
                    p.setLineWidth(0.4)
                    p.line(hx + (0.50 / 24.0) * grid_w, ry_top, hx + (0.50 / 24.0) * grid_w, ry_top - 8)
                    p.line(hx + (0.50 / 24.0) * grid_w, ry_bot, hx + (0.50 / 24.0) * grid_w, ry_bot + 8)

                    # 45 min tick
                    p.setLineWidth(0.3)
                    p.line(hx + (0.75 / 24.0) * grid_w, ry_top, hx + (0.75 / 24.0) * grid_w, ry_top - 4)
                    p.line(hx + (0.75 / 24.0) * grid_w, ry_bot, hx + (0.75 / 24.0) * grid_w, ry_bot + 4)

        # Right Column: Total Hours Lines & Values
        p.setStrokeColor(colors.black)
        line_totals = sheet.get("line_totals", {})
        totals_map = {
            1: line_totals.get("line_1_off_duty", 0.0),
            2: line_totals.get("line_2_sleeper_berth", 0.0),
            3: line_totals.get("line_3_driving", 0.0),
            4: line_totals.get("line_4_on_duty_not_driving", 0.0)
        }

        for r_idx in range(4):
            ry = grid_top_y - (r_idx * row_h) - 16
            line_val = totals_map[r_idx + 1]
            p.setLineWidth(0.6)
            p.line(totals_col_x + 6, ry - 2, totals_col_x + 50, ry - 2)
            p.setFont("Helvetica-Bold", 8)
            p.drawCentredString(totals_col_x + 28, ry, f"{line_val:.2f}")

        # 5. DRAW THE CONTINUOUS STEPPED DUTY STATUS LINE
        # Calculate Y coordinate for Line 1..4 (centered inside row)
        def get_line_y(line_num):
            return grid_top_y - ((line_num - 0.5) * row_h)

        def get_hour_x(hour_val):
            return grid_left_x + (min(24.0, max(0.0, hour_val)) / 24.0) * grid_w

        polyline = sheet.get("grid_polyline", [])
        if polyline and len(polyline) >= 2:
            p.setStrokeColor(colors.Color(0.08, 0.38, 0.74)) # Bold Royal Blue
            p.setLineWidth(2.2)

            for pt_idx in range(len(polyline) - 1):
                p1 = polyline[pt_idx]
                p2 = polyline[pt_idx + 1]
                x1 = get_hour_x(p1["x"])
                y1 = get_line_y(p1["y"])
                x2 = get_hour_x(p2["x"])
                y2 = get_line_y(p2["y"])
                p.line(x1, y1, x2, y2)

        # 6. Remarks Section
        remarks_top_y = grid_bottom_y - 25
        p.setStrokeColor(colors.black)
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(margin_x, remarks_top_y, "REMARKS")

        p.setFont("Helvetica-Bold", 7.5)
        p.drawString(margin_x, remarks_top_y - 15, "Shipping Documents:")
        p.setFont("Helvetica", 7.5)
        p.drawString(margin_x + 95, remarks_top_y - 15, str(sheet.get("shipping_documents", "")))
        p.line(margin_x + 90, remarks_top_y - 17, margin_x + 350, remarks_top_y - 17)

        # Table of Remarks
        y_rem = remarks_top_y - 35
        p.setFont("Helvetica-Bold", 7)
        p.drawString(margin_x, y_rem, "TIME")
        p.drawString(margin_x + 40, y_rem, "STATUS")
        p.drawString(margin_x + 130, y_rem, "LOCATION")
        p.drawString(margin_x + 250, y_rem, "ACTIVITY / REMARKS")
        p.line(margin_x, y_rem - 3, page_w - margin_x, y_rem - 3)
        y_rem -= 12

        remarks_list = sheet.get("remarks", [])
        p.setFont("Helvetica", 6.5)
        for rem in remarks_list[:10]: # Up to 10 remarks per page
            p.drawString(margin_x, y_rem, str(rem.get("time_12h", rem.get("time", ""))))
            status_text = rem.get("status", "").replace("_", " ").title()
            p.drawString(margin_x + 40, y_rem, status_text[:18])
            p.drawString(margin_x + 130, y_rem, str(rem.get("location", ""))[:25])
            p.drawString(margin_x + 250, y_rem, str(rem.get("remark", ""))[:55])
            y_rem -= 11

        # 7. 70-Hour / 8-Day Recap Box & Signatures (Bottom)
        recap_y = 110
        p.rect(margin_x, recap_y - 45, content_w, 55)

        p.setFont("Helvetica-Bold", 7.5)
        p.drawString(margin_x + 6, recap_y + 2, "RECAP: 70 Hour / 8 Day Drivers")

        p.setFont("Helvetica", 6.5)
        # Column 1: On-duty today
        p.drawString(margin_x + 10, recap_y - 14, "On-Duty Hours Today:")
        p.setFont("Helvetica-Bold", 8)
        p.drawString(margin_x + 10, recap_y - 28, f"{sheet.get('recap', {}).get('today_on_duty', 0.0):.2f} hrs")

        # Column 2: Line A
        p.setFont("Helvetica", 6.5)
        p.drawString(margin_x + 110, recap_y - 14, "A. Total Hours Last 7 Days:")
        p.setFont("Helvetica-Bold", 8)
        p.drawString(margin_x + 110, recap_y - 28, f"{sheet.get('recap', {}).get('recap_a_total_last_7_days', 0.0):.2f} hrs")

        # Column 3: Line B
        p.setFont("Helvetica", 6.5)
        p.drawString(margin_x + 230, recap_y - 14, "B. Available Tomorrow (70 - A):")
        p.setFont("Helvetica-Bold", 8)
        avail = sheet.get('recap', {}).get('recap_b_available_tomorrow', 0.0)
        p.drawString(margin_x + 230, recap_y - 28, f"{avail:.2f} hrs")

        # Column 4: Line C
        p.setFont("Helvetica", 6.5)
        p.drawString(margin_x + 370, recap_y - 14, "C. Total Hours Last 8 Days:")
        p.setFont("Helvetica-Bold", 8)
        p.drawString(margin_x + 370, recap_y - 28, f"{sheet.get('recap', {}).get('recap_c_total_last_8_days', 0.0):.2f} hrs")

        # Signatures
        sig_y = 40
        p.setFont("Helvetica-Bold", 7)
        p.drawString(margin_x, sig_y + 10, "Driver's Signature:")
        p.setFont("Helvetica-Oblique", 9)
        p.drawString(margin_x + 85, sig_y + 10, str(sheet.get("driver_name", "Authorized Commercial Driver")))
        p.line(margin_x + 80, sig_y + 8, margin_x + 280, sig_y + 8)

        p.setFont("Helvetica-Bold", 7)
        p.drawString(page_w - 240, sig_y + 10, "Carrier Certification:")
        p.setFont("Helvetica", 7)
        p.drawString(page_w - 150, sig_y + 10, "Certified True & Correct")
        p.line(page_w - 155, sig_y + 8, page_w - margin_x, sig_y + 8)

        # Page Footer
        p.setFont("Helvetica", 6)
        p.drawCentredString(page_w / 2.0, 20, "FMCSA Form 49 CFR Part 395 Compliant Logbook  |  Generated by Spotter ELD & HOS Trip Planner")

        # Finish Page
        p.showPage()

    p.save()
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
