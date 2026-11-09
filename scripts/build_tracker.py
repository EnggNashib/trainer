#!/usr/bin/env python3
"""Build the Excel workout tracker from a program.json.

    python3 build_tracker.py program.json [--outdir .] [--rows 1000]

Six sheets: Dashboard, Workout Plan, Workout Log, Weekly Progress,
Personal Records, Training Notes. Every calculation is a live spreadsheet
formula — open it, type a session into the Log, and the rest updates.

Requires openpyxl:   pip install openpyxl

Compatibility note: only pre-2007 worksheet functions are used (SUMPRODUCT,
SUMIFS, COUNTIF(S), AVERAGEIFS, INDEX, IFERROR). Newer ones such as MAXIFS
need an "_xlfn." prefix when written by a library and render as #NAME? in
Excel, so they are deliberately avoided.
"""

import argparse
import json
import os
import sys
from datetime import date, datetime

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
except ImportError:
    sys.exit(
        "error: openpyxl is required to build the Excel tracker.\n"
        "       Install it with:  pip install openpyxl\n"
        "       (The PDF/mobile plan does not need it — build_plan.py works without.)"
    )

# ---------------------------------------------------------------- styling
INK = "1F2933"
ACCENT = "2F6F4E"
ACCENT_SOFT = "E3EFE8"
HEAD_FILL = PatternFill("solid", fgColor=ACCENT)
SUB_FILL = PatternFill("solid", fgColor=ACCENT_SOFT)
ZEBRA = PatternFill("solid", fgColor="F6F8F7")
HEAD_FONT = Font(bold=True, color="FFFFFF", size=11)
TITLE_FONT = Font(bold=True, size=16, color=INK)
SUB_FONT = Font(bold=True, size=11, color=INK)
MUTED = Font(size=9, color="6B7A74", italic=True)
THIN = Side(style="thin", color="D5DEDA")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center")


def header_row(ws, row, headers, widths=None):
    for i, h in enumerate(headers, start=1):
        c = ws.cell(row=row, column=i, value=h)
        c.fill, c.font, c.border = HEAD_FILL, HEAD_FONT, BOX
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    if widths:
        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[row].height = 28


def title(ws, text, subtitle=None, span=8):
    ws["A1"] = text
    ws["A1"].font = TITLE_FONT
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=span)
    if subtitle:
        ws["A2"] = subtitle
        ws["A2"].font = MUTED
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=span)


def kv(ws, row, label, value, fmt=None, bold=False):
    a = ws.cell(row=row, column=1, value=label)
    a.font = SUB_FONT if bold else Font(size=10, color=INK)
    b = ws.cell(row=row, column=2, value=value)
    if fmt:
        b.number_format = fmt
    b.font = Font(size=10, bold=bold, color=INK)
    return b


