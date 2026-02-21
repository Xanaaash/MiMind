#!/usr/bin/env python3
"""Check consistency between two locale JSON files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

PLACEHOLDER_PATTERN = re.compile(r"\{\{[^{}]+\}\}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate locale key/value consistency")
    parser.add_argument("--source", required=True, help="Source locale JSON")
    parser.add_argument("--target", required=True, help="Target locale JSON")
    parser.add_argument(
        "--check-placeholders",
        action="store_true",
        help="Validate placeholder sets are identical for aligned keys",
    )
    return parser.parse_args()


def flatten_mapping(value: Any, prefix: str = "") -> Dict[str, Any]:
    if not isinstance(value, dict):
        return {prefix: value}

    output: Dict[str, Any] = {}
    for key, child in value.items():
        next_prefix = f"{prefix}.{key}" if prefix else key
        output.update(flatten_mapping(child, next_prefix))
    return output


def placeholders_of(text: str) -> List[str]:
    return sorted(PLACEHOLDER_PATTERN.findall(text))


def main() -> int:
    args = parse_args()
    source = json.loads(Path(args.source).read_text(encoding="utf-8"))
    target = json.loads(Path(args.target).read_text(encoding="utf-8"))

    source_flat = flatten_mapping(source)
    target_flat = flatten_mapping(target)
    source_keys = set(source_flat.keys())
    target_keys = set(target_flat.keys())

    missing_in_target = sorted(source_keys - target_keys)
    extra_in_target = sorted(target_keys - source_keys)

    issues: List[str] = []

    if missing_in_target:
        issues.append(f"missing keys in target: {len(missing_in_target)}")
        issues.extend([f"  - {key}" for key in missing_in_target[:50]])
    if extra_in_target:
        issues.append(f"extra keys in target: {len(extra_in_target)}")
        issues.extend([f"  - {key}" for key in extra_in_target[:50]])

    for key in sorted(source_keys & target_keys):
        source_value = source_flat[key]
        target_value = target_flat[key]
        if isinstance(source_value, str) and not source_value.strip():
            issues.append(f"empty source value: {key}")
        if isinstance(target_value, str) and not target_value.strip():
            issues.append(f"empty target value: {key}")
        if args.check_placeholders and isinstance(source_value, str) and isinstance(target_value, str):
            if placeholders_of(source_value) != placeholders_of(target_value):
                issues.append(f"placeholder mismatch: {key}")

    if issues:
        print("[FAIL] locale consistency check failed")
        for item in issues:
            print(item)
        return 1

    print("[OK] locale files are consistent")
    print(f"aligned keys: {len(source_keys)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
