# mlr-agent-lab

A small lab for experimenting with coding agents and ML-adjacent tooling. It
starts deliberately tiny: one runnable script, one test, and a set of working
rules for agent-assisted work in [`AGENTS.md`](AGENTS.md).

## Requirements

- **uv** — installed per-user at `~/.local/bin/uv` (no administrator rights
  needed). If `uv` is not found, add `~/.local/bin` to `PATH`.
- **Python 3.12+** — `uv` manages this itself; no system Python install needed.
- **gh** (optional) — for GitHub operations, at `~/.local/bin/gh`.

## Setup

```bash
uv sync
```

This creates `.venv/` and installs the locked dependencies from `uv.lock`.

## Running things

```bash
uv run python hello.py       # the example program -> prints "hello"
```

## Checks

Run all of these before considering a change done.

```bash
uv run pytest                        # tests
uv run ruff check .                  # lint
uv run ruff format --check .         # formatting
```

## Layout

| Path | Purpose |
|---|---|
| `AGENTS.md` | Working rules for humans and agents. Read first. |
| `CLAUDE.md` | One `@AGENTS.md` import, so Claude Code loads the same rules. |
| `PLAN.md` | Progress and the next step. Read second, keep updated. |
| `RUNS.md` | Log of agent runs: model, request, how it was verified. |
| `hello.py` | Example entry point. |
| `tests/` | Tests, run with `uv run pytest`. `test_docs.py` fails if a working rule in `AGENTS.md` is dropped. |

## Note on the Python version

`pyproject.toml` declares `requires-python = ">=3.12"`. The current `.venv`
resolves to **Python 3.13.5**; `uv` picks a compatible interpreter rather than
an exact one. To pin exactly, run `uv python pin 3.12`.

## Repository

<https://github.com/ApolenaPrikrylova/mlr-agent-lab> — public.
