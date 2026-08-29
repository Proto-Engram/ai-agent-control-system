# Photo Critic — AI-Native Engineering Control System

**Status:** Process guidance — **not** implementation authorization  
**Authority:** Subordinate to [`AGENTS.md`](../AGENTS.md), [`docs/00-STAGE.md`](00-STAGE.md), [`docs/07-DECISIONS.md`](07-DECISIONS.md), and [`docs/11-AGENT-OPERATING-PROTOCOL.md`](11-AGENT-OPERATING-PROTOCOL.md) (HD-08)

This document maps the seven-stage AI-native control loop onto existing repository artifacts. It does **not** create new human decisions or replace the evaluation protocol, prompt freeze, or decision ledger.

---

## Control loop

```text
REQUEST → SPECIFY → CONSTRAIN → PLAN → IMPLEMENT → TEST → REVIEW → GATE → EVIDENCE → HUMAN DECISION
```

| Stage | Purpose | Primary artifacts |
|-------|---------|-------------------|
| **SPECIFY** | Falsifiable task contract | Domain specs, `templates/task-contract.md`, JSON schemas |
| **CONSTRAIN** | Authorization envelope | `AGENTS.md`, Protocol 11 §9.2, HD-10/11/13, pre-commit hooks |
| **REVIEW** | Adversarial falsification | Protocol 11 §8.5 verifier, `prompts/review/` |
| **TEST** | Mechanical falsification | `pytest`, `scripts/validate_output.py`, fixtures |
| **GATE** | Verify reality of claims | `scripts/preflight_p1.py`, ledger parser, hash verify |
| **EVIDENCE** | Independent verifiability | `scripts/collect_evidence.py`, gate JSON outputs |
| **HUMAN DECISION** | Judgment and authorization | `docs/07-DECISIONS.md` only |

**Independence rule:** Passing TEST ≠ REVIEW approval ≠ GATE authorization ≠ human approval.

---

## Four enforcement types

| Type | Meaning | Example |
|------|---------|---------|
| **Instruction** | Tells agent what to do | `AGENTS.md`, task contract |
| **Detection** | Detects violation after the fact | pre-commit, `hash_prompts --verify`, pytest |
| **Prevention** | Makes violation difficult | Runner re-executes live preflight; scope checker rejects out-of-envelope diffs |
| **Authorization** | Legitimate permission | HD ledger entries |

Markdown instructions alone are **not** enforcement. Prefer Detection where practical.

---

## Protocol 11 mapping

| Protocol 11 | Control stage |
|-------------|---------------|
| INSPECT | SPECIFY + CONSTRAIN |
| PLAN | PLAN (between CONSTRAIN and IMPLEMENT) |
| WORK / WORKER | IMPLEMENT |
| WORK COMPLETE | EVIDENCE (partial — not sufficient alone) |
| INDEPENDENT VERIFY | REVIEW |
| COMMIT CANDIDATE | EVIDENCE |
| HUMAN REVIEW | HUMAN DECISION |
| §7 HUMAN DECISION REQUIRED | HUMAN DECISION |
| §6 Gate Model | GATE + HUMAN DECISION |

---

## Mechanical tooling

| Script | Stage | Blocking |
|--------|-------|----------|
| `scripts/verify_policy.py` | CONSTRAIN | Yes at commit (via pre-commit → `--staged`) |
| `scripts/hooks_status.py` | CONSTRAIN | Reports configured / installed / executed / passed |
| `scripts/bootstrap_controls.py` | CONSTRAIN | Installs hooks + dev deps (once per clone) |
| `scripts/check_task_scope.py` | CONSTRAIN | Yes when `tasks/active-envelope` set |
| `scripts/check_ledger_integrity.py` | CONSTRAIN | Yes — blocks agent HD-13 hash row edits |
| `scripts/check_verification_bundle.py` | REVIEW | Validates worker/verifier evidence binding |
| `scripts/hash_prompts.py --verify` | CONSTRAIN + GATE | Yes for prompt integrity |
| `scripts/check_repo_policy.py` | CONSTRAIN | Yes (via `verify_policy.py`) |
| `scripts/validate_output.py` | TEST | Yes for contract validation |
| `scripts/preflight_p1.py` | GATE | Yes before P1 execution |
| `scripts/collect_evidence.py --role worker\|verifier` | EVIDENCE | Separate evidence artifacts |
| `scripts/run_p1_experiment.py` | GATE + Prevention | Re-executes live preflight; no cached JSON auth |

