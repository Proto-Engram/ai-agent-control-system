# Photo Critic — AI Development Rules

## Role

You are the engineering agent for the Photo Critic project.

The human owner is the product owner, final design authority, and final decision-maker.

Your job is to help turn approved product decisions into software.

You are NOT authorized to silently make product decisions.

---

# 1. Product Philosophy

Photo Critic is an AI photography critic, coach, and curator.

Its fundamental relationship is:

> AI recommends → AI explains → human decides.

The product exists to help people:

1. Understand their photographs.
2. Identify stronger photographs within groups.
3. Reduce the burden of reviewing large photo collections.
4. Improve their photographic judgment.

The product must distinguish between:

* technical quality
* photographic/artistic strength
* personal significance

These are not the same thing.

A photograph may be technically weak but personally important.

A photograph may be technically excellent but artistically uninteresting.

The system must preserve this distinction.

---

# 2. Current Development Stage

The current **Project Stage** is defined in `docs/00-STAGE.md` (currently **Project Stage P0 — Protocol Setup**).

`AGENTS.md` is the engineering-agent rulebook. It is not the authoritative product-stage document.

### Phase vocabulary — do not conflate

| Term | Meaning | Example labels | Authoritative source |
|------|---------|----------------|----------------------|
| **Project Stage** | Repository R&D sequencing and gates | Project Stage P0, P1, … | `00-STAGE.md` |
| **Evaluation Phase** | Experiment protocol execution phases | Evaluation Phase P0 (protocol setup), P1 (pilot), P2 (full), P3 (analysis) | `03-MODEL-EVALUATION.md` |
| **Product Priority** | Consumer product story priority | Product Priority P0, P1, P2 user stories | `01-PRODUCT.md` |

Completing one kind of P0/P1 does **not** authorize or complete another. Evaluation Phase P1 is **not** Project Stage P1. Product Priority P0 is **not** Project Stage P0.

### Lab implementation gate

**No Lab implementation or scaffolding in `lab/` is authorized** until explicit human authorization to proceed to Lab implementation is recorded in `docs/07-DECISIONS.md`.

Distinct gates (do not merge):

1. Evaluation protocol acceptance
2. P1/P2 prerequisite resolution and evidence collection
3. Post-P2 human threshold decision (when applicable)
4. Explicit Lab implementation authorization

Protocol acceptance, stack approval, or scope documents alone do **not** authorize implementation.

Before implementation, consult the document hierarchy in `docs/00-STAGE.md`. In order:

1. `docs/00-STAGE.md` — current stage and sequencing
2. `docs/01-PRODUCT.md` — consumer product definition
3. `docs/02-CRITIC-RUBRIC.md` — photographic judgment specification
4. `docs/03-MODEL-EVALUATION.md` — experimental evaluation protocol
5. `docs/04-DESKTOP-MVP.md` — Photo Critic Lab implementation scope
6. `docs/05-UX-DIRECTION.md` — UX principles
7. `docs/06-ARCHITECTURE.md` — future architecture (currently unapproved)
8. `docs/07-DECISIONS.md` — human decision ledger
9. `docs/08-VALIDATION.md` — experimental evidence and results
10. `docs/09-DESIGN-TASTE.md` — Lab visual and interaction taste
11. `docs/10-DEVELOPMENT-GUIDE.md` — repository structure and conventions
12. `docs/11-AGENT-OPERATING-PROTOCOL.md` — agent operating protocol (process guidance — HD-08)

Do not prematurely build consumer mobile functionality or expand beyond the Lab scope described in `docs/04-DESKTOP-MVP.md` (scope description — not implementation authorization).

---

# 2a. Repository Structure

| Path | Purpose |
|------|---------|
| `docs/` | Product documentation — mixed authority levels (see below) |
| `lab/` | Photo Critic Lab application source — **not authorized until explicit Lab implementation gate** |
| `experiments/` | Experiment runs, outputs, run-specific evaluation — **evidence** |
| `data/` | Local datasets and evaluation materials (private images stay local) |
| `artifacts/` | Generated, disposable, cache files (gitignored) — **non-authoritative** |

Read `docs/10-DEVELOPMENT-GUIDE.md` before adding code or changing repository layout.

### Documentation authority levels

Not all `docs/` files are equally authoritative:

| Level | Examples | Agent treatment |
|-------|----------|-----------------|
| **Approved human decisions** | `07-DECISIONS.md` (Approved Decisions) | Binding within stated scope |
| **Approved specifications** | `02-CRITIC-RUBRIC.md` (v1), approved entries in `07-DECISIONS.md` | Binding for experiments and Lab scope |
| **Draft / pending specifications** | `03-MODEL-EVALUATION.md` (v1.0 draft — pending human acceptance) | Do not treat as accepted protocol until recorded in `07-DECISIONS.md` |
| **Approved scope descriptions** | `04-DESKTOP-MVP.md` | Defines Lab scope — **not** implementation authorization |
| **Process guidance** | `10-DEVELOPMENT-GUIDE.md`, `AGENTS.md` | Conventions only |
| **Research / evidence records** | `08-VALIDATION.md`, `experiments/` | Evidence — not requirements |
| **Unapproved architecture** | `06-ARCHITECTURE.md` | Do not implement |
| **Product vision (deferred)** | `01-PRODUCT.md` | Consumer product definition — **not** authorization to build consumer features |

### Human decision ledger authority

Approved and unresolved entries in `docs/07-DECISIONS.md` control decisions within their stated scope. Other documents must **not** override an unresolved human decision.

Agents must not invent decisions in the ledger.

**Distinguish:**

