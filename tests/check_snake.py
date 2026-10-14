# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright"]
# ///
"""Check snake/index.html in headless Chrome.

Run with:  uv run tests/check_snake.py [screenshot.png]

Uses the Google Chrome already installed on this Mac, so no browser download
is needed. Exits non-zero if any check fails.
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PAGE = (Path(__file__).resolve().parent.parent / "snake" / "index.html").as_uri()

# Each case runs in the page against the pure Snake rules and returns true/false.
RULE_CASES = {
    "starts with 10 segments, ready, food off the snake": """() => {
        const g = Snake.createGame();
        return Snake.START_LENGTH === 10 && g.snake.length === 10 && g.status === 'ready' &&
            g.food && !g.snake.some(c => c.x === g.food.x && c.y === g.food.y);
    }""",
    "moves one cell per step without changing length": """() => {
        const g = Snake.createGame(); g.status = 'running'; g.food = {x: 0, y: 0};
        const x = g.snake[0].x; Snake.step(g);
        return g.snake[0].x === x + 1 && g.snake.length === 10;
    }""",
    "ignores a turn straight back into the body": """() => {
        const g = Snake.createGame();
        return Snake.turn(g, 'left') === false && Snake.turn(g, 'up') === true;
    }""",
    "two quick turns in one tick both apply": """() => {
        const g = Snake.createGame(); g.status = 'running'; g.food = {x: 0, y: 0};
        Snake.turn(g, 'up'); Snake.turn(g, 'left');
        Snake.step(g); const a = g.dir; Snake.step(g);
        return a === 'up' && g.dir === 'left';
    }""",
    "eating makes the snake one segment shorter and scores": """() => {
        const g = Snake.createGame(); g.status = 'running';
        const h = g.snake[0]; g.food = {x: h.x + 1, y: h.y};
        Snake.step(g);
        return g.score === 1 && g.snake.length === 9 && g.status === 'running' &&
            g.snake[0].x === h.x + 1 && g.food !== null &&
            !g.snake.some(c => c.x === g.food.x && c.y === g.food.y);
    }""",
    "food never appears on the snake (500 random placements)": """() => {
        let seed = 1;
        const rng = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
        for (let t = 0; t < 500; t++) {
            const g = Snake.createGame({cols: 6, rows: 6, rng});
            // Random self-avoiding walk to get varied snake shapes.
            const snake = [{x: Math.floor(rng() * 6), y: Math.floor(rng() * 6)}];
            for (let k = 0; k < 30; k++) {
                const h = snake[0];
                const opts = Object.values(Snake.DIRS).map(d => ({x: h.x + d.x, y: h.y + d.y}))
                    .filter(c => c.x >= 0 && c.y >= 0 && c.x < 6 && c.y < 6 &&
                                 !snake.some(s => s.x === c.x && s.y === c.y));
                if (!opts.length) break;
                snake.unshift(opts[Math.floor(rng() * opts.length)]);
            }
            g.snake = snake;
            const f = Snake.placeFood(g);
            if (f === null || snake.some(s => s.x === f.x && s.y === f.y)) return false;
        }
        return true;
    }""",
    "food stays off the snake during a long automatic game": """() => {
        let seed = 7;
        const rng = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
        const g = Snake.createGame({rng, length: 10}); g.status = 'running';
        // Steer greedily towards the food, avoiding walls and the body when possible.
        for (let i = 0; i < 2000 && g.status === 'running'; i++) {
            const h = g.snake[0], body = g.snake.slice(0, -1);
            const safe = Object.entries(Snake.DIRS).filter(([name, d]) => {
                const c = {x: h.x + d.x, y: h.y + d.y};
                return name !== Snake.OPPOSITE[g.dir] && c.x >= 0 && c.y >= 0 &&
                    c.x < g.cols && c.y < g.rows && !body.some(s => s.x === c.x && s.y === c.y);
            });
            if (safe.length) {
                safe.sort(([, a], [, b]) =>
                    Math.abs(h.x + a.x - g.food.x) + Math.abs(h.y + a.y - g.food.y) -
                    Math.abs(h.x + b.x - g.food.x) - Math.abs(h.y + b.y - g.food.y));
                Snake.turn(g, safe[0][0]);
            }
            const len = g.snake.length, score = g.score;
            Snake.step(g);
            if (g.snake.length > len) return false;
            if (g.score > score && g.snake.length !== len - 1) return false;
            if (g.food && g.snake.some(s => s.x === g.food.x && s.y === g.food.y)) return false;
        }
        return g.status === 'won' && g.snake.length === 1 && g.score === 9;
    }""",
    "hitting a wall ends the game": """() => {
        const g = Snake.createGame({cols: 5, rows: 5}); g.status = 'running'; g.food = {x: 0, y: 4};
        for (let i = 0; i < 10 && g.status === 'running'; i++) Snake.step(g);
        return g.status === 'over' && g.snake[0].x === 4;
    }""",
    "running into itself ends the game": """() => {
        // Head at (5,5) heading right; (6,5) is part of the body, not the tail.
        const g = Snake.createGame(); g.status = 'running'; g.food = {x: 0, y: 0};
        g.snake = [{x:5,y:5},{x:4,y:5},{x:4,y:4},{x:5,y:4},{x:6,y:4},{x:6,y:5},{x:6,y:6}];
        g.dir = 'right'; Snake.step(g);
        return g.status === 'over' && g.snake.length === 7;
    }""",
    "may move into the cell the tail is leaving": """() => {
        const g = Snake.createGame(); g.status = 'running'; g.food = {x: 0, y: 0};
        g.snake = [{x:5,y:5},{x:6,y:5},{x:6,y:6},{x:5,y:6}]; g.dir = 'left';
        Snake.turn(g, 'down'); Snake.step(g);
        return g.status === 'running' && g.snake[0].x === 5 && g.snake[0].y === 6;
    }""",
    "shrinking to one segment wins": """() => {
        const g = Snake.createGame({length: 2}); g.status = 'running';
        const h = g.snake[0]; g.food = {x: h.x + 1, y: h.y};
        Snake.step(g);
        return g.status === 'won' && g.snake.length === 1 && g.food === null &&
            g.snake[0].x === h.x + 1;
    }""",
    "length 2 without food does not win": """() => {
        const g = Snake.createGame({length: 2}); g.status = 'running'; g.food = {x: 0, y: 0};
        Snake.step(g);
        return g.status === 'running' && g.snake.length === 2;
    }""",
    "speeds up with score, never below 60 ms": """() => {
        const g = Snake.createGame(); const t0 = Snake.tickMs(g);
        g.score = 10; const t10 = Snake.tickMs(g); g.score = 999;
        return t0 === 140 && t10 === 110 && Snake.tickMs(g) === 60;
    }""",
}


def main() -> int:
    screenshot = sys.argv[1] if len(sys.argv) > 1 else None
    failures = []

    def check(name: str, ok: bool) -> None:
        print(("PASS " if ok else "FAIL ") + name)
        if not ok:
            failures.append(name)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 600, "height": 800})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: m.type == "error" and errors.append(m.text))
        # Random food could land in the snake's scripted path and add surprise
        # bites. With Math.random fixed at 0 the food always goes to the first
        # free cell, the top-left corner, which the scripted moves never reach.
        page.add_init_script("Math.random = () => 0;")
        page.goto(PAGE)

        for name, js in RULE_CASES.items():
            check(name, page.evaluate(js) is True)

        # Drive the real page with key presses.
        state = "() => ({status: snakeApp.game.status, head: snakeApp.game.snake[0], dir: snakeApp.game.dir})"
        check("page shows the start overlay", page.is_visible("#overlay"))
        start = page.evaluate(state)
        page.keyboard.press("ArrowUp")
        page.wait_for_timeout(400)
        moved = page.evaluate(state)
        check("arrow key starts the game and the snake moves up",
              moved["status"] == "running" and moved["dir"] == "up"
              and moved["head"]["y"] < start["head"]["y"])
        check("overlay hides while running", not page.is_visible("#overlay"))
        if screenshot:
            page.screenshot(path=screenshot)
        page.keyboard.press("Space")
        paused = page.evaluate(state)
        page.wait_for_timeout(400)
        check("Space pauses and the snake stops",
              paused["status"] == "paused" and page.evaluate(state)["head"] == paused["head"]
              and page.is_visible("#overlay"))
        page.keyboard.press("Space")
        page.wait_for_timeout(2500)
        over = page.evaluate(state)
        check("running into the top wall ends the game",
              over["status"] == "over" and page.inner_text("#overlay-title") == "Game over")
        page.keyboard.press("Space")
        check("Space after game over starts a new game at length 10",
              page.evaluate("() => snakeApp.game.status === 'running' && snakeApp.game.score === 0"
                            " && snakeApp.game.snake.length === 10")
              and page.inner_text("#length") == "10")

        # Put food right in front of the head and check the page shows the bite.
        page.keyboard.press("Space")
        page.evaluate("""() => { const g = snakeApp.game, h = g.snake[0], d = Snake.DIRS[g.dir];
                                 g.food = {x: h.x + d.x, y: h.y + d.y}; }""")
        page.keyboard.press("Space")
        page.wait_for_timeout(400)
        check("eating on the page shows length 9 and score 1",
              page.inner_text("#length") == "9" and page.inner_text("#score") == "1")

        # Shrink to length 2 with food ahead, then the next bite wins.
        page.keyboard.press("Space")
        page.evaluate("""() => { const g = snakeApp.game, d = Snake.DIRS[g.dir];
                                 g.snake = g.snake.slice(0, 2);
                                 g.food = {x: g.snake[0].x + d.x, y: g.snake[0].y + d.y}; }""")
        page.keyboard.press("Space")
        page.wait_for_timeout(400)
        check("last bite shows the win screen at length 1",
              page.evaluate("() => snakeApp.game.status") == "won"
              and page.is_visible("#overlay")
              and page.inner_text("#overlay-title") == "You won!"
              and page.inner_text("#length") == "1")
        if screenshot:
            page.screenshot(path=screenshot.replace(".png", "-won.png"))

        # High-score table: the win above (score 2) is recorded and survives a reload.
        rows = "() => [...document.querySelectorAll('#scores-body tr')].map(r => [...r.cells].map(c => c.textContent))"
        table = page.evaluate(rows)
        check("the win is added to the high-score table and highlighted",
              len(table) == 1 and table[0][:3] == ["1", "2", "Won"]
              and page.evaluate("() => document.querySelector('#scores-body tr').className") == "new"
              and "New high score: #1!" in page.inner_text("#overlay-text"))
        page.reload()
        check("the high-score table survives a reload",
              page.evaluate(rows) == table and page.inner_text("#best") == "2"
              and not page.is_visible("#scores-empty"))
        if screenshot:
            page.screenshot(path=screenshot.replace(".png", "-scores.png"), full_page=True)

        # A game over with no bites is not recorded.
        page.keyboard.press("ArrowUp")
        page.wait_for_function("() => snakeApp.game.status === 'over'", timeout=5000)
        check("a game with no bites is not added", len(page.evaluate(rows)) == 1)

        page.evaluate("() => localStorage.setItem('snake-high-scores', '{not json')")
        page.reload()
        check("corrupted saved scores show an empty table instead of breaking",
              page.evaluate(rows) == [] and page.is_visible("#scores-empty"))

        page.evaluate("() => localStorage.setItem('snake-high-scores', JSON.stringify("
                      "[{score: 9, length: 1, timeMs: 61000, date: Date.now()}]))")
        page.reload()
        page.once("dialog", lambda d: d.accept())
        page.click("#clear-scores")
        page.reload()
        check("Clear empties the table, also after a reload",
              page.evaluate(rows) == [] and page.inner_text("#best") == "0")

        # With storage blocked, the page still works and says scores won't be kept.
        blocked = browser.new_page()
        blocked.on("pageerror", lambda e: errors.append(str(e)))
        blocked.add_init_script("""
            for (const m of ['getItem', 'setItem', 'removeItem'])
                Storage.prototype[m] = () => { throw new Error('blocked'); };
        """)
        blocked.goto(PAGE)
        blocked.keyboard.press("Space")
        blocked.evaluate("""() => { const g = snakeApp.game; g.snake = g.snake.slice(0, 2);
                                    g.food = {x: g.snake[0].x + 1, y: g.snake[0].y}; }""")
        blocked.wait_for_function("() => snakeApp.game.status === 'won'", timeout=5000)
        check("with storage blocked, scores still show for this visit and a note explains",
              len(blocked.evaluate(rows)) == 1 and blocked.is_visible("#storage-note"))
        blocked.close()

        check("no JavaScript errors", not errors)
        for e in errors:
            print("   ", e)
        browser.close()

    print(f"\n{len(failures)} failed" if failures else "\nAll checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