---

## Agent boundaries

**Agents may:** draft contracts, run read-only inspection, prepare COMMIT CANDIDATE, run pytest/preflight, implement within task contract paths.

**Agents may not:** authorize P1/API calls, write HD approvals, modify HD-13 frozen prompts, generate human reference judgments, declare gates passed without script output, commit without human instruction.

---

## P1 integration

P1 evaluation SPECIFY is satisfied by HD-13 frozen artifacts. Before first external API call:

1. `python scripts/preflight_p1.py --manifest <path>` → PASS
2. HD-14 recorded in `07-DECISIONS.md` by human owner
3. `python scripts/run_p1_experiment.py` **re-executes live preflight** (cached JSON is evidence only)

Green preflight validates **prerequisites** — not photographic quality (human scoring required).

---

## Policy hook states (C1)

These four states are **not interchangeable**:

| State | Meaning | How to check |
|-------|---------|--------------|
| **configured** | `.pre-commit-config.yaml` exists | `python scripts/hooks_status.py --json` |
| **installed** | `.git/hooks/pre-commit` invokes pre-commit or verify_policy | `hooks_status.py` |
| **executed** | `verify_policy.py` ran and wrote last-run record | `hooks_status.py` |
| **passed** | Last execution exit code 0 | `hooks_status.py` |

Bootstrap once per clone: `python scripts/bootstrap_controls.py`

Canonical audit (CI-compatible when authorized): `python scripts/verify_policy.py --all-files`

**No pre-commit recursion:** pre-commit → `verify_policy.py --staged` → underlying checks directly.

---

## Task scope envelope (C3)

Machine-readable envelope: `tasks/envelopes/<task-id>.json` (schema: `schemas/task-envelope.schema.json`).

Active task pointer: `tasks/active-envelope` (one-line path to envelope file).

Human-readable companion: `templates/task-contract.md` — **not** the enforcement mechanism.

Check: `python scripts/check_task_scope.py --envelope <path> --staged`

---

## Verification evidence roles (C4)

| Role | Artifact | Script |
|------|----------|--------|
| Worker | `artifacts/evidence/<task-id>/worker-evidence.json` | `collect_evidence.py --role worker` |
| Verifier | `artifacts/evidence/<task-id>/verifier-evidence.json` | `collect_evidence.py --role verifier --worker-evidence <path>` |
| Human | `docs/07-DECISIONS.md` | Human owner only |

Bundle check: `python scripts/check_verification_bundle.py --task-id <id>`

> This mechanically verifies evidence separation and command replay, but **cannot prove** that two invocations came from independent AI sessions.

---

## HD-13 integrity boundary (C5)

> **Hash verification establishes consistency, not authorization.**

| Attack | Detection |
|--------|-----------|
| Prompt changed, ledger unchanged | `hash_prompts.py --verify` FAIL |
| Agent changes prompt + ledger hash rows | `check_ledger_integrity.py` FAIL |
| Human-authorized re-freeze | Human sets `PHOTO_CRITIC_HUMAN_LEDGER=1` or `--human-override` |

Coordinated prompt+ledger tamper by an agent is blocked at commit gate. Cryptographic provenance is **not** implemented at this stage.

---

## Control-plane changes

Changes to enforcement scripts, schemas, pre-commit config, or task envelopes are flagged as `CONTROL_PLANE_CHANGE` in policy and worker evidence output. These are not ordinary application work.

---

## Related documents

| Document | Role |
|----------|------|
| [`docs/P1-HUMAN-PREREQUISITES.md`](P1-HUMAN-PREREQUISITES.md) | Human-owned P1 checklist |
| [`templates/task-contract.md`](../templates/task-contract.md) | SPECIFY template |
| [`schemas/`](../schemas/) | Machine-readable specs |
| [`prompts/review/`](../prompts/review/) | Adversarial REVIEW prompts |
