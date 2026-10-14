# Plan

## Progress

- [x] Install `gh` and `uv` into `~/.local/bin` without admin rights
- [x] Clear the old files from the GitHub repo and start fresh
- [x] `hello.py` prints `hello`
- [x] Working rules (`AGENTS.md`, loaded by `CLAUDE.md`), `README.md`,
      `PLAN.md` and `RUNS.md`
- [x] Full rule set in `AGENTS.md`
- [x] `.gitignore` for Python/uv on macOS
- [x] Snake game in `snake/index.html`, with checks in `tests/check_snake.py`
- [x] Reverse-Snake rule: eating shrinks the snake, length 1 wins
- [x] `snake/README.md` with the rules; pytest tests for the rules
- [x] High-score table that survives a reload

## Decisions

- Python is run and managed with uv only; tools live in `~/.local/bin`.
- Nothing is pushed or published without asking first.
- Snake is one HTML file with no libraries. The rules are pure functions
  (`Snake.createGame`, `turn`, `step`) kept apart from drawing and input, so
  they can be tested directly. Walls are deadly; the board is 20×20.
- Rule (chosen by the user instead of the five suggestions): each bite makes
  the snake one segment shorter; length 1 wins; walls and self still lose; food
  never appears on the snake. Start length is 10 (`START_LENGTH`) so a game
  takes 9 bites; at the old length of 3 it would be won in 2.
- Browser checks use Playwright through uv with the installed Google Chrome,
  because Node is not installed.
- Rule tests use pytest plus mini-racer (V8 in Python) and load only
  `<script id="snake-logic">`, so they test the real game code without a
  browser. The repo is now a uv project (`uv init --bare`, then
  `uv add --dev pytest mini-racer`).
- High scores: top 10 in `localStorage` (key `snake-high-scores`), ranked by
  score, then faster play time, then earlier date; games with no bites are not
  recorded; no player names (single local player). Ranking and parsing are
  pure functions in the rules script, so pytest covers them. The old
  `snake-best` value is no longer used; "Best" now comes from the table.

## Next step

Play the reverse Snake and decide whether the start length (10) feels right,
then commit and push the game (after showing what will be uploaded).
