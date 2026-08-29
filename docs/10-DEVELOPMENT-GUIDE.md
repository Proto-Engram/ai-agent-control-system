# Photo Critic — Development Guide

**Status:** Repository foundation — process guidance (not implementation authorization)  
**Audience:** Human developers and AI coding agents

This document describes how to work in this repository. It does **not** approve a technology stack, architecture, or Lab implementation.

### Lab implementation gate

**No Lab implementation or scaffolding in `lab/` is authorized** until explicit human authorization to proceed to Lab implementation is recorded in `07-DECISIONS.md`.

Illustrative sequences below are **not** implementation authorization.

---

## Before you write code

1. Read `docs/00-STAGE.md` — confirm current project stage and that Lab implementation is authorized.
2. Read `docs/07-DECISIONS.md` — distinguish **approved** decisions from **open** ones.
3. Read `docs/04-DESKTOP-MVP.md` — confirm the feature is in Lab scope (scope ≠ authorization).
4. Read `AGENTS.md` — engineering agent rules.

If Lab implementation authorization is not recorded in `07-DECISIONS.md`, **do not add code to `lab/`**.

If a decision is listed under **HUMAN DECISIONS REQUIRED** in `07-DECISIONS.md`, stop and flag it. Do not implement as if decided.

---

## Repository map

```
Photo Critic/
├── docs/                 # Product documentation (mixed authority — see AGENTS.md)
├── lab/                  # Lab application source — not authorized until explicit gate
├── experiments/          # Experiment runs and run-specific outputs (evidence)
├── data/                 # Local datasets and evaluation materials
├── artifacts/            # Generated/disposable files (gitignored; non-authoritative)
├── AGENTS.md             # AI agent behavioral rules
└── README.md             # Project entry point
```

### Evidence boundary

Generated artifacts, AI reviews, model outputs, experiment results, and other generated material are **evidence**, not requirements or decisions, unless explicitly promoted in `07-DECISIONS.md`.

### Boundary rules

| Content | Location | Committed? | Authority |
|---------|----------|------------|-----------|
| Approved human decisions | `docs/07-DECISIONS.md` | Yes | Binding within scope |
| Approved specifications | `docs/02-CRITIC-RUBRIC.md`, etc. | Yes | Binding when approved |
| Draft specifications | `docs/03-MODEL-EVALUATION.md` | Yes | Pending — not accepted until ledger records acceptance |
| Lab scope description | `docs/04-DESKTOP-MVP.md` | Yes | Scope — not implementation authorization |
| Experiment run folders | `experiments/` | Yes (metadata/outputs; not private images) | Evidence |
| Photograph datasets | `data/datasets/` | **No** — local only | Local |
| Dataset manifests (no sensitive paths) | `data/evaluation/` | Optional JSON — see `data/README.md` | Local or committed per manifest policy |
| Build output, caches, logs | `artifacts/` | **No** — gitignored | Non-authoritative |
| Secrets, API keys | `.env` (local) | **Never** | — |

---

## What agents must not do

- Convert an **open product question** into an **implementation decision**.
- Add a feature because it seems useful but is not in `04-DESKTOP-MVP.md`.
- Create infrastructure "for later" (databases, cloud, agents, RAG, etc.).
- Choose a model or provider without human approval.
- Choose a technology stack without human approval.
- Implement from `06-ARCHITECTURE.md` (not approved).
- Commit private photographs or sensitive datasets.
- Delete, move, overwrite, or modify source photographs.

When uncertain: **stop and ask**.

---

## What agents should do

- Prefer the **smallest implementation** that tests the current hypothesis.
- Keep model providers **replaceable**.
- Operate on photographs **read-only**.
- Record experiment metadata (see below).
- Follow `docs/09-DESIGN-TASTE.md` for Lab UI choices.
- Match existing naming and structure when code exists.

---

## Experiment recording

Every experiment must record (from `AGENTS.md` §8):

- dataset
- model
- model version
- prompt / rubric version
- image-processing settings
- timestamp
- cost (where available)
- output
- human evaluation
- result

Store formal runs under `experiments/YYYY-MM-DD_<description>/`. Summarize significant findings in `docs/08-VALIDATION.md`.

Do not change multiple experimental variables without recording the change.

---

## Naming conventions

### Directories

- `kebab-case` for multi-word directory names where used
- Experiment folders: `YYYY-MM-DD_<short-description>`

