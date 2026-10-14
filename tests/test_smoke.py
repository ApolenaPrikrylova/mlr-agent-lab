"""Smoke test: the project's entry point runs and prints."""

import subprocess
import sys
from pathlib import Path

HELLO = Path(__file__).resolve().parent.parent / "hello.py"


def test_hello_prints_greeting():
    result = subprocess.run(
        [sys.executable, str(HELLO)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "hello"
