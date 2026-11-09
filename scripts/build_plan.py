#!/usr/bin/env python3
"""Render the workout plan from program.json.

    python3 build_plan.py program.json --pdf --mobile [--outdir .]

--pdf      printable A4 guide (needs reportlab: pip install reportlab)
--mobile   self-contained responsive HTML for use in the gym (no dependencies)

Covers every section SKILL.md §4 requires: assessment, goals, strategy and
rationale, weekly schedule, daily workouts, warm-up/cool-down, progression,
recovery, benchmarks and the review date.
"""

import argparse
import html
import json
import os
import sys
from datetime import date, datetime, timedelta

INK = "#1F2933"
ACCENT = "#2F6F4E"
MUTED = "#6B7A74"


# ------------------------------------------------------------------ shared
def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        sys.exit(f"error: no such file: {path}")
    except json.JSONDecodeError as exc:
        sys.exit(f"error: {path} is not valid JSON — {exc}")


def review_date(block):
    try:
        start = datetime.strptime(block.get("start_date", ""), "%Y-%m-%d").date()
    except ValueError:
        start = date.today()
    return start + timedelta(weeks=int(block.get("review_after_weeks") or 4))


def fmt_rest(sec):
    if not sec:
        return "—"
    return f"{sec // 60}:{sec % 60:02d}" if sec >= 60 else f"{sec}s"


# ------------------------------------------------------------------ mobile
def build_mobile(prog, out):
    c = prog.get("client", {})
    s = prog.get("strategy", {})
    b = prog.get("block", {})
    units = c.get("units", "kg")
    e = html.escape

    cards = []
    for sess in prog.get("sessions", []):
        rows = []
        for ex in sess.get("exercises", []):
            alt = ex.get("alternative")
            cue = ex.get("cues")
            rows.append(f"""
      <div class="ex">
        <div class="exhead"><span class="name">{e(ex.get('name',''))}</span>
          <span class="sr">{ex.get('sets','')} × {e(str(ex.get('reps','')))}</span></div>
        <div class="meta"><span>rest {fmt_rest(ex.get('rest_sec'))}</span>
          <span>RIR {e(str(ex.get('rir','')))}</span>
          {'<span>' + e(str(ex.get('muscles', [''])[0])) + '</span>' if ex.get('muscles') else ''}</div>
        {f'<div class="cue">{e(cue)}</div>' if cue else ''}
        {f'<div class="alt">swap → {e(alt)}</div>' if alt else ''}
      </div>""")
        warm = ""
        if sess.get("warmup"):
            items = "".join(f"<li>{e(w)}</li>" for w in sess["warmup"])
            warm = f'<details class="wu"><summary>Warm-up</summary><ul>{items}</ul></details>'
        cool = ""
        if sess.get("cooldown"):
            items = "".join(f"<li>{e(w)}</li>" for w in sess["cooldown"])
            cool = f'<details class="wu"><summary>Cool-down</summary><ul>{items}</ul></details>'
        cards.append(f"""
  <details class="day" open>
    <summary><b>{e(sess.get('day',''))}</b> — {e(sess.get('name',''))}
      <span class="focus">{e(sess.get('focus',''))}</span></summary>
    {warm}{''.join(rows)}{cool}
  </details>""")

    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(c.get('name','Training'))} — {e(b.get('name','Plan'))}</title>
