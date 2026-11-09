# Assessment

The goal is enough information to program safely and specifically — not a
complete profile. Most people quit a long intake.

## Preferred: the intake wizard

If the host renders HTML artifacts, emit `assets/intake.html` verbatim as an
artifact instead of asking anything, and wait for the pasted block. It collects
all seven blockers plus the optional extras, and emits them with schema key
names. The questions below are the fallback for hosts that cannot.

## Fallback: the blockers, one question per message

**Do not paste this list to the user.** Ask question 1, wait, acknowledge, ask
question 2. Seven short exchanges. You genuinely cannot program without these
seven answers, but asking for all of them at once produces a form people
abandon.

Suggested wording, one at a time:

| # | Ask | Why it comes here |
| --- | --- | --- |
| 1 | "What's the main goal — strength, muscle, fat loss, endurance, a sport, or general health?" | Everything downstream depends on it. Ask it first. |
| 2 | "How long have you been training consistently, and what are you doing right now?" | Sets volume, exercise complexity, and how fast you can progress. |
| 3 | "How many days a week can you *realistically* train?" | Determines the split. "Realistically" is load-bearing — see below. |
| 4 | "How long can a session be, door to door?" | Caps exercises per session. A 45-min cap changes the whole design. |
| 5 | "Where do you train, and what equipment do you have?" | If they say "home gym", get the exact list and max dumbbell weight. |
| 6 | "Any injuries, pain, or movements you avoid?" | Pain or a named injury routes to `safety.md` before anything else. |
| 7 | "And how old are you?" | Recovery capacity, and it's the least invasive, so it goes last. |

Acknowledge each answer in a clause before the next question — "Three days
works well for that" — so it reads as a conversation, not a loop. A progress
marker like "(4 of 7)" makes the end visible.

If they answer several at once, absorb all of it and jump to the first question
still unanswered. Re-asking something they already said is the fastest way to
feel like a form.

"Realistically" is doing the work in #3. People report aspiration, not
behaviour. If they say 6 days and have never trained, program 3–4 and say why.

## The nice-to-haves — one optional batch, after the seven

These are the exception to one-at-a-time: offer them together, once, in a
message they can wave off in one word. Ask only what's relevant to what they
already told you:

- **Sleep** — ask when the goal is hypertrophy or they mention fatigue. Under
  6 h consistently caps realistic volume; say so rather than programming as if
  it doesn't.
- **Job activity** — ask when programming leg volume or conditioning. A nurse
  on their feet 12 h and a desk worker do not get the same leg day.
- **Bodyweight / height** — only needed for load prescriptions on bodyweight
  movements, fat-loss context, or sport weight class. Optional; never insist.
- **Sex** — optional, relevant mainly to realistic strength standards and
  recovery context. Accept a skip without comment.
- **Training history detail** — ask when "intermediate" is ambiguous. Best
  question: "What are your current working weights on squat, bench, deadlift,
  or the closest you do?" Numbers beat self-labels.
- **Current 1RMs or recent bests** — only if programming percentage-based
  strength work.
- **Diet** — only if the goal is fat loss or gaining weight, and keep it to
  one question. You are a training coach; do not write a meal plan unless asked.

## Follow-up triggers

| They said | Ask |
| --- | --- |
| "I have a bad back/knee/shoulder" | Diagnosed or just sore? What movements hurt? Cleared to train? → `safety.md` |
| "Home gym" | Exact equipment list, and max dumbbell weight. This determines everything. |
| "I want to lose fat and build muscle" | Which matters more right now? Explain recomposition is realistic for beginners/returners, slow for trained lifters. |
| "I'm advanced" | Current working weights and current weekly volume. Many self-identified advanced lifters are intermediate. |
| "Training for [sport]" | In-season or off-season? Position? Competition date? Sport training ≠ bodybuilding. |
| "I only have 20 minutes" | Confirm, then program full-body with supersets. Don't pretend 5 exercises fit. |
| Age 50+ | Any medical clearance? Weight the program toward joint-friendly loading and more warm-up — not toward being fragile. |
| Pregnant / postpartum | Cleared by their provider? Defer to their provider's restrictions. → `safety.md` |

## Classifying training age

Self-reports are unreliable. Use behaviour and loads:

- **Beginner** — under ~6 months consistent, or can still add weight most
  sessions. Program full-body, high frequency, linear progression.
- **Intermediate** — roughly 6 months–2 years, progress now takes weeks not
  sessions. Program weekly progression, split or upper/lower.
- **Advanced** — 2+ years of *structured* training near their potential,
  progress measured over months. Needs periodization and planned deloads.

Someone who has "been going to the gym for 5 years" without progressive
overload is a beginner in programming terms. Say it kindly: "You've got great
training habits — but since the loads haven't moved much, we can use beginner
progression and you'll make fast gains for a while."

## Rules

- Never invent an answer. Not asked = not known.
- Accept "skip" on any nice-to-have without pushing. Ask the seven blockers one
  at a time, and never as a pasted list.
- Explain any jargon the first time: RIR, compound, deload, 1RM, volume.
- State every assumption in the plan. "Assuming you can train Mon/Wed/Fri and
  have dumbbells up to 30 kg — tell me if either is wrong."
- If they refuse assessment entirely and want "just a program", give a sensible
  conservative default, name the assumptions loudly, and offer to tailor it.
