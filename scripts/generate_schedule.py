# -*- coding: utf-8 -*-
"""
generate_schedule.py

Rerun this ANY TIME you add new puzzles (or new solutions) to puzzle_bank.xlsx.

It reads the Excel file and writes TWO files:
  1. ../data/puzzles.js - the day-by-day schedule the LIVE GAME uses
                          (start/final words only - never includes solutions,
                          so today's and future puzzles are never exposed).
  2. ../data/hints.js   - powers the in-game hint button AND the "Yesterday's
                          solution" page. Covers the entire scheduled window
                          (past, today, and future), so solutions.html can
                          always find "yesterday" correctly on its own -
                          regardless of exactly when this script was last
                          run - by computing that date client-side and
                          looking it up here directly.

HOW TO USE:
1. Update puzzle_bank.xlsx with your new rows / solutions (see the
   "Solution" column below - optional, comma-separated words, e.g.
   "a,at,tan,rant,train,strain,retains,strainer,restraint").
2. Edit START_DATE and NUM_DAYS below if needed.
3. Run:  python3 generate_schedule.py
4. This overwrites ../data/puzzles.js and ../data/hints.js, and bumps the
   cache-busting version numbers in index.html and solutions.html.
5. Commit + push the updated files to GitHub.

Requires: pip install pandas openpyxl
"""

import pandas as pd
from datetime import date, timedelta
import json
import os
import re
import time

# ---------------- SETTINGS YOU CAN EDIT ----------------
EXCEL_PATH = os.path.join(os.path.dirname(__file__), "puzzle_bank.xlsx")
PUZZLES_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "puzzles.js")
HINTS_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "hints.js")
INDEX_HTML_PATH = os.path.join(os.path.dirname(__file__), "..", "index.html")
SOLUTIONS_HTML_PATH = os.path.join(os.path.dirname(__file__), "..", "solutions.html")

START_DATE = date(2026, 7, 27)  # <-- change this to your real launch date
NUM_DAYS = 10                    # <-- how many days of schedule to generate
# ---------------------------------------------------------

# Which tier a puzzle falls into is now based entirely on its
# Assign_Puzzle_Difficulty (APD) value, not the old "Level" text column:
#   APD < EASY_MAX               -> easy
#   EASY_MAX <= APD <= MEDIUM_MAX -> medium
#   MEDIUM_MAX < APD <= HARD_MAX  -> hard
#   APD > HARD_MAX (or blank)     -> excluded (no real difficulty assigned yet)
EASY_MAX_APD = 1.25
MEDIUM_MAX_APD = 2.8
HARD_MAX_APD = 5


def compute_tier(apd):
    """Returns 'easy', 'medium', 'hard', or None (excluded) for a given
    Assign_Puzzle_Difficulty value."""
    if apd is None:
        return None
    try:
        apd = float(apd)
    except (TypeError, ValueError):
        return None
    if apd < EASY_MAX_APD:
        return "easy"
    if apd <= MEDIUM_MAX_APD:
        return "medium"
    if apd <= HARD_MAX_APD:
        return "hard"
    return None


def parse_solution(raw):
    """Turns 'a,at,tan,rant' into ['a','at','tan','rant']. Returns None if
    the cell is blank/missing, so puzzles without a solution yet are simply
    skipped rather than breaking anything."""
    if raw is None:
        return None
    text = str(raw).strip()
    if not text or text.lower() == "nan":
        return None
    return [w.strip().lower() for w in text.split(",") if w.strip()]


def load_puzzles():
    df = pd.read_excel(EXCEL_PATH, sheet_name="Puzzle Bank")
    df.columns = df.columns.str.strip()
    df["_tier"] = df["Assign_Puzzle_Difficulty"].apply(compute_tier)
    df = df[df["_tier"].notna()]
    df = df.sort_values(by="Assign_Puzzle_Difficulty").reset_index(drop=True)

    has_solution_col = "Solution" in df.columns

    tiers = {"easy": [], "medium": [], "hard": []}
    for _, row in df.iterrows():
        solution = parse_solution(row["Solution"]) if has_solution_col else None
        if solution is None:
            # Never include a puzzle with no solution in the actual live
            # schedule - it would be genuinely unsolvable for players.
            continue
        entry = {
            "start": str(row["Starting_Word"]).strip().lower(),
            "final": str(row["Final_Word"]).strip().lower(),
            "solution": solution,
        }
        tiers[row["_tier"]].append(entry)
    return tiers


