#!/usr/bin/env python3
"""Fail on common i18n anti-patterns in frontend source code."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List

TRANSLATION_COMPARE_PATTERN = re.compile(r"t\([^)\n]*\)\s*(?:===|!==|==|!=)\s*(['\"]).*?\1")
LANG_TERNARY_PATTERN = re.compile(
    r"i18n\.language\s*(?:===|!==|==|!=)\s*(['\"]).*?\1\s*\?\s*(['\"])(.*?)\2\s*:\s*(['\"])(.*?)\4"
)
LOCALE_LITERAL_PATTERN = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")
TOKEN_LITERAL_PATTERN = re.compile(r"^[a-z0-9_-]+$")
SHORT_CODE_PATTERN = re.compile(r"^[A-Z]{1,3}$")
HAS_CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect i18n anti-patterns in source files")
    parser.add_argument("--root", default="frontend/user/src", help="Frontend source root")
    return parser.parse_args()


def is_text_literal(value: str) -> bool:
    text = value.strip()
    if not text:
        return False
    if LOCALE_LITERAL_PATTERN.fullmatch(text):
        return False
    if TOKEN_LITERAL_PATTERN.fullmatch(text):
        return False
    if SHORT_CODE_PATTERN.fullmatch(text):
        return False
    if text.isdigit():
        return False
    if HAS_CJK_PATTERN.search(text):
        return True
    return bool(re.search(r"\s|[/:.,!?]", text))


def iter_source_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".ts", ".tsx", ".js", ".jsx"}:
            continue
        if "__tests__" in path.parts:
            continue
        files.append(path)
    return files


def check_file(path: Path) -> List[str]:
    errors: List[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(lines, start=1):
        if "i18n-check-ignore" in line:
            continue

        if TRANSLATION_COMPARE_PATTERN.search(line):
            errors.append(
                f"{path}:{line_number} avoid comparing translated text literals; use translation keys directly"
            )

        lang_match = LANG_TERNARY_PATTERN.search(line)
        if lang_match:
            left = lang_match.group(3)
            right = lang_match.group(5)
            if is_text_literal(left) or is_text_literal(right):
                errors.append(
                    f"{path}:{line_number} avoid language-branch literals; move text to locale JSON"
                )
    return errors


def main() -> int:
    args = parse_args()
    root = Path(args.root)
    if not root.exists():
        print(f"[FAIL] source root not found: {root}")
        return 1

    all_errors: List[str] = []
    for file in iter_source_files(root):
        all_errors.extend(check_file(file))

    if all_errors:
        print("[FAIL] i18n anti-patterns detected")
        for error in all_errors:
            print(error)
        return 1

    print("[OK] no blocked i18n anti-patterns found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
