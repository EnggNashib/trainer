# trainer — evidence-based strength & physique programming

An agent skill that works like a strength coach rather than a workout
generator: it assesses the person, explains the training strategy and gets
agreement, asks what they actually want built, and then produces **real files**
— a printable PDF plan, a mobile view for the gym, and an Excel tracker whose
formulas genuinely calculate.

## What makes it a system, not a generator

- **Assessment before programming.** Where the host can render artifacts, an
  8-step clickable intake wizard (`assets/intake.html`) whose output is a
  ready-made `client` object; everywhere else, one question per message like a
  conversation rather than a form. Nothing is invented; every assumption is
  stated in the plan.
- **Strategy agreed before exercises are picked.** A wrong split caught at that
  point costs one message instead of a whole program.
- **One source of truth.** The coach writes `program.json`; the PDF, the mobile
  page and the workbook all render from it, so they cannot disagree.
- **A mechanical quality gate.** `validate_program.py` fails the build when
  sessions exceed available days, an exercise needs equipment the person
  doesn't own, a session overruns its time budget, or sets/reps/rest/RIR are
  missing.
- **Planned vs actual.** The tracker records both. The gap between them is the
  only thing that tells you whether the program is working.

## Install

The skill is one folder named `trainer`. Nothing in it is host-specific — no
tool is required by name, and every path is resolved relative to the skill's own
directory — so the same folder works everywhere below.

### claude.ai, web or desktop — no terminal needed

1. Download **`trainer.zip`** from the
   [latest release](../../releases/latest).
2. In claude.ai, go to **Settings → Capabilities → Skills** and upload it.
3. Ask: *"build me a training program"*.

That's the whole thing. The intake form appears as a clickable wizard; you fill
it in and paste one block back.

### Claude Code

```bash
git clone https://github.com/EnggNashib/trainer.git
cd trainer && ./install.sh               # all projects (~/.claude/skills)
./install.sh --project                   # this project only
```

Then `/reload-skills` and call it with `/trainer`. Plain `cp -R trainer
~/.claude/skills/` works just as well if you'd rather not run a script.

### Codex CLI

```bash
./install.sh --codex                     # → ~/.agents/skills
```

### ChatGPT

There is no skill installer, so it runs one of two ways. Either
paste `SKILL.md` into a Project's custom instructions (or a custom GPT) and
upload the `scripts/` files when a deliverable is wanted, or upload
`trainer.zip` into the conversation and ask it to unpack and follow `SKILL.md`.
Behaviour is the same; only file handling is manual.

Then just ask: *"build me a training program"* or *"I need a workout tracker"*.
In Claude Code you can also invoke it directly as `/trainer`.

## Dependencies

| Deliverable | Needs | Status |
| --- | --- | --- |
| Interactive plan (HTML) | nothing (stdlib) | always works |
| Interactive logger (HTML) | nothing (stdlib) | always works |
| Validator | nothing (stdlib) | always works |
| PDF plan | `reportlab` | `pip install reportlab` |
| Excel tracker | `openpyxl` | `pip install openpyxl` |

On claude.ai the two HTML deliverables are emitted as artifacts — they open in
one click, and they are the two that cannot fail on a missing dependency.

Both scripts exit non-zero with the exact install command if a dependency is
missing — they never silently skip a deliverable.

## Layout

```
trainer/
├── SKILL.md                    workflow, hard rules, quality gate
├── assets/
│   └── intake.html             clickable 8-step intake wizard, zero dependencies
├── references/
│   ├── assessment.md           question bank, follow-up triggers, classifying training age
│   ├── programming.md          splits, volume, intensity, progression, deloads, cardio
│   ├── exercises.md            movement patterns, equipment substitution ladders, cues
│   ├── safety.md               boundaries, referral triggers, training around injury
│   └── tracker-guide.md        what each sheet does, how to read it as a coach
└── scripts/
    ├── program_schema.json     the contract
    ├── example_program.json    worked 4-day upper/lower
    ├── validate_program.py     the quality gate, stdlib only
    ├── build_plan.py           → PDF + mobile HTML
    ├── build_logger.py         → interactive HTML logger, stdlib only
    └── build_tracker.py        → 6-sheet xlsx with live formulas
```

## Try it

```bash
python3 scripts/validate_program.py scripts/example_program.json
python3 scripts/build_plan.py    scripts/example_program.json --pdf --mobile --outdir /tmp
python3 scripts/build_logger.py  scripts/example_program.json --outdir /tmp
python3 scripts/build_tracker.py scripts/example_program.json --outdir /tmp
```

## The tracker's formulas are tested

Not "written and hoped for". The workbook was filled with real sessions and
every formula evaluated with the `formulas` engine, checked against values
computed independently in Python:

- distinct session counting (date + session, not row counts)
- weekly and total volume rollups
- consistency percentage
- per-exercise best weight, best reps, best estimated 1RM (Epley)
- block week numbers derived from the start date

That testing caught a real bug: reading estimated 1RM from the Log's derived
column returned 0, because empty rows hold `""` and boolean × text is
`#VALUE!`. The PR formulas now compute from the raw numeric inputs instead.

Only pre-2007 worksheet functions are used (`SUMPRODUCT`, `SUMIFS`, `COUNTIF`,
`AVERAGEIFS`, `INDEX`, `IFERROR`). Newer ones like `MAXIFS` need an `_xlfn.`
prefix when written by a library and show up as `#NAME?` in Excel.

## Contributing

Issues and pull requests welcome. The useful ones, in rough order:

- **Programming judgement** — volume landmarks, split selection, progression
  rules. These live in `references/programming.md` and are the substance of the
  skill. Cite a guideline body (ACSM, NSCA, WHO) or say "general finding"; the
  skill refuses fabricated citations and so does the repo.
- **Equipment substitutions** — `references/exercises.md`. Home-gym and
  minimal-kit coverage is the weakest part.
- **Exercise safety** — `references/safety.md`. Referral triggers especially.
- **The intake wizard** — `assets/intake.html`. Steps are declarative at the top
  of the `<script>`; add or reorder them there rather than touching the renderer.

Run `make check` before opening a PR — it runs the validator and the
dependency-free plan build. `make zip` rebuilds the release artifact.

Keep the hard rules in `SKILL.md` intact. They exist because an agent that
invents a citation, promises a result by a date, or claims a file exists before
writing it is worse than no coach at all.

## Boundaries

This is general fitness guidance, not medical advice. The skill does not
diagnose, does not prescribe rehabilitation, refuses to program through pain,
and refers out on the red flags listed in `references/safety.md`. It will not
fabricate a citation, promise a result by a date, or claim a file exists before
it has been written.
