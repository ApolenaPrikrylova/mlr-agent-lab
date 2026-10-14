"""Tests for the Snake game rules in snake/index.html.

Run with:  uv run pytest

Only the rules script (<script id="snake-logic">) is loaded, into a bare V8
engine via mini-racer, so there is no browser, page or drawing involved.
"""

import json
import re
from pathlib import Path

import pytest
from py_mini_racer import MiniRacer

PAGE = Path(__file__).resolve().parent.parent / "snake" / "index.html"


def load_logic_source() -> str:
    html = PAGE.read_text(encoding="utf-8")
    match = re.search(r'<script id="snake-logic">(.*?)</script>', html, re.S)
    assert match, 'snake/index.html has no <script id="snake-logic">'
    return match.group(1)


@pytest.fixture(scope="module")
def js():
    """Return a function that runs a JS function body and gives back its result.

    The body can use `Snake` (the rules), `running(opts)` (a new game that is
    already running, with the food parked out of the way), `seeded(n)` (a
    repeatable random number generator) and `state(g)` (a plain copy of a
    game). Results travel back as JSON.
    """
    ctx = MiniRacer()
    ctx.eval(load_logic_source())
    ctx.eval("""
        function seeded(seed) {
            return () => (seed = (seed * 16807) % 2147483647) / 2147483647;
        }
        function running(opts) {
            const g = Snake.createGame(opts);
            g.status = 'running';
            g.food = {x: 0, y: 0};
            return g;
        }
        function state(g) {
            return {snake: g.snake, dir: g.dir, queue: g.queue, food: g.food,
                    score: g.score, status: g.status};
        }
    """)

    def run(body: str):
        return json.loads(ctx.eval(f"JSON.stringify((() => {{ {body} }})())"))

    return run


def on_snake(cell, snake) -> bool:
    return any(c == cell for c in snake)


# --- Starting position ------------------------------------------------------

def test_new_game_starts_ready_with_10_segments_facing_right(js):
    g = js("return state(Snake.createGame());")
    assert js("return Snake.START_LENGTH;") == 10
    assert g["status"] == "ready"
    assert g["score"] == 0
    assert g["dir"] == "right"
    assert g["snake"] == [{"x": 10 - i, "y": 10} for i in range(10)]


def test_new_game_food_is_on_the_board_and_off_the_snake(js):
    for seed in range(1, 51):
        g = js(f"return state(Snake.createGame({{rng: seeded({seed})}}));")
        food = g["food"]
        assert 0 <= food["x"] < 20 and 0 <= food["y"] < 20
        assert not on_snake(food, g["snake"])


def test_start_length_is_trimmed_to_fit_a_small_board(js):
    g = js("return state(Snake.createGame({cols: 5, rows: 5}));")
    assert g["snake"] == [{"x": 2, "y": 2}, {"x": 1, "y": 2}, {"x": 0, "y": 2}]


def test_nothing_moves_until_the_game_is_running(js):
    for status in ["ready", "paused", "over", "won"]:
        before = js("return state(Snake.createGame({rng: seeded(1)}));")
        after = js(f"""
            const g = Snake.createGame({{rng: seeded(1)}});
            g.status = '{status}';
            Snake.step(g);
            return state(g);
        """)
        assert after["snake"] == before["snake"], status
        assert after["status"] == status


# --- Moving and turning -----------------------------------------------------

def test_each_step_moves_one_cell_without_changing_length(js):
    g = js("const g = running(); Snake.step(g); Snake.step(g); return state(g);")
    assert g["snake"][0] == {"x": 12, "y": 10}
    assert len(g["snake"]) == 10
    assert g["status"] == "running"


def test_turning_straight_back_or_the_same_way_is_ignored(js):
    assert js("return Snake.turn(running(), 'left');") is False
    assert js("return Snake.turn(running(), 'right');") is False
    assert js("return Snake.turn(running(), 'sideways');") is False
    assert js("return Snake.turn(running(), 'up');") is True


def test_two_quick_turns_apply_on_consecutive_steps(js):
    dirs = js("""
        const g = running();
        Snake.turn(g, 'up'); Snake.turn(g, 'left');
        Snake.step(g); const first = g.dir;
        Snake.step(g);
        return [first, g.dir, g.snake[0]];
    """)
    assert dirs == ["up", "left", {"x": 9, "y": 9}]


