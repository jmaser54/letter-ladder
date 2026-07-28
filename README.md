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
2. (Optional) Fill in a `Solution` column for any puzzle - a comma-separated
   chain of words showing one valid path, e.g.
   `a,at,tan,rant,train,strain,retains,strainer,restraint`. This powers the
   "Past solutions" page (see below). Leave it blank if you don't have one
   yet - it's entirely optional per puzzle.
3. Open `scripts/generate_schedule.py` and adjust `START_DATE` / `NUM_DAYS` if you want.
4. Run it locally: `python3 generate_schedule.py` (needs `pip install pandas openpyxl`)
5. This rewrites `data/puzzles.js` AND `data/solutions.js`, and automatically
   bumps the cache-busting version numbers in `index.html` and
   `solutions.html` - nothing to do by hand.
6. On GitHub, upload the updated files to replace the old ones - GitHub will ask "these files already exist, replace them?" - say yes, then commit.
7. Your live site updates automatically within a minute or two.

## Past solutions page

`solutions.html` shows one worked solution for each **past** day's puzzles
(never today's or future ones - those are deliberately left out of the
generated file entirely, so there's nothing to find even by inspecting the
page's source). It only shows a day/tier once you've filled in a `Solution`
for it in the spreadsheet, and only once that day has actually passed.

## Keeping your puzzle bank private

`NUM_DAYS` in `generate_schedule.py` controls how many days of puzzles get
published into `data/puzzles.js` at once (currently 10). Since that file is
publicly visible to anyone who looks, keeping this number modest means only
a small window of upcoming puzzles is ever exposed at a time, rather than
your whole bank sitting out in the open. Just re-run the generator every so
often to roll the window forward as time passes.

## A note on "hiding" the puzzle answers

Because this is a fully static site (no server), the word list and today's
puzzle answers technically live in files anyone *could* open and inspect via
their browser's developer tools. Casual players never will — this is exactly
how Wordle, Connections, and most browser word games work too. If you'd
rather have puzzle answers live on a real server that visitors truly cannot
inspect, that's a different (and more involved) setup — worth revisiting if
this becomes a bigger project down the line.
