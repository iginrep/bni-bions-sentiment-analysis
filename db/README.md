# MongoDB Database Design

Database: `bni_bions_sentiment`

MongoDB dipilih karena data sosial media/app review/news bersifat non-relational: tiap platform punya payload, identitas, metrik, pagination, dan struktur komentar yang beda. Prinsip desain: satu canonical layer untuk API/dashboard + simpan raw payload asli untuk replay/reprocess.

## Naming conventions

- Collection: `snake_case` plural-ish.
- App fields: `camelCase` mengikuti existing Python scaffold.
- Dates: BSON Date UTC. UI render timezone `Asia/Jakarta`.
- Sentiment label exact: `positive`, `neutral`, `negative`.
- Raw platform data wajib disimpan di `rawPayload` atau `rawHtml`.
- Risky collectors disabled by default.

## ER-ish overview

```txt
collector_providers 1 ── n collection_runs
keywords            1 ── n collection_runs
keywords            1 ── n social_items
collection_runs     1 ── n social_items
social_items        1 ── n sentiment_results
social_items        1 ── n dashboard_actions
exports             n ── 1 users/requester optional
schedules           1 ── n collection_runs
```

Core collections:

```txt
collector_providers
keywords
schedules
collection_runs
social_items
sentiment_jobs
sentiment_results
exports
dashboard_views
dashboard_actions
system_events
```

Optional later:

```txt
users
api_tokens
annotation_tasks
labeled_examples
model_versions
```

---

## 1. `collector_providers`

Registry provider/adapter aktual. Dipakai API admin, scheduler, health dashboard.

```json
{
  "_id": "provider_google_play_reviews",
  "platform": "google_play",
  "providerName": "google-play-scraper",
  "adapterClass": "GooglePlayAdapter",
  "sourceTypes": ["app_review"],
  "accessMode": "unofficial_api",
  "costLevel": "free",
  "riskLevel": "medium",
  "enabledByDefault": true,
  "isEnabled": true,
  "requiresAuth": false,
  "requiresBrowser": false,
  "requiresApiKey": false,
  "configSchema": {
    "appId": "string",
    "country": "string",
    "language": "string"
  },
  "rateLimit": {
    "requestsPerMinute": 10,
    "burst": 2,
    "backoffSeconds": 60
  },
  "health": {
    "status": "working",
    "lastCheckedAt": "2026-06-21T14:00:00Z",
    "lastSuccessAt": "2026-06-21T14:00:00Z",
    "lastError": null
  },
  "notes": "cheap MVP source for BIONS app reviews",
  "createdAt": "2026-06-21T00:00:00Z",
  "updatedAt": "2026-06-21T00:00:00Z"
}
```

Indexes:

```js
db.collector_providers.createIndex({ platform: 1, providerName: 1 }, { unique: true })
db.collector_providers.createIndex({ isEnabled: 1, riskLevel: 1 })
db.collector_providers.createIndex({ "health.status": 1, "health.lastCheckedAt": -1 })
```

Seed providers:

```txt
google_play: google-play-scraper, unofficial_api, free, medium, enabled
app_store: itunes-rss-json, rss, free, low, enabled
youtube: youtube-data-api-v3, official_api, free quota, low, enabled after API key
news: google-news-rss, rss, free, low, enabled
news: bing-news-rss, rss, free, low, enabled
stockbit: playwright, automation, free, high, disabled
x: twscrape, unofficial_api, free, high, disabled
instagram: instaloader, unofficial_api, free, high, disabled
threads: threads-api-official, official_api, free/paid, medium, disabled
tiktok: TikTokApi, unofficial_api, free, high, disabled
```

---

## 2. `keywords`

Target brand/query/entity. Scheduler membaca dari sini.

```json
{
  "_id": "kw_bni_google_play",
  "keyword": "BNI",
  "normalizedKeyword": "bni",
  "targetEntity": "bni",
  "entityType": "brand",
  "platform": "google_play",
  "sourceType": "app_review",
  "providerId": "provider_google_play_reviews",
  "queryConfig": {
    "appId": "id.bni.wondr",
    "country": "id",
    "language": "id",
    "sort": "newest"
  },
  "isActive": true,
  "priority": 100,
  "createdAt": "2026-06-21T00:00:00Z",
  "updatedAt": "2026-06-21T00:00:00Z"
}
```

