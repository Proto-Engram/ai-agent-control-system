# Adversarial Security Review

**Purpose:** REVIEW stage — attempt to **falsify** security and privacy compliance.  
**Authority references:** HD-10 (R&D privacy), HD-11 (tool exposure), AGENTS.md §8–9

---

## Instructions for reviewer

Assume the implementation has a security flaw until proven otherwise. Do not perform a superficial checklist review.

---

## 1. Secret and credential exposure

| Check | Finding |
|-------|---------|
| Any API keys, tokens, or credentials in diff? | |
| Any credentials in committed JSON/manifests? | |
| Gitleaks/pre-commit would catch staged secrets? | |

Re-run if applicable: `pre-commit run gitleaks --all-files`

---

## 2. Photograph and path exposure

| Check | Finding |
|-------|---------|
| Any image bytes staged outside `docs/`? | |
| Any `local_path`, `absolute_path`, or home-directory paths in committed JSON? | |
| Any code that would transmit photos beyond HD-10 scope? | |

Re-run: `python scripts/check_repo_policy.py` (with staged files if commit review)

---

## 3. External communication boundary

| Check | Finding |
|-------|---------|
| Does new code make external API calls? | |
| Is HD-14 + preflight PASS required before any call? | |
| Does code respect HD-11 tool exposure tiers? | |

**FAIL if:** external API call path exists without gate check.

---

## 4. Destructive operations

| Check | Finding |
|-------|---------|
| Any deletion/overwrite of source photographs? | |
| Any modification of frozen prompt files? | |
| Any removal of experiment evidence? | |

---

## 5. Human reference judgment integrity

| Check | Finding |
|-------|---------|
| Were `human_reference_keep_preference` values agent-generated? | |

**FAIL if:** agent generated human reference judgments (protocol §2.4).

---

## Verdict

- [ ] PASS
- [ ] FAIL
- [ ] INCONCLUSIVE

**Reviewer type:** `<verifier session | human>`
