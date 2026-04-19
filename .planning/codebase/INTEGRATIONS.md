# External Integrations

**Analysis Date:** 2026-04-19

## GitHub API

**Live dashboard push (`tools/live-reporter.js`):**
- Endpoint: `PUT /repos/eduardolaloyom/qa/contents/public/live.json`
- Auth: `Authorization: token ${GITHUB_TOKEN}` (env var, optional — silently skips if absent)
- User-Agent: `yom-qa-live-reporter`
- Accept: `application/vnd.github.v3+json`
- Mechanism: GET file SHA first (cached in `_ghSha`), then PUT with base64-encoded content
- Rate limiting: self-imposed 10-second minimum interval between pushes (`PUSH_INTERVAL_MS = 10_000`)
- Final push on `onEnd` bypasses the interval (always fires)
- Effect: `public/live.json` in the GitHub repo is updated in real time during a Playwright run

**Static deploy via git push (`tests/e2e/global-teardown.ts`):**
- Not an API call — uses `git add public/ && git commit && git push` via `execSync`
- On push rejection: retries with `git pull --rebase`
- Skipped in CI environments (`process.env.CI` set)
- Commit message format: `chore: publish playwright results YYYY-MM-DD`

**GitHub Actions deploy (`/.github/workflows/deploy-qa-dashboard.yml`):**
- Trigger: push to `main` branch with changes in `public/**`
- Action: `peaceiris/actions-gh-pages@v3`
- Publishes `public/` directory to GitHub Pages
- Auth: `secrets.GITHUB_TOKEN` (built-in, no configuration needed)
- Result: dashboard live at `https://{user}.github.io/qa`

## MongoDB

**Three clusters, two environments (6 URI variables total):**

| Cluster | Production URI var | Staging URI var |
|---|---|---|
| Legacy (products, orders, customers, salesterms) | `MONGO_LEGACY_URI` | `MONGO_LEGACY_STAGING_URI` |
| Microservices (feature flags, promotions, banners) | `MONGO_MICRO_URI` | `MONGO_MICRO_STAGING_URI` |
| Integrations (segments, overrides, user segments) | `MONGO_INTEGRATIONS_URI` | `MONGO_INTEGRATIONS_STAGING_URI` |

**Connection details:**
- All URIs are `mongodb+srv://` (Atlas SRV DNS format)
- Client library: `pymongo[srv]` (Python) — not in `package.json`, installed separately via pip
- Used exclusively by `data/mongo-extractor.py`
- URIs loaded from `.env` at repo root via `_load_env()` (custom parser, no dotenv dependency)

**`--env` flag controls which set of URIs is used:**
- `--env staging` → uses `MONGO_*_STAGING_URI` vars; output default: `data/qa-matrix-staging.json`
- `--env production` → uses `MONGO_*_URI` vars; output default: `data/qa-matrix.json` (gitignored)

**Data flow from MongoDB:**
```
mongo-extractor.py --env staging --output data/qa-matrix-staging.json
    ↓
tools/sync-clients.py --input data/qa-matrix-staging.json
    ↓
tests/e2e/fixtures/clients.ts  (AUTO-GENERATED — never edit manually)
    ↓
Playwright fixtures use clients.ts for per-client test parametrization
```

**`publish-results.py` also reads MongoDB-derived data:**
- Loads `data/qa-matrix-staging.json` via `load_staging_urls()` to map client slugs to display names and URLs
- Used to populate per-client stats in `public/history/{date}.json`

## Live Dashboard Polling

**Mechanism:**
- Dashboard (`public/index.html`) calls `pollLive()` on `DOMContentLoaded`
- Fetches `live.json?t={timestamp}` (cache-busting) every 3 seconds while `d.running === true`
- When `running` transitions to `false` and was previously `true`: shows "Run completado" banner for 3 seconds, then reloads `history/index.json` and the latest `{date}.json` to refresh all dashboard panels
- `live.json` is served from the same GitHub Pages origin — no CORS issues
- If fetch fails or returns non-2xx: `hideLivePanel()` is called silently

**`live.json` schema:**
```json
{
  "running": true,
  "startTime": "ISO8601",
  "total": 57,
  "passed": 23,
  "failed": 2,
  "skipped": 1,
  "currentTest": "bastien: C2-08 ...",
  "recentTests": [
    { "title": "...", "status": "passed|failed|skipped", "duration": 1234 }
  ]
}
```
- Written atomically: `live.json.tmp` → renamed to `live.json` on each test event
- Written locally by `tools/live-reporter.js` to `public/live.json`
- Pushed to GitHub (same path) every 10s or on run end

