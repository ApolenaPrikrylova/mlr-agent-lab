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

## Checks

Run before calling any change done:

```sh
uv run hello.py   # must print: hello
```

## Files

- `AGENTS.md`: working rules for agents (`CLAUDE.md` loads it)
- `PLAN.md`: progress and next step
- `RUNS.md`: log of each request: model, what was asked, how it was checked
- `hello.py`: prints `hello`