### Files

- `kebab-case` or `snake_case` — pick one per area when code exists; until then, prefer `kebab-case` for config and `snake_case` for Python if Python is chosen
- Documentation: `NN-TOPIC.md` in `docs/` (numbered, uppercase topic)

### Identifiers in experiment output

- `photograph_id` — stable reference to a source image within a run
- `group_id` — comparison group identifier
- `rubric_version` — e.g. `"1.0"` per `02-CRITIC-RUBRIC.md`

Follow structured output field names in `02-CRITIC-RUBRIC.md` §17 where applicable.

---

## Implementation sequencing

**Illustrative sequence — not implementation authorization.**

These are organizational suggestions only. Human approval is required before each phase. The sequence does **not** override the Lab implementation gate in `00-STAGE.md` and `07-DECISIONS.md`.

1. **Stack decision** — record in `07-DECISIONS.md` (does not authorize scaffolding alone)
2. **Lab implementation authorization** — explicit gate in `07-DECISIONS.md` before any `lab/` code
3. **Scaffolding** — minimal app shell in `lab/` with folder picker stub
4. **Image discovery** — read-only scan of supported formats
5. **Model integration** — behind replaceable interface; one approved model
6. **Individual critique** — rubric v1 output per `02-CRITIC-RUBRIC.md`
7. **Comparative judgment** — human-curated groups (HD-05)
8. **Human decision recording** — persist experiment results
9. **Review UI** — photograph-first per `09-DESIGN-TASTE.md`

Do not skip ahead to clustering, batch curation, or consumer features.

---

## Testing

- Control-system tests use **pytest** (`requirements-dev.txt`). Run: `pytest tests/`
- Prefer testing **behavior** (schema validation, scope enforcement, gate logic) over snapshotting AI prose.
- Do not commit private photographs as test fixtures without explicit approval.

---

## Document hierarchy

When documents conflict, follow order in `00-STAGE.md`. This guide does not override product documents.

| # | Document | Role |
|---|----------|------|
| 1 | `00-STAGE.md` | Current stage |
| 2 | `01-PRODUCT.md` | Consumer product (deferred) |
| 3 | `02-CRITIC-RUBRIC.md` | Judgment specification |
| 4 | `03-MODEL-EVALUATION.md` | Evaluation protocol |
| 5 | `04-DESKTOP-MVP.md` | Lab implementation scope |
| 6 | `05-UX-DIRECTION.md` | UX principles |
| 7 | `06-ARCHITECTURE.md` | Future architecture (unapproved) |
| 8 | `07-DECISIONS.md` | Human decision ledger |
| 9 | `08-VALIDATION.md` | Experiment evidence |
| 10 | `09-DESIGN-TASTE.md` | Lab visual/interaction taste |
| 11 | `10-DEVELOPMENT-GUIDE.md` | This document |

`AGENTS.md` is the engineering rulebook; it does not override `00-STAGE.md`.

`docs/11-AGENT-OPERATING-PROTOCOL.md` is approved agent operating protocol (process guidance — HD-08); it does not override `00-STAGE.md` or `07-DECISIONS.md`.

---

## Open prerequisites before implementation

See `07-DECISIONS.md`. At minimum, unresolved items include:

- Image preprocessing policy
- Prompt version(s), evaluator assignment, retry/inference parameters, pilot dataset (P1 prerequisites — see protocol §10)
- Technology stack
- Numerical quality thresholds and Lab success criteria (post-Evaluation Phase P2 only)
- **Lab implementation authorization** (explicit proceed-to-implementation gate)

Do not begin `lab/` implementation or scaffolding until Lab implementation authorization is recorded. Stack approval alone is insufficient.

---

## Control-system bootstrap

Once per clone, install enforcement hooks and dev dependencies:

```bash
python scripts/bootstrap_controls.py
```

Verify hook state (configured / installed / executed / passed):

```bash
python scripts/hooks_status.py --json
```

Run full policy audit:

```bash
python scripts/verify_policy.py --all-files
```

Task scope check (when envelope active):

```bash
python scripts/check_task_scope.py --envelope tasks/envelopes/<task-id>.json --staged
```

CI/CD is **not authorized** without explicit human approval in `07-DECISIONS.md` (`AGENTS.md` §Git Safety). Use `verify_policy.py --all-files` as the CI-compatible entrypoint when authorized.
