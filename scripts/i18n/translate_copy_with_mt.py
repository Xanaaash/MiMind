#!/usr/bin/env python3
"""Generate bilingual copy drafts with configurable MT/LLM providers.

Examples:
  uv run --extra i18n python scripts/i18n/translate_copy_with_mt.py \
    --provider openai \
    --from-lang en-US \
    --to-lang zh-CN \
    --input scripts/i18n/examples/catq_en.json \
    --output /tmp/catq_zh_draft.json \
    --glossary scripts/i18n/neuro_glossary.json \
    --style-guide scripts/i18n/style_guide.txt

  uv run --extra i18n python scripts/i18n/translate_copy_with_mt.py \
    --provider google \
    --from-lang zh-CN \
    --to-lang en-US \
    --input frontend/user/public/locales/zh-CN.json \
    --output frontend/user/public/locales/en-US.json \
    --preserve-existing
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple

PLACEHOLDER_PATTERN = re.compile(r"\{\{[^{}]+\}\}")
LANG_ALIAS = {
    "en": "en",
    "en-US": "en",
    "en-GB": "en",
    "zh": "zh",
    "zh-CN": "zh-CN",
    "zh-TW": "zh-TW",
}


class Translator(Protocol):
    def translate(self, text: str, *, key_path: str) -> str:
        ...


class DeepTranslatorAdapter:
    def __init__(self, engine: Any):
        self._engine = engine

    def translate(self, text: str, *, key_path: str) -> str:
        return self._engine.translate(text)


class OpenAITranslator:
    def __init__(self, model: str, from_lang: str, to_lang: str, style_guide: str, api_key: Optional[str]):
        try:
            from openai import OpenAI
        except Exception as exc:
            raise RuntimeError(
                "openai package is required for --provider openai. Run: uv sync --extra i18n"
            ) from exc

        self._from_lang = from_lang
        self._to_lang = to_lang
        self._style_guide = style_guide.strip()
        self._client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self._model = model

    def translate(self, text: str, *, key_path: str) -> str:
        system_parts = [
            "You are a professional product localization translator.",
            "Keep tone natural, concise, and culturally fluent.",
            "Do not add explanations. Output translated text only.",
            "Keep placeholders like {{name}} unchanged.",
            "Avoid diagnostic or medicalized claims.",
            f"Source locale: {self._from_lang}",
            f"Target locale: {self._to_lang}",
        ]
        if self._style_guide:
            system_parts.append(f"Style guide:\n{self._style_guide}")

        response = self._client.chat.completions.create(
            model=self._model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "\n".join(system_parts)},
                {
                    "role": "user",
                    "content": f"Key path: {key_path}\nText:\n{text}",
                },
            ],
        )
        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise RuntimeError(f"OpenAI returned empty translation for key: {key_path}")
        return content.strip()


class LibreTranslateTranslator:
    def __init__(self, from_lang: str, to_lang: str, url: str, timeout_seconds: float):
        if not url:
            raise ValueError("--libre-url is required when provider=libretranslate")
        self._from_lang = from_lang
        self._to_lang = to_lang
        self._url = url
        self._timeout_seconds = timeout_seconds

    def translate(self, text: str, *, key_path: str) -> str:
        import httpx

        with httpx.Client(timeout=self._timeout_seconds) as client:
            response = client.post(
                self._url,
                json={
                    "q": text,
                    "source": self._from_lang,
                    "target": self._to_lang,
                    "format": "text",
                },
            )
            response.raise_for_status()
            payload = response.json()
        value = payload.get("translatedText")
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(f"LibreTranslate returned invalid result for key: {key_path}")
        return value.strip()


class DummyTranslator:
    def __init__(self, to_lang: str):
        self._to_lang = to_lang

    def translate(self, text: str, *, key_path: str) -> str:
        return f"[{self._to_lang}] {text}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Translate JSON copy with configurable translation providers")
    parser.add_argument(
        "--provider",
        choices=["openai", "google", "mymemory", "libretranslate", "dummy"],
        default="openai",
        help="Translation provider",
    )
    parser.add_argument("--from-lang", required=True, help="Source locale, e.g. en-US or zh-CN")
    parser.add_argument("--to-lang", required=True, help="Target locale, e.g. zh-CN or en-US")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument("--glossary", help="Optional glossary JSON file")
    parser.add_argument("--style-guide", help="Optional style guide text file (recommended for openai)")
    parser.add_argument("--openai-model", default="gpt-4o-mini", help="OpenAI model for provider=openai")
    parser.add_argument("--openai-api-key", help="OpenAI API key (or use OPENAI_API_KEY)")
    parser.add_argument("--libre-url", help="LibreTranslate URL, e.g. http://localhost:5000/translate")
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout in seconds")
    parser.add_argument(
        "--preserve-existing",
        action="store_true",
        help="If output file exists, keep existing non-empty strings and only translate missing values",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail fast on translation or placeholder errors (default falls back to source text)",
    )
    parser.add_argument("--indent", type=int, default=2, help="JSON indent")
    return parser.parse_args()


def canonical_lang(locale: str) -> str:
    if locale in LANG_ALIAS:
        return LANG_ALIAS[locale]
    return locale.split("-")[0]


def load_translator(args: argparse.Namespace, from_lang: str, to_lang: str) -> Translator:
    provider = args.provider
    style_guide = Path(args.style_guide).read_text(encoding="utf-8") if args.style_guide else ""
    if provider == "openai":
        return OpenAITranslator(
            model=args.openai_model,
            from_lang=args.from_lang,
            to_lang=args.to_lang,
            style_guide=style_guide,
            api_key=args.openai_api_key,
        )
    if provider == "google":
        from deep_translator import GoogleTranslator

        return DeepTranslatorAdapter(GoogleTranslator(source=from_lang, target=to_lang))
    if provider == "mymemory":
        from deep_translator import MyMemoryTranslator

        return DeepTranslatorAdapter(MyMemoryTranslator(source=from_lang, target=to_lang))
    if provider == "libretranslate":
        return LibreTranslateTranslator(
            from_lang=from_lang,
            to_lang=to_lang,
            url=str(args.libre_url or ""),
            timeout_seconds=args.timeout,
        )
    return DummyTranslator(to_lang=args.to_lang)


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


def placeholders_of(text: str) -> List[str]:
    return PLACEHOLDER_PATTERN.findall(text)


def translation_is_missing(value: Any) -> bool:
    return not isinstance(value, str) or not value.strip()


def translate_value(
    value: Any,
    translator: Translator,
    glossary: Dict[str, str],
    *,
    key_path: str,
    existing_value: Any,
    strict: bool,
) -> Any:
    if isinstance(value, str):
        if not translation_is_missing(existing_value):
            return existing_value
        protected, placeholders = protect_placeholders(value)
        try:
            translated = translator.translate(protected, key_path=key_path)
            translated = apply_glossary(translated, glossary)
            restored = restore_placeholders(translated, placeholders)
            if sorted(placeholders_of(restored)) != sorted(placeholders_of(value)):
                raise ValueError(f"placeholder mismatch at key: {key_path}")
            return restored
        except Exception as exc:
            if strict:
                raise
            print(f"[WARN] fallback to source for key {key_path}: {exc}")
            return value
    if isinstance(value, list):
        existing_items = existing_value if isinstance(existing_value, list) else []
        result: List[Any] = []
        for index, item in enumerate(value):
            existing_item = existing_items[index] if index < len(existing_items) else None
            result.append(
                translate_value(
                    item,
                    translator,
                    glossary,
                    key_path=f"{key_path}[{index}]",
                    existing_value=existing_item,
                    strict=strict,
                )
            )
        return result
    if isinstance(value, dict):
        existing_mapping = existing_value if isinstance(existing_value, dict) else {}
        output: Dict[str, Any] = {}
        for key, item in value.items():
            child_key_path = f"{key_path}.{key}" if key_path else key
            output[key] = translate_value(
                item,
                translator,
                glossary,
                key_path=child_key_path,
                existing_value=existing_mapping.get(key),
                strict=strict,
            )
        return output
    return value


def main() -> None:
    args = parse_args()
    source_lang = canonical_lang(args.from_lang)
    target_lang = canonical_lang(args.to_lang)
    locale_pair = f"{args.from_lang}->{args.to_lang}"

    translator = load_translator(args, source_lang, target_lang)
    glossary = load_glossary(Path(args.glossary), locale_pair) if args.glossary else {}

    source_data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    output_path = Path(args.output)
    existing_target: Any = None
    if args.preserve_existing and output_path.exists():
        existing_target = json.loads(output_path.read_text(encoding="utf-8"))

    translated = translate_value(
        source_data,
        translator,
        glossary,
        key_path="",
        existing_value=existing_target,
        strict=args.strict,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(translated, ensure_ascii=False, indent=args.indent) + "\n",
        encoding="utf-8",
    )
    print(f"[OK] translated -> {output_path}")


if __name__ == "__main__":
    main()