def test_a_quick_double_turn_cannot_reverse_into_the_neck(js):
    # 'up' is queued, so 'down' would reverse it and must be refused.
    assert js("const g = running(); Snake.turn(g, 'up'); return Snake.turn(g, 'down');") is False


def test_at_most_three_turns_are_queued(js):
    results = js("""
        const g = running();
        return ['up', 'left', 'down', 'right'].map(d => Snake.turn(g, d));
    """)
    assert results == [True, True, True, False]


# --- Eating makes the snake shorter ----------------------------------------

def test_eating_makes_the_snake_one_segment_shorter_and_scores(js):
    g = js("""
        const g = running({rng: seeded(3)});
        g.food = {x: 11, y: 10};
        Snake.step(g);
        return state(g);
    """)
    assert len(g["snake"]) == 9
    assert g["score"] == 1
    assert g["snake"][0] == {"x": 11, "y": 10}
    assert g["snake"][-1] == {"x": 3, "y": 10}
    assert g["status"] == "running"


def test_new_food_after_a_bite_is_off_the_snake(js):
    for seed in range(1, 51):
        g = js(f"""
            const g = running({{rng: seeded({seed})}});
            g.food = {{x: 11, y: 10}};
            Snake.step(g);
            return state(g);
        """)
        assert g["food"] is not None
        assert not on_snake(g["food"], g["snake"])


def test_moving_without_eating_never_changes_length_or_score(js):
    g = js("""
        const g = running();
        Snake.turn(g, 'down'); Snake.step(g);
        Snake.turn(g, 'left'); Snake.step(g); Snake.step(g);
        return state(g);
    """)
    assert len(g["snake"]) == 10
    assert g["score"] == 0


# --- Winning ----------------------------------------------------------------

def test_shrinking_to_one_segment_wins(js):
    g = js("""
        const g = running({length: 2});
        g.food = {x: 11, y: 10};
        Snake.step(g);
        return state(g);
    """)
    assert g["status"] == "won"
    assert g["snake"] == [{"x": 11, "y": 10}]
    assert g["food"] is None


def test_length_two_without_food_keeps_playing(js):
    g = js("const g = running({length: 2}); Snake.step(g); return state(g);")
    assert g["status"] == "running"
    assert len(g["snake"]) == 2


def test_after_winning_the_snake_stays_put(js):
    g = js("""
        const g = running({length: 2});
        g.food = {x: 11, y: 10};
        Snake.step(g); Snake.step(g);
        return state(g);
    """)
    assert g["status"] == "won"
    assert g["snake"] == [{"x": 11, "y": 10}]


def test_full_game_from_10_wins_after_9_bites(js):
    g = js("""
        const g = running({rng: seeded(11)});
        g.food = Snake.placeFood(g);
        // Steer greedily towards the food, avoiding walls and the body.
        for (let i = 0; i < 2000 && g.status === 'running'; i++) {
            const h = g.snake[0], body = g.snake.slice(0, -1);
            const safe = Object.entries(Snake.DIRS).filter(([name, d]) => {
                const c = {x: h.x + d.x, y: h.y + d.y};
                return name !== Snake.OPPOSITE[g.dir] && c.x >= 0 && c.y >= 0 &&
                    c.x < g.cols && c.y < g.rows &&
                    !body.some(s => s.x === c.x && s.y === c.y);
            });
            safe.sort(([, a], [, b]) =>
                Math.abs(h.x + a.x - g.food.x) + Math.abs(h.y + a.y - g.food.y) -
                Math.abs(h.x + b.x - g.food.x) - Math.abs(h.y + b.y - g.food.y));
            if (safe.length) Snake.turn(g, safe[0][0]);
            const len = g.snake.length, score = g.score;
            Snake.step(g);
            if (g.snake.length > len) throw new Error('snake grew');
            if (g.score > score && g.snake.length !== len - 1) throw new Error('bite did not shrink');
            if (g.score === score && g.snake.length !== len) throw new Error('length changed without a bite');
            if (g.food && g.snake.some(s => s.x === g.food.x && s.y === g.food.y))
                throw new Error('food on the snake');
        }
        return state(g);
    """)
    assert g["status"] == "won"
    assert g["score"] == 9
    assert len(g["snake"]) == 1


