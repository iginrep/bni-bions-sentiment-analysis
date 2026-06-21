# TikTok / Instagram / Threads cheapest-first collection plan — BNI/BIONS

Scope: Indonesia public sentiment re BNI Sekuritas/BIONS. No login by agent. No scraping behind auth. High-risk collectors disabled by default.

## Search seeds

- Core: `BIONS`, `BNI Sekuritas`, `BNI Sekuritas BIONS`, `aplikasi BIONS`, `BIONS error`, `BIONS login`, `BIONS lemot`, `BIONS down`, `BIONS saham`, `BNIS`, `BNI Sekuritas error`, `BNI Sekuritas login`.
- Indonesian variants: `gagal login BIONS`, `tidak bisa jual beli`, `order BIONS`, `withdraw BIONS`, `RDN BNI Sekuritas`, `fee BNI Sekuritas`, `CS BNI Sekuritas`.
- Hashtags: `#BIONS`, `#BNISekuritas`, `#BNISekuritasBIONS`, `#saham`, `#investasisaham`, `#tradingindonesia`.
- Official/owned accounts to confirm manually: BNI Sekuritas Instagram/TikTok/Threads handles, BIONS campaign posts, influencer/finance creator posts mentioning BIONS.

## Cheapest-first ranking

| Rank | Platform | Path | Cost | Auth | Coverage | Risk | Default |
|---:|---|---|---|---|---|---|---|
| 1 | Instagram | Meta Graph API for owned IG Business/Creator account comments/mentions where allowed | free quota | human Meta app + page/IG perms | owned-media comments/replies, limited mentions | low-med | off until provisioned |
| 2 | Threads | Threads API for owned account media/replies/insights where allowed | free quota | human Meta app + Threads acct perms | owned Threads posts/replies; broad keyword search limited | med | off until provisioned |
| 3 | TikTok | Manual URL intake + public metadata/comment prototype only for explicitly approved public URLs | free | none by agent | known videos only; search fragile | high | off |
| 4 | Instagram | Manual URL/hashtag watchlist + public page snapshot via browser automation w/o login | free | none by agent | limited public pages; often blocked | high | off |
| 5 | All | Low-cost vendors/scraper APIs (Apify, Bright Data, Outscraper, SerpApi-like, Exolyt/Analisa.io/social listening trials) | cheap→paid | vendor key | broader public search/comments | med-high legal/vendor | off |
| 6 | Official enterprise/social listening | Brandwatch/Talkwalker/Sprinklr/Meltwater/Emplifi/Meta/TikTok partner | paid/expensive | contract | stable/compliant-ish | low-med | later |

## Platform notes

### TikTok

Cheapest viable:
- Start with manual seed URLs discovered by human/public web search. Agent fetches only public pages if reachable without login; no CAPTCHA bypass.
- Prototype libs: `TikTokApi` (Python, Playwright-backed), `playwright`, `httpx` for oEmbed/public metadata if enough.
- Vendor fallback: Apify TikTok Scraper actors, Bright Data TikTok, Exolyt, Analisa.io, Popsters, HypeAuditor. Use only after approval/key.

Collectable fields:
- `platform=tiktok`, `source_type=video|comment`, `source_id=video_id/comment_id`, `parent_source_id`, `conversation_id=video_id`, `keyword`, `target_entity`.
- author: `author_id`, `author_username`, `author_display_name` if public.
- text: video caption/comment text, hashtags, language.
- url/time: `source_url`, `posted_at`, `collected_at`.
- metrics: `likes`, `comments`, `shares`, `views`, `saves` if public.
- raw: JSON/HTML snapshot hash, collector version, access mode.

Limits/caveats:
- No stable public search/comment API for general keyword monitoring. TikTok Research API limited/approval-based; commercial API not general scraping.
- Anti-bot/CAPTCHA frequent; public web varies by region/device. Rate: prototype ≤1 req/page per 30-90s, small daily caps; stop on 403/429/CAPTCHA.
- ToS risk high for scraping/automation; comments may require auth. Keep disabled; use vendors/official approval for production.

### Instagram

Cheapest viable:
- Official Meta Graph API if BNI can provide IG Business/Creator connected to FB Page + app review/perms. Best for owned posts/comments/replies; not broad public keyword search.
- Public no-login browser automation only for approved public URLs/hashtags; expect heavy blocking/login walls.
- Libs: `httpx` for Graph API, `facebook-business` SDK optional, `playwright` for public snapshots, `instaloader` only for manual/known public posts and disabled by default.
- Vendors: Apify Instagram Scraper, Bright Data, Outscraper, Phantombuster (risk), Brandwatch/Talkwalker/Meltwater/Sprinklr/Emplifi.