## History Data API (Static JSON)

**All reads are static fetches from GitHub Pages — no backend:**

| File | Fetch | Purpose |
|---|---|---|
| `public/history/index.json` | `history/index.json?t={ts}` | Rolling 30-day run index (date, total, passed, failed, duration) |
| `public/history/{date}.json` | `history/{date}.json?t={ts}` | Full run detail: suites, clients, failure_groups, pending_b2b, evidence |
| `public/live.json` | `live.json?t={ts}` | Real-time run state |
| `public/manifest.json` | `manifest.json?v={ts}` | Cowork report index |
| `public/app-reports/manifest.json` | fetched from APP tab | Maestro report index |

**Cache-busting:** timestamp query param appended to every fetch call.

## Cowork Session Reports

**Connection to dashboard (indirect — no API):**
1. Cowork (claude.ai) generates a Cowork session HTML report and saves it to `public/qa-reports/{client}-{date}.html`
2. `public/qa-reports/manifest.json` is updated manually (or by `/report-qa` command) with metadata: `client`, `date`, `file`, `verdict`, `score`, `modes_done`
3. Dashboard fetches `manifest.json` and renders a card grid under the "Reportes Cowork" tab
4. Each card links to the individual `public/qa-reports/*.html` file

**`public/qa-reports/manifest.json` schema:**
```json
{
  "reports": [
    {
      "client": "Sonrie",
      "date": "2026-04-16",
      "file": "sonrie-2026-04-16.html",
      "verdict": "CON CONDICIONES",
      "score": 89,
      "modes_done": ["FULL"]
    }
  ]
}
```

**Cowork → dashboard flow summary:**
```
Cowork session (claude.ai)
    ↓ /report-qa {CLIENTE} {FECHA}
QA/{CLIENTE}/{FECHA}/cowork-session.md  (source of truth)
    ↓ generates
public/qa-reports/{client}-{date}.html
public/qa-reports/manifest.json (updated)
    ↓ git commit + push
GitHub Pages → dashboard "Reportes Cowork" tab
```

## Maestro App Reports

**Connection to dashboard:**
1. `tools/run-maestro.sh` generates `public/app-reports/{cliente}-{date}.html` inline Python
2. Updates `public/app-reports/manifest.json` with: `client`, `client_slug`, `date`, `file`, `platform`, `environment`, `passed`, `manual`, `failed`, `skipped`, `total`, `health`, `verdict`
3. Dashboard fetches `app-reports/manifest.json` and renders under the "APP" tab
4. Reports sorted by date descending; grouped by client with history accordion

**`public/app-reports/manifest.json` schema (per entry):**
```json
{
  "client": "Prinorte",
  "client_slug": "prinorte",
  "date": "2026-04-15",
  "file": "prinorte-2026-04-15.html",
  "platform": "app",
  "environment": "production",
  "passed": 0,
  "manual": 0,
  "failed": 1,
  "skipped": 0,
  "total": 1,
  "health": 0,
  "verdict": "BLOQUEADO"
}
```

## Environment Configuration

**Required env vars (in `.env` at repo root):**
```
# MongoDB — Production
MONGO_LEGACY_URI=mongodb+srv://...
MONGO_MICRO_URI=mongodb+srv://...
MONGO_INTEGRATIONS_URI=mongodb+srv://...

# MongoDB — Staging
MONGO_LEGACY_STAGING_URI=mongodb+srv://...
MONGO_MICRO_STAGING_URI=mongodb+srv://...
MONGO_INTEGRATIONS_STAGING_URI=mongodb+srv://...
```

**Required env vars (for live dashboard push):**
```
GITHUB_TOKEN=ghp_...   # Personal access token with repo write scope
```

**Per-client Playwright credentials (in `.env`):**
```
{CLIENT_SLUG}_EMAIL=...
{CLIENT_SLUG}_PASSWORD=...
BASE_URL=https://{slug}.solopide.me
```
Note: client key hyphens must be converted to underscores in var names (e.g., `seis-sur` → `SEIS_SUR_EMAIL`).

**Secrets location:**
- `.env` (gitignored, repo root)
- `GITHUB_TOKEN` used at runtime only — never written to disk in pipeline scripts

## Webhooks & Notifications

**Incoming:** None.

**Outgoing:** None (no Slack/email notifications from pipeline scripts; triage hint is printed to stdout only).

---

*Integration audit: 2026-04-19*
