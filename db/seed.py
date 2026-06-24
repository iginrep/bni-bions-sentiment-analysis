from __future__ import annotations
import sys
from datetime import datetime, timezone
import pymongo
from pymongo import MongoClient, TEXT, ASCENDING, DESCENDING


def seed_db():
    uri = "mongodb://localhost:27017"
    db_name = "bni_bions_sentiment"
    
    print(f"Connecting to MongoDB at {uri}...")
    client = MongoClient(uri, serverSelectionTimeoutMS=2000)
    try:
        client.server_info()
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        sys.exit(1)
        
    db = client[db_name]
    
    collections = [
        'collector_providers',
        'keywords',
        'schedules',
        'collection_runs',
        'social_items',
        'sentiment_jobs',
        'sentiment_results',
        'exports',
        'dashboard_views',
        'dashboard_actions',
        'system_events',
        'labeled_examples',
        'model_versions'
    ]
    
    existing_collections = db.list_collection_names()
    
    # Drop existing collections if they have duplicate data causing index failures
    collections_to_reset = ['social_items', 'collection_runs']
    for name in collections_to_reset:
        if name in existing_collections:
            db.drop_collection(name)
            print(f"Dropped existing collection to reset indexes: {name}")
            existing_collections.remove(name)

    for name in collections:
        if name not in existing_collections:
            db.create_collection(name)
            print(f"Created collection: {name}")
        else:
            print(f"Collection already exists: {name}")
            
    print("\nCreating indexes...")
    
    # collector_providers
    db.collector_providers.create_index([("platform", ASCENDING), ("providerName", ASCENDING)], unique=True)
    db.collector_providers.create_index([("isEnabled", ASCENDING), ("riskLevel", ASCENDING)])
    db.collector_providers.create_index([("health.status", ASCENDING), ("health.lastCheckedAt", DESCENDING)])
    
    # keywords
    db.keywords.create_index([("platform", ASCENDING), ("targetEntity", ASCENDING), ("isActive", ASCENDING)])
    db.keywords.create_index([("providerId", ASCENDING), ("isActive", ASCENDING), ("priority", DESCENDING)])
    db.keywords.create_index([("keyword", ASCENDING), ("platform", ASCENDING), ("sourceType", ASCENDING)], unique=True)
    db.keywords.create_index([("normalizedKeyword", TEXT), ("targetEntity", TEXT)])
    
    # schedules
    db.schedules.create_index([("isActive", ASCENDING), ("timezone", ASCENDING)])
    db.schedules.create_index([("keywordIds", ASCENDING)])
    db.schedules.create_index([("providerIds", ASCENDING)])
    
    # collection_runs
    db.collection_runs.create_index([("platform", ASCENDING), ("startedAt", DESCENDING)])
    db.collection_runs.create_index([("providerId", ASCENDING), ("startedAt", DESCENDING)])
    db.collection_runs.create_index([("keywordId", ASCENDING), ("startedAt", DESCENDING)])
    db.collection_runs.create_index([("status", ASCENDING), ("startedAt", DESCENDING)])
    db.collection_runs.create_index([("scheduleId", ASCENDING), ("startedAt", DESCENDING)])
    
    # social_items
    db.social_items.create_index(
        [("platform", ASCENDING), ("sourceType", ASCENDING), ("sourceId", ASCENDING)],
        unique=True,
        partialFilterExpression={"sourceId": {"$type": "string"}}
    )
    db.social_items.create_index(
        [("platform", ASCENDING), ("sourceType", ASCENDING), ("content.contentHash", ASCENDING), ("parentSourceId", ASCENDING)],
        unique=True,
        partialFilterExpression={"content.contentHash": {"$exists": True}}
    )
    db.social_items.create_index([("targetEntity", ASCENDING), ("postedAt", DESCENDING)])
    db.social_items.create_index([("platform", ASCENDING), ("postedAt", DESCENDING)])
    db.social_items.create_index([("sourceType", ASCENDING), ("postedAt", DESCENDING)])
    db.social_items.create_index([("keywordId", ASCENDING), ("collectedAt", DESCENDING)])
    db.social_items.create_index([("sentiment.label", ASCENDING), ("postedAt", DESCENDING)])
    db.social_items.create_index([("sentiment.topics", ASCENDING), ("postedAt", DESCENDING)])
    db.social_items.create_index([("processing.analysisStatus", ASCENDING), ("collectedAt", ASCENDING)])
    db.social_items.create_index([("metrics.rating", ASCENDING), ("postedAt", DESCENDING)])
    db.social_items.create_index([("conversationId", ASCENDING), ("postedAt", ASCENDING)])
    db.social_items.create_index([("content.text", TEXT), ("content.cleanedText", TEXT)], language_override="none")
    
    # sentiment_jobs / results
    db.sentiment_jobs.create_index([("status", ASCENDING), ("startedAt", DESCENDING)])
    db.sentiment_jobs.create_index([("method", ASCENDING), ("modelVersion", ASCENDING), ("startedAt", DESCENDING)])
    db.sentiment_results.create_index([("socialItemId", ASCENDING), ("createdAt", DESCENDING)])
    db.sentiment_results.create_index([("label", ASCENDING), ("createdAt", DESCENDING)])
    db.sentiment_results.create_index([("method", ASCENDING), ("modelVersion", ASCENDING), ("createdAt", DESCENDING)])
    db.sentiment_results.create_index([("topics", ASCENDING), ("createdAt", DESCENDING)])
    
    # exports
    db.exports.create_index([("createdAt", DESCENDING)])
    db.exports.create_index([("status", ASCENDING), ("createdAt", DESCENDING)])
    db.exports.create_index([("requestedBy", ASCENDING), ("createdAt", DESCENDING)])
    
    # dashboard
    db.dashboard_views.create_index([("createdBy", ASCENDING), ("isDefault", DESCENDING)])
    db.dashboard_views.create_index([("name", ASCENDING)], unique=True)
    db.dashboard_actions.create_index([("socialItemId", ASCENDING), ("createdAt", DESCENDING)])
    db.dashboard_actions.create_index([("actionType", ASCENDING), ("createdAt", DESCENDING)])
    db.dashboard_actions.create_index([("userId", ASCENDING), ("createdAt", DESCENDING)])
    
    # system events
    db.system_events.create_index([("level", ASCENDING), ("createdAt", DESCENDING)])
    db.system_events.create_index([("component", ASCENDING), ("createdAt", DESCENDING)])
    db.system_events.create_index([("providerId", ASCENDING), ("createdAt", DESCENDING)])
    
    # optional labels/models
    db.labeled_examples.create_index([("socialItemId", ASCENDING), ("createdAt", DESCENDING)])
    db.labeled_examples.create_index([("label", ASCENDING), ("createdAt", DESCENDING)])
    db.model_versions.create_index([("method", ASCENDING), ("version", ASCENDING)], unique=True)
    db.model_versions.create_index([("isActive", ASCENDING), ("method", ASCENDING)])
    
    print("Indexes created successfully.")
    
    # Seed providers
    print("\nSeeding providers...")
    now = datetime.now(timezone.utc)
    providers = [
        ('provider_google_play_reviews', 'google_play', 'google-play-scraper', 'GooglePlayAdapter', 'unofficial_api', 'free', 'medium', True, False, False, False),
        ('provider_app_store_reviews', 'app_store', 'itunes-rss-json', 'AppStoreAdapter', 'rss', 'free', 'low', True, False, False, False),
        ('provider_youtube_comments', 'youtube', 'youtube-data-api-v3', 'YouTubeAdapter', 'official_api', 'free', 'low', True, False, False, True),
        ('provider_google_news_rss', 'news', 'google-news-rss', 'GoogleNewsRssAdapter', 'rss', 'free', 'low', True, False, False, False),
        ('provider_bing_news_rss', 'news', 'bing-news-rss', 'BingNewsRssAdapter', 'rss', 'free', 'low', True, False, False, False),
        ('provider_stockbit_playwright', 'stockbit', 'playwright', 'StockbitPlaywrightAdapter', 'automation', 'free', 'high', False, True, True, False),
        ('provider_x_twscrape', 'x', 'twscrape', 'XTwScrapeAdapter', 'unofficial_api', 'free', 'high', False, True, False, False),
        ('provider_instagram_instaloader', 'instagram', 'instaloader', 'InstagramInstaloaderAdapter', 'unofficial_api', 'free', 'high', False, True, False, False),
        ('provider_threads_api', 'threads', 'threads-api-official', 'ThreadsApiAdapter', 'official_api', 'free', 'medium', False, True, False, True),
        ('provider_tiktok_api', 'tiktok', 'TikTokApi', 'TikTokApiAdapter', 'unofficial_api', 'free', 'high', False, False, True, False)
    ]
    
    for p in providers:
        db.collector_providers.update_one(
            {"_id": p[0]},
            {"$setOnInsert": {
                "_id": p[0],
                "platform": p[1],
                "providerName": p[2],
                "adapterClass": p[3],
                "sourceTypes": [],
                "accessMode": p[4],
                "costLevel": p[5],
                "riskLevel": p[6],
                "enabledByDefault": p[7],
                "isEnabled": p[7],
                "requiresAuth": p[8],
                "requiresBrowser": p[9],
                "requiresApiKey": p[10],
                "rateLimit": {"requestsPerMinute": 10, "burst": 2, "backoffSeconds": 60},
                "health": {"status": "unknown", "lastCheckedAt": None, "lastSuccessAt": None, "lastError": None},
                "createdAt": now,
                "updatedAt": now
            }},
            upsert=True
        )
    print("Providers seeded.")
    
    # Seed keywords
    print("\nSeeding keywords...")
    keywords = [
        ('kw_bions_google_play', 'BIONS', 'bions', 'product', 'google_play', 'app_review', 'provider_google_play_reviews', {
            'appId': 'id.bions.bnis.android',
            'url': 'https://play.google.com/store/apps/details?id=id.bions.bnis.android&hl=id',
            'country': 'id', 'language': 'id', 'sort': 'newest', 'saveUsername': True
        }),
        ('kw_bions_app_store', 'BIONS', 'bions', 'product', 'app_store', 'app_review', 'provider_app_store_reviews', {
            'appId': '6736508566',
            'url': 'https://apps.apple.com/id/app/bions/id6736508566',
            'country': 'id', 'saveUsername': True
        }),
        ('kw_bni_youtube_channel', 'BNI', 'bni', 'brand', 'youtube', 'comment', 'provider_youtube_comments', {
            'channelHandle': 'BNI1946', 'channelUrl': 'https://www.youtube.com/@BNI1946', 'saveUsername': True
        }),
        ('kw_bni_sekuritas_youtube_channel', 'BNI Sekuritas', 'bni_sekuritas', 'brand', 'youtube', 'comment', 'provider_youtube_comments', {
            'channelHandle': 'bnisekuritas46', 'channelUrl': 'https://www.youtube.com/@bnisekuritas46', 'saveUsername': True
        }),
        ('kw_bni_news', 'BNI', 'bni', 'brand', 'news', 'news_article', 'provider_google_news_rss', {'query': 'BNI OR "BNI Sekuritas" OR BIONS', 'country': 'id'}),
        ('kw_bions_youtube', 'BIONS', 'bions', 'product', 'youtube', 'comment', 'provider_youtube_comments', {'query': 'BIONS BNI Sekuritas', 'saveUsername': True}),
        ('kw_bbni_stockbit', 'BBNI', 'bbni', 'ticker', 'stockbit', 'finance_forum', 'provider_stockbit_playwright', {'symbol': 'BBNI'})
    ]
    
    for k in keywords:
        db.keywords.update_one(
            {"_id": k[0]},
            {"$setOnInsert": {
                "_id": k[0],
                "keyword": k[1],
                "normalizedKeyword": k[2],
                "targetEntity": k[2],
                "entityType": k[3],
                "platform": k[4],
                "sourceType": k[5],
                "providerId": k[6],
                "queryConfig": k[7],
                "isActive": True,
                "priority": 100,
                "createdAt": now,
                "updatedAt": now
            }},
            upsert=True
        )
    print("Keywords seeded.")

    # Seed schedules
    print("\nSeeding schedules...")
    schedules = [
        ('sched_bions_daily_10am', 'Daily BIONS collection at 10 AM WIB', {
            'hour': 10, 'minute': 0
        }, 'Asia/Jakarta', True, 100)
    ]
    
    for s in schedules:
        db.schedules.update_one(
            {"_id": s[0]},
            {"$setOnInsert": {
                "_id": s[0],
                "name": s[1],
                "cron": s[2],
                "timezone": s[3],
                "isActive": s[4],
                "priority": s[5],
                "createdAt": now,
                "updatedAt": now
            }},
            upsert=True
        )
    print("Schedules seeded.")
    print("\nDatabase seeding completed successfully.")


if __name__ == "__main__":
    seed_db()
