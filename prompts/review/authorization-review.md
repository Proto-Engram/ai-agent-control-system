# Adversarial Authorization Review

**Purpose:** REVIEW stage — attempt to **falsify** scope and authorization compliance.  
**Status:** Process template — not authority  
**Does not replace:** Protocol 11 §8.5 independent verifier

---

## Instructions for reviewer (separate session from worker)

Treat all worker claims as **untrusted**. Inspect the actual diff and task contract — not worker narrative.

Your job is to find failures, not to approve.

---

## 1. Authority traceability

| Question | Finding |
|----------|---------|
| Does every changed file fall within `allowed_paths` in the task contract? | |
| Were any `forbidden_paths` modified? | |
| Were any frozen artifacts (HD-13 prompts) touched? | |
| Was `docs/07-DECISIONS.md` modified without explicit human authorization? | |
| Does the work exceed what session instruction or HD entry authorized? | |

**FAIL if:** any forbidden path modified or scope expanded without human decision.

---

## 2. Gate conflation check

| Claim | Verified independently? |
|-------|-------------------------|
| "Tests pass" | Re-run `pytest tests/` — record exit code |
| "Preflight passed" | Re-run `python scripts/preflight_p1.py` — inspect JSON output |
| "Hashes verified" | Re-run `python scripts/hash_prompts.py --verify` |
| "Task complete" | Map each AC-* to evidence |

**FAIL if:** worker claim lacks independent command replay.

---

## 3. Acceptance criteria mapping

| AC ID | Criterion | Evidence | PASS/FAIL |
|-------|-----------|----------|-----------|
| | | | |

**FAIL if:** any AC lacks falsifiable evidence.

---

## 4. Residual risks

List authorization mistakes, scope creep, or assumptions not in the task contract.

---

## Verdict

- [ ] PASS — no authorization or scope deficiencies found
- [ ] FAIL — deficiencies listed above
- [ ] INCONCLUSIVE — insufficient evidence; escalate to human

**Reviewer type:** `<verifier session | human>`  
**Reviewer must not be the worker session.**
