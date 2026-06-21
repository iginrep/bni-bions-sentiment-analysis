# docs

Human-facing documentation for the BNI/BIONS sentiment monitoring project.

Use this directory for strategy, architecture, data contracts, research, approval records, and operational notes.

## Reading order

1. `architecture.md` — system overview.
2. `collector-strategy.md` — cheapest-first source plan.
3. `human-approval-checklist.md` — current approvals and risk gates.
4. `data-contract.md` — canonical normalized item reference.
5. `provider-decision-matrix.md` — source/API/vendor tradeoffs.
6. `labeling-guideline.md` — sentiment labeling rules.

## Research docs

| File | Purpose |
| --- | --- |
| `stockbit-x-collection-research.md` | Stockbit and X/Twitter collection options, risks, approval needs. |
| `tiktok-instagram-threads-cheapest-first.md` | TikTok, Instagram, Threads options and safety posture. |
| `source-limitations.md` | Known source limitations. |

## Documentation style

Use Diátaxis framing:

- tutorials for onboarding walkthroughs.
- how-to guides for task recipes.
- reference for exact schemas, commands, APIs.
- explanation for tradeoffs and architecture.

Keep safety/compliance notes explicit. This project intentionally prioritizes low-risk collection over maximum volume.
