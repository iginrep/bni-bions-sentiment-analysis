# Dashboard app

Next.js dashboard scaffold for viewing BNI/BIONS sentiment outputs.

## Purpose

The dashboard is the visual layer for analysts. It should show sentiment trends, collected comments/reviews, keyword/source configuration, schedules, and export actions.

## Current stack

```txt
Next.js
React
TypeScript
Recharts
TanStack React Table
```

See `package.json` for exact dependency declarations.

## Important files

| Path | Purpose |
| --- | --- |
| `src/pages/index.tsx` | Main dashboard page. |
| `src/lib/api.ts` | API client helpers. |
| `src/types/comment.ts` | Comment/item types. |
| `src/components/SentimentChart.tsx` | Sentiment visualization. |
| `src/components/CommentTable.tsx` | Raw/normalized item table. |
| `src/components/KeywordManager.tsx` | Keyword controls. |
| `src/components/ScheduleManager.tsx` | Schedule controls. |
| `src/components/ExportButton.tsx` | Export action. |

## Local run

```bash
cd /home/hp/dev/work/bni-bions-sentiment-analysis/apps/dashboard
npm install
npm run dev
```

## Data expectations

The dashboard should consume API responses, not read pipeline files directly.

Display priorities:

1. sentiment trend over time.
2. negative feedback drivers/topics.
3. source breakdown: Google Play, App Store, YouTube.
4. recent high-signal comments/reviews.
5. export controls.

## Privacy rules

- Hide or collapse raw usernames by default in public/shareable views.
- Do not render raw payload JSON unless an internal debug mode is explicit.
- Never display API keys, tokens, cookies, or connection strings.