# ---------------------------------------------------------------- sheets
def build(prog: dict, outpath: str, nrows: int) -> str:
    client = prog.get("client", {})
    strategy = prog.get("strategy", {})
    block = prog.get("block", {})
    sessions = prog.get("sessions", [])
    units = client.get("units", "kg")

    start_raw = block.get("start_date")
    try:
        start = datetime.strptime(start_raw, "%Y-%m-%d").date() if start_raw else date.today()
    except (TypeError, ValueError):
        start = date.today()

    per_week = len(sessions)
    weeks = int(block.get("weeks") or 8)

    # Flat list of (session_name, exercise) in program order
    plan_rows = []
    for s in sessions:
        for ex in s.get("exercises", []):
            plan_rows.append((s, ex))
    exercise_names = sorted({ex.get("name", "") for _, ex in plan_rows if ex.get("name")})

    wb = Workbook()

    LOG = "Workout Log"
    FIRST, LAST = 3, 2 + nrows  # log data rows

    # ============================================================ Log
    ws = wb.active
    ws.title = LOG
    title(
        ws,
        "Workout Log",
        "One row per exercise per session. Fill the white columns; grey ones calculate themselves. "
        "Status drives the Dashboard and Weekly Progress — set it on every row you train.",
        span=16,
    )
    headers = [
        "Date", "Week", "Session", "Exercise",
        "Plan Sets", "Plan Reps",
        "Actual Sets", "Actual Reps", f"Weight ({units})",
        "RIR", "Rest (s)", "Status",
        "Volume", "Est. 1RM", "_tag", "_new",
    ]
    widths = [12, 7, 16, 30, 9, 10, 9, 10, 12, 7, 9, 13, 11, 10, 18, 7]
    header_row(ws, 4, headers, widths)
    ws.freeze_panes = "A5"

    # Pre-seed the first week so the user sees the intended shape
    seed = []
    for s in sessions:
        for ex in s.get("exercises", []):
            seed.append((s.get("name", ""), ex))

    for i in range(nrows):
        r = FIRST + 2 + i  # data starts at row 5 (header on 4)
        if i < len(seed):
            sname, ex = seed[i]
            ws.cell(row=r, column=3, value=sname)
            ws.cell(row=r, column=4, value=ex.get("name", ""))
            ws.cell(row=r, column=5, value=ex.get("sets"))
            ws.cell(row=r, column=6, value=str(ex.get("reps", "")))
            ws.cell(row=r, column=10, value=str(ex.get("rir", "")))
            ws.cell(row=r, column=11, value=ex.get("rest_sec"))
        # Week number within the block
        ws.cell(row=r, column=2).value = (
            f'=IF($A{r}="","",INT(($A{r}-DATE({start.year},{start.month},{start.day}))/7)+1)'
        )
        # Volume = actual sets x actual reps x weight
        ws.cell(row=r, column=13).value = (
            f'=IF(OR($G{r}="",$H{r}="",$I{r}=""),"",$G{r}*$H{r}*$I{r})'
        )
        # Epley estimated 1RM from the working set
        ws.cell(row=r, column=14).value = (
            f'=IF(OR($H{r}="",$I{r}="",$H{r}=0),"",ROUND($I{r}*(1+$H{r}/30),1))'
        )
        # Helper: session tag, and 1 on the first row of each session
        ws.cell(row=r, column=15).value = f'=IF($A{r}="","",$A{r}&"|"&$C{r})'
        ws.cell(row=r, column=16).value = (
            f'=IF($A{r}="","",IF(COUNTIF($O$5:$O{r},$O{r})=1,1,0))'
        )

        for col in range(1, 17):
            cell = ws.cell(row=r, column=col)
            cell.border = BOX
            if col in (2, 13, 14, 15, 16):
                cell.fill = ZEBRA
        ws.cell(row=r, column=1).number_format = "yyyy-mm-dd"
        ws.cell(row=r, column=9).number_format = "0.0"
        ws.cell(row=r, column=13).number_format = "#,##0"

    # Dropdowns
    dv_status = DataValidation(
        type="list", formula1='"Completed,Partial,Skipped"', allow_blank=True,
        showErrorMessage=True, error="Pick Completed, Partial or Skipped.",
    )
    ws.add_data_validation(dv_status)
    dv_status.add(f"L5:L{LAST + 2}")

    if sessions:
        names = ",".join(s.get("name", "") for s in sessions)[:250]
        dv_sess = DataValidation(type="list", formula1=f'"{names}"', allow_blank=True)
        ws.add_data_validation(dv_sess)
        dv_sess.add(f"C5:C{LAST + 2}")

    ws.column_dimensions["O"].hidden = True
    ws.column_dimensions["P"].hidden = True
    LOG_FIRST, LOG_LAST = 5, LAST + 2

    def L(col):  # absolute reference into the log
        return f"'{LOG}'!${col}${LOG_FIRST}:${col}${LOG_LAST}"

    # ============================================================ Dashboard
    dash = wb.create_sheet("Dashboard", 0)
    title(
        dash,
        f"{client.get('name', 'Training')} — {block.get('name', 'Training Block')}",
        f"{strategy.get('split', '')} · {client.get('goal_primary', '')} · "
        f"{per_week} sessions/week · {weeks}-week block · starts {start.isoformat()}",
        span=6,
    )
    dash.column_dimensions["A"].width = 30
    dash.column_dimensions["B"].width = 18
    for c in "CDEF":
        dash.column_dimensions[c].width = 16

    dash["A4"] = "Consistency"
    dash["A4"].font = SUB_FONT
    dash["A4"].fill = SUB_FILL
    dash.merge_cells("A4:B4")

    kv(dash, 5, "Current week of block", f'=MAX(1,INT((TODAY()-DATE({start.year},{start.month},{start.day}))/7)+1)')
    kv(dash, 6, "Sessions logged", f"=SUM({L('P')})")
    kv(dash, 7, "Sessions planned to date", f"=MIN({weeks},$B$5)*{per_week}")
    c = kv(dash, 8, "Consistency", '=IFERROR($B$6/$B$7,"")', fmt="0%", bold=True)
    c.font = Font(bold=True, size=12, color=ACCENT)
    kv(dash, 9, "Sessions skipped", f'=COUNTIF({L("L")},"Skipped")')

    dash["A11"] = "Training volume"
    dash["A11"].font = SUB_FONT
    dash["A11"].fill = SUB_FILL
    dash.merge_cells("A11:B11")
    kv(dash, 12, f"Total volume logged ({units}·reps)", f'=IFERROR(SUM({L("M")}),0)', fmt="#,##0")
    kv(dash, 13, "This week's volume", f'=IFERROR(SUMIFS({L("M")},{L("B")},$B$5),0)', fmt="#,##0")
    kv(dash, 14, "Last week's volume", f'=IFERROR(SUMIFS({L("M")},{L("B")},$B$5-1),0)', fmt="#,##0")
    kv(dash, 15, "Change vs last week", '=IFERROR(IF($B$14=0,"",$B$13/$B$14-1),"")', fmt="+0%;-0%;0%")
    kv(dash, 16, "Average RIR logged", f'=IFERROR(AVERAGEIFS({L("J")},{L("J")},">=0"),"")', fmt="0.0")

    dash["A18"] = "Recovery (last 7 days)"
    dash["A18"].font = SUB_FONT
    dash["A18"].fill = SUB_FILL
    dash.merge_cells("A18:B18")
    N = "'Training Notes'"
    kv(dash, 19, "Avg sleep (h)", f'=IFERROR(AVERAGEIFS({N}!$B$5:$B$400,{N}!$A$5:$A$400,">="&TODAY()-7),"")', fmt="0.0")
    kv(dash, 20, "Avg energy (1-5)", f'=IFERROR(AVERAGEIFS({N}!$D$5:$D$400,{N}!$A$5:$A$400,">="&TODAY()-7),"")', fmt="0.0")
    kv(dash, 21, "Avg fatigue (1-5)", f'=IFERROR(AVERAGEIFS({N}!$F$5:$F$400,{N}!$A$5:$A$400,">="&TODAY()-7),"")', fmt="0.0")
    kv(dash, 22, "Days with pain reported", f'=COUNTIF({N}!$G$5:$G$400,"Yes")')

    dash["D4"] = "Top lifts (best estimated 1RM)"
    dash["D4"].font = SUB_FONT
    dash["D4"].fill = SUB_FILL
    dash.merge_cells("D4:F4")
    header_row(dash, 5, ["", "", "", "Exercise", f"Best ({units})", "Est. 1RM"])
    for i in range(min(8, max(1, len(exercise_names)))):
        r = 6 + i
        pr = 5 + i
        dash.cell(row=r, column=4).value = f"=IF('Personal Records'!$A{pr}=\"\",\"\",'Personal Records'!$A{pr})"
        dash.cell(row=r, column=5).value = f"=IF('Personal Records'!$A{pr}=\"\",\"\",'Personal Records'!$B{pr})"
        dash.cell(row=r, column=6).value = f"=IF('Personal Records'!$A{pr}=\"\",\"\",'Personal Records'!$D{pr})"
        for col in (4, 5, 6):
            dash.cell(row=r, column=col).border = BOX

    dash["D16"] = "Deload trigger"
    dash["D16"].font = SUB_FONT
    dash.merge_cells("D16:F16")
    dash["D17"] = (prog.get("recovery", {}) or {}).get("deload_trigger", strategy.get("deload_policy", ""))
    dash["D17"].alignment = WRAP
    dash.merge_cells("D17:F20")

    dash["A24"] = (
        "Consistency is the number that predicts results. Volume is context, not a score — "
        "chasing it while technique or recovery slips is how people stall."
    )
    dash["A24"].font = MUTED
    dash.merge_cells("A24:F25")

    # ============================================================ Plan
    plan = wb.create_sheet("Workout Plan", 1)
    title(plan, "Workout Plan", "Reference — what you're meant to do. Record what you actually did in the Log.", span=9)
    header_row(
        plan, 4,
        ["Day", "Session", "Exercise", "Sets", "Reps", "Rest (s)", "RIR", "Cues", "Alternative"],
        [8, 15, 30, 7, 11, 9, 7, 42, 26],
    )
    plan.freeze_panes = "A5"
    r = 5
    for s in sessions:
        first = r
        for ex in s.get("exercises", []):
            vals = [
                s.get("day", ""), s.get("name", ""), ex.get("name", ""),
                ex.get("sets"), str(ex.get("reps", "")), ex.get("rest_sec"),
                str(ex.get("rir", "")), ex.get("cues", ""), ex.get("alternative", ""),
            ]
            for i, v in enumerate(vals, start=1):
                c = plan.cell(row=r, column=i, value=v)
                c.border = BOX
                c.alignment = WRAP if i in (8, 9) else Alignment(vertical="top")
            r += 1
        if s.get("warmup"):
            c = plan.cell(row=r, column=3, value="Warm-up: " + " · ".join(s["warmup"]))
            c.font = MUTED
            c.alignment = WRAP
            plan.merge_cells(start_row=r, start_column=3, end_row=r, end_column=9)
            r += 1
        if s.get("cooldown"):
            c = plan.cell(row=r, column=3, value="Cool-down: " + " · ".join(s["cooldown"]))
            c.font = MUTED
            c.alignment = WRAP
            plan.merge_cells(start_row=r, start_column=3, end_row=r, end_column=9)
            r += 1
        for rr in range(first, r):
            plan.cell(row=rr, column=1).fill = ZEBRA
            plan.cell(row=rr, column=2).fill = ZEBRA
        r += 1

    plan.cell(row=r + 1, column=1, value="Progression").font = SUB_FONT
    pc = plan.cell(row=r + 2, column=1, value=strategy.get("progression_model", ""))
    pc.alignment = WRAP
    plan.merge_cells(start_row=r + 2, start_column=1, end_row=r + 3, end_column=9)

    # ============================================================ Weekly Progress
    wk = wb.create_sheet("Weekly Progress", 3)
    title(wk, "Weekly Progress", "Week-over-week comparison. Everything here reads from the Log.", span=8)
    header_row(
        wk, 4,
        ["Week", "Sessions logged", "Planned", "Consistency", f"Volume ({units}·reps)",
         "Change vs prev", "Avg RIR", "Sets logged"],
        [8, 16, 10, 13, 18, 15, 10, 12],
    )
    wk.freeze_panes = "A5"
    for i in range(weeks):
        r = 5 + i
        wk.cell(row=r, column=1, value=i + 1)
        wk.cell(row=r, column=2).value = f'=IFERROR(SUMIFS({L("P")},{L("B")},$A{r}),0)'
        wk.cell(row=r, column=3, value=per_week)
        wk.cell(row=r, column=4).value = f'=IFERROR($B{r}/$C{r},"")'
        wk.cell(row=r, column=4).number_format = "0%"
        wk.cell(row=r, column=5).value = f'=IFERROR(SUMIFS({L("M")},{L("B")},$A{r}),0)'
        wk.cell(row=r, column=5).number_format = "#,##0"
        wk.cell(row=r, column=6).value = (
            f'=IFERROR(IF($E{r - 1}=0,"",$E{r}/$E{r - 1}-1),"")' if i else '=""'
        )
        wk.cell(row=r, column=6).number_format = "+0%;-0%;0%"
        wk.cell(row=r, column=7).value = f'=IFERROR(AVERAGEIFS({L("J")},{L("B")},$A{r},{L("J")},">=0"),"")'
        wk.cell(row=r, column=7).number_format = "0.0"
        wk.cell(row=r, column=8).value = f'=IFERROR(SUMIFS({L("G")},{L("B")},$A{r}),0)'
        for col in range(1, 9):
            wk.cell(row=r, column=col).border = BOX

    note = wk.cell(
        row=6 + weeks, column=1,
        value="Two consecutive weeks of falling volume or reps at the same load is a deload signal, "
              "not a reason to add weight. Check sleep and stress before changing the program.",
    )
    note.font = MUTED
    note.alignment = WRAP
    wk.merge_cells(start_row=6 + weeks, start_column=1, end_row=7 + weeks, end_column=8)

    # ============================================================ Personal Records
    pr = wb.create_sheet("Personal Records", 4)
    title(pr, "Personal Records", "Calculated from the Log — nothing to fill in by hand.", span=7)
    header_row(
        pr, 4,
        ["Exercise", f"Best weight ({units})", "Best reps (any load)", "Best est. 1RM",
         "Date of best 1RM", "Sets logged", "Last trained"],
        [30, 17, 18, 15, 16, 12, 14],
    )
    pr.freeze_panes = "A5"
    for i, name in enumerate(exercise_names):
        r = 5 + i
        esc = name.replace('"', '""')
        pr.cell(row=r, column=1, value=name)
        pr.cell(row=r, column=2).value = f'=IFERROR(SUMPRODUCT(MAX(({L("D")}=$A{r})*{L("I")})),0)'
        pr.cell(row=r, column=3).value = f'=IFERROR(SUMPRODUCT(MAX(({L("D")}=$A{r})*{L("H")})),0)'
        # Derive the 1RM from the raw numeric inputs (weight, reps) rather than
        # from the Log's Est. 1RM column: that column holds "" on empty rows, and
        # boolean * text is #VALUE!, which would silently collapse to 0 here.
        epley = f'{L("I")}*(1+{L("H")}/30)'
        pr.cell(row=r, column=4).value = (
            f'=IFERROR(ROUND(SUMPRODUCT(MAX(({L("D")}=$A{r})*{epley})),1),0)'
        )
        pr.cell(row=r, column=5).value = (
            f'=IFERROR(IF($D{r}=0,"",SUMPRODUCT(MAX(({L("D")}=$A{r})'
            f'*(ROUND({epley},1)=$D{r})*{L("A")}))),"")'
        )
        pr.cell(row=r, column=5).number_format = "yyyy-mm-dd"
        pr.cell(row=r, column=6).value = f'=COUNTIF({L("D")},$A{r})'
        pr.cell(row=r, column=7).value = (
            f'=IFERROR(IF(COUNTIF({L("D")},$A{r})=0,"",SUMPRODUCT(MAX(({L("D")}=$A{r})*{L("A")}))),"")'
        )
        pr.cell(row=r, column=7).number_format = "yyyy-mm-dd"
        for col in range(1, 8):
            pr.cell(row=r, column=col).border = BOX
        if i % 2:
            for col in range(1, 8):
                pr.cell(row=r, column=col).fill = ZEBRA

    n = pr.cell(
        row=6 + len(exercise_names), column=1,
        value="Estimated 1RM uses the Epley formula (weight x (1 + reps/30)). It is an estimate, "
              "most reliable under about 10 reps — useful for tracking a trend, not for picking a max attempt.",
    )
    n.font = MUTED
    n.alignment = WRAP
    pr.merge_cells(start_row=6 + len(exercise_names), start_column=1, end_row=7 + len(exercise_names), end_column=7)

    # ============================================================ Training Notes
    tn = wb.create_sheet("Training Notes", 5)
    title(tn, "Training Notes", "Recovery inputs. The Dashboard averages the last 7 days — "
                                "this is how you tell a programming problem from a recovery problem.", span=8)
    header_row(
        tn, 4,
        ["Date", "Sleep (h)", "Sleep quality 1-5", "Energy 1-5", "Soreness 1-5",
         "Fatigue 1-5", "Pain?", "Comments"],
        [12, 10, 16, 12, 13, 12, 9, 50],
    )
    tn.freeze_panes = "A5"
    dv_1_5 = DataValidation(type="whole", operator="between", formula1=1, formula2=5, allow_blank=True)
    tn.add_data_validation(dv_1_5)
    dv_yn = DataValidation(type="list", formula1='"No,Yes"', allow_blank=True)
    tn.add_data_validation(dv_yn)
    for i in range(400):
        r = 5 + i
        for col in range(1, 9):
            tn.cell(row=r, column=col).border = BOX
        tn.cell(row=r, column=1).number_format = "yyyy-mm-dd"
        tn.cell(row=r, column=8).alignment = WRAP
    dv_1_5.add(f"C5:F404")
    dv_yn.add(f"G5:G404")
    tip = tn.cell(
        row=406, column=1,
        value="Pain is not soreness. Any 'Yes' in the Pain column that persists beyond a couple of "
              "sessions means stop loading that movement and get it assessed.",
    )
    tip.font = MUTED
    tip.alignment = WRAP
    tn.merge_cells(start_row=406, start_column=1, end_row=407, end_column=8)

    wb.save(outpath)
    return outpath


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the Excel workout tracker from program.json")
    ap.add_argument("program")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--rows", type=int, default=1000, help="log rows to pre-format")
    a = ap.parse_args()

    try:
        with open(a.program, encoding="utf-8") as fh:
            prog = json.load(fh)
    except FileNotFoundError:
        print(f"error: no such file: {a.program}")
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: {a.program} is not valid JSON — {exc}")
        return 2

    name = (prog.get("client", {}).get("name") or "client").lower().replace(" ", "-")
    outdir = a.outdir.rstrip("/") or "."
    try:
        os.makedirs(outdir, exist_ok=True)
    except OSError as exc:
        print(f"error: cannot write to {outdir} — {exc}")
        return 2
    out = f"{outdir}/{name}-tracker.xlsx"
    path = build(prog, out, a.rows)
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
