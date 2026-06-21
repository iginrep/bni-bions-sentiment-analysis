# Stockbit + X/Twitter Collection Research — BNI/BIONS

Scope: cheapest-first sentiment collection for Indonesia/BNI Sekuritas/BIONS. No login performed. No behind-auth scraping performed. High-risk collectors default OFF.

## Search universe

Keywords/entities:

```txt
BIONS
BIONS Mobile
BNI Sekuritas
BNISekuritas
BNI sekuritas
BBNI
$BBNI
aplikasi BIONS
BIONS error
BIONS down
BIONS login
BIONS tidak bisa
BIONS lemot
BIONS maintenance
BIONS gagal order
BNI Sekuritas error
```

Exclude/noise candidates:

```txt
BNI bank retail complaints unrelated to securities app
BBNI pure stock-price chatter without BIONS/sekuitas context
English word "bions" false positives
```

## Cheapest-first path

| Priority | Path | Cost | Risk | Auth | Use when | Notes |
|---:|---|---|---|---|---|---|
| 1 | Manual seed URLs + public web checks | free | low | none | initial discovery | Agent can inspect public pages only; low volume; no login. |
| 2 | Stockbit Playwright PoC | free | high | dedicated account/session if approved | Stockbit signal required | Disabled default; human login only; no CAPTCHA bypass. |
| 3 | X public web/manual export | free | medium-high | none/session may be needed | tiny validation | Search visibility limited; brittle. |
| 4 | X unofficial libs (`twscrape`) | free | high | throwaway X accounts | prototype only | Account ban/breakage risk. |
| 5 | Cheap vendors/actors | cheap | medium | vendor key | need scheduled data w/o building scraper | Apify/Bright Data/etc; verify ID coverage. |
| 6 | Official/partner APIs | paid | low-medium | API contract/key | production/SLA/compliance | X API v2 paid; Stockbit partnership/vendor if available. |

## Stockbit

Recommended MVP: Playwright browser automation, OFF by default.

Why: Stockbit has high Indonesian retail-investor signal for `$BBNI` and broker/app complaints, but no obvious public official API for keyword harvesting. Avoid mobile API reverse-engineering.

Libraries/options:

```txt
playwright                 browser automation; preferred over Selenium
beautifulsoup4/lxml         parse rendered/static HTML snapshots
httpx                       only for public static assets/endpoints discovered w/o auth bypass
pydantic                    normalize RawSocialItem
sqlite/postgres/mongo       checkpoint + raw payload store
```

Browser config:

```txt
persistent browser profile path outside repo
headful first-run for human login only if approved
headless after session exists only if stable
rate: very low; e.g. 1 page/search every 30-120s + jitter
stop immediately on CAPTCHA, 401, 403, 429, forced relogin
screenshots + raw_html on parser failure
selectors externalized in config
```

Targets:

```txt
Stockbit symbol page/community for BBNI / $BBNI
Stockbit search for BIONS, BNI Sekuritas, BNI sekuritas error, aplikasi BIONS
Known Stockbit post URLs supplied by analyst
```

Fields to collect:

```txt
platform="stockbit"
source_type: post|comment|reply|symbol_stream|search_result
source_id: visible post/comment id if available; else stable hash
parent_source_id
conversation_id/thread_id
symbol: BBNI if applicable
keyword/query
text
language: likely id/en/mixed
author_username/display_name if visible
author_profile_url if visible
posted_at visible timestamp; preserve raw timestamp text
collected_at
source_url
metrics: likes, comments, replies, reposts if visible
raw_payload: html/json snippet + screenshot path on failures
content_hash: hash(platform, author, posted_at_raw, text)
collection_method="automation"
access_risk="high"
```

Human approval/provisioning:

```txt
Approve Stockbit ToS/legal risk for prototype
Provide dedicated Stockbit account; no personal/corporate primary acct
Human performs login locally in persistent browser profile
Approve allowed keywords/symbols + daily volume cap
Approve retention of raw HTML/screenshots containing public usernames/text
Define stop conditions + escalation contact
Confirm whether production use is allowed or PoC only
```

Agent can discover itself:

```txt
Publicly visible page structure/selectors
Whether pages require login for target searches
Candidate keywords/URLs from public search/web
Parser/checkpoint implementation
Dedupe rules
Backoff/stop logic
```

Risks/caveats:

```txt
Likely ToS restriction on automated access/scraping
Account/session lock, CAPTCHA, IP throttling
Selector/UI changes break parser
Search results may be personalized/incomplete
Legal/privacy review needed before production
No CAPTCHA bypass, credential harvesting, or mobile/API reverse-engineering
```

