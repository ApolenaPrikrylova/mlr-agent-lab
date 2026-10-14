# RUNS.md

Log of agent runs: which model, what was asked, how the result was checked.
Newest last.

## Model identification

| Field | Value |
|---|---|
| Claude Code CLI | 2.1.299 |
| Model as configured | `agentic` (`ANTHROPIC_MODEL` in `~/.claude/settings.json`) |
| Opus / Sonnet / Haiku aliases | `thinker` / `agentic` / `mini` |
| Upstream | a proxy, not api.anthropic.com |

**Caveat, stated plainly:** the model name above was read out of
`~/.claude/settings.json`, not off the `/status` panel — an agent cannot read
that panel. It is an *alias*, so the real underlying model is unknown and not
recoverable from the local config. `/status` may show a resolved name that
differs from what is recorded here. Ask for `/status` output if you need the
resolved value logged exactly.

---

## Run 1 — 2026-10-14

**Model:** `agentic` (alias; see caveat above)
**Asked:** Write a Python program that prints hello, and run it.
**Result:** `hello.py`, one line, `print("hello")`.
**Checked by:** running `python3 hello.py` — stdout was `hello`.

## Run 2 — 2026-10-14

**Model:** `agentic`
**Asked:** Install GitHub CLI (`gh`) and `uv` into the user folder without
administrator rights, and check that both work.
**Result:** `gh` 2.102.0, `uv` + `uvx` 0.13.1 into `~/.local/bin`. No `sudo`, no
Homebrew, no profile edits (`~/.local/bin` was already on `PATH`).
**Checked by:**
- SHA-256 of both downloads verified against the vendors' published checksums —
  both reported `OK`.
- `shasum` on the gh archive initially failed with "No such file or directory"
  because I had saved it under a shortened filename; renamed and re-verified.
  That was my error, not a bad download.
- Both binaries run: `gh --version`, `uv --version`, `uvx --version`.
- Functional, not just version banners: `uv venv --python 3.12` + install +
  execute printed `uv import OK, python 3.12.0`; `uvx --from cowsay cowsay`
  rendered.
- `which gh uv uvx` in a fresh `zsh -l` all resolve to `~/.local/bin`, and the
  `PATH` line was confirmed present in `~/.zshrc:17` (so the earlier `zsh -l`
  check, which inherits my session PATH, was not on its own sufficient proof).
- No quarantine xattr on either binary, so Gatekeeper will not block them.
**Not fully clean:** `gh auth status` reported "not logged into any GitHub
hosts" — correct for a fresh install, but it meant `gh` was not usable until you
ran the interactive login yourself. Several Bash calls failed with an
agentic-classifier timeout during this run and were retried.

## Run 3 — 2026-10-14

**Model:** `agentic`
**Asked:** Use `gh` to create a public repo `mlr-agent-lab` from this folder,
showing what would be uploaded before pushing.
**Result:** <https://github.com/ApolenaPrikrylova/mlr-agent-lab> created public;
`main` pushed; commit `999d7f5` "Initial commit".
**Checked by:**
- Preview generated from staged state (`git ls-files`, `git ls-tree`), not from
  a hand-written file list: one file, `hello.py`, 15 bytes.
- Confirmed no parent repo and no name collision before starting; confirmed no
  remote configured at preview time, so nothing could have leaked early.
- Verified global `~/.gitignore_global` (`*~`, `.DS_Store`) and
  `git status --ignored` so nothing was silently dropped.
- After push, verified from the **GitHub API** rather than local git:
  `visibility: PUBLIC`, `isPrivate: false`, `contents` lists exactly `hello.py`
  at 15 bytes, commit sha and author match local, `git status -sb` clean with
  tracking set.
**Decision surfaced, not assumed:** your `a.prikrylova@centrum.cz` becomes
publicly visible in history. Asked before committing; you chose to keep it.

## Run 4 — 2026-10-14

**Model:** `agentic`
**Asked:** Write `AGENTS.md` with working rules (read README/PLAN first, use uv,
run checks before claiming done); make `CLAUDE.md` load it; create `README.md`,
`PLAN.md`, `RUNS.md`.
**Result:** all five files, plus `pyproject.toml`, `uv.lock`, `.gitignore`,
`tests/test_smoke.py`.
**Checked by:**
- `uv run python hello.py` → `hello`, rc=0.
- `uv run pytest` → 1 passed (the test asserts stdout equals `hello`, so it is
  not a trivially-passing test).
