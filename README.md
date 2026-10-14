# mlr-agent-lab

## Goal

A small sandbox for learning how to work with coding agents (Claude Code and
others): set clear working rules, make small changes, check them, and keep a
record of each run.

## How to run things

Requires [uv](https://docs.astral.sh/uv/), installed in `~/.local/bin`.

Run the program:

```sh
uv run hello.py
```

Expected output:

```
hello
```

Play Snake: open `snake/index.html` in a browser (`open snake/index.html`).
It is a reverse Snake: the snake starts 10 segments long, each bite makes it
one segment shorter, and you win when it is down to one segment. Walls and
your own body still end the game.

## Checks

Run before calling any change done:

```sh
uv run hello.py              # must print: hello
uv run pytest                # Snake rules; must end with: passed, none failed
uv run tests/check_snake.py  # must end with: All checks passed
```

`uv run pytest` runs `tests/test_snake_logic.py`, which loads only the rules
script from `snake/index.html` into a V8 engine (mini-racer), so no browser is
needed. The dev dependencies (pytest, mini-racer) are in `pyproject.toml` and
pinned in `uv.lock`.

`tests/check_snake.py` drives the whole page in headless Google Chrome (the
installed app, so no browser download). uv installs its one dependency,
Playwright, from the script header.

## Files

- `AGENTS.md`: working rules for agents (`CLAUDE.md` loads it)
- `PLAN.md`: progress and next step
- `RUNS.md`: log of each request: model, what was asked, how it was checked
- `hello.py`: prints `hello`
- `snake/index.html`: Snake game, a single self-contained HTML file
- `snake/README.md`: the game's rules and controls
- `tests/test_snake_logic.py`: pytest tests for the Snake rules
- `tests/check_snake.py`: checks for the whole Snake page in Chrome
- `pyproject.toml`, `uv.lock`: uv project with the dev dependencies