Indexes:

```js
db.keywords.createIndex({ platform: 1, targetEntity: 1, isActive: 1 })
db.keywords.createIndex({ providerId: 1, isActive: 1, priority: -1 })
db.keywords.createIndex({ keyword: 1, platform: 1, sourceType: 1 }, { unique: true })
db.keywords.createIndex({ normalizedKeyword: "text", targetEntity: "text" })
```

Seed keywords:

```txt
BNI
BNI Sekuritas
BIONS
wondr by BNI
BBNI
BIONS error
BIONS login
BIONS lemot
```

---

## 3. `schedules`

User-configured collection schedule dari dashboard Keyword & Schedule Manager.

```json
{
  "_id": "schedule_default_bni_daily",
  "name": "Default BNI monitoring",
  "timezone": "Asia/Jakarta",
  "cron": "0 8,18 * * *",
  "runTimesLocal": ["08:00", "18:00"],
  "keywordIds": ["kw_bni_google_play", "kw_bni_news"],
  "providerIds": ["provider_google_play_reviews", "provider_google_news_rss"],
  "isActive": true,
  "maxItemsPerRun": 200,
  "createdBy": "system",
  "createdAt": "2026-06-21T00:00:00Z",
  "updatedAt": "2026-06-21T00:00:00Z"
}
```

Indexes:

```js
db.schedules.createIndex({ isActive: 1, timezone: 1 })
db.schedules.createIndex({ keywordIds: 1 })
db.schedules.createIndex({ providerIds: 1 })
```

---

## 4. `collection_runs`

Audit setiap collector execution. Dipakai operational dashboard dan debugging.

```json
{
  "_id": "run_20260621_080000_google_play_bni",
  "scheduleId": "schedule_default_bni_daily",
  "providerId": "provider_google_play_reviews",
  "keywordId": "kw_bni_google_play",
  "platform": "google_play",
  "sourceType": "app_review",
  "triggerType": "scheduled",
  "status": "success",
  "cursorBefore": {
    "lastSeenSourceId": "gp_123",
    "lastCollectedAt": "2026-06-20T18:00:00Z"
  },
  "cursorAfter": {
    "lastSeenSourceId": "gp_456",
    "lastCollectedAt": "2026-06-21T08:00:00Z"
  },
  "stats": {
    "fetched": 120,
    "inserted": 95,
    "updated": 3,
    "duplicates": 22,
    "failed": 0,
    "sentimentQueued": 98
  },
  "requestMeta": {
    "query": "BNI",
    "limit": 200,
    "country": "id"
  },
  "error": null,
  "startedAt": "2026-06-21T01:00:00Z",
  "finishedAt": "2026-06-21T01:00:12Z",
  "durationMs": 12000
}
```

Indexes:

```js
db.collection_runs.createIndex({ platform: 1, startedAt: -1 })
db.collection_runs.createIndex({ providerId: 1, startedAt: -1 })
db.collection_runs.createIndex({ keywordId: 1, startedAt: -1 })
db.collection_runs.createIndex({ status: 1, startedAt: -1 })
db.collection_runs.createIndex({ scheduleId: 1, startedAt: -1 })
```

---

## 5. `social_items`

Collection utama. Satu dokumen per item mentah yang sudah dinormalisasi: review, post, comment, reply, tweet, news article.

