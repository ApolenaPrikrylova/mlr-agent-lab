# Working rules

These rules apply to any coding agent working in this repository.

1. **Read first; keep decisions in the repository.** Before starting, read
   `README.md` (goal, how to run things) and `PLAN.md` (progress, next step).
   Write decisions down in `PLAN.md`, not only in the chat.
2. **Try the tools before asking.** Use the available tools (shell, `gh`, `uv`,
   …) to do a technical step yourself before asking the user to do it by hand.
   Prefer installing tools into ~/.local/bin or with uv. Ask me before using sudo, Homebrew or a .pkg installer.
3. **Use uv for Python.**
   - Run scripts with `uv run …` (for example `uv run hello.py`).
   - Add packages with `uv add <package>`.
   - No global `pip install`.
   - Record tool versions and the commands you ran in `RUNS.md`.
4. **Run meaningful checks before claiming completion.** Run the checks listed
   in `README.md`, plus whatever actually exercises the change, and report the
   real output. If a check fails or was skipped, say so.
5. **Do not weaken a test to make it pass.** If you think a test is wrong,
   explain the disagreement first and let the user decide.
6. **Never publish secrets or private data; ask before publishing anything.**
   That includes `git push`, creating releases, gists or issues, and sharing
   artifacts. Show what will be published and wait for a yes.
7. **Keep the docs current.** Update `PLAN.md` when progress or the next step
   changes, and add an entry to `RUNS.md` for each request.