# --- Losing -----------------------------------------------------------------

@pytest.mark.parametrize(
    "direction, head",
    [("up", (2, 0)), ("down", (2, 4)), ("left", (0, 2)), ("right", (4, 2))],
)
def test_hitting_any_wall_loses(js, direction, head):
    g = js(f"""
        const g = running({{cols: 5, rows: 5, length: 2}});
        g.snake = [{{x: {head[0]}, y: {head[1]}}}, {{x: 2, y: 2}}];
        g.dir = '{direction}';
        Snake.step(g);
        return state(g);
    """)
    assert g["status"] == "over"
    assert g["snake"][0] == {"x": head[0], "y": head[1]}


def test_running_into_your_own_body_loses(js):
    # Head at (5,5) heading right into (6,5), which is body, not the tail.
    g = js("""
        const g = running();
        g.snake = [{x:5,y:5},{x:4,y:5},{x:4,y:4},{x:5,y:4},{x:6,y:4},{x:6,y:5},{x:6,y:6}];
        g.dir = 'right';
        Snake.step(g);
        return state(g);
    """)
    assert g["status"] == "over"
    assert len(g["snake"]) == 7


def test_moving_into_the_cell_the_tail_is_leaving_is_allowed(js):
    g = js("""
        const g = running();
        g.snake = [{x:5,y:5},{x:6,y:5},{x:6,y:6},{x:5,y:6}];
        g.dir = 'left';
        Snake.turn(g, 'down');
        Snake.step(g);
        return state(g);
    """)
    assert g["status"] == "running"
    assert g["snake"][0] == {"x": 5, "y": 6}


# --- Food placement ---------------------------------------------------------

def test_food_never_lands_on_the_snake_in_500_random_shapes(js):
    bad = js("""
        const rng = seeded(1);
        const bad = [];
        for (let t = 0; t < 500; t++) {
            const g = Snake.createGame({cols: 6, rows: 6, rng});
            const snake = [{x: Math.floor(rng() * 6), y: Math.floor(rng() * 6)}];
            for (let k = 0; k < 30; k++) {
                const h = snake[0];
                const next = Object.values(Snake.DIRS)
                    .map(d => ({x: h.x + d.x, y: h.y + d.y}))
                    .filter(c => c.x >= 0 && c.y >= 0 && c.x < 6 && c.y < 6 &&
                                 !snake.some(s => s.x === c.x && s.y === c.y));
                if (!next.length) break;
                snake.unshift(next[Math.floor(rng() * next.length)]);
            }
            g.snake = snake;
            const f = Snake.placeFood(g);
            if (f === null || snake.some(s => s.x === f.x && s.y === f.y)) bad.push({snake, f});
        }
        return bad;
    """)
    assert bad == []


def test_food_can_land_on_every_free_cell(js):
    # With a 3x1 board and the snake on the middle cell, the lowest and highest
    # random numbers must pick the two free end cells.
    cells = js("""
        const g = Snake.createGame({cols: 3, rows: 1, length: 2});
        g.snake = [{x: 1, y: 0}];
        return [0, 0.9999].map(r => { g.rng = () => r; return Snake.placeFood(g); });
    """)
    assert cells == [{"x": 0, "y": 0}, {"x": 2, "y": 0}]


def test_no_food_when_the_board_is_full(js):
    assert js("""
        const g = Snake.createGame({cols: 2, rows: 1, length: 2});
        return Snake.placeFood(g);
    """) is None


# --- Speed ------------------------------------------------------------------

@pytest.mark.parametrize("score, ms", [(0, 140), (1, 137), (9, 113), (26, 62), (27, 60), (999, 60)])
def test_speed_rises_with_score_down_to_60_ms(js, score, ms):
    assert js(f"const g = Snake.createGame(); g.score = {score}; return Snake.tickMs(g);") == ms


# --- High scores ------------------------------------------------------------

def entry(score, time_ms=10_000, date=1, length=None):
    return {"score": score, "length": 10 - score if length is None else length,
            "timeMs": time_ms, "date": date}