```json
{
  "_id": "google_play:app_review:review_abc123",
  "platform": "google_play",
  "providerId": "provider_google_play_reviews",
  "collectionRunId": "run_20260621_080000_google_play_bni",
  "sourceType": "app_review",
  "sourceId": "review_abc123",
  "parentSourceId": null,
  "conversationId": "id.bni.wondr",
  "threadDepth": 0,
  "sourceUrl": "https://play.google.com/store/apps/details?id=id.bni.wondr",
  "keywordId": "kw_bni_google_play",
  "keyword": "BNI",
  "targetEntity": "bni",
  "matchedTerms": ["BNI"],
  "author": {
    "id": null,
    "username": null,
    "displayName": "Sample User",
    "profileUrl": null,
    "isVerified": null,
    "followerCount": null
  },
  "content": {
    "title": null,
    "text": "Aplikasi BNI sering error saat login.",
    "cleanedText": "aplikasi bni sering error saat login",
    "language": "id",
    "isSpam": false,
    "spamReason": null,
    "contentHash": "sha256:..."
  },
  "metrics": {
    "rating": 1,
    "likeCount": null,
    "thumbsUpCount": 12,
    "replyCount": 0,
    "shareCount": null,
    "viewCount": null,
    "quoteCount": null
  },
  "platformFields": {
    "appId": "id.bni.wondr",
    "appVersion": "1.2.3",
    "reviewCreatedVersion": "1.2.2",
    "developerReply": null,
    "country": "id"
  },
  "sentiment": {
    "label": "negative",
    "score": -0.82,
    "confidence": 0.91,
    "method": "rule_based",
    "modelVersion": "rules-v0.1",
    "topics": ["login", "app_error"],
    "explanation": "contains error and login complaint",
    "analyzedAt": "2026-06-21T01:00:15Z",
    "resultId": "sent_google_play_review_abc123_rules_v01"
  },
  "processing": {
    "collectStatus": "collected",
    "analysisStatus": "analyzed",
    "exportStatus": "ready",
    "lastError": null,
    "retryCount": 0
  },
  "collectionMethod": "unofficial_api",
  "accessRisk": "medium",
  "collectorVersion": "google-play-scraper@1.2.x",
  "rawPayload": {
    "reviewId": "review_abc123",
    "score": 1
  },
  "rawHtml": null,
  "postedAt": "2026-06-20T14:10:00Z",
  "collectedAt": "2026-06-21T01:00:12Z",
  "updatedAt": "2026-06-21T01:00:15Z"
}
```

Indexes:

```js
// reliable platform ids
db.social_items.createIndex(
  { platform: 1, sourceType: 1, sourceId: 1 },
  { unique: true, partialFilterExpression: { sourceId: { $exists: true, $ne: null } } }
)

// fallback dedupe when source id unreliable
db.social_items.createIndex(
  { platform: 1, sourceType: 1, "content.contentHash": 1, parentSourceId: 1 },
  { unique: true, partialFilterExpression: { "content.contentHash": { $exists: true } } }
)

// dashboard filters
db.social_items.createIndex({ targetEntity: 1, postedAt: -1 })
db.social_items.createIndex({ platform: 1, postedAt: -1 })
db.social_items.createIndex({ sourceType: 1, postedAt: -1 })
db.social_items.createIndex({ keywordId: 1, collectedAt: -1 })
db.social_items.createIndex({ "sentiment.label": 1, postedAt: -1 })
db.social_items.createIndex({ "sentiment.topics": 1, postedAt: -1 })
db.social_items.createIndex({ "processing.analysisStatus": 1, collectedAt: 1 })
db.social_items.createIndex({ "metrics.rating": 1, postedAt: -1 })
db.social_items.createIndex({ conversationId: 1, postedAt: 1 })
db.social_items.createIndex({ "content.text": "text", "content.cleanedText": "text" })
```

Dashboard query examples:

```js
// sentiment trend by day
db.social_items.aggregate([
  { $match: { targetEntity: "bni", postedAt: { $gte: ISODate("2026-06-01") } } },
  { $group: {
    _id: {
      day: { $dateTrunc: { date: "$postedAt", unit: "day", timezone: "Asia/Jakarta" } },
      label: "$sentiment.label"
    },
    count: { $sum: 1 }
  }},
  { $sort: { "_id.day": 1 } }
])

// recent negative complaints
db.social_items.find({
  targetEntity: "bni",
  "sentiment.label": "negative"
}).sort({ postedAt: -1 }).limit(50)
```

---

## 6. `sentiment_jobs`

Queue/job audit untuk analysis pipeline. Bisa dipakai sebelum Celery/RQ; MVP bisa poll Mongo.

```json
{
  "_id": "sent_job_20260621_080015_batch_001",
  "status": "completed",
  "method": "rule_based",
  "modelVersion": "rules-v0.1",
  "inputFilter": {
    "processing.analysisStatus": "pending",
    "platform": "google_play"
  },
  "stats": {
    "queued": 98,
    "processed": 98,
    "failed": 0
  },
  "startedAt": "2026-06-21T01:00:15Z",
  "finishedAt": "2026-06-21T01:00:19Z",
  "error": null
}
```

Indexes:

