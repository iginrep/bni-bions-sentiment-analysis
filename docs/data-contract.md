# Canonical Social Item

```python
RawSocialItem(
  platform,
  source_type,
  source_id,
  parent_source_id,
  conversation_id,
  keyword,
  target_entity,
  author_id,
  author_username,
  author_display_name,
  text,
  language,
  source_url,
  posted_at,
  collected_at,
  metrics,
  raw_payload,
  content_hash,
)
```

Use `social_items` collection, not platform-specific one-off collections.

## Collection: social_items

Canonical normalized items. One row per review/comment.

```txt
_id                ObjectId
platform           string       "google_play" | "app_store" | "youtube"
source_type        string       "app_review" | "comment"
source_id          string       platform-specific unique ID
parent_source_id   string|null  video_id, media_id, tweet_id
conversation_id    string|null  thread/conversation root
keyword            string|null  search keyword used
target_entity      string|null  "bions", "bni_sekuritas"
author_id          string|null  platform author ID
author_username    string|null  platform username
author_display_name string|null display name
text               string       review/comment body
language           string|null  detected language
source_url         string|null  direct link to source
posted_at          string|datetime  when posted (ISO format, may have timezone offset)
collected_at       datetime     when collected
metrics            object       platform-specific (rating, thumbs_up, like_count, etc.)
raw_payload        object       full platform response for audit
content_hash       string       dedupe hash of normalized text
```

Dedupe: `platform + source_type + source_id` (primary), `platform + source_type + content_hash + parent_source_id` (fallback).

## Collection: collection_checkpoints

Backfill window status. One row per platform/date-window.

```txt
_id                ObjectId
platform           string       "google_play" | "app_store" | "youtube"
windowStart        datetime     ISO window start
windowEnd          datetime     ISO window end
status             string       "complete" | "partial"
collectedCount     int          items fetched from API
insertedCount      int          items written to social_items
errorMessage       string|null  error if stopped
createdAt          datetime     first attempt
completedAt        datetime|null completion timestamp
```

Unique index: `platform + windowStart + windowEnd`.

Behavior:
- complete old windows → skip API call on rerun
- partial windows → resume from last checkpoint
- recent overlap (7d) → re-collect to catch late reviews
- `--refetch-existing-windows` overrides all checkpoints

## Collection: collection_runs

Per-run audit trail. One row per collector run.

```txt
_id                ObjectId
platform           string       adapter platform name
status             string       "running" | "completed" | "error"
startedAt          datetime     run start
finishedAt         datetime|null run end
collectedCount     int          items returned by adapter
writtenCount       int          items persisted to social_items
errorCount         int          adapter errors during run
keywords           list         keywords used in this run
```

## Collection: collector_providers

Adapter registry + health. One row per provider, seeded in mongo-init.js.

```txt
_id                string       provider identifier (e.g. "provider_google_play_reviews")
platform           string       "google_play" | "app_store" | "youtube" | ...
library            string       package used
adapterClass       string       Python class name
accessType         string       "official_api" | "unofficial_api" | "rss" | "automation"
costTier           string       "free" | "paid"
riskLevel          string       "low" | "medium" | "high"
isFree             bool         no env/keys needed
isEnvRequired      bool         needs env vars
isRisky            bool         tos/automation risk
needsBrowser       bool         requires browser/playwright
isActive           bool         enabled in pipeline
lastHealthStatus   string|null  "ok" | "error"
lastHealthCheck    datetime|null last health check timestamp
updatedAt          datetime     last update
```

## Collection: keywords

Search keyword registry. One row per keyword.

```txt
_id                ObjectId
keyword            string       search term
targetEntity       string       entity to associate results with
createdAt          datetime     when added
isActive           bool         whether to collect on
```

## Collection: schedules

Cron schedule definitions. Scheduler reads active schedules from DB.

```txt
_id                string       schedule identifier
name               string       human-readable name
isActive           bool         whether scheduler should run this
timezone           string       IANA timezone (e.g. "Asia/Jakarta")
cron               object       { hour, minute }
priority           int          lower = higher priority
createdAt          datetime
updatedAt          datetime
```

## Collection: sentiment_jobs

Sentiment analysis run metadata. One row per run.

```txt
_id                ObjectId
status             string       "running" | "completed" | "error"
method             string       "rule_based" | future model names
modelVersion       string       "rules-v0.1" | version string
totalItems         int          items to process
processedItems     int          successfully classified
errorItems         int          failed classifications
startedAt          datetime
finishedAt         datetime|null
errors             list|null    error messages if any
```

## Collection: sentiment_results

Classification output. One row per item per classification.

```txt
_id                ObjectId
socialItemId       string       references social_items._id
label              string       "positive" | "negative" | "neutral" | "mixed"
score              float        sentiment score
confidence         float        model confidence
topics             list         extracted topics
method             string       classification method used
modelVersion       string       model version used
cleanedText        string       preprocessed text
collectionRunId    string|null  references collection_runs._id (if from live collect)
createdAt          datetime
```

## Collection: exports

CSV/XLSX export log.

```txt
_id                ObjectId
format             string       "csv" | "xlsx"
filePath           string       relative path to exported file
rowCount           int          rows in export
requestedBy        string|null  user or "system"
status             string       "completed" | "error"
createdAt          datetime
```

## Collection: dashboard_views

Saved dashboard filter/chart configurations.

```txt
_id                ObjectId
name               string       unique view name
config             object       filters, charts, layout
createdBy          string       user or "system"
isDefault          bool         default view
createdAt          datetime
updatedAt          datetime
```

## Collection: dashboard_actions

User action audit trail.

```txt
_id                ObjectId
actionType         string       "view" | "favorite" | "comment" | "export"
socialItemId       string|null  references social_items._id
userId             string|null  user or "system"
metadata           object|null  extra context
createdAt          datetime
```

## Collection: system_events

Pipeline event log.

```txt
_id                ObjectId
level              string       "info" | "warn" | "error"
component          string       pipeline module name
message            string       event description
providerId         string|null  adapter provider ID if relevant
metadata           object|null  extra context
createdAt          datetime
```

## Collection: labeled_examples

Manual label annotations for training/evaluation.

```txt
_id                ObjectId
socialItemId       string       references social_items._id
label              string       annotated sentiment label
topics             list         annotated topics
annotator          string|null  who labeled
notes              string|null  labeling notes
createdAt          datetime
```

## Collection: model_versions

Active model registry.

```txt
_id                ObjectId
method             string       "rule_based" | future methods
version            string       version identifier
isActive           bool         currently active model
createdAt          datetime
updatedAt          datetime
```
