#!/usr/bin/env python3
"""Fail if unresolved merge conflict markers exist in tracked files."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import List

MARKER_PATTERN = re.compile(r"^(<<<<<<< .+|=======|>>>>>>> .+)$")


def tracked_files() -> List[str]:
    output = subprocess.check_output(["git", "ls-files"], text=True)
    return [line.strip() for line in output.splitlines() if line.strip()]


def is_probably_text(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:1024]
    except OSError:
        return False
    return b"\x00" not in chunk


def main() -> int:
    violations: List[str] = []
    for rel_path in tracked_files():
        path = Path(rel_path)
        if not path.exists() or not path.is_file() or not is_probably_text(path):
            continue

        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(lines, start=1):
            if MARKER_PATTERN.match(line):
                violations.append(f"{rel_path}:{line_number}: {line}")

    if violations:
        print("[FAIL] unresolved merge conflict markers detected")
        for item in violations:
            print(item)
        return 1

    print("[OK] no unresolved merge conflict markers found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