```js
db.sentiment_jobs.createIndex({ status: 1, startedAt: -1 })
db.sentiment_jobs.createIndex({ method: 1, modelVersion: 1, startedAt: -1 })
```

---

## 7. `sentiment_results`

Versioned sentiment history. `social_items.sentiment` menyimpan latest result untuk dashboard cepat; collection ini menyimpan audit/model comparison.

```json
{
  "_id": "sent_google_play_review_abc123_rules_v01",
  "socialItemId": "google_play:app_review:review_abc123",
  "sentimentJobId": "sent_job_20260621_080015_batch_001",
  "label": "negative",
  "score": -0.82,
  "confidence": 0.91,
  "method": "rule_based",
  "modelVersion": "rules-v0.1",
  "topics": ["login", "app_error"],
  "explanation": "contains error and login complaint",
  "inputTextHash": "sha256:...",
  "createdAt": "2026-06-21T01:00:15Z"
}
```

Indexes:

```js
db.sentiment_results.createIndex({ socialItemId: 1, createdAt: -1 })
db.sentiment_results.createIndex({ label: 1, createdAt: -1 })
db.sentiment_results.createIndex({ method: 1, modelVersion: 1, createdAt: -1 })
db.sentiment_results.createIndex({ topics: 1, createdAt: -1 })
```

---

## 8. `exports`

Async export/report jobs dari dashboard/API.

```json
{
  "_id": "export_20260621_090000_bni_negative",
  "type": "csv",
  "status": "success",
  "requestedBy": "system",
  "filters": {
    "targetEntity": "bni",
    "platforms": ["google_play", "app_store", "youtube"],
    "sourceTypes": ["app_review", "comment"],
    "sentimentLabels": ["negative"],
    "topics": ["login", "app_error"],
    "from": "2026-06-01T00:00:00Z",
    "to": "2026-06-21T23:59:59Z"
  },
  "columns": ["postedAt", "platform", "sourceType", "keyword", "text", "sentiment.label", "sentiment.score", "sourceUrl"],
  "filePath": "data/exports/bni_negative_20260621.csv",
  "downloadUrl": "/api/exports/export_20260621_090000_bni_negative/download",
  "rowCount": 250,
  "error": null,
  "createdAt": "2026-06-21T02:00:00Z",
  "finishedAt": "2026-06-21T02:00:03Z"
}
```

Indexes:

```js
db.exports.createIndex({ createdAt: -1 })
db.exports.createIndex({ status: 1, createdAt: -1 })
db.exports.createIndex({ requestedBy: 1, createdAt: -1 })
```

---

## 9. `dashboard_views`

Saved filters/views untuk dashboard.

```json
{
  "_id": "view_bni_negative_complaints",
  "name": "BNI Negative Complaints",
  "description": "Recent negative complaints across app stores and social sources",
  "filters": {
    "targetEntity": "bni",
    "platforms": ["google_play", "app_store", "youtube", "news"],
    "sentimentLabels": ["negative"],
    "dateRange": "last_30_days"
  },
  "widgets": [
    { "type": "sentiment_trend", "position": 1 },
    { "type": "platform_breakdown", "position": 2 },
    { "type": "recent_comments", "position": 3 }
  ],
  "createdBy": "system",
  "isDefault": true,
  "createdAt": "2026-06-21T00:00:00Z",
  "updatedAt": "2026-06-21T00:00:00Z"
}
```

Indexes:

```js
db.dashboard_views.createIndex({ createdBy: 1, isDefault: -1 })
db.dashboard_views.createIndex({ name: 1 }, { unique: true })
```

---

## 10. `dashboard_actions`

Audit UI actions: clicked source URL, exported report, marked spam, corrected sentiment.

```json
{
  "_id": "act_20260621_091000_open_source",
  "actionType": "open_source",
  "socialItemId": "google_play:app_review:review_abc123",
  "userId": "local_user",
  "payload": {
    "sourceUrl": "https://play.google.com/store/apps/details?id=id.bni.wondr"
  },
  "createdAt": "2026-06-21T02:10:00Z"
}
```

Indexes:

```js
db.dashboard_actions.createIndex({ socialItemId: 1, createdAt: -1 })
db.dashboard_actions.createIndex({ actionType: 1, createdAt: -1 })
db.dashboard_actions.createIndex({ userId: 1, createdAt: -1 })
```

---

## 11. `system_events`

