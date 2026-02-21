# i18n Workflow (Neuro Copy)

Use open-source `deep-translator` for draft generation, then do human review in-context.

## 1) Install i18n extras

```bash
uv sync --extra i18n
```

## 2) Generate draft

```bash
uv run --extra i18n python scripts/i18n/translate_copy_with_mt.py \
  --provider google \
  --from-lang en-US \
  --to-lang zh-CN \
  --input scripts/i18n/examples/catq_en.json \
  --output /tmp/catq_zh_draft.json \
  --glossary scripts/i18n/neuro_glossary.json
```

## 3) Human post-edit

- Keep product boundary terms stable: `特质探索 / trait exploration`, `非临床诊断 / not a clinical diagnosis`.
- Avoid medicalized wording.
- Check tone consistency in both locales inside real UI screens.