<style>
  :root {{ --ink:{INK}; --accent:{ACCENT}; --muted:{MUTED}; --line:#E3E8E6; --bg:#fff; --card:#fff; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --ink:#E8EDEB; --accent:#7FC6A0; --muted:#9BAAA4; --line:#2B3633; --bg:#141A18; --card:#1B2321; }}
  }}
  /* Artifact hosts stamp data-theme on the root; it must win in both directions. */
  :root[data-theme="light"] {{ --ink:{INK}; --accent:{ACCENT}; --muted:{MUTED}; --line:#E3E8E6; --bg:#fff; --card:#fff; }}
  :root[data-theme="dark"] {{ --ink:#E8EDEB; --accent:#7FC6A0; --muted:#9BAAA4; --line:#2B3633; --bg:#141A18; --card:#1B2321; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:16px 14px 64px; background:var(--bg); color:var(--ink);
    font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; max-width:760px; margin-inline:auto; }}
  h1 {{ font-size:1.35rem; margin:0 0 4px; }}
  .sub {{ color:var(--muted); font-size:.85rem; margin-bottom:18px; }}
  .strategy {{ background:var(--card); border:1px solid var(--line); border-left:3px solid var(--accent);
    border-radius:8px; padding:12px 14px; margin-bottom:18px; font-size:.9rem; }}
  .strategy b {{ color:var(--accent); }}
  details.day {{ background:var(--card); border:1px solid var(--line); border-radius:10px;
    margin-bottom:14px; padding:4px 0; }}
  details.day > summary {{ cursor:pointer; padding:12px 14px; font-size:1.05rem; list-style:none; }}
  details.day > summary::-webkit-details-marker {{ display:none; }}
  .focus {{ display:block; color:var(--muted); font-size:.78rem; font-weight:400; margin-top:2px; }}
  .ex {{ padding:11px 14px; border-top:1px solid var(--line); }}
  .exhead {{ display:flex; justify-content:space-between; align-items:baseline; gap:10px; }}
  .name {{ font-weight:600; }}
  .sr {{ font-variant-numeric:tabular-nums; font-weight:700; color:var(--accent); white-space:nowrap; }}
  .meta {{ display:flex; gap:12px; flex-wrap:wrap; color:var(--muted); font-size:.78rem; margin-top:3px; }}
  .cue {{ font-size:.82rem; margin-top:5px; }}
  .alt {{ font-size:.78rem; color:var(--muted); margin-top:3px; font-style:italic; }}
  details.wu {{ margin:8px 14px; font-size:.84rem; color:var(--muted); }}
  details.wu ul {{ margin:6px 0 0; padding-left:18px; }}
  .foot {{ margin-top:22px; font-size:.8rem; color:var(--muted); border-top:1px solid var(--line); padding-top:12px; }}
</style></head><body>
<h1>{e(c.get('name','Training Plan'))}</h1>
<div class="sub">{e(b.get('name',''))} · {e(s.get('split',''))} · {e(c.get('goal_primary',''))}
 · {b.get('weeks','')} weeks · loads in {e(units)}</div>
<div class="strategy"><b>Progression.</b> {e(s.get('progression_model',''))}
{f"<br><b>Deload.</b> {e(s.get('deload_policy',''))}" if s.get('deload_policy') else ''}</div>
{''.join(cards)}
<div class="foot">Review on {review_date(b).isoformat()}. Log every session —
what you actually did is the only thing that tells you whether this is working.<br>
General fitness guidance, not medical advice. Stop any exercise that causes sharp or
joint pain and get it assessed.</div>
</body></html>"""
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(doc)
    return out


# ------------------------------------------------------------------ pdf
def build_pdf(prog, out):
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import (KeepTogether, PageBreak, Paragraph,
                                        SimpleDocTemplate, Spacer, Table, TableStyle)
    except ImportError:
        sys.exit("error: reportlab is required for PDF.\n       pip install reportlab\n"
                 "       (--mobile works without it.)")

    c = prog.get("client", {})
    s = prog.get("strategy", {})
    b = prog.get("block", {})
    units = c.get("units", "kg")
    ink, acc = colors.HexColor(INK), colors.HexColor(ACCENT)
    muted = colors.HexColor(MUTED)

    ss = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=ss["Title"], fontSize=20, textColor=ink, alignment=TA_LEFT, spaceAfter=2)
    SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontSize=9.5, textColor=muted, spaceAfter=14)
    H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=12.5, textColor=acc, spaceBefore=14, spaceAfter=5)
    H3 = ParagraphStyle("H3", parent=ss["Heading3"], fontSize=10.5, textColor=ink, spaceBefore=9, spaceAfter=3)
    BODY = ParagraphStyle("BODY", parent=ss["Normal"], fontSize=9.5, leading=13.5, textColor=ink)
    SMALL = ParagraphStyle("SMALL", parent=ss["Normal"], fontSize=8, leading=11, textColor=muted)
    CELL = ParagraphStyle("CELL", parent=ss["Normal"], fontSize=8.2, leading=10.5, textColor=ink)

    doc = SimpleDocTemplate(
        out, pagesize=A4, title=f"{c.get('name','')} — {b.get('name','Training Plan')}",
        author="trainer",
        leftMargin=16 * mm, rightMargin=16 * mm, topMargin=15 * mm, bottomMargin=15 * mm,
    )
    F = []

    F.append(Paragraph(html.escape(c.get("name", "Training Plan")), H1))
    F.append(Paragraph(
        f"{html.escape(b.get('name',''))} &nbsp;·&nbsp; {html.escape(s.get('split',''))} "
        f"&nbsp;·&nbsp; {b.get('weeks','')} weeks &nbsp;·&nbsp; starts "
        f"{html.escape(str(b.get('start_date','')))} &nbsp;·&nbsp; loads in {units}", SUB))

    # --- assessment
    F.append(Paragraph("1. Assessment", H2))
    rows = [
        ["Training age", c.get("training_age", "—"), "Days / week", c.get("days_per_week", "—")],
        ["Primary goal", c.get("goal_primary", "—"), "Session length", f"{c.get('session_minutes','—')} min"],
        ["Secondary goal", c.get("goal_secondary", "—"), "Environment", c.get("environment", "—")],
        ["Age", c.get("age", "—"), "Sleep", f"{c.get('sleep_hours','—')} h"],
    ]
    t = Table([[Paragraph(f"<b>{html.escape(str(a))}</b>", CELL), Paragraph(html.escape(str(bb)), CELL),
                Paragraph(f"<b>{html.escape(str(cc))}</b>", CELL), Paragraph(html.escape(str(d)), CELL)]
               for a, bb, cc, d in rows], colWidths=[30 * mm, 48 * mm, 30 * mm, 48 * mm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDE5E2")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F7F5")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#F3F7F5")),
    ]))
    F.append(t)

    if c.get("equipment"):
        F.append(Spacer(1, 5))
        F.append(Paragraph("<b>Equipment:</b> " + html.escape(", ".join(c["equipment"])), BODY))
    if c.get("limitations"):
        F.append(Paragraph("<b>Limitations worked around:</b> " + html.escape("; ".join(c["limitations"])), BODY))

    # --- strategy
    F.append(Paragraph("2. Strategy", H2))
    F.append(Paragraph(html.escape(s.get("rationale", "")), BODY))
    for label, key in (("Weekly volume", "weekly_volume_notes"),
                       ("Progression", "progression_model"),
                       ("Deload", "deload_policy")):
        if s.get(key):
            F.append(Spacer(1, 4))
            F.append(Paragraph(f"<b>{label}.</b> " + html.escape(s[key]), BODY))
    if s.get("assumptions"):
        F.append(Spacer(1, 6))
        F.append(Paragraph("<b>Assumptions this plan is built on</b> — tell me if any are wrong:", BODY))
        for a in s["assumptions"]:
            F.append(Paragraph("• " + html.escape(a), SMALL))

    # --- schedule
    F.append(Paragraph("3. Weekly schedule", H2))
    sched = [[Paragraph("<b>Day</b>", CELL), Paragraph("<b>Session</b>", CELL),
              Paragraph("<b>Focus</b>", CELL), Paragraph("<b>Exercises</b>", CELL)]]
    for sess in prog.get("sessions", []):
        sched.append([Paragraph(html.escape(sess.get("day", "")), CELL),
                      Paragraph(html.escape(sess.get("name", "")), CELL),
                      Paragraph(html.escape(sess.get("focus", "")), CELL),
                      Paragraph(str(len(sess.get("exercises", []))), CELL)])
    t = Table(sched, colWidths=[18 * mm, 34 * mm, 90 * mm, 20 * mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), acc), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDE5E2")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAF9")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    F.append(t)

    # --- sessions
    F.append(PageBreak())
    F.append(Paragraph("4. Workouts", H2))
    for sess in prog.get("sessions", []):
        blk = [Paragraph(f"{html.escape(sess.get('day',''))} — {html.escape(sess.get('name',''))}", H3)]
        if sess.get("warmup"):
            blk.append(Paragraph("<b>Warm-up:</b> " + html.escape(" · ".join(sess["warmup"])), SMALL))
            blk.append(Spacer(1, 3))
        data = [[Paragraph(f"<b>{h}</b>", CELL) for h in
                 ("Exercise", "Sets", "Reps", "Rest", "RIR", "Cues / alternative")]]
        for ex in sess.get("exercises", []):
            notes = []
            if ex.get("cues"):
                notes.append(html.escape(ex["cues"]))
            if ex.get("alternative"):
                notes.append(f"<i>swap → {html.escape(ex['alternative'])}</i>")
            if ex.get("note"):
                notes.append(f"<i>{html.escape(ex['note'])}</i>")
            data.append([
                Paragraph(f"<b>{html.escape(ex.get('name',''))}</b>", CELL),
                Paragraph(str(ex.get("sets", "")), CELL),
                Paragraph(html.escape(str(ex.get("reps", ""))), CELL),
                Paragraph(fmt_rest(ex.get("rest_sec")), CELL),
                Paragraph(html.escape(str(ex.get("rir", ""))), CELL),
                Paragraph("<br/>".join(notes), CELL),
            ])
        t = Table(data, colWidths=[44 * mm, 11 * mm, 17 * mm, 13 * mm, 10 * mm, 67 * mm], repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E3EFE8")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDE5E2")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        blk.append(t)
        if sess.get("cooldown"):
            blk.append(Spacer(1, 3))
            blk.append(Paragraph("<b>Cool-down:</b> " + html.escape(" · ".join(sess["cooldown"])), SMALL))
        blk.append(Spacer(1, 9))
        F.append(KeepTogether(blk))

    # --- progression, recovery, benchmarks
    F.append(PageBreak())
    F.append(Paragraph("5. Progressive overload", H2))
    F.append(Paragraph(html.escape(s.get("progression_model", "")), BODY))
    F.append(Spacer(1, 4))
    F.append(Paragraph(
        "Read it off the log, not off the calendar: hit the top of the rep range on every set with "
        "clean technique, then add load and drop back to the bottom of the range. Same performance "
        "two weeks running means hold. Declining performance two weeks running means deload — "
        "not more weight.", BODY))

    rec = prog.get("recovery", {}) or {}
    if rec:
        F.append(Paragraph("6. Recovery", H2))
        for label, key in (("Sleep", "sleep"), ("Nutrition", "nutrition_note"),
                           ("Deload trigger", "deload_trigger"), ("Notes", "notes")):
            if rec.get(key):
                F.append(Paragraph(f"<b>{label}.</b> " + html.escape(rec[key]), BODY))
                F.append(Spacer(1, 3))

    if prog.get("benchmarks"):
        F.append(Paragraph("7. Benchmarks", H2))
        data = [[Paragraph(f"<b>{h}</b>", CELL) for h in ("Metric", "How to test", "Every")]]
        for bm in prog["benchmarks"]:
            data.append([Paragraph(html.escape(bm.get("metric", "")), CELL),
                         Paragraph(html.escape(bm.get("how", "")), CELL),
                         Paragraph(f"{bm.get('every_weeks','—')} wk", CELL)])
        t = Table(data, colWidths=[46 * mm, 100 * mm, 16 * mm], repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E3EFE8")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDE5E2")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        F.append(t)

    F.append(Paragraph("8. Review", H2))
    F.append(Paragraph(
        f"Next review: <b>{review_date(b).isoformat()}</b>. Bring the tracker — the decision about what "
        "to change should come from logged sessions, not from memory. Come back sooner if anything hurts, "
        "performance drops two weeks in a row, or your schedule changes.", BODY))

    F.append(Spacer(1, 12))
    F.append(Paragraph(
        "General fitness guidance, not medical advice. This plan does not diagnose or treat injury. "
        "Stop any exercise causing sharp, radiating or joint pain and have it assessed. "
        "Results depend on consistency, sleep, nutrition and factors outside any program.", SMALL))

    doc.build(F)
    return out


# ------------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser(description="Render the workout plan from program.json")
    ap.add_argument("program")
    ap.add_argument("--pdf", action="store_true")
    ap.add_argument("--mobile", action="store_true")
    ap.add_argument("--outdir", default=".")
    a = ap.parse_args()
    if not (a.pdf or a.mobile):
        a.pdf = a.mobile = True

    prog = load(a.program)
    name = (prog.get("client", {}).get("name") or "client").lower().replace(" ", "-")
    outdir = a.outdir.rstrip("/") or "."
    try:
        os.makedirs(outdir, exist_ok=True)
    except OSError as exc:
        print(f"error: cannot write to {outdir} — {exc}")
        return 2
    base = f"{outdir}/{name}"

    made = []
    if a.pdf:
        made.append(build_pdf(prog, f"{base}-plan.pdf"))
    if a.mobile:
        made.append(build_mobile(prog, f"{base}-plan-mobile.html"))
    for m in made:
        print(f"wrote {m}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
