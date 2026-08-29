# JSON Schemas

Machine-readable specifications derived from approved markdown sources. **Not authority** — source documents remain canonical.

| Schema | Source | Control stage |
|--------|--------|---------------|
| `task-envelope.schema.json` | `templates/task-contract.md` | SPECIFY, CONSTRAIN |
| `worker-evidence.schema.json` | Protocol 11 §8.5 | EVIDENCE |
| `verifier-evidence.schema.json` | Protocol 11 §8.5 | REVIEW |
| `dataset-manifest.schema.json` | `docs/03-MODEL-EVALUATION.md` §1.5 | SPECIFY, GATE |
| `experiment-manifest.schema.json` | `docs/03-MODEL-EVALUATION.md` §6.1 + HD-12/13 | SPECIFY, GATE |
| `p1-output-contract.schema.json` | `P1-OUTPUT-CONTRACT-v1.0.md` (HD-13) | TEST |

Validate with:

```bash
python scripts/validate_output.py <json-file>
python scripts/preflight_p1.py --manifest <experiment-manifest.json>
```
