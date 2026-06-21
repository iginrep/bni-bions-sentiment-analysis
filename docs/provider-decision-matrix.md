# Provider Decision Matrix

Goal: cheapest-first collectors for BNI Sekuritas/BIONS sentiment monitoring. Use free/unofficial/public collectors for MVP. Upgrade to official API or vendor after schema, dashboard, labels, and business value stabilize.

## Decision rule

1. Prefer public/free source with strong signal.
2. Prefer library over manual scraper if library is active enough.
3. Prefer manual Playwright only when no usable public package/API exists.
4. Keep high-risk collectors disabled by default.
5. Store raw payload/HTML for replay.
6. Promote to official API/vendor when reliability, compliance, or scale matters.

## MVP provider matrix

| Source | MVP provider | Type | Package/tool | Auth | Cost | Risk | Default | Why |
|---|---|---|---|---|---|---|---|---|
| Google Play | google-play-scraper Python | unofficial API/scraper | `google-play-scraper` | none | free | medium | on | highest BIONS app complaint signal |
| Apple App Store | Apple RSS JSON | public RSS/API | `httpx` | none | free | low | on | stable cheap iOS review source |
| YouTube | YouTube Data API v3 | official API | `google-api-python-client` | API key | free quota | low | on | official free enough, reliable comments |
| Stockbit | Playwright browser scraper | automation | `playwright` | dedicated account/session | free | high | off | no public official API, finance sentiment high value |
| X/Twitter | twscrape | unofficial API/scraper | `twscrape` | throwaway X accounts | free | high | off | cheap but fragile/account-risk; upgrade later |
| Instagram | Instaloader | unofficial scraper | `instaloader` | optional/dedicated account | free | high | off | cheap for known posts; broad public monitoring fragile |
| Threads | official Threads API if scope fits, else Apify | official/vendor | Meta API / Apify | Meta app or Apify key | free/paid | medium | off | unofficial libs fragile; public search limited |
| TikTok | TikTokApi | unofficial scraper | `TikTokApi` + Playwright | no login usually, token/browser context | free | high | off | cheapest prototype; frequent breakage |
| News/RSS | RSS + simple extraction | public web | `httpx`, feedparser/readability later | none | free | low-medium | on | market/context enrichment |
| Telegram public | Telethon | official-ish client API | `telethon` | Telegram API id/hash + account | free | medium | off | useful if known public saham channels exist |

## Platform notes

### Google Play

Recommended MVP:

```bash
pip install google-play-scraper
```

Use for BIONS Android reviews. Store:

```txt
reviewId, userName, content, score, thumbsUpCount, reviewCreatedVersion, at, replyContent, repliedAt, appVersion
```

Why not manual scraper first: package already handles Play endpoints/pagination. Manual scraper adds maintenance with little upside.

Upgrade path: Google Play Developer API if BNI-owned Play Console access needed for official review management/replies.

### Apple App Store

Recommended MVP: direct RSS JSON via `httpx`.

Endpoint pattern:

```txt
https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json
```

Store:

```txt
review_id, author, title, content, rating, updated, version, country, app_id
```

Why not package first: RSS is simple, stable, no dependency needed.

Upgrade path: App Store Connect API if BNI-owned account access exists.

### YouTube

Recommended MVP: official YouTube Data API v3.

```bash
pip install google-api-python-client
```

Use API key. Free quota usually enough for MVP. Store:

```txt
video_id, comment_id, parent_id, authorDisplayName, authorChannelId, textOriginal, likeCount, publishedAt, updatedAt, totalReplyCount
```

Fallback if no Google Cloud setup: `youtube-comment-downloader`, but mark risk medium and keep swappable.

### Stockbit

Recommended MVP: manual Playwright scraper, disabled by default.

```bash
pip install playwright beautifulsoup4
python -m playwright install chromium
```

Use a dedicated Stockbit account. First run manual login with persistent browser profile. Scrape BBNI symbol/community pages and search terms:

```txt
BBNI
BNI Sekuritas
BIONS
BIONS Mobile
BNI sekuritas error
aplikasi BIONS
```

Implementation rules:

```txt
low rate only
persistent session profile
save raw_html/raw_json_blob
dedupe by post_id if visible else hash(author,timestamp,text)
stop on captcha/401/403/429
selectors in config, not hardcoded in parser body
screenshots on parse failure
```

Do not start with mobile API reverse engineering. That has highest ToS/security risk.

Upgrade path: official partnership or vendor if Stockbit coverage exists.

### X/Twitter

Recommended MVP: defer unless needed. If needed cheap:

```bash
pip install twscrape
```

Use dedicated throwaway accounts/cookies, low rate. Store:

```txt
tweet_id, conversation_id, author_id, username, text, created_at, lang, url, reply_count, retweet_count, like_count, quote_count, raw_payload
```

Risk: high breakage/account ban. Do not use personal/corporate account.

Upgrade path: X API v2 paid via Tweepy/twitter-api-v2, or vendor such as Apify/Bright Data if API cost/limits bad.

### Instagram

Recommended MVP only for known post/account targets:

```bash
pip install instaloader
```

Use dedicated account session if comments require login. Store:

```txt
post_shortcode, comment_id, parent_id, username, text, created_at, likes, post_url, raw_payload
```

Do not promise broad keyword monitoring from Instagram cheaply. Public search/hashtag data is fragile.

Upgrade path: Instagram Graph API for owned/authorized Business/Creator accounts, or vendor.

### Threads

Recommended MVP: official Threads API if monitoring owned/authorized posts fits. If broad public monitoring required, use Apify actor before custom scraper.

Avoid unofficial reverse-engineered libraries as primary. Ecosystem is less stable.

Upgrade path: official Threads API or vendor.

### TikTok

Recommended cheap prototype:

```bash
pip install TikTokApi playwright
python -m playwright install chromium
```

Use for public videos/comments/search where available. Store:

```txt
video_id, comment_id, parent_id, author, text, create_time, like_count, reply_count, video_url, raw_payload
```

Risk: high. Expect token/proxy/browser breakage.

Upgrade path: TikAPI/Apify for production-lite, TikTok Research API if eligible.

## Vendor bakeoff later

Only after MVP proves value, run a vendor comparison for 2-4 weeks.

Vendors to check:

```txt
NoLimit
Drone Emprit
Kazee
Dataxet
Brand24
Talkwalker
Meltwater
Apify
Bright Data
TikAPI
```

Ask each:

```txt
Stockbit coverage?
X/Instagram/TikTok/news/forum/app review coverage?
API or scheduled export?
historical backfill?
raw text access?
sentiment confidence?
Bahasa Indonesia finance slang quality?
pricing by keyword/mention/seat?
data retention/export rights?
```

## Implementation order

1. Google Play reviews.
2. Apple App Store reviews.
3. YouTube official comments.
4. News/RSS context.
5. Stockbit Playwright PoC.
6. X/Twitter only if demand justifies high risk.
7. Instagram/TikTok/Threads only after exact target URLs/accounts/hashtags are defined.

## Final recommendation

Start with app reviews + YouTube + news because signal is strong and cost/risk low. Add Stockbit as a controlled Playwright PoC because domain relevance is high but risk is high. Delay X/Instagram/TikTok/Threads broad monitoring until MVP validates dashboard/value or vendor budget exists.
