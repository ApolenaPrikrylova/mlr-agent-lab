# Reverse Snake

A browser Snake game in one HTML file, with a twist: eating makes the snake
**shorter**. Open `index.html` in any browser to play; it needs no server or
internet connection.

## Rules

- The board is 20 × 20 cells. The snake starts **10 segments** long in the
  middle of the board, heading right.
- The snake moves one cell at a time. It speeds up with each bite: a move
  takes 140 ms at first, 3 ms less per bite, and never less than 60 ms.
- **Each time the snake eats, it gets one segment shorter** and you score a
  point.
- **You win when the snake is down to one segment**, after 9 bites.
- **You lose if the head hits a wall or the snake's own body.** Moving into
  the cell the tail is just leaving is allowed.
- Food never appears on the snake. After each bite, new food appears on a
  random free cell.
- The snake cannot turn straight back on itself; that key press is ignored.
  Quick key presses are queued (up to three), so a fast double turn works.

## Controls

| Action | Keyboard | Touch screen |
| --- | --- | --- |
| Steer | Arrow keys or W A S D | Swipe on the board, or the arrow buttons |
| Start | Any arrow key, Space or Enter | Tap the board |
| Pause / resume | Space, P or Esc (Esc only pauses) | Tap the board to resume |
| Play again | Space or Enter | Tap the board |

The game pauses by itself when you switch to another tab.

## High scores

- The table under the board keeps the **top 10 games**. It is saved in the
  browser (`localStorage`), so it survives a reload or closing the browser.
- Games are ranked by **score** (bites); equal scores rank by **faster time**,
  then by whoever got there first. Every win scores 9, so wins are ranked by
  time. Time counts only actual play, not pauses.
- A game with no bites is not recorded. A new entry is highlighted and the
  end screen shows its rank.
- **Clear** (with a confirmation) deletes the table.
- Scores are per browser and per computer, and are not shared or uploaded.
  If the browser blocks saved data (for example some private windows), the
  table still works until the page is closed and a note says so.

## Changing the rules

The rules are in `<script id="snake-logic">` near the bottom of
`index.html`, as plain functions (`createGame`, `turn`, `step`, `placeFood`,
`tickMs`, and `addHighScore`, `parseHighScores`, `compareScores` for the
table) with no drawing code. The start length is `START_LENGTH`; the table
size is `HIGH_SCORE_LIMIT`.

## Tests

From the repository root:

```sh
uv run pytest                # rules only: loads the snake-logic script into V8 (mini-racer)
uv run tests/check_snake.py  # the whole page in headless Google Chrome
```
