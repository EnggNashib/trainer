#!/usr/bin/env python3
"""Build a self-contained HTML workout logger from a program.json.

    python3 build_logger.py program.json [--outdir .]

Stdlib only — no dependencies, ever. The output is one HTML file that can be
opened in a browser or emitted as an artifact: pick the session, type what you
actually lifted, and export rows that paste straight into columns A–L of the
Excel tracker's Log sheet.

It is a logger, not a tracker. It holds the current session in the browser
(localStorage, when the host allows it) and exports on demand. The Excel
workbook from build_tracker.py is the durable record with the rollup formulas —
this is for the gym floor, where a spreadsheet is unusable.
"""

import argparse
import json
import os
import sys
from datetime import date

INK = "#1F2933"
ACCENT = "#2F6F4E"
MUTED = "#6B7A74"

# Columns A–L of the tracker's Log sheet, in order. Volume, Est. 1RM, _tag and
# _new are formula columns and are deliberately not exported.
LOG_COLUMNS = [
    "Date", "Week", "Session", "Exercise", "Plan Sets", "Plan Reps",
    "Actual Sets", "Actual Reps", "Weight", "RIR", "Rest (s)", "Status",
]


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        sys.exit(f"error: no such file: {path}")
    except json.JSONDecodeError as exc:
        sys.exit(f"error: {path} is not valid JSON — {exc}")


def model(prog):
    """Reduce program.json to only what the logger needs, as plain JSON."""
    client = prog.get("client", {})
    block = prog.get("block", {})
    sessions = []
    for s in prog.get("sessions", []):
        exercises = []
        for e in s.get("exercises", []):
            # Key names follow program_schema.json exactly.
            exercises.append({
                "name": e.get("name", "—"),
                "sets": e.get("sets") or 0,
                "reps": str(e.get("reps", "")),
                "rir": e.get("rir", ""),
                "rest": e.get("rest_sec") or 0,
                "cue": e.get("cues") or "",
                "load": e.get("load_guidance") or "",
                "alt": e.get("alternative") or "",
            })
        sessions.append({
            "name": s.get("name") or s.get("day") or "Session",
            "focus": s.get("focus") or "",
            "exercises": exercises,
        })
    return {
        "program": block.get("name") or "Training block",
        "client": client.get("name") or "",
        "units": client.get("units") or "kg",
        "weeks": int(block.get("weeks") or 4),
        "start": block.get("start_date") or str(date.today()),
        "sessions": sessions,
    }