Collectable fields:
- media/post: `ig_media_id`, shortcode/permalink, caption, media_type, timestamp, like_count, comments_count.
- comment: `comment_id`, parent comment id, text, username, timestamp, like_count/replies where exposed.
- account: handle, display name, verified if public.
- canonical contract fields from `docs/data-contract.md`.

Limits/caveats:
- Basic Display API deprecated/limited for user media; Graph API requires Business/Creator + permissions. Hashtag search exists but constrained; public_content_access requires review/eligibility and is not guaranteed.
- Rate limits app/page/account-scoped; Meta returns usage headers, not fixed universal numbers. Implement backoff; poll owned posts hourly/daily, not minute-level.
- Scraping public IG violates/risks ToS, login walls, IP/account blocks. No agent login; no session/cookie import unless explicit human/legal approval.

### Threads

Cheapest viable:
- Threads API via Meta for owned Threads account publishing/insights/replies where permitted. General public keyword search currently limited/not suitable for broad BIONS monitoring.
- Manual public URL intake + no-login snapshots for approved public Threads only.
- Libs: `httpx` for Threads API, `playwright` for public snapshots. Avoid unofficial private API packages for production.
- Vendors: Apify Threads Scraper, Bright Data, social listening vendors adding Threads coverage.

Collectable fields:
- thread/post id, parent/root id, text, permalink, timestamp, author handle/name where public.
- replies: reply id, parent id, text, timestamp, author public fields.
- metrics: likes, replies, reposts/quotes/views if exposed.

Limits/caveats:
- API maturity/coverage changing; owned-account focus. Keyword discovery weak. Meta permissions/app review needed.
- Public scraping can hit login walls and ToS risk. Rate: conservative ≤1 page/30-90s; stop on 403/429/login/CAPTCHA.

## Human approval/provisioning checklist

Required from human:
1. Legal/compliance approval for each access mode: `official_api`, `public_no_login_snapshot`, `vendor`, `browser_automation`. Explicitly approve/deny ToS-risk collectors.
2. Official owned handles/URLs for BNI Sekuritas/BIONS on TikTok, Instagram, Threads.
3. Seed list: known posts/videos/campaigns/influencers/customer complaint URLs; approved hashtags/keywords.
4. Meta developer assets if using IG/Threads API: Business Manager, FB Page, IG Business/Creator acct, Threads acct, Meta app id, approved products/permissions, system user/token process. No secrets in repo.
5. Vendor approval + budget ceiling + DPA/security review + API keys via secret manager only.
6. Rate policy: max daily items/platform, crawl windows WIB, incident stop conditions, contact owner.
7. Data policy: retention, PII masking, username storage, raw HTML storage approval, takedown/delete process.
8. Account policy: if any login-based automation ever allowed, must be dedicated account, written approval, MFA/credential storage procedure. Agent must not perform login by default.

Agent can discover without secrets/login:
- Public official account candidates, public URLs from search engine results/pages, hashtag spellings, public metadata reachable no-login, vendor docs/pricing pages, API docs, schema mapping, dry-run adapters returning empty/fixtures.

Agent must not do unless approved/provisioned:
- Login, import cookies/session, bypass CAPTCHA, scrape private/auth-only comments, create fake accounts, evade rate limits, store secrets in files/git.

## Implementation defaults

- Env flags: `ENABLE_TIKTOK=false`, `ENABLE_INSTAGRAM=false`, `ENABLE_THREADS=false`, `ALLOW_BROWSER_AUTOMATION=false`, `ALLOW_VENDOR_COLLECTORS=false`.
- Store `access_mode`, `cost_level`, `risk_level`, `collector_version`, `raw_payload`, `source_url`, `collected_at`.
- Backoff: exponential on 429/5xx; immediate disable on CAPTCHA/login/403 spike.
- Dedup: `platform + source_id` if present else normalized `source_url + content_hash`.
- Timezone: normalize to UTC, keep `source_timezone=Asia/Jakarta` when inferred.

## Recommendation

MVP: enable none by default. First use official IG/Threads APIs only if BNI supplies owned-account Meta access. For TikTok, begin with human-supplied public URL watchlist/manual export; evaluate vendor trial before building brittle scraper. Use browser automation only as approved lab prototype, never production default.
