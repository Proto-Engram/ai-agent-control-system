# Generated Artifacts

This directory is for **generated, disposable, and cache files** produced during development and experiments.

Contents are **gitignored** by default. This README exists only to document the boundary.

**Authority:** Material here is **non-authoritative evidence** unless explicitly promoted by a human decision in `docs/07-DECISIONS.md`.

## What belongs here

- Build output
- Temporary image derivatives (thumbnails, resized copies for API calls)
- Logs
- Local caches
- Scratch processing output
- Downloaded model responses saved for debugging (when not part of a formal experiment run)
- AI-generated reviews and audits (e.g. `artifacts/reviews/`)

## What does not belong here

- Formal experiment results with evaluation metadata → `experiments/`
- Application source → `lab/`
- Authoritative validation records → `docs/08-VALIDATION.md`

## AI-generated reviews

Files such as `artifacts/reviews/03-EVALUATION-PROTOCOL-REVIEW.md` are **audit evidence**, not:

- protocol acceptance
- an authoritative specification
- a substitute for human decisions in `docs/07-DECISIONS.md`

Treat review findings as input to human review. Do not treat a review status (e.g. "READY FOR HUMAN REVIEW") as approval.

## Rule

If a file is reproducible or disposable, it belongs here — not in `lab/` or `experiments/`.

Do not promote artifact content into requirements without a recorded human decision.
