# database

Database assets for BNI/BIONS sentiment monitoring.

## Active database

MongoDB is the active target.

```txt
database: bni_bions_sentiment
init file: db/mongo-init.js
```

## Files

| File | Status | Purpose |
| --- | --- | --- |
| `mongo-init.js` | active | MongoDB collections, indexes, seed keyword/source config. |
| `schema.sql` | legacy/reference | Earlier relational schema reference. Do not treat as source of truth without reconciling with Mongo. |
| `seed_keywords.sql` | legacy/reference | Earlier SQL seed data reference. |

## Mongo usage

Validate init script syntax:

```bash
node --check db/mongo-init.js
```

Use Mongo for normalized social items, keyword/source configs, schedules, and sentiment results.

## Canonical item

Collectors normalize data into `RawSocialItem` before persistence.

See:

```txt
pipeline/collector/base.py
docs/data-contract.md
.agents/collector-contract.md
```

## Indexing goals

Indexes should support:

- dedupe by platform/source id.
- filtering by platform, source type, target entity, keyword.
- time-series views by posted/collected time.
- sentiment summaries.

## Data safety

Do not commit raw database dumps.

Do not store secrets, cookies, tokens, passwords, or connection strings as documents.

User approved storing public usernames/display names, but exports should avoid them unless needed.

Raw retention default: 180 days.

Aggregate retention default: 365 days.
