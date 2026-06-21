db = db.getSiblingDB('bni_bions_sentiment');

db.createCollection('keywords');
db.createCollection('collection_runs');
db.createCollection('social_items');
db.createCollection('exports');

db.keywords.createIndex({ platform: 1, targetEntity: 1, isActive: 1 });
db.keywords.createIndex({ keyword: 1, platform: 1 }, { unique: true });

db.collection_runs.createIndex({ platform: 1, startedAt: -1 });
db.collection_runs.createIndex({ keywordId: 1, startedAt: -1 });
db.collection_runs.createIndex({ status: 1, startedAt: -1 });

db.social_items.createIndex({ platform: 1, sourceId: 1 }, { unique: true });
db.social_items.createIndex({ targetEntity: 1, postedAt: -1 });
db.social_items.createIndex({ platform: 1, postedAt: -1 });
db.social_items.createIndex({ 'sentiment.label': 1, postedAt: -1 });
db.social_items.createIndex({ 'sentiment.topics': 1, postedAt: -1 });
db.social_items.createIndex({ keywordId: 1, collectedAt: -1 });
db.social_items.createIndex({ 'content.contentHash': 1 });
db.social_items.createIndex({ 'content.text': 'text', 'content.cleanedText': 'text' });

db.exports.createIndex({ createdAt: -1 });
db.exports.createIndex({ status: 1, createdAt: -1 });

db.keywords.updateOne(
  { keyword: 'bions', platform: 'youtube' },
  { $setOnInsert: { keyword: 'bions', targetEntity: 'bions', platform: 'youtube', isActive: true, createdAt: new Date(), updatedAt: new Date() } },
  { upsert: true }
);