def add(js, table, new, limit=None):
    extra = f", {limit}" if limit is not None else ""
    return js(f"return Snake.addHighScore({json.dumps(table)}, {json.dumps(new)}{extra});")


def test_first_game_with_a_bite_goes_in_at_rank_1(js):
    result = add(js, [], entry(3))
    assert result == {"table": [entry(3)], "rank": 1}


def test_game_with_no_bites_is_not_recorded(js):
    result = add(js, [entry(2)], entry(0))
    assert result == {"table": [entry(2)], "rank": None}


def test_higher_score_ranks_first(js):
    result = add(js, [entry(5), entry(2)], entry(4))
    assert [e["score"] for e in result["table"]] == [5, 4, 2]
    assert result["rank"] == 2


def test_equal_scores_rank_by_faster_time(js):
    table = [entry(9, time_ms=40_000), entry(9, time_ms=60_000)]
    result = add(js, table, entry(9, time_ms=50_000))
    assert [e["timeMs"] for e in result["table"]] == [40_000, 50_000, 60_000]
    assert result["rank"] == 2


def test_equal_score_and_time_keeps_the_earlier_game_first(js):
    result = add(js, [entry(4, date=100)], entry(4, date=200))
    assert [e["date"] for e in result["table"]] == [100, 200]
    assert result["rank"] == 2


def test_table_keeps_only_the_top_10(js):
    assert js("return Snake.HIGH_SCORE_LIMIT;") == 10
    full = [entry(9, time_ms=1000 * (i + 1)) for i in range(10)]

    worse = add(js, full, entry(1))
    assert worse == {"table": full, "rank": None}

    better = add(js, full, entry(9, time_ms=500))
    assert len(better["table"]) == 10
    assert better["rank"] == 1
    assert better["table"][0]["timeMs"] == 500
    assert {"score": 9, "length": 1, "timeMs": 10_000, "date": 1} not in better["table"]


def test_adding_does_not_change_the_old_table(js):
    unchanged = js("""
        const table = [{score: 2, length: 8, timeMs: 5, date: 1}];
        const copy = JSON.stringify(table);
        Snake.addHighScore(table, {score: 7, length: 3, timeMs: 5, date: 2});
        return JSON.stringify(table) === copy;
    """)
    assert unchanged is True


@pytest.mark.parametrize("saved", [None, "", "not json", "{}", "42", '"text"', "[1, 2, null]"])
def test_unreadable_saved_scores_give_an_empty_table(js, saved):
    assert js(f"return Snake.parseHighScores({json.dumps(saved)});") == []


def test_malformed_entries_are_dropped_and_extra_fields_removed(js):
    good = entry(3, date=5)
    saved = [
        {**good, "name": "<script>", "extra": True},
        {"score": 0, "length": 10, "timeMs": 1, "date": 1},     # no bites
        {"score": 2.5, "length": 7, "timeMs": 1, "date": 1},    # not a whole number
        {"score": -1, "length": 7, "timeMs": 1, "date": 1},
        {"score": 4, "length": 0, "timeMs": 1, "date": 1},      # impossible length
        {"score": 4, "length": 6, "timeMs": -5, "date": 1},     # negative time
        {"score": 4, "length": 6, "timeMs": 1},                 # missing date
        {"score": "4", "length": 6, "timeMs": 1, "date": 1},    # text, not a number
    ]
    assert js(f"return Snake.parseHighScores({json.dumps(json.dumps(saved))});") == [good]


def test_saved_scores_are_sorted_and_capped_at_10(js):
    saved = [entry(i % 9 + 1, time_ms=i) for i in range(25)]
    table = js(f"return Snake.parseHighScores({json.dumps(json.dumps(saved))});")
    assert len(table) == 10
    assert table == sorted(table, key=lambda e: (-e["score"], e["timeMs"], e["date"]))
    assert table[0]["score"] == 9


def test_saved_table_reads_back_unchanged(js):
    table = add(js, [entry(9, time_ms=30_000), entry(5)], entry(7))["table"]
    assert js(f"return Snake.parseHighScores({json.dumps(json.dumps(table))});") == table
