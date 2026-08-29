# Task Contract

**Status:** SPECIFY artifact — **not** authority  
**Task ID:** `<unique-id>`  
**Date:** `<YYYY-MM-DD>`

Complete before non-trivial implementation. Trivial fixes may use Protocol 11 §7.3 shortcut.

---

## 1. Request summary

What exactly is being requested?

`<one paragraph>`

---

## 2. Authority

| Source | Reference | Scope |
|--------|-----------|-------|
| Session instruction | `<yes/no — quote if yes>` | |
| Ledger entry | `<HD-XX or none>` | |
| Stage-appropriate work | `<00-STAGE.md reference>` | |

If no authority covers this task → **STOP — HUMAN DECISION REQUIRED**

---

## 3. Scope

### In scope

- `<bullet list>`

### Out of scope

- `<bullet list — include lab/, consumer features, frozen prompts unless explicitly authorized>`

---

## 4. Authorization envelope (CONSTRAIN)

```yaml
allowed_paths:
  - # e.g. scripts/
forbidden_paths:
  - prompts/evaluation/P1-A-v1.1.md
  - prompts/evaluation/P1-B-v1.1.md
  - prompts/evaluation/P1-PHOTOGRAPHIC-CRITICAL-FRAMEWORK-v1.0.md
  - prompts/evaluation/P1-OUTPUT-CONTRACT-v1.0.md
  - prompts/evaluation/P1-CROSS-MODEL-INVARIANTS-v1.0.md
  - docs/07-DECISIONS.md  # unless human explicitly authorizes ledger edit
allowed_operations:
  - read
  - write  # within allowed_paths only
forbidden_operations:
  - external_api_call
  - photograph_transmission
  - lab_scaffolding
  - autonomous_commit
allowed_dependencies:
  - none  # or explicit list after human approval
frozen_artifacts:
  - HD-13 prompt set
authority:
  - # HD/session refs
external_io_allowed: false
commit_allowed: false  # unless explicit session instruction
```

**Machine-readable envelope (enforcement):** `tasks/envelopes/<task-id>.json` per `schemas/task-envelope.schema.json`. Set active task via `tasks/active-envelope`. The markdown contract above is the human-readable companion only.

---

## 5. Assumptions (explicit — not silent)

| ID | Assumption | Risk if wrong |
|----|------------|---------------|
| A1 | `<assumption>` | `<impact>` |

If assumption requires human confirmation → **STOP**

---

## 6. Unresolved decisions (blocking)

| Decision | Status | Blocks |
|----------|--------|--------|
| `<decision>` | OPEN | `<what>` |

Empty means no blockers identified.

---

## 7. Acceptance criteria (falsifiable)

Each criterion must map to a test, script exit code, or human review item.

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-1 | `<criterion>` | `<pytest / script / human>` |
| AC-2 | | |

Vague criteria ("works correctly") are **invalid** — rewrite before implementation.

---

## 8. Applicable controls

| Stage | Artifact / command |
|-------|-------------------|
| TEST | `pytest tests/` |
| GATE | `python scripts/preflight_p1.py` (if P1-related) |
| EVIDENCE | `python scripts/collect_evidence.py` |
| REVIEW | Separate verifier session + `prompts/review/` |

---

## 9. Sign-off

| Role | Status | Date |
|------|--------|------|
| Worker (draft) | | |
| Human (ambiguity resolved) | pending | |
| Verifier (post-implementation) | pending | |
