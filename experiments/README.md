# Experiments

This directory holds **experimental runs and their artifacts** — distinct from application source (`lab/`) and from raw datasets (`data/`).

**Authority:** Experiment outputs are **evidence**, not requirements or decisions, unless explicitly promoted by a human decision in `docs/07-DECISIONS.md`.

## What belongs here

- Individual experiment run folders (dated or named by hypothesis)
- Model comparison runs
- Prompt/rubric variant tests
- Recorded AI outputs tied to a specific experiment
- Human evaluation results for a run
- Cost and latency measurements from a run

## What does not belong here

- Application source code → `lab/`
- Raw photograph datasets → `data/datasets/` (local only; not committed)
- Build output, caches, logs → `artifacts/` (gitignored)
- Product decisions → `docs/07-DECISIONS.md`
- Authoritative validation summaries → `docs/08-VALIDATION.md`

## Evidence rules

Experiment outputs are evidence. Specifically:

- model outputs are evidence
- scores are evidence
- analysis is evidence
- mean scores and agreement rates are descriptive summaries — not automatic rankings or pass/fail

Experiment results do **not** automatically:

- become product requirements
- establish numerical thresholds
- select a model or provider
- authorize Lab implementation

Human promotion through `docs/07-DECISIONS.md` is required for any of the above.

**Human reference judgments:** Must exist before model evaluation. AI output must never manufacture reference judgments. Evaluator independence is preferred; if curator and evaluator are the same person, record that limitation in experiment notes (see `03-MODEL-EVALUATION.md` §2.4).

## Naming convention

Use descriptive, sortable folder names:

```
experiments/
  YYYY-MM-DD_<short-description>/
    manifest.json          # dataset, model, rubric version, prompt version, timestamp
    outputs/               # AI responses for this run
    human-evaluation/      # scorer notes, disagreement records
    notes.md               # observations, anomalies, decisions prompted
```

Adjust structure as needed, but always record: **dataset, model, model version, rubric version, prompt version, timestamp, cost, output, human evaluation**.

See `docs/03-MODEL-EVALUATION.md` and `AGENTS.md` §10 (Experimental Discipline).

## Privacy

Do not commit private photographs. Experiment folders may reference local paths or anonymized identifiers — not image files themselves unless explicitly approved for a shared, non-sensitive fixture set.

**Approved boundary (HD-10):** External API calls transmitting photograph content are authorized **only** for the Evaluation Phase P1 pilot subset (10–20 evaluation photographs) to providers hosting HD-12 matrix candidates, for Tasks A/B only. P2/full-dataset transmission requires a separate scope-expansion entry in `07-DECISIONS.md`.
