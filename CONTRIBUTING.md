# Contributing

Fork it, change whatever you like, run it however you want — that's what the
MIT license is for. You never need permission to modify your own copy.

What you can't do is push to `main` here; that's protected. Changes reach this
repo the normal way: fork, branch, pull request, review.

## Workflow

```bash
gh repo fork EnggNashib/trainer --clone
cd trainer
git checkout -b my-change
# ... edit ...
make check
git commit -am "describe the change"
gh pr create
```

`make check` runs the validator and the two dependency-free builders. CI runs
the same thing on every PR, plus the PDF and workbook builders with their
optional dependencies installed.

## What's worth a PR

In rough order of value:

- **Programming judgement** — volume landmarks, split selection, progression and
  deload rules, in `references/programming.md`. This is the substance of the
  skill. Cite a guideline body (ACSM, NSCA, WHO) at the level of its actual
  recommendation, or write "the general finding is…". A fabricated citation is
  an automatic no, and the skill's hard rules forbid it for the same reason.
- **Equipment substitutions** — `references/exercises.md`. Home-gym and
  minimal-kit coverage is the thinnest part of the repo.
- **Safety boundaries** — `references/safety.md`, especially referral triggers.
  Err toward referring out.
- **The intake wizard** — `assets/intake.html`. Steps are declarative at the top
  of the `<script>`; add or reorder them there rather than touching the
  renderer. Keep it dependency-free.
- **The builders** — `scripts/`. Everything must render from a validated
  `program.json` so the plan, the logger and the workbook cannot disagree.

## House rules

- **No new runtime dependencies** for the validator, the mobile plan or the
  logger. Those three must work in a sandbox with no network, because that's
  what makes them reliable on claude.ai.
- **Keep the hard rules in `SKILL.md`.** An agent that invents a citation,
  promises a result by a date, or claims a file exists before writing it is
  worse than no coach at all. PRs that weaken them will be declined.
- **Excel formulas stay pre-2007.** `SUMPRODUCT`, `SUMIFS`, `COUNTIF`,
  `AVERAGEIFS`, `INDEX`, `IFERROR`. Newer functions need an `_xlfn.` prefix when
  written by a library and render as `#NAME?` in Excel.
- **Don't widen the medical scope.** No rehab protocols, no diagnosis, no
  nutrition plans. The skill works around injuries or refers out.
- Match the surrounding prose style in the markdown files: direct, specific,
  no filler.

## Reporting things

Issues are welcome, including "the coach did something daft" reports — paste the
conversation if you can. For anything that looks like a safety problem (the
skill programming through pain, or giving medical advice), say so in the title;
those get looked at first.
