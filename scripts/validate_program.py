#!/usr/bin/env python3
"""Validate a program.json before generating deliverables.

Mechanises the quality gate in SKILL.md §7 — the checks a coach would
otherwise have to eyeball. Standard library only, so it always runs.

    python3 validate_program.py program.json

Exit codes: 0 = clean (warnings allowed) · 1 = errors found · 2 = bad usage
"""

import json
import re
import sys

ERRORS: list[str] = []
WARNINGS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


# Words in an exercise name that imply a piece of equipment.
EQUIPMENT_HINTS = {
    "barbell": ["barbell", "bench press", "back squat", "front squat", "deadlift", "rack pull", "good morning"],
    "dumbbells": ["dumbbell", "db "],
    "cables": ["cable", "pushdown", "face pull", "pulldown"],
    "machines": ["machine", "leg press", "hack squat", "pec deck", "leg curl", "leg extension", "smith"],
    "pull-up bar": ["pull-up", "pullup", "chin-up", "chinup", "hanging"],
    "bench": ["bench", "incline", "decline", "chest-supported"],
    "kettlebell": ["kettlebell", "kb "],
    "bands": ["band"],
    "trap bar": ["trap-bar", "trap bar"],
}

# Rough seconds consumed per working set, including rest, by rest length.
def session_minutes_estimate(session: dict) -> float:
    total = 0.0
    for ex in session.get("exercises", []):
        sets = ex.get("sets", 0) or 0
        rest = ex.get("rest_sec", 90) or 90
        # ~40 s under tension + rest, per set
        total += sets * (40 + rest)
    warmup = 8 * 60 if session.get("warmup") else 5 * 60
    cooldown = 4 * 60 if session.get("cooldown") else 0
    return (total + warmup + cooldown) / 60.0


def check_client(c: dict) -> None:
    for key in ("training_age", "goal_primary", "days_per_week", "session_minutes", "equipment"):
        if key not in c or c[key] in (None, "", []):
            err(f"client.{key} is missing — cannot program without it (SKILL.md §1 'must have')")
    if c.get("training_age") not in (None, "beginner", "intermediate", "advanced"):
        err(f"client.training_age '{c.get('training_age')}' must be beginner, intermediate or advanced")
    dpw = c.get("days_per_week")
    if isinstance(dpw, int) and not 1 <= dpw <= 7:
        err(f"client.days_per_week {dpw} is outside 1-7")


def check_strategy(s: dict, client: dict) -> None:
    for key in ("split", "rationale", "progression_model", "assumptions"):
        if not s.get(key):
            err(f"strategy.{key} is missing — §2 requires it before programming")
    if len(str(s.get("rationale", ""))) < 40:
        warn("strategy.rationale is very short — explain why THIS split for THIS person")
    if not s.get("deload_policy"):
        warn("strategy.deload_policy is empty — say when you would deload")
    # Every limitation should be visible somewhere in the reasoning.
    blob = json.dumps(s).lower()
    for lim in client.get("limitations", []) or []:
        key = re.sub(r"[^a-z ]", "", str(lim).lower())
        token = next((w for w in key.split() if len(w) > 4), None)
        if token and token not in blob:
            warn(f"limitation '{lim}' is not mentioned in strategy — say how you programmed around it")


def check_sessions(sessions: list, client: dict) -> None:
    dpw = client.get("days_per_week")
    if isinstance(dpw, int) and len(sessions) > dpw:
        err(f"{len(sessions)} sessions programmed but client only has {dpw} days available")

    equipment = {e.lower() for e in (client.get("equipment") or [])}
    bodyweight_only = (client.get("environment", "") or "").lower().startswith("bodyweight")
    seen_names: set[str] = set()

    for i, s in enumerate(sessions):
        label = f"sessions[{i}] ({s.get('name', 'unnamed')})"
        for key in ("day", "name", "exercises"):
            if not s.get(key):
                err(f"{label}: missing '{key}'")
        if not s.get("warmup"):
            warn(f"{label}: no warmup — §7 requires warm-up guidance")

        exercises = s.get("exercises") or []
        if not exercises:
            err(f"{label}: has no exercises")

        for j, ex in enumerate(exercises):
            name = ex.get("name", f"exercise[{j}]")
            tag = f"{label} → {name}"
            for key in ("sets", "reps", "rest_sec", "rir"):
                if ex.get(key) in (None, "", 0):
                    err(f"{tag}: missing '{key}' — every exercise needs sets, reps, rest and RIR/RPE")

            rest = ex.get("rest_sec")
            if isinstance(rest, int) and not 15 <= rest <= 600:
                err(f"{tag}: rest_sec {rest} is outside 15-600")

            sets = ex.get("sets")
            if isinstance(sets, int) and sets > 8:
                warn(f"{tag}: {sets} sets is high for one exercise — check weekly volume")

            rir = str(ex.get("rir", ""))
            for n in re.findall(r"\d+", rir):
                if int(n) > 6:
                    warn(f"{tag}: RIR {rir} is very easy — is that intended?")

            if not ex.get("alternative"):
                warn(f"{tag}: no alternative given — §exercises recommends one per exercise")

            # Equipment reachability
            low = name.lower()
            for kit, hints in EQUIPMENT_HINTS.items():
                if any(h in low for h in hints):
                    if bodyweight_only and kit not in ("pull-up bar", "bands"):
                        err(f"{tag}: needs '{kit}' but environment is bodyweight only")
                    elif equipment and kit not in equipment and not any(kit in e for e in equipment):
                        warn(f"{tag}: appears to need '{kit}', not in client.equipment {sorted(equipment)}")
                    break

            seen_names.add(low)

        est = session_minutes_estimate(s)
        budget = client.get("session_minutes")
        if isinstance(budget, int) and est > budget * 1.15:
            err(f"{label}: ~{est:.0f} min of work but client has {budget} min — cut exercises or sets")
        elif isinstance(budget, int) and est > budget:
            warn(f"{label}: ~{est:.0f} min estimated vs {budget} min budget — tight")

    # Pattern coverage across the week
    patterns = {str(e.get("pattern", "")).lower() for s in sessions for e in (s.get("exercises") or [])}
    for needed, label in (("hinge", "hinge"), ("squat", "squat"), ("vertical pull", "vertical pull")):
        if needed not in patterns:
            warn(f"no '{label}' pattern anywhere in the week — commonly skipped, check it's deliberate")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as fh:
            prog = json.load(fh)
    except FileNotFoundError:
        print(f"error: no such file: {argv[1]}")
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: {argv[1]} is not valid JSON — {exc}")
        return 1

    for key in ("client", "strategy", "block", "sessions"):
        if key not in prog:
            err(f"top-level '{key}' is missing")
    if ERRORS:
        report()
        return 1

    check_client(prog["client"])
    check_strategy(prog["strategy"], prog["client"])
    check_sessions(prog["sessions"], prog["client"])

    if not prog.get("benchmarks"):
        warn("no benchmarks — §7 asks for something testable every 4-6 weeks")
    if not prog.get("recovery"):
        warn("no recovery section — §7 requires recovery to be addressed")

    report()
    return 1 if ERRORS else 0


def report() -> None:
    for w in WARNINGS:
        print(f"  WARN  {w}")
    for e in ERRORS:
        print(f" ERROR  {e}")
    if not ERRORS and not WARNINGS:
        print("OK — program passes every check.")
    else:
        print(f"\n{len(ERRORS)} error(s), {len(WARNINGS)} warning(s).")
        if ERRORS:
            print("Fix the errors before generating deliverables.")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
