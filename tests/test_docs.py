"""Checks that the working rules are actually present, not just mentioned.

These fail loudly when a rule is dropped or a required file is removed, which
is the failure mode that a lint-only check would miss.
"""

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
CLAUDE = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")

# Each rule -> a pattern that must appear in AGENTS.md.
REQUIRED_RULES = {
    "read README.md and PLAN.md first": r"read these two files.*before",
    "keep decisions in the repository": r"keep decisions in the repository",
    "try tools before asking": r"try the tools yourself before asking",
    "uv for python": r"python goes through uv",
    "no global pip install": r"never `pip install` into a global",
    "record versions and commands": r"record versions and commands",
    "run checks before claiming completion": r"run checks before claiming",
    "checks must be meaningful": r"make the checks.*meaningful",
    "do not weaken a test": r"do not weaken a test to make it pass",
    "explain the disagreement first": r"explain the disagreement first",
    "never publish secrets": r"never publish secrets or private data",
    "ask before publishing": r"ask before publishing anything",
}


def test_all_required_rules_present_in_agents_md():
    missing = [
        name
        for name, pattern in REQUIRED_RULES.items()
        if not re.search(pattern, AGENTS, re.IGNORECASE | re.DOTALL)
    ]
    assert not missing, f"AGENTS.md is missing rules: {missing}"


def test_claude_md_loads_agents_md():
    assert CLAUDE.strip() == "@AGENTS.md", (
        "CLAUDE.md must be exactly the @AGENTS.md import so both tools share "
        "one source of rules"
    )


def test_agents_md_has_no_secret_values():
    # Keyword scans miss real tokens, so match value shapes instead.
    offenders = re.findall(r"sk-[A-Za-z0-9]{20,}|gh[po]_[A-Za-z0-9]{20,}", AGENTS)
    assert not offenders, "AGENTS.md appears to contain credential-like values"


def test_dev_dependencies_are_pinned_in_lock():
    data = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    locked = {p["name"]: p["version"] for p in data.get("package", [])}
    for pkg in ("ruff", "pytest"):
        assert pkg in locked, f"{pkg} missing from uv.lock"
        assert re.fullmatch(r"\d+\.\d+\.\d+.*", locked[pkg])
