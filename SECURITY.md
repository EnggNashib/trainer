# Security

This skill is markdown plus four standard-library Python scripts. It makes no
network requests, needs no credentials, and stores nothing server-side.

Two things are still worth reporting:

- **Code execution.** The scripts read `program.json` and write HTML, PDF and
  xlsx. If you find a path where crafted input escapes that — writing outside
  `--outdir`, or injecting executable content into a generated file — report it.
- **HTML injection.** `assets/intake.html` and the generated logger escape
  user-supplied text before rendering it. A bypass that lands live markup in a
  page is a real bug.

Email **engg.nashib@gmail.com** rather than opening a public issue, and give it
a few days before disclosing.

Not security issues: the logger keeping entries in `localStorage` (documented,
and why `Save rows` exists), or the skill running Python at all — that's the
whole point of it.
