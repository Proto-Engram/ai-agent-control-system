# Test and Evaluation Data

This directory is the boundary for **local datasets and human evaluation materials** used in Lab experiments.

## Status

Empty by design. **Do not commit private photographs or sensitive personal images.**

## Intended structure

```
data/
  datasets/           # Human-curated comparison groups, labeled sets (local only)
  evaluation/         # Dataset manifests (sanitized JSON, no image bytes; local paths stay local)
  fixtures/           # Optional: small approved non-sensitive test images (if ever added)
```

## Rules

1. **Private photographs stay local.** The repository structure exists to organize work — not to store user photo libraries.
2. **Human-curated comparison groups** are required for initial Lab experiments (see `docs/07-DECISIONS.md` HD-05).
3. **Dataset manifests** (JSON, no image bytes) may live in `data/evaluation/` when they contain no sensitive metadata or local file paths. Committed manifests must use anonymized identifiers only — not `local_path` values that reveal private directories.
4. **Run-specific scoring sheets** belong under `experiments/<run>/human-evaluation/` (see `03-MODEL-EVALUATION.md`).
5. If a shared fixture set is ever needed, it must be explicitly approved and must contain only non-sensitive images.

### `data/evaluation/` storage

| Content | Location | Committed? |
|---------|----------|------------|
| Reusable dataset manifest (no sensitive paths) | `data/evaluation/*.json` | Optional — if sanitized |
| Local-only manifest with `local_path` | `data/evaluation/` or local copy | **No** — keep local |
| Run-specific human scoring | `experiments/<run>/human-evaluation/` | Yes (no private images) |

## Related documentation

| Document | Relevance |
|----------|-----------|
| `docs/02-CRITIC-RUBRIC.md` | Dataset focus (travel/documentary); comparison group rules |
| `docs/03-MODEL-EVALUATION.md` | Dataset requirements for model evaluation |
| `docs/08-VALIDATION.md` | Where summarized experiment evidence is recorded |