- `uv run ruff check .` → All checks passed. `--show-files` confirms it visits
  only `hello.py`, `tests/test_smoke.py`, `pyproject.toml` — `.venv` is excluded
  via `.gitignore`.
- `uv run ruff format --check .` → "7 files already formatted". That count
  initially looked wrong (only 2 `.py` files exist), so I traced it: ruff 0.17
  also formats Python blocks inside Markdown. Verified with a probe file
  containing badly-formatted code in a ```python fence, which ruff flagged for
  reformatting. 2 `.py` + 5 `.md` = 7. Correct, and it means the code samples in
  these docs are themselves linted.
- `CLAUDE.md` contains exactly `@AGENTS.md` (the import form Claude Code
  expands).
- Secret scan before commit: grepped the working tree for the *actual* token and
  proxy-host values read out of `~/.claude/settings.json`, and both came back
  absent. A broader pattern grep hit one line — this file's own sentence naming
  `ANTHROPIC_AUTH_TOKEN` — which is a variable *name* in prose, not a value.
**Deliberate omission:** the proxy URL and `ANTHROPIC_AUTH_TOKEN` from
`~/.claude/settings.json` are **not** reproduced in this file. This repo is
public; the "Never publish secrets or private data" rule in `AGENTS.md` forbids
internal URLs and credentials here. *(Cited as "rule 4" when this entry was
written; the rules were renumbered in Run 5.)*

## Run 5 — 2026-10-14

**Model:** `agentic`
**Asked:** Add any missing rules from a proposed set of six (read README/PLAN
first + keep decisions in the repo; try tools before asking me to do a technical
step by hand; uv for Python + record versions and commands; run meaningful
checks; do not weaken tests, explain the disagreement first; never publish
secrets, ask before publishing).
**Result:** `AGENTS.md` now 7 sections. Gap analysis against the six:

| Proposed rule | Before this run | Action |
|---|---|---|
| Read README/PLAN first | present | kept |
| Keep decisions in the repository | **absent** | new subsection, §1 |
| Try tools before asking by hand | **absent** | new §2 |
| uv run / uv add / no global pip | present | kept |
| Record versions and commands | partly (lock only) | added RUNS.md + real-interpreter check, §3 |
| Run meaningful checks | present as "run checks" | added "meaningful" clause, §4 |
| Do not weaken a test; explain first | one clause buried in old §3 | promoted to §5, incl. the legitimate-test-change case |
| Never publish secrets | present, repo-scoped | generalized to all publishing, §6 |
| Ask before publishing anything | **absent** | new in §6 |

Three were genuinely missing, three were partial. Renumbering made the old
"rule 4" citation in Run 4 stale; fixed there rather than leaving a dangling
reference.

**Checked by:**
- `tests/test_docs.py` (new): asserts each rule is present by pattern, that
  `CLAUDE.md` is exactly `@AGENTS.md`, that no credential-shaped value sits in
  `AGENTS.md`, and that `ruff`/`pytest` are pinned in `uv.lock`. 5 passed.
- **Negative controls**, because rule 4 now says a test that cannot fail proves
  nothing. Each ran against a deliberately broken copy, then was restored:
  - `CLAUDE.md` replaced with prose → `test_claude_md_loads_agents_md` FAILED.
  - "ask before publishing" sentence deleted from `AGENTS.md` →
    `AssertionError: AGENTS.md is missing rules: ['ask before publishing']` —
    it names the exact rule instead of failing vaguely.
  - After restoring both: 5 passed, `CLAUDE.md` back to `@AGENTS.md`,
    `grep -c` confirms rule text present, 7 sections intact.
- `uv run ruff check .` → All checks passed.
  `uv run ruff format --check .` → 8 files already formatted (was 7; +1 new test).
- A zero-byte `.Rhistory` appeared mid-run. Not created by me — R/RStudio writes
  it when touching the cwd. Verified empty, added it plus `.RData` and
  `.Rapp.history` to `.gitignore` so it cannot be committed.
- Temp files (`/tmp/AGENTS.bak`, `/tmp/CLAUDE.md.bak`, `/tmp/probe.md`)
  confirmed removed.
**Note:** §2 (try the tools yourself) and §6 (ask before publishing) are in
tension by design, and §2 states the limit explicitly: automating local,
reversible work is not licence to publish outward-facing things unprompted.
