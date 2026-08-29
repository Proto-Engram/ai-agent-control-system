# AI Agent Control System

*Research demonstration — mechanical controls for untrusted AI implementation participants*

This repository demonstrates **agent orchestration and governance** through concrete enforcement mechanisms: task scope envelopes, JSON Schema contracts, pre-commit policy gates, evidence replay, and adversarial review protocols.

It is not a shipping product. It is not a claim that AI output is trustworthy. It shows one approach to closing the gap between **policy** and **mechanical enforcement** when AI agents participate in software engineering.

> Developed in private R&D; this public repo is the portfolio-safe control-plane demonstration only.

---

## Why does this exist?

AI-assisted development creates a new trust problem. An agent can produce plausible code, fabricated test claims, scope violations, and hand-written gate artifacts. Ordinary CI answers whether tests passed; this system also asks whether **claims are mechanically falsifiable**.

---

## Control loop

```text
Human Authority → SPECIFY → CONSTRAIN → IMPLEMENT → TEST → EVIDENCE → REVIEW → GATE → Human Decision
```

| Control | Mechanism | Enforcement |
| ------- | --------- | ----------- |
| Prompt integrity (demo) | `hash_prompts.py --verify` | Mechanical |
| Output contract | JSON Schema + `validate_output.py` | Mechanical |
| Demo preflight | `preflight_p1.py` + demo manifest | Mechanical |
| Task scope | `check_task_scope.py` + envelope | Mechanical |
| Evidence replay | `collect_evidence.py` | Mechanical |
| Verification bundle | `check_verification_bundle.py` | Mechanical |
| Repo policy / secrets | `check_repo_policy.py` + gitleaks | Mechanical |
| Human approval | Procedural | Human |

See [`docs/PUBLIC-ENGINEERING-CASE-STUDY.md`](docs/PUBLIC-ENGINEERING-CASE-STUDY.md) and [`docs/12-CONTROL-SYSTEM.md`](docs/12-CONTROL-SYSTEM.md).

---

## Repository structure

| Path | Demonstrates |
| ---- | ------------ |
| [`scripts/`](scripts/) | Policy gates, scope, evidence, preflight |
| [`schemas/`](schemas/) | Machine-readable contracts |
| [`tests/`](tests/) | Adversarial validation (demo mode) |
| [`examples/demo-prompt/`](examples/demo-prompt/) | Generic frozen prompt fixtures |
| [`examples/demo-manifest/`](examples/demo-manifest/) | Demo preflight manifests |
| [`tasks/`](tasks/) | Scope envelope examples |
| [`prompts/review/`](prompts/review/) | Adversarial review checklists |

**Mode:** `config/control-plane.json` sets `"mode": "demo"`.

---

## Verification

```bash
python scripts/bootstrap_controls.py
pytest tests/
python scripts/hash_prompts.py --verify
python scripts/verify_policy.py --all-files
python scripts/preflight_p1.py --manifest examples/demo-manifest/manifest.json --allow-dirty
python scripts/validate_output.py tests/fixtures/output/task_a_valid_minimal.json
```

---

## Known limitations

- Local hooks bypassable with `git commit --no-verify`
- No CI configured in this repository
- Session independence is procedural, not cryptographic
- Hash verification is integrity, not authorization
- Demo fixtures are synthetic — not product prompts

---

## What this demonstrates

- AI governance and untrusted-implementer model
- Agent orchestration with mechanical scope constraints
- Evidence-based verification and adversarial validation
- Python tooling, JSON Schema, pre-commit enforcement
- Human-in-the-loop boundaries with honest limitation disclosure

---

## Private product

Photo Critic product R&D continues in a **private repository**. This public repo intentionally contains **no product IP**, prompts, rubric, datasets, or internal decision ledger.
