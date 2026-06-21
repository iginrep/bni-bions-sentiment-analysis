# Human Approval Checklist — BNI/BIONS Collectors

Status: user approved cheapest-first public collection and saving usernames.

## Approved source inputs

```yaml
google_play:
  url: https://play.google.com/store/apps/details?id=id.bions.bnis.android&hl=id
  app_id: id.bions.bnis.android
  country: id
  language: id
  collection: approved
  save_username: true

apple_app_store:
  url: https://apps.apple.com/id/app/bions/id6736508566
  app_id: "6736508566"
  country: id
  collection: approved
  save_username: true

youtube:
  channels:
    - url: https://www.youtube.com/@BNI1946
      handle: BNI1946
    - url: https://www.youtube.com/@bnisekuritas46
      handle: bnisekuritas46
  needs_env:
    - YOUTUBE_API_KEY
  collection: approved
  save_username: true
```

## Current approval scope

Approved:
- collect public Google Play reviews for BIONS.
- collect public Apple App Store reviews for BIONS.
- collect public YouTube channel/video/comment metadata for listed channels.
- store usernames/display names from source payloads.
- cheapest-first MVP before official/paid APIs.

Not approved yet:
- logged-in Stockbit automation.
- X/Twitter scraping using throwaway accounts or unofficial APIs.
- TikTok scraping/browser automation/vendor.
- Instagram scraping/browser automation/vendor.
- Threads scraping/browser automation/vendor.
- CAPTCHA bypass.
- importing personal account cookies into repo or chat.

Stop rules:
- stop on CAPTCHA, login wall, 401, 403, 429, forced relogin.
- no credential/token/cookie commits.
- no raw data commits.

## Still needed from user

```txt
YOUTUBE_API_KEY in .env
max_items_per_run
backfill_days
retention_days
stockbit_account_available: yes/no
x_login_or_vendor_available: yes/no
tiktok_login_or_vendor_available: yes/no
instagram_login_or_vendor_available: yes/no
threads_login_or_vendor_available: yes/no
```

Recommended defaults if user does not specify:

```yaml
max_items_per_run: 100
backfill_days: 30
retention_days: 365
schedule_timezone: Asia/Jakarta
schedule_times: ["08:00", "18:00"]
```
