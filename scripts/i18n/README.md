# i18n Workflow (Quality-First)

Use an LLM-first workflow for natural copy, with open-source fallback and automated consistency checks.

## 1) Install i18n extras

```bash
uv sync --extra i18n
```

## 2) Validate current locale consistency (before/after translation)

```bash
uv run --extra i18n python scripts/i18n/check_locale_consistency.py \
  --source frontend/user/public/locales/zh-CN.json \
  --target frontend/user/public/locales/en-US.json \
  --check-placeholders
```

## 3) Generate draft with OpenAI (preferred, natural tone)

```bash
uv run --extra i18n python scripts/i18n/translate_copy_with_mt.py \
  --provider openai \
  --openai-model gpt-4o-mini \
  --from-lang en-US \
  --to-lang zh-CN \
  --input scripts/i18n/examples/catq_en.json \
  --output /tmp/catq_zh_draft.json \
  --glossary scripts/i18n/neuro_glossary.json \
  --style-guide scripts/i18n/style_guide.txt \
  --strict
```

## 4) Open-source fallback options

Google/MyMemory via `deep-translator`:

```bash
uv run --extra i18n python scripts/i18n/translate_copy_with_mt.py \
  --provider google \
  --from-lang en-US \
  --to-lang zh-CN \
  --input scripts/i18n/examples/catq_en.json \
  --output /tmp/catq_zh_draft.json \
  --glossary scripts/i18n/neuro_glossary.json
```

LibreTranslate API:

```bash
uv run --extra i18n python scripts/i18n/translate_copy_with_mt.py \
  --provider libretranslate \
  --libre-url http://localhost:5000/translate \
  --from-lang en-US \
  --to-lang zh-CN \
  --input scripts/i18n/examples/catq_en.json \
  --output /tmp/catq_zh_draft.json
```

## 5) Update an existing locale file without overwriting reviewed strings

```bash
uv run --extra i18n python scripts/i18n/translate_copy_with_mt.py \
  --provider openai \
  --from-lang zh-CN \
  --to-lang en-US \
  --input frontend/user/public/locales/zh-CN.json \
  --output frontend/user/public/locales/en-US.json \
  --style-guide scripts/i18n/style_guide.txt \
  --preserve-existing
```

## 6) Human post-edit in UI context

- Keep product boundary terms stable: `特质探索 / trait exploration`, `非临床诊断 / not a clinical diagnosis`.
- Avoid medicalized wording.
- Check tone consistency in both locales inside real UI screens.
