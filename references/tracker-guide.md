# The tracker workbook

What each sheet does, and how to explain it in one line when you hand it over.

## Sheets

| Sheet | What it's for |
| --- | --- |
| **Dashboard** | Read-only summary. Consistency, volume trend, recovery averages, top lifts. |
| **Workout Plan** | Reference copy of the program. What you're *meant* to do. |
| **Workout Log** | The only sheet you type into regularly. What you *actually* did. |
| **Weekly Progress** | Week-over-week comparison, calculated from the Log. |
| **Personal Records** | Best weight, best reps, best estimated 1RM per exercise. Calculated. |
| **Training Notes** | Sleep, energy, soreness, fatigue, pain. Daily, takes 15 seconds. |

## Workout Log columns

White = you type it. Grey = calculated, don't touch.

| Column | Notes |
| --- | --- |
| Date | Real date. Drives the week number and every weekly rollup. |
| Week | *Calculated* — week of the block, from the start date. |
| Session | Dropdown of your session names. |
| Exercise | Must match the plan's spelling exactly, or PRs won't group. |
| Plan Sets / Plan Reps | Pre-filled from the program — what you were asked to do. |
| Actual Sets / Actual Reps / Weight | What happened. The honest columns. |
| RIR | Reps left in reserve on the hardest set. |
| Rest (s) | Optional; useful when you suspect rushing. |
| Status | Completed / Partial / Skipped. **Drives consistency — don't leave it blank.** |
| Volume | *Calculated* — sets × reps × weight. |
| Est. 1RM | *Calculated* — Epley. An estimate, best under ~10 reps. |

The first week is pre-seeded with your program so the shape is obvious. Copy
the block down for week 2 onward, or just type as you go.

**Planned vs actual is the entire point.** A log that only records what you
intended tells you nothing. The gap between the two columns is the data.

## Explaining it when you hand it over

> Log every set as you go, or right after. The only columns that matter are
> weight, reps, and Status — everything else calculates. At the end of the
> week, glance at Weekly Progress: if volume and reps are climbing at the same
> RIR, it's working. Next time we talk, send me the file.

## Reading it as a coach

When they send it back, look in this order:

1. **Consistency %** — below ~80% is a scheduling problem, not a programming
   problem. Fix the schedule before touching the program.
2. **Weekly volume trend** — flat or falling for two weeks at constant load is
   a fatigue signal.
3. **PRs** — which lifts moved? A program where nothing moved in 4 weeks needs
   changing. One where everything moved means the progression is working;
   leave it alone.
4. **Training Notes** — sleep under 6 h, fatigue 4–5, or any "Yes" in Pain
   reframes everything above. Low performance plus bad sleep is a recovery
   problem; do not add volume to fix it.
5. **Skipped sessions** — which day keeps getting skipped? That day is wrong
   for their life. Move it or shrink it.

## Honest limits

- **Excel only computes when opened in a spreadsheet app.** openpyxl writes
  formulas, it does not evaluate them. The file will look blank-ish in a plain
  text preview — that's normal. Open it in Excel, Numbers, LibreOffice or
  Google Sheets.
- **You do not remember their history between sessions.** The workbook *is*
  the memory. Ask for the current file every time; never reconstruct from
  what you think you recall.
- **Estimated 1RM is an estimate.** Useful as a trend line, not as a number to
  attempt. Say so if they treat it as a max.
- Exercise names must match between Log and Plan for PR grouping. If someone
  types "DB bench" one week and "Dumbbell bench press" the next, they get two
  PR rows. Mention it once when handing over.