Rate limits: no published public Stockbit scraper limits found in repo/docs. Use conservative self-limit: <=50-200 viewed items/day/account during PoC; lower if any warnings/blocks. Treat 429/CAPTCHA as hard stop.

## X/Twitter

Recommended MVP: do not start with X unless stakeholders need it. Start app reviews/YouTube/news first; add X only after keywords prove business value.

Options:

```txt
twscrape                  cheapest unofficial search/scrape; high risk; account pool required
snscrape                  historically useful, often broken/limited after X changes; not reliable primary
playwright                public web prototype only; brittle/login walls common
Tweepy                    official X API v2 client; paid tiers required for useful search
Apify X actors            cheap-ish vendor/prod-lite; check current pricing/limits
Bright Data / Data365 / SocialGrep-like vendors if available  paid/vendor route
Brand24/Talkwalker/Meltwater/Drone Emprit/NoLimit/Kazee/Dataxet social listening  vendor route; ask X + Stockbit coverage
```

Official X API reality:

```txt
Free tier generally unsuitable for broad search/listening
Recent search/full-archive access usually paid/limited by tier
Rate limits change by plan; verify current X developer portal before procurement
Production compliance best via official API or licensed vendor
```

Unofficial `twscrape` PoC:

```txt
Use throwaway/research accounts only if approved
Do not use employee/personal/corporate accounts
Low query frequency; random jitter; store checkpoints
Stop on locked account, CAPTCHA, 401/403/429, suspicious activity
No evasion arms race/proxy rotation unless legal approves vendorized collection
```

Suggested PoC rates:

```txt
Manual/public web: <=20 searches/day
Unofficial account-based: <=5-20 keyword searches/day/account, <=100-500 tweets/day/account until stable
Official API/vendor: follow contracted rate limits exactly
```

Fields to collect:

```txt
platform="x"
source_type: tweet|reply|quote|retweet
source_id/tweet_id
conversation_id
parent_source_id/in_reply_to_id
keyword/query
text
lang
author_id
author_username
author_display_name if available
verified/account metadata if available
created_at
collected_at
source_url
metrics: reply_count, repost/retweet_count, like_count, quote_count, view_count if available
entities: hashtags, cashtags, mentions, urls
raw_payload
content_hash
collection_method: official_api|unofficial_api|automation|vendor
access_risk
```

Human approval/provisioning:

```txt
Decide X path: official API vs vendor vs unofficial PoC
If official: X developer project/app, paid tier, bearer token; approved use-case text
If vendor: vendor contract/API key, keyword quota, historical window, export rights
If unofficial: legal/ToS approval, dedicated throwaway accounts, allowed volume, lockout policy
Approve storage of public usernames/tweet text + deletion/takedown handling
Approve whether to collect retweets/quotes/replies or original posts only
```

Agent can discover itself:

```txt
Keyword list tuning
Public tweet URL normalization
Collector adapter/schema impl
Vendor comparison questionnaire
Dry-run parser using provided sample exports/URLs
```

Risks/caveats:

```txt
X ToS/API policy restricts scraping/automation and redistribution
Unofficial libs frequently break; account locks likely
Search completeness varies by auth/tier/vendor
Deleted/protected tweets: must respect removal if detected via official/vendor updates
PII/public handle processing requires privacy review
Political/financial sentiment can be noisy/manipulated/bot-driven
```

## Vendor questions

Ask every vendor:

```txt
Do you cover Indonesia-language X? Stockbit? BBNI/$BBNI? BIONS/BNI Sekuritas?
Historical backfill length?
Near-real-time latency?
Raw text + author handle export allowed?
API/webhook/scheduled CSV?
Rate/mention quotas and overage fees?
Deduping retweets/quotes/replies?
Deleted content handling?
Bahasa Indonesia + finance slang sentiment quality?
Data residency/security?
Can we run a 2-week trial on exact keywords above?
```

Indonesia vendors to check first for local coverage:

```txt
NoLimit
Drone Emprit
Kazee
Dataxet
```

Global/prod-lite:

```txt
Apify
Bright Data
Brand24
Talkwalker
Meltwater
```

## Recommendation

1. Keep Stockbit + X collectors disabled by default.
2. Run Stockbit Playwright PoC only after explicit human approval + dedicated acct.
3. Delay X unofficial collection; prefer vendor trial or official API if X becomes mandatory.
4. Store normalized `RawSocialItem` + raw payload for every item.
5. Promote to official/vendor when: useful signal + repeated breakage + reporting SLA/compliance need + budget.
