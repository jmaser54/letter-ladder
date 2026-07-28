# Letter Ladder

A daily word-ladder puzzle game — three puzzles a day (Easy / Medium / Hard).
Everything runs entirely in the visitor's browser (no server needed), which
means it's free to host and can handle any amount of traffic.

## Folder guide

```
index.html          the game itself
about.html           how-to-play / about page
data/words.js        the dictionary used to validate guesses
data/puzzles.js       the day-by-day puzzle schedule (auto-generated, see below)
scripts/generate_schedule.py   run this locally whenever you add new puzzles
scripts/puzzle_bank.xlsx        your puzzle spreadsheet
```

## Putting this on GitHub (one-time setup)

1. Go to https://github.com and create a free account if you don't have one.
2. Click the **+** in the top right → **New repository**.
3. Name it something like `letter-ladder` (this becomes part of your game's URL). Set it to **Public**. Don't check any of the boxes to add a README/gitignore — leave it empty. Click **Create repository**.
4. On the next page, click **uploading an existing file** (a blue link in the instructions).
5. Drag in every file and folder from this project (`index.html`, `about.html`, the `data` folder, the `scripts` folder). Commit the changes.
6. Go to your repo's **Settings** tab → **Pages** (left sidebar).
7. Under "Build and deployment", set **Source** to `Deploy from a branch`, Branch to `main` and folder to `/ (root)`. Click **Save**.
8. Wait a minute or two, then refresh that Pages settings screen — it'll show you a live URL like:
   `https://yourusername.github.io/letter-ladder/`

That URL is what you share with people to play the game. Anyone visiting it plays instantly — nothing to install.

## Adding more puzzles later

1. Open `scripts/puzzle_bank.xlsx` and add new rows the same way you have been (same columns: `Starting_Word`, `Final_Word`, `Level`, etc.)
2. Open `scripts/generate_schedule.py` and adjust `START_DATE` / `NUM_DAYS` if you want.
3. Run it locally: `python3 generate_schedule.py` (needs `pip install pandas openpyxl`)
4. This rewrites `data/puzzles.js`.
5. On GitHub, upload the new `data/puzzles.js` (and updated `puzzle_bank.xlsx`) to replace the old ones — GitHub will ask "these files already exist, replace them?" — say yes, then commit.
6. Your live site updates automatically within a minute or two.

## A note on "hiding" the puzzle answers

Because this is a fully static site (no server), the word list and today's
puzzle answers technically live in files anyone *could* open and inspect via
their browser's developer tools. Casual players never will — this is exactly
how Wordle, Connections, and most browser word games work too. If you'd
rather have puzzle answers live on a real server that visitors truly cannot
inspect, that's a different (and more involved) setup — worth revisiting if
this becomes a bigger project down the line.