HTML = """<title>{title}</title>
<style>
  :root {{
    --ink:{ink}; --accent:{accent}; --muted:{muted};
    --line:#E3E8E6; --bg:#F6F7F5; --card:#FFFFFF; --wash:#EAF2ED; --ok:#2F6F4E;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --ink:#E8EDEB; --accent:#7FC6A0; --muted:#9BAAA4;
      --line:#2B3633; --bg:#141A18; --card:#1B2321; --wash:#1F2C25; --ok:#7FC6A0;
    }}
  }}
  :root[data-theme="light"] {{
    --ink:{ink}; --accent:{accent}; --muted:{muted};
    --line:#E3E8E6; --bg:#F6F7F5; --card:#FFFFFF; --wash:#EAF2ED; --ok:#2F6F4E;
  }}
  :root[data-theme="dark"] {{
    --ink:#E8EDEB; --accent:#7FC6A0; --muted:#9BAAA4;
    --line:#2B3633; --bg:#141A18; --card:#1B2321; --wash:#1F2C25; --ok:#7FC6A0;
  }}
  @media (prefers-reduced-motion: reduce) {{ * {{ transition:none !important; }} }}

  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:14px 12px 96px; background:var(--bg); color:var(--ink);
    font:16px/1.5 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif;
    max-width:720px; margin-inline:auto; -webkit-font-smoothing:antialiased; }}

  header {{ margin-bottom:14px; }}
  h1 {{ font-size:1.2rem; margin:0 0 2px; letter-spacing:-.01em; }}
  .sub {{ color:var(--muted); font-size:.82rem; }}

  .controls {{ display:flex; gap:8px; flex-wrap:wrap; margin:14px 0 16px; }}
  .controls label {{ display:block; font-size:.72rem; text-transform:uppercase;
    letter-spacing:.08em; color:var(--muted); margin-bottom:4px; font-weight:600; }}
  select, input[type="date"], input[type="number"] {{
    font:inherit; color:inherit; background:var(--card);
    border:1px solid var(--line); border-radius:7px; padding:9px 10px; }}
  select {{ flex:1 1 150px; min-width:0; }}
  input[type="date"] {{ flex:0 0 auto; }}
  input:focus, select:focus, button:focus-visible {{
    outline:2px solid var(--accent); outline-offset:1px; }}

  .ex {{ background:var(--card); border:1px solid var(--line); border-radius:10px;
    margin-bottom:12px; overflow:hidden; }}
  .exhead {{ display:flex; justify-content:space-between; align-items:baseline;
    gap:10px; padding:12px 14px 8px; }}
  .exname {{ font-weight:600; }}
  .plan {{ font-variant-numeric:tabular-nums; font-weight:700; color:var(--accent);
    white-space:nowrap; font-size:.9rem; }}
  .cue {{ padding:0 14px 8px; font-size:.8rem; color:var(--muted); }}

  table {{ width:100%; border-collapse:collapse; font-variant-numeric:tabular-nums; }}
  thead th {{ font-size:.68rem; text-transform:uppercase; letter-spacing:.07em;
    color:var(--muted); font-weight:600; text-align:left;
    padding:6px 8px; border-top:1px solid var(--line); }}
  thead th:first-child {{ padding-left:14px; width:38px; }}
  tbody td {{ padding:5px 8px; border-top:1px solid var(--line); }}
  tbody td:first-child {{ padding-left:14px; color:var(--muted); font-size:.82rem; }}
  tbody input {{ width:100%; min-width:58px; padding:7px 8px; }}
  tr.done {{ background:var(--wash); }}
  .tick {{ appearance:none; width:22px; height:22px; border:1px solid var(--line);
    border-radius:5px; background:var(--card); cursor:pointer; display:grid;
    place-items:center; padding:0; color:transparent; font-size:13px; font-weight:700; }}
  .tick[aria-pressed="true"] {{ background:var(--ok); border-color:var(--ok); color:#fff; }}

  .bar {{ position:fixed; left:0; right:0; bottom:0; background:var(--card);
    border-top:1px solid var(--line); padding:10px 14px;
    display:flex; align-items:center; gap:10px; flex-wrap:wrap; }}
  .bar .tally {{ flex:1 1 auto; font-size:.84rem; color:var(--muted);
    font-variant-numeric:tabular-nums; }}
  .bar .tally b {{ color:var(--ink); }}
  button.act {{ font:inherit; font-size:.88rem; font-weight:600; cursor:pointer;
    border-radius:7px; padding:9px 14px; border:1px solid var(--line);
    background:transparent; color:var(--ink); }}
  button.act.primary {{ background:var(--accent); border-color:var(--accent); color:#fff; }}

  dialog {{ border:1px solid var(--line); border-radius:10px; background:var(--card);
    color:var(--ink); max-width:min(680px,92vw); padding:18px; }}
  dialog::backdrop {{ background:rgba(0,0,0,.45); }}
  dialog h2 {{ margin:0 0 6px; font-size:1rem; }}
  dialog p {{ margin:0 0 12px; font-size:.85rem; color:var(--muted); }}
  pre {{ margin:0; padding:12px; background:var(--bg); border:1px solid var(--line);
    border-radius:7px; font:12px/1.5 ui-monospace,Menlo,Consolas,monospace;
    overflow:auto; max-height:46vh; white-space:pre; }}
  .row {{ display:flex; gap:8px; justify-content:flex-end; margin-top:12px; }}
  .note {{ font-size:.76rem; color:var(--muted); margin-top:18px; text-align:center; }}
</style>

<header>
  <h1>{heading}</h1>
  <div class="sub" id="sub"></div>
</header>

<div class="controls">
  <div><label for="sess">Session</label><select id="sess"></select></div>
  <div><label for="wk">Week</label><select id="wk"></select></div>
  <div><label for="dt">Date</label><input type="date" id="dt"></div>
</div>

<div id="body"></div>

<p class="note" id="note"></p>

<div class="bar">
  <span class="tally" id="tally"></span>
  <button class="act" id="clear" type="button">Clear session</button>
  <button class="act primary" id="export" type="button">Export rows</button>
</div>

<dialog id="dlg">
  <h2>Rows for the tracker</h2>
  <p>Paste into the Log sheet at the first empty row, column A. Columns match
     A–L exactly; Volume and Est.&nbsp;1RM are formulas and fill themselves.</p>
  <pre id="out"></pre>
  <div class="row">
    <button class="act" id="csv" type="button">Download CSV</button>
    <button class="act" id="cp" type="button">Copy</button>
    <button class="act primary" id="close" type="button">Done</button>
  </div>
</dialog>

<script>
const P = {model};
const COLS = {cols};

const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c =>
  ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[c]));

/* ---- state: {{ "<week>|<session>|<date>": {{ "<ex>|<set>": {{w,r,done}} }} }} ---- */
const KEY = "trainer-log:" + P.program;
let state = {{}};
try {{ state = JSON.parse(localStorage.getItem(KEY) || "{{}}"); }} catch {{}}
const save = () => {{ try {{ localStorage.setItem(KEY, JSON.stringify(state)); }} catch {{}} }};

const slot = () => `${{$("wk").value}}|${{$("sess").value}}|${{$("dt").value}}`;
const bucket = () => (state[slot()] = state[slot()] || {{}});

function boot() {{
  $("sub").textContent =
    [P.client, P.units === "lb" ? "pounds" : "kilograms"].filter(Boolean).join(" · ");
  $("sess").innerHTML = P.sessions
    .map((s, i) => `<option value="${{i}}">${{esc(s.name)}}</option>`).join("");
  $("wk").innerHTML = Array.from({{length: P.weeks}}, (_, i) =>
    `<option value="${{i + 1}}">Week ${{i + 1}}</option>`).join("");
  $("dt").value = new Date().toISOString().slice(0, 10);
  $("note").textContent = "Entries stay in this browser. Export before you close the tab.";
  ["sess", "wk", "dt"].forEach(id => $(id).onchange = render);
  render();
}}

function render() {{
  const s = P.sessions[+$("sess").value];
  const b = bucket();
  $("body").innerHTML = s.exercises.map((e, ei) => {{
    const rows = Array.from({{length: Math.max(1, e.sets)}}, (_, si) => {{
      const k = `${{ei}}|${{si}}`;
      const v = b[k] || {{}};
      return `<tr data-k="${{k}}" class="${{v.done ? "done" : ""}}">
        <td>${{si + 1}}</td>
        <td><input type="number" step="0.5" inputmode="decimal" data-f="w"
             value="${{v.w ?? ""}}" placeholder="—"></td>
        <td><input type="number" step="1" inputmode="numeric" data-f="r"
             value="${{v.r ?? ""}}" placeholder="${{esc(e.reps)}}"></td>
        <td><button class="tick" type="button" aria-pressed="${{!!v.done}}"
             aria-label="Set ${{si + 1}} done">&check;</button></td>
      </tr>`;
    }}).join("");
    const rest = e.rest ? `${{Math.floor(e.rest / 60)}}:${{String(e.rest % 60).padStart(2, "0")}}` : "—";
    return `<div class="ex" data-ei="${{ei}}">
      <div class="exhead">
        <span class="exname">${{esc(e.name)}}</span>
        <span class="plan">${{e.sets}}&times;${{esc(e.reps)}}${{
          e.rir !== "" && e.rir !== null ? ` @ RIR ${{esc(e.rir)}}` : ""}}</span>
      </div>
      <div class="cue">rest ${{rest}}${{e.load ? " · " + esc(e.load) : ""}}${{
        e.cue ? " · " + esc(e.cue) : ""}}${{e.alt ? " · or " + esc(e.alt) : ""}}</div>
      <table>
        <thead><tr><th>Set</th><th>${{P.units}}</th><th>Reps</th><th></th></tr></thead>
        <tbody>${{rows}}</tbody>
      </table>
    </div>`;
  }}).join("");
  wire();
  tally();
}}

function wire() {{
  $("body").querySelectorAll("tr").forEach(tr => {{
    const ei = +tr.closest(".ex").dataset.ei;
    const k = `${{ei}}|${{tr.dataset.k.split("|")[1]}}`;
    const b = bucket();
    tr.querySelectorAll("input").forEach(inp => {{
      inp.oninput = () => {{
        b[k] = b[k] || {{}};
        const v = inp.value === "" ? null : +inp.value;
        b[k][inp.dataset.f] = v;
        if (v !== null && !b[k].done) {{ b[k].done = true; tr.classList.add("done");
          tr.querySelector(".tick").setAttribute("aria-pressed", "true"); }}
        save(); tally();
      }};
    }});
    const tick = tr.querySelector(".tick");
    tick.onclick = () => {{
      b[k] = b[k] || {{}};
      b[k].done = !b[k].done;
      tick.setAttribute("aria-pressed", !!b[k].done);
      tr.classList.toggle("done", !!b[k].done);
      save(); tally();
    }};
  }});
}}

function tally() {{
  const s = P.sessions[+$("sess").value];
  const b = bucket();
  let sets = 0, vol = 0, planned = 0;
  s.exercises.forEach((e, ei) => {{
    planned += Math.max(1, e.sets);
    for (let si = 0; si < Math.max(1, e.sets); si++) {{
      const v = b[`${{ei}}|${{si}}`];
      if (v && v.done) {{ sets++; if (v.w && v.r) vol += v.w * v.r; }}
    }}
  }});
  $("tally").innerHTML =
    `<b>${{sets}}</b>/${{planned}} sets · volume <b>${{Math.round(vol)}}</b> ${{P.units}}`;
}}

/* ---- export: columns A–L of the tracker's Log sheet ---- */
function rows() {{
  const s = P.sessions[+$("sess").value];
  const b = bucket();
  const out = [];
  s.exercises.forEach((e, ei) => {{
    let actual = 0;
    const reps = [], weights = [];
    for (let si = 0; si < Math.max(1, e.sets); si++) {{
      const v = b[`${{ei}}|${{si}}`];
      if (v && v.done) {{ actual++; if (v.r) reps.push(v.r); if (v.w) weights.push(v.w); }}
    }}
    if (!actual) return;
    const avg = a => a.length ? Math.round(a.reduce((x, y) => x + y, 0) / a.length * 10) / 10 : "";
    out.push([
      $("dt").value, $("wk").value, s.name, e.name,
      e.sets, e.reps, actual, avg(reps), avg(weights),
      e.rir ?? "", e.rest || "", "Done",
    ]);
  }});
  return out;
}}

$("export").onclick = () => {{
  const r = rows();
  $("out").textContent = r.length
    ? [COLS.join("\\t"), ...r.map(x => x.join("\\t"))].join("\\n")
    : "Nothing logged yet — tick a set first.";
  $("dlg").showModal();
}};
$("close").onclick = () => $("dlg").close();
$("cp").onclick = async () => {{
  try {{ await navigator.clipboard.writeText($("out").textContent); $("cp").textContent = "Copied"; }}
  catch {{ const rg = document.createRange(); rg.selectNodeContents($("out"));
    const sel = getSelection(); sel.removeAllRanges(); sel.addRange(rg);
    $("cp").textContent = "Select + copy"; }}
  setTimeout(() => $("cp").textContent = "Copy", 1600);
}};
$("csv").onclick = () => {{
  const r = rows();
  if (!r.length) return;
  const q = x => /[",\\n]/.test(String(x)) ? '"' + String(x).replace(/"/g, '""') + '"' : x;
  const csv = [COLS.map(q).join(","), ...r.map(x => x.map(q).join(","))].join("\\n");
  const a = document.createElement("a");
  a.href = "data:text/csv;charset=utf-8," + encodeURIComponent(csv);
  a.download = `${{$("dt").value}}-${{P.sessions[+$("sess").value].name}}.csv`
    .replace(/\\s+/g, "-").toLowerCase();
  a.click();
}};
$("clear").onclick = () => {{
  if (!confirm("Clear everything logged for this session and date?")) return;
  delete state[slot()]; save(); render();
}};

boot();
</script>
"""


def build_logger(prog, out):
    m = model(prog)
    if not m["sessions"]:
        sys.exit("error: program.json has no sessions — nothing to log")
    title = f"{m['program']} — logger"
    html = HTML.format(
        title=title,
        heading=m["program"],
        ink=INK, accent=ACCENT, muted=MUTED,
        model=json.dumps(m, ensure_ascii=False),
        cols=json.dumps(LOG_COLUMNS),
    )
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the HTML workout logger from program.json")
    ap.add_argument("program")
    ap.add_argument("--outdir", default=".")
    a = ap.parse_args()

    prog = load(a.program)
    name = (prog.get("client", {}).get("name") or "client").lower().replace(" ", "-")
    outdir = a.outdir.rstrip("/") or "."
    try:
        os.makedirs(outdir, exist_ok=True)
    except OSError as exc:
        print(f"error: cannot write to {outdir} — {exc}")
        return 2

    print(f"wrote {build_logger(prog, f'{outdir}/{name}-logger.html')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
