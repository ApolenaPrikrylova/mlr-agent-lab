# AGENTS.md — working rules

Working rules for anyone (human or agent) working in this repository.
`CLAUDE.md` loads this file, so these rules apply in Claude Code too.

## 1. Read before you act

Read these two files **before** making any change:

1. [`README.md`](README.md) — what this project is for and how to run it
2. [`PLAN.md`](PLAN.md) — current state, what is done, and the next step

If a request conflicts with what those files say, say so instead of quietly
diverging. If you change what the project does or how it runs, update both
files in the same change.

**Keep decisions in the repository.** Decisions, their reasons, and their
trade-offs belong in `PLAN.md` (or here, when they are rules) — not only in a
chat transcript that nobody can read afterwards. Record rejected options too:
"we tried X, it failed because Y" is what stops the next person repeating it.
A decision that lives only in a conversation has effectively not been made.

## 2. Try the tools yourself before asking

Do not hand a technical step back to the human because it feels awkward.
Attempt it with the tools available first — `gh`, `uv`, `uvx`, `git`, `curl`,
the shell — and read the error. Ask only when you have actually tried and can
say what failed, or when the step genuinely needs a decision, a secret you do
not hold, or an interactive login you cannot complete.

- Check whether something already exists before declaring it impossible.
  Example: `gh` turned out to be authenticated on this machine after an initial
  check said it was not, so "I'm not logged in" was the wrong answer.
- Prefer a fix you can verify over an instruction you cannot.

**The limit on this rule:** it covers local and reversible work. It does not
license doing outward-facing or hard-to-undo things without asking — see
section 6. Automation and asking are not opposites: try silently, publish
loudly.

## 3. Python goes through uv

`uv` is the only supported way to manage Python here. It was installed per-user
into `~/.local/bin` and needs no administrator rights.

| Do | Do not |
|---|---|
| `uv run <script>` / `uv run python -c ...` | `python`, `python3`, `pip` directly |
| `uv add <pkg>` (edits `pyproject.toml` + `uv.lock`) | `pip install <pkg>` |
| `uv add --dev <pkg>` for test/lint tools | `pip install --user <pkg>` |
| `uvx <tool>` for one-off tool runs | global installs of any kind |
| `uv sync` to install the locked env | `conda` (an Anaconda install is on PATH — ignore it) |

**Never `pip install` into a global or system environment.** No `sudo pip`, no
`--break-system-packages`, no activating `source /opt/anaconda3/bin/activate`.

**Record versions and commands.** Two places, both committed:

- `pyproject.toml` + `uv.lock` — exact dependency versions, so a fresh
  `uv sync` reproduces the environment bit for bit.
- [`RUNS.md`](RUNS.md) — the commands actually run and the tool versions used,
  so a result can be reproduced from the log alone. Note the interpreter a
  command really used (`uv run python -c "import sys; print(sys.executable)"`),
  not the version you intended.

## 4. Run checks before claiming completion

Do not report work as finished on the strength of having written it. Run the
checks, read the output, and report what actually happened.

```bash
uv run python hello.py     # the project runs
uv run pytest              # tests
uv run ruff check .        # lint
uv run ruff format --check .
```

Then:

- Quote the failing command and its output if anything failed. A pass you did
  not run is not a pass.
- Make the checks *meaningful*. A test that cannot fail proves nothing; a check
  asserting nothing is worse than no check, because it reads like evidence.
- Verify behaviour at the boundary, not just the exit code. For a push, read it
  back from the remote. For a file, look at the file. For an install, run the
  binary.
- If a check could not be run (no network, no permission), say that plainly
  rather than implying the work was verified.

## 5. Do not weaken a test to make it pass

When a test disagrees with your change, the disagreement is information. Resolve
it on the merits, and say which way it went.

- **Do not** edit the assertion, delete the test, mark it skipped, widen its
  tolerance, or `xfail` it in order to get to green.
- Explain the disagreement first — in the commit message or `PLAN.md` — and let
  the human decide if the test itself is what is wrong.
- Changing a test *is* legitimate when it encodes an old contract that the
  agreed change deliberately replaces. Then the test change is part of the
  work, it gets argued for, and it lands visibly in the diff — not quietly
  alongside a fix.
- Same applies to your own verification claims: do not soften "this failed"
  into "this is mostly working".

## 6. Never publish secrets or private data; ask before publishing

Publishing is a one-way door. A secret in a public commit stays reachable in
forks, mirrors, caches, and scrapers after you delete it.

- **Never publish** credentials, tokens, keys, internal or non-public URLs,
  personal data, or patient/subject data — in commits, PR text, issue
  comments, logs, examples, or docstrings. "It is only a test token" is not an
  exception.
- **Ask before publishing anything**, including things that look routine:
  `git push`, opening or commenting on PRs and issues, `gh release`, pushing
  container images, uploading to any external service. State what will become
  public and where, then wait. Approval for one push is not approval for the
  next.
- Check the diff, not the intent, before each push. Specifically grep the tree
  for the *values* you know are secret, not for words that look sensitive —
  a real token in a README passes a keyword scan.
- Secrets live outside the repository (environment, keychain, keyring). If one
  is ever committed, say so immediately; deleting it in a later commit does not
  remove it from history.

## 7. Repo conventions

- `main` is the default branch.
- This repository is **public**, so section 6 applies to every commit in it.
- Local tooling lives in `~/.local/bin` (`gh`, `uv`, `uvx`). No `brew install`
  or `.pkg` installers; this machine has no administrator rights.
- Log substantive runs in [`RUNS.md`](RUNS.md): the model used, what was asked,
  and how it was checked.