def build_schedule(tiers):
    """Returns the full day-by-day schedule (used to derive both output
    files below), with each day's puzzle entries carrying their solution
    alongside them (solutions.js will later filter this down to past days,
    and puzzles.js will strip solutions out entirely)."""
    schedule = {}
    counters = {"easy": 0, "medium": 0, "hard": 0}
    for i in range(NUM_DAYS):
        the_date = START_DATE + timedelta(days=i)
        key = the_date.isoformat()
        day_entry = {}
        for tier in ("easy", "medium", "hard"):
            pool = tiers[tier]
            if not pool:
                continue
            puzzle = pool[counters[tier] % len(pool)]
            counters[tier] += 1
            day_entry[tier] = puzzle
        schedule[key] = day_entry
    return schedule


def write_puzzles_js(schedule):
    """The live game's data file. Deliberately strips solutions out
    entirely, so nothing in here ever exposes an answer - today's or
    future's - no matter how closely someone inspects it."""
    stripped = {}
    for day_key, day_entry in schedule.items():
        stripped[day_key] = {
            tier: {"start": p["start"], "final": p["final"]}
            for tier, p in day_entry.items()
        }
    with open(PUZZLES_OUTPUT_PATH, "w") as f:
        f.write("// AUTO-GENERATED by scripts/generate_schedule.py - do not hand-edit\n")
        f.write("const PUZZLE_SCHEDULE = ")
        f.write(json.dumps(stripped, indent=2))
        f.write(";\n")
    print(f"Wrote {len(stripped)} days of puzzles to {PUZZLES_OUTPUT_PATH}")


def write_hints_js(schedule):
    """Powers the in-game hint button. Uses the SAME rolling window as
    puzzles.js (today through NUM_DAYS out) rather than a separate/larger
    window, so this never exposes more of the puzzle bank than the live
    game already does."""
    result = {}
    for day_key, day_entry in schedule.items():
        tiers_with_solutions = {
            tier: p for tier, p in day_entry.items() if p.get("solution")
        }
        if tiers_with_solutions:
            result[day_key] = tiers_with_solutions

    with open(HINTS_OUTPUT_PATH, "w") as f:
        f.write("// AUTO-GENERATED by scripts/generate_schedule.py - do not hand-edit\n")
        f.write("// Powers the in-game hint button. Same rolling window as\n")
        f.write("// puzzles.js - not a bigger exposure than the live game already has.\n")
        f.write("const HINTS_SCHEDULE = ")
        f.write(json.dumps(result, indent=2))
        f.write(";\n")
    print(f"Wrote hint data for {len(result)} day(s) to {HINTS_OUTPUT_PATH}")


def bump_cache_version_in(path, script_filename):
    """Force browsers to fetch the freshly generated file instead of a
    cached copy, by rewriting the ?v= number in the given HTML file."""
    if not os.path.exists(path):
        return
    with open(path, "r") as f:
        html = f.read()
    new_version = int(time.time())
    pattern = rf'({re.escape(script_filename)}\?v=)\d+'
    html, count = re.subn(pattern, rf'\g<1>{new_version}', html)
    if count == 0:
        print(f"NOTE: no {script_filename}?v= tag found in {path} to bump "
              f"(fine if that file doesn't reference it).")
        return
    with open(path, "w") as f:
        f.write(html)
    print(f"Bumped cache-busting version for {script_filename} in {path} to {new_version}")


def main():
    tiers = load_puzzles()
    print(f"Loaded puzzles -> easy: {len(tiers['easy'])}, "
          f"medium: {len(tiers['medium'])}, hard: {len(tiers['hard'])}")

    schedule = build_schedule(tiers)
    write_puzzles_js(schedule)
    write_hints_js(schedule)

    bump_cache_version_in(INDEX_HTML_PATH, "data/puzzles.js")
    bump_cache_version_in(INDEX_HTML_PATH, "data/hints.js")
    # solutions.html now reads from hints.js directly (which always covers
    # the full scheduled window regardless of exactly when this script was
    # last run) instead of the old, narrower solutions.js that only ever
    # contained whatever was "already past" at generation time - so this
    # is the file that actually needs bumping here now.
    bump_cache_version_in(SOLUTIONS_HTML_PATH, "data/hints.js")


if __name__ == "__main__":
    main()