Structured logs for collector/API/scheduler errors visible in admin dashboard.

```json
{
  "_id": "evt_20260621_stockbit_captcha",
  "level": "warning",
  "component": "collector",
  "providerId": "provider_stockbit_playwright",
  "collectionRunId": "run_20260621_stockbit_bni",
  "message": "Stockbit captcha detected; collector paused",
  "details": {
    "statusCode": 429,
    "screenshotPath": "data/raw/stockbit/captcha_20260621.png"
  },
  "createdAt": "2026-06-21T01:30:00Z"
}
```

Indexes:

```js
db.system_events.createIndex({ level: 1, createdAt: -1 })
db.system_events.createIndex({ component: 1, createdAt: -1 })
db.system_events.createIndex({ providerId: 1, createdAt: -1 })
```

---

## Optional later collections

### `labeled_examples`

Human labels for model improvement/evaluation.

```json
{
  "_id": "label_google_play_review_abc123_user1",
  "socialItemId": "google_play:app_review:review_abc123",
  "label": "negative",
  "topics": ["login", "app_error"],
  "annotator": "user1",
  "notes": "clear login complaint",
  "createdAt": "2026-06-21T03:00:00Z"
}
```

### `model_versions`

Model registry for rule-based, IndoBERT, LLM classifier.

```json
{
  "_id": "model_rules_v0_1",
  "method": "rule_based",
  "version": "rules-v0.1",
  "labels": ["positive", "neutral", "negative"],
  "topics": ["login", "app_error", "order_execution", "performance_speed", "customer_service"],
  "metrics": {
    "accuracy": null,
    "macroF1": null
  },
  "isActive": true,
  "createdAt": "2026-06-21T00:00:00Z"
}
```

---

## API coverage map

```txt
GET  /health                         system_events + db ping
GET  /providers                      collector_providers
PATCH /providers/{id}                collector_providers.isEnabled/config/rateLimit
GET  /keywords                       keywords
POST /keywords                       keywords
PATCH /keywords/{id}                 keywords
GET  /schedules                      schedules
POST /schedules                      schedules
POST /collect/run                    collection_runs + social_items
GET  /collection-runs                collection_runs
GET  /comments                       social_items
GET  /comments/{id}                  social_items
GET  /sentiment/summary              social_items aggregate
GET  /sentiment/trend                social_items aggregate
POST /sentiment/analyze              sentiment_jobs + sentiment_results + social_items.sentiment
GET  /exports                        exports
POST /exports                        exports async job
GET  /exports/{id}/download          export file
POST /dashboard/actions              dashboard_actions
GET  /system-events                  system_events
```

---

## Dashboard widgets supported

```txt
sentiment_summary_cards      social_items aggregate by sentiment.label
sentiment_trend_chart        social_items date histogram by label
platform_breakdown           social_items aggregate by platform/sourceType
recent_comments_table        social_items find/sort/paginate
negative_complaints_table    social_items filter label=negative
keyword_manager              keywords CRUD
schedule_manager             schedules CRUD
provider_health              collector_providers + collection_runs
export_history               exports
source_click_tracking        dashboard_actions
system_alerts                system_events
```

---

## Data retention

Suggested MVP:

```txt
social_items: keep indefinitely while volume small
rawPayload/rawHtml: keep 180 days, then archive/compress if needed
collection_runs: keep 365 days
system_events: keep 180 days
exports: keep files 30-90 days, metadata 365 days
sentiment_results: keep indefinitely for model comparison
```

TTL indexes if needed later:

```js
db.system_events.createIndex({ createdAt: 1 }, { expireAfterSeconds: 15552000 })
db.exports.createIndex({ finishedAt: 1 }, { expireAfterSeconds: 7776000 })
```

---

## Required invariants

1. `social_items.platform + sourceType + sourceId` unique when sourceId exists.
2. Fallback dedupe uses `platform + sourceType + contentHash + parentSourceId`.
3. Dashboard never reads Mongo directly; only API.
4. Sentiment engine stateless: `text -> label/score/confidence/topics`.
5. Latest sentiment embedded in `social_items.sentiment`.
6. Historical sentiment saved in `sentiment_results`.
7. Raw source payload saved for replay/debug.
8. High-risk collectors disabled until explicitly enabled.
9. No secrets/cookies/tokens in database docs or git. Store only secret references, never values.
