# PLAN.md

Progress and the next step. Read this before working; update it in the same
change that moves something forward. Mark a step done only with a check that
shows it is done.

## Done

- [x] User-folder toolchain, no administrator rights: `gh` 2.102.0, `uv` 0.13.1,
      `uvx` installed into `~/.local/bin`. Both verified by running them, not
      just `--version` — `uv venv` + package install + code execution, and
      `uvx --from cowsay` for an ephemeral tool run.
      Checksums of both downloads verified against the vendors' published
      SHA-256 values.
- [x] `hello.py` runs: prints `hello`.
- [x] Public repo created and pushed:
      <https://github.com/ApolenaPrikrylova/mlr-agent-lab>. Verified from the
      GitHub API — `visibility: PUBLIC`, one file (`hello.py`, 15 bytes), commit
      `999d7f5` matching the local commit, `main` tracking `origin/main`.
- [x] Working rules written to `AGENTS.md`; `CLAUDE.md` loads it via an
      `@AGENTS.md` import.
- [x] `AGENTS.md` expanded to the full six-rule set (2026-10-14), now seven
      sections: read-first + decisions-in-repo, try-tools-before-asking, uv for
      Python + record versions/commands, meaningful checks, do-not-weaken-tests,
      do-not-publish-secrets + ask-before-publishing, repo conventions.
      Cross-references updated after renumbering (see `RUNS.md` Run 5).
- [x] uv project initialised: `pyproject.toml`, `uv.lock`, `.venv`. Dev deps
      `ruff` 0.17.0 and `pytest` 9.1.1 added with `uv add --dev`. No global pip
      used.
- [x] `tests/test_smoke.py` — asserts `hello.py` exits 0 and prints `hello`, so
      the pytest check is not vacuous.
- [x] `.gitignore` for `.venv/`, caches, `__pycache__/`.

## Next step

**Decide what this lab is actually for.** The toolchain, repo, rules, and docs
are in place, so the scaffolding is done — but there is no experiment here yet,
only one toy script. The next change should replace that placeholder with a
first real task, and it needs a decision from you first (see Open questions).

Then, once the direction is set:

1. Replace `hello.py` with the first real experiment and record its baseline
   run in `RUNS.md`.
2. Add a `Makefile` or justfile so the check sequence is one command rather than
   three copy-pasted lines.

## Open questions

- What is the first experiment? Nothing is pinned down beyond "ML-research-ish
  agent lab", and the current contents are a placeholder.
- Should this stay a single flat script collection, or become an installable
  package (`src/` layout) now while the cost is low?
- Commit author email is `a.prikrylova@centrum.cz` on a public repo — decided,
  keep as-is, but flagging that it is visible to anyone scraping history.

## Blocked

Nothing blocked. Note: `gh` is authenticated (account `ApolenaPrikrylova`,
scopes `gist`, `read:org`, `repo`, `workflow`) but has no `user` scope, so
GitHub API calls that read your profile's email settings return HTTP 404. Run
`gh auth refresh -h github.com -s user` if that is ever needed.