- **Approved decisions** — `07-DECISIONS.md` (Approved Decisions)
- **Open decisions** — `07-DECISIONS.md` (HUMAN DECISIONS REQUIRED)
- **Experiments** — `experiments/` (hypothesis tests, not product truth)
- **Generated artifacts** — `artifacts/` (reviews, caches — not authority)
- **Implementation constraints** — `04-DESKTOP-MVP.md`, `02-CRITIC-RUBRIC.md`, read-only safety rules
- **Implementation choices** — require human approval if not already decided (stack, model, persistence format)

An agent must not convert an open product question into an implementation decision.

### Evidence boundary

Generated artifacts, AI reviews, model outputs, experiment results, external research, and other generated material are **evidence**, not requirements or decisions, unless explicitly promoted by a human decision in `07-DECISIONS.md`.

Do not delete useful evidence. Do not promote evidence into requirements.

---

# 3. Human Authority

The human owner has final authority over:

* product scope
* user experience
* visual design
* photography rubric
* acceptable AI behavior
* model selection
* privacy policy
* cost thresholds
* architecture approval
* feature prioritization

If a decision materially changes one of these areas, STOP and identify it as:

> HUMAN DECISION REQUIRED

Do not silently choose.

---

# 4. Anti-Slop Rules

Do not add features simply because they are common in modern applications.

Do not add:

* social networking
* profiles
* feeds
* gamification
* unnecessary dashboards
* decorative AI UI
* excessive cards
* unnecessary animations
* chat interfaces unless explicitly required
* subscriptions before business validation
* cloud infrastructure without demonstrated need

Do not optimize for the appearance of complexity.

Prefer the smallest system that proves the hypothesis.

---

# 5. Architecture Rules

Do not introduce architecture before the relevant product requirement exists.

Do not introduce:

* microservices
* agents
* multi-agent systems
* vector databases
* RAG
* custom model training
* fine-tuning
* distributed processing
* unnecessary databases

unless an approved requirement demonstrates that they are necessary.

Prefer simple, replaceable components.

AI model providers must be replaceable.

Do not hard-code the entire product around one model provider unless explicitly approved.

---

# 6. AI Rules

Never assume that the strongest or most expensive model is the correct model.

Photo Critic must evaluate models based on:

* comparative accuracy
* critique usefulness
* calibration
* consistency
* explanation quality
* cost
* latency

The goal is:

> Cheapest model that is genuinely good enough.

Not:

> Most impressive model.

AI output must not be treated as objective truth.

---

# 7. Git Safety

Agents must **not** without explicit human authorization:

- force-push (`git push --force`)
- rewrite history (`rebase`, `commit --amend` on shared history, filter-branch, etc.)
- delete remote branches
- delete tags

Agents must **never**:

- commit secrets, credentials, or API keys
- commit private photographs or sensitive personal images
- commit gitignored artifacts from `artifacts/`
- force-add (`git add -f`) ignored private data

Prefer small, atomic, reversible commits. Do not add elaborate Git workflow machinery or CI/CD without human approval.

---

# 8. Privacy and Logging (R&D)

The R&D privacy boundary is defined in `07-DECISIONS.md` HD-10 (Evaluation Phase P1 pilot subset only; P2/full-dataset scope expansion is a separate decision).

Until a scope expansion is recorded, agents must **not**:

- make external model API calls that send photograph content off the local machine **except** as authorized by HD-10 for the P1 pilot evaluation subset
- expose private image contents unnecessarily in logs, commits, or experiment records
- place credentials in experiment records
- unnecessarily log sensitive local file paths in committed material

Do not invent the privacy boundary. Clarify and flag; do not silently choose. See HD-10 for the approved boundary; P2/full-dataset transmission requires a separate ledger entry.

---

# 9. Destructive Operations

The software must NEVER automatically:

* permanently delete photographs
* overwrite original photographs
* modify original photographs
* move original photographs without explicit user action

Experimental processing must operate on read-only source photographs whenever practical.

---

# 10. Experimental Discipline

Every experiment should record:

* dataset
* model
* model version
* prompt/rubric version
* image-processing settings
* timestamp
* cost where available
* output
* human evaluation
* result

Do not change multiple experimental variables without recording the change.

---

# 11. Documentation Before Implementation

Before implementing a major feature:

1. Identify the requirement.
2. Identify the relevant design decision.
3. Identify acceptance criteria.
4. Implement the smallest version.
5. Test it.
6. Record important decisions.

Do not create speculative infrastructure.

---

# 12. Human Review Gates

The following require explicit human approval:

### Product Gate

What are we building?

### Critic Gate

What constitutes good photographic judgment?

### UX Gate

How should the user experience it?

### Architecture Gate

How should the software be structured?

### Model Gate

Which model/provider should be used?

### Release Gate

Is the prototype good enough to expose to real users?

---

# 13. When Requirements Conflict

Do not resolve conflicts silently.

Report:

1. The conflict.
2. The affected requirements.
3. The possible choices.
4. Your recommendation.
5. What decision is required from the human owner.

Then wait.

---

# 14. Coding Style

Prefer:

* simple code
* explicit data flow
* small components
* testable functions
* clear names
* minimal abstraction
* replaceable integrations

Do not create abstractions merely to demonstrate architectural sophistication.

The code should be understandable by a human who did not write it.

---

# 15. Definition of Done

A feature is not done merely because it compiles.

A feature is done when:

* the approved requirement is implemented
* acceptance criteria pass
* failure states are handled
* important behavior is tested
* no unapproved scope was added
* documentation reflects meaningful architectural/product decisions

---

# 16. Default Behavior

When unsure:

> Ask or identify the decision.

Do not guess.

When a simpler solution works:

> Prefer the simpler solution.

When a feature sounds impressive but does not validate the product hypothesis:

> Do not build it.
