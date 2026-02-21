#!/usr/bin/env python3
"""Generate bilingual copy drafts with deep-translator + glossary post-edit.

Usage:
  uv run --extra i18n python scripts/i18n/translate_copy_with_mt.py \
    --provider google \
    --from-lang en-US \
    --to-lang zh-CN \
    --input scripts/i18n/examples/catq_en.json \
    --output /tmp/catq_zh_draft.json \
    --glossary scripts/i18n/neuro_glossary.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from deep_translator import GoogleTranslator, MyMemoryTranslator

PLACEHOLDER_PATTERN = re.compile(r"\{\{[^{}]+\}\}")
LANG_ALIAS = {
    "en": "en",
    "en-US": "en",
    "en-GB": "en",
    "zh": "zh",
    "zh-CN": "zh-CN",
    "zh-TW": "zh-TW",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Translate JSON copy with deep-translator")
    parser.add_argument(
        "--provider",
        choices=["google", "mymemory"],
        default="google",
        help="MT engine provider",
    )
    parser.add_argument("--from-lang", required=True, help="Source locale, e.g. en-US or zh-CN")
    parser.add_argument("--to-lang", required=True, help="Target locale, e.g. zh-CN or en-US")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument("--glossary", help="Optional glossary JSON file")
    parser.add_argument("--indent", type=int, default=2, help="JSON indent")
    return parser.parse_args()


def canonical_lang(locale: str) -> str:
    if locale in LANG_ALIAS:
        return LANG_ALIAS[locale]
    return locale.split("-")[0]


def load_translator(provider: str, from_lang: str, to_lang: str):
    if provider == "google":
        return GoogleTranslator(source=from_lang, target=to_lang)
    return MyMemoryTranslator(source=from_lang, target=to_lang)


def load_glossary(path: Path, locale_pair: str) -> Dict[str, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    values = data.get(locale_pair, {})
    if not isinstance(values, dict):
        return {}
    return {str(k): str(v) for k, v in values.items()}


def protect_placeholders(text: str) -> Tuple[str, List[str]]:
    placeholders: List[str] = []

    def repl(match: re.Match[str]) -> str:
        placeholders.append(match.group(0))
        return f"__PH_{len(placeholders) - 1}__"

    return PLACEHOLDER_PATTERN.sub(repl, text), placeholders


def restore_placeholders(text: str, placeholders: List[str]) -> str:
    result = text
    for idx, value in enumerate(placeholders):
        result = result.replace(f"__PH_{idx}__", value)
    return result


def apply_glossary(text: str, glossary: Dict[str, str]) -> str:
    if not glossary:
        return text
    output = text
    for source, target in sorted(glossary.items(), key=lambda item: len(item[0]), reverse=True):
        output = output.replace(source, target)
    return output


def translate_value(value: Any, translator, glossary: Dict[str, str]) -> Any:
    if isinstance(value, str):
        protected, placeholders = protect_placeholders(value)
        translated = translator.translate(protected)
        translated = apply_glossary(translated, glossary)
        return restore_placeholders(translated, placeholders)
    if isinstance(value, list):
        return [translate_value(item, translator, glossary) for item in value]
    if isinstance(value, dict):
        return {key: translate_value(item, translator, glossary) for key, item in value.items()}
    return value


def main() -> None:
    args = parse_args()
    source_lang = canonical_lang(args.from_lang)
    target_lang = canonical_lang(args.to_lang)
    locale_pair = f"{args.from_lang}->{args.to_lang}"

    translator = load_translator(args.provider, source_lang, target_lang)
    glossary = load_glossary(Path(args.glossary), locale_pair) if args.glossary else {}

    source_data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    translated = translate_value(source_data, translator, glossary)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(translated, ensure_ascii=False, indent=args.indent) + "\n",
        encoding="utf-8",
    )
    print(f"[OK] translated -> {output_path}")


if __name__ == "__main__":
    main()
