# MongoDB Database Design

Database: `bni_bions_sentiment`

MongoDB dipilih karena payload sosial media beda-beda per platform. Simpan dokumen canonical + raw payload asli.

## Collections

### `keywords`

Keyword target untuk collector.

```json
{
  "_id": "kw_bions_youtube",
  "keyword": "bions",
  "targetEntity": "bions",
  "platform": "youtube",
  "isActive": true,
  "createdAt": "2026-06-21T00:00:00Z",
  "updatedAt": "2026-06-21T00:00:00Z"
}
```

Indexes:

```js
db.keywords.createIndex({ platform: 1, targetEntity: 1, isActive: 1 })
db.keywords.createIndex({ keyword: 1, platform: 1 }, { unique: true })
```

### `collection_runs`

Audit setiap sesi collect 08:00/18:00/manual.

```json
{
  "_id": "run_20260621_080000_youtube_bions",
  "platform": "youtube",
  "keywordId": "kw_bions_youtube",
  "status": "success",
  "startedAt": "2026-06-21T08:00:00+07:00",
  "finishedAt": "2026-06-21T08:00:12+07:00",
  "stats": {
    "fetched": 120,
    "inserted": 95,
    "duplicates": 25,
    "failed": 0
  },
  "error": null
}
```

Indexes:

```js
db.collection_runs.createIndex({ platform: 1, startedAt: -1 })
db.collection_runs.createIndex({ keywordId: 1, startedAt: -1 })
db.collection_runs.createIndex({ status: 1, startedAt: -1 })
```

### `social_items`

Collection utama. Satu dokumen per tweet/comment/reply/post.

```json
{
  "_id": "youtube:yt_comment_1",
  "platform": "youtube",
  "sourceType": "comment",
  "sourceId": "yt_comment_1",
  "parentSourceId": null,
  "conversationId": "youtube_video_id",
  "keywordId": "kw_bions_youtube",
  "keyword": "bions",
  "targetEntity": "bions",
  "author": {
    "id": "channel_id",
    "username": null,
    "displayName": "Sample User"
  },
  "content": {
    "text": "BIONS sekarang lebih lancar, order cepat.",
    "cleanedText": "bions sekarang lebih lancar order cepat",
    "language": "id",
    "isSpam": false,
    "spamReason": null,
    "contentHash": "sha256"
  },
  "metrics": {
    "likeCount": 3,
    "replyCount": 0,
    "shareCount": null,
    "viewCount": null
  },
  "sentiment": {
    "label": "positive",
    "score": 0.75,
    "confidence": 0.85,
    "method": "rule_based",
    "modelVersion": "rules-v0.1",
    "topics": ["order_execution", "performance_speed"],
    "explanation": "contains lancar, cepat",
    "analyzedAt": "2026-06-21T08:00:15+07:00"
  },
  "sourceUrl": "https://www.youtube.com/watch?v=...&lc=...",
  "postedAt": "2026-06-20T21:10:00Z",
  "collectedAt": "2026-06-21T08:00:12+07:00",
  "updatedAt": "2026-06-21T08:00:15+07:00",
  "rawPayload": {
    "id": "raw platform payload"
  }
}
```

Indexes:

```js
db.social_items.createIndex({ platform: 1, sourceId: 1 }, { unique: true })
db.social_items.createIndex({ targetEntity: 1, postedAt: -1 })
db.social_items.createIndex({ platform: 1, postedAt: -1 })
db.social_items.createIndex({ "sentiment.label": 1, postedAt: -1 })
db.social_items.createIndex({ "sentiment.topics": 1, postedAt: -1 })
db.social_items.createIndex({ keywordId: 1, collectedAt: -1 })
db.social_items.createIndex({ "content.contentHash": 1 })
db.social_items.createIndex({ "content.text": "text", "content.cleanedText": "text" })
```

### `exports`

Report generation history.

```json
{
  "_id": "export_20260621_090000",
  "type": "csv",
  "status": "success",
  "filters": {
    "targetEntity": "bions",
    "platforms": ["youtube", "x"],
    "sentimentLabels": ["negative"],
    "from": "2026-06-01T00:00:00Z",
    "to": "2026-06-21T23:59:59Z"
  },
  "filePath": "data/exports/bions_negative_20260621.csv",
  "rowCount": 250,
  "createdAt": "2026-06-21T09:00:00+07:00"
}
```

Indexes:

```js
db.exports.createIndex({ createdAt: -1 })
db.exports.createIndex({ status: 1, createdAt: -1 })
```

## Why embedded sentiment in `social_items`?

Sentiment is current derived state for dashboard. Simpler reads, fewer joins, fits Mongo. If later need model history, add `sentiment_runs` collection.

## Query patterns

Dashboard trend:

```js
db.social_items.aggregate([
  { $match: { targetEntity: "bions", postedAt: { $gte: ISODate("2026-06-01") } } },
  { $group: {
    _id: { day: { $dateTrunc: { date: "$postedAt", unit: "day" } }, label: "$sentiment.label" },
    count: { $sum: 1 }
  } },
  { $sort: { "_id.day": 1 } }
])
```

Top complaints:

```js
db.social_items.find({
  targetEntity: "bions",
  "sentiment.label": "negative"
}).sort({ postedAt: -1 }).limit(50)
```
