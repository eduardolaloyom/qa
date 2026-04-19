# Codebase Structure — QA Reporting Pipeline

**Analysis Date:** 2026-04-19
**Focus:** Directories and files relevant to the reporting pipeline

---

## Directory Layout

```
qa/
├── public/                      # GitHub Pages root — everything here is published
│   ├── index.html               # Dashboard (single-file, ~2600 lines)
│   ├── live.json                # Real-time run state (gitignored, API-pushed)
│   ├── manifest.json            # Unified report listing (B2B Cowork + APP Maestro)
│   ├── grouped-report.html      # Test structure grouped by tag category
│   ├── staging-full-report.html # Full staging summary (manually regenerated)
│   ├── accionables.html         # Actionable items view
│   ├── staging-index.html       # Staging run index page
│   ├── history/                 # Playwright run history
│   │   ├── index.json           # Rolling 30-day index of run summaries
│   │   └── YYYY-MM-DD.json      # Full run data per day (stats + clients + failures)
│   ├── reports/                 # Playwright HTML reports (native Playwright output)
│   │   ├── index.html           # Shared fallback report (when no --client flag)
│   │   ├── results.json         # Shared fallback results
│   │   └── {client-slug}/       # Per-client Playwright HTML report (when --client used)
│   ├── qa-reports/              # Cowork session HTML reports
│   │   ├── index.html           # Directory listing
│   │   └── {client}-{date}.html # Standalone report per client per day
│   ├── app-reports/             # Maestro APP HTML reports
│   │   ├── manifest.json        # (legacy — superseded by public/manifest.json)
│   │   └── {client}-{date}.html # Standalone report per client per day
│   └── data/                    # Failure screenshots (gitignored for webm/zip)
│       └── *.png                # Screenshots from failed Playwright tests
│
├── tools/                       # Pipeline scripts
│   ├── publish-results.py       # Playwright → public/history/ publisher
│   ├── live-reporter.js         # Playwright Reporter → public/live.json (real-time)
│   ├── run-live.sh              # One-command: run tests + publish + push
│   ├── run-qa.sh                # Quick pipeline: MongoDB → sync → checklist → Playwright
│   ├── run-maestro.sh           # Maestro runner → public/app-reports/ + manifest
│   ├── sync-clients.py          # Regenerates tests/e2e/fixtures/clients.ts
│   ├── analyze-failures.py      # Standalone failure analysis tool
│   ├── b2b-feature-validator.py # B2B feature validation helper
│   ├── checklist-generator.py   # Generates QA checklists from MongoDB data
│   └── report/
│       └── generate-grouped-report.py  # Generates grouped-report.html from spec files
│
├── tests/e2e/                   # Playwright tests
│   ├── playwright.config.ts     # Workers=4, reporters, projects (b2b/admin)
│   ├── global-setup.ts          # Auth state setup
│   ├── global-teardown.ts       # Auto-publishes results + git push after every run
│   ├── playwright-report/       # Playwright output dir (gitignored)
│   │   ├── results.json         # Machine-readable results (source for publish-results.py)
│   │   └── index.html           # Native Playwright HTML report
│   ├── test-results/            # Screenshots, traces, videos (gitignored)
│   ├── reporters/
│   │   └── grouped-report.ts    # Custom Playwright Reporter for tag-based grouping
│   ├── b2b/                     # B2B spec files
│   │   ├── config-validation/   # Per-client config tests (cv-*.spec.ts)
│   │   │   ├── cv-access.spec.ts
│   │   │   ├── cv-cart.spec.ts
│   │   │   ├── cv-catalog.spec.ts
│   │   │   ├── cv-orders.spec.ts
│   │   │   ├── cv-payments.spec.ts
│   │   │   └── cv-ui-features.spec.ts
│   │   ├── cart.spec.ts
│   │   ├── catalog.spec.ts
│   │   ├── checkout.spec.ts
│   │   ├── coupons.spec.ts
│   │   ├── mongo-data.spec.ts
│   │   ├── multi-client.spec.ts
│   │   ├── orders.spec.ts
│   │   ├── payment-documents.spec.ts
│   │   ├── payments.spec.ts
│   │   ├── prices.spec.ts
│   │   ├── promotions.spec.ts
│   │   └── step-pricing.spec.ts
│   ├── admin/                   # Admin spec files
│   └── fixtures/
│       ├── clients.ts           # AUTO-GENERATED — never edit manually
│       └── login.ts             # Auth helper (Enter-to-submit pattern)
│
├── tests/app/                   # Maestro APP tests
│   ├── flows/                   # Flow definitions per client
│   │   ├── {client}-session.yaml       # Single-session flow (1 retry max)
│   │   ├── {client}-NN-{feature}.yaml  # Numbered individual flows (3 retries)
│   │   └── helpers/                    # Shared Maestro helpers
│   └── config/                  # Client environment config
│       ├── config.{client}.yaml # Preferred: env: section only (gitignored)
│       ├── env.{client}.yaml    # Legacy: all vars (gitignored)
│       ├── config.example.yaml  # Template (committed)
│       └── env.example.yaml     # Template (committed)
│
├── QA/                          # Per-client per-date QA results (local only)
│   └── {Client}/
│       └── {YYYY-MM-DD}/
│           ├── cowork-session.md         # All Cowork HANDOFFs for the day (appended)
│           ├── qa-report-{date}.md       # Final consolidated report (from /report-qa)
│           ├── maestro.log               # Raw Maestro output
│           └── checklist.md             # Generated checklist (from run-qa.sh)
│
├── ai-specs/
│   ├── .commands/               # Workflow definitions (slash commands)
│   │   ├── report-qa.md         # Cowork → HTML report + manifest update
│   │   ├── run-playwright.md    # Playwright execution guide
│   │   ├── qa-client-validation.md  # Full pipeline: MongoDB → Playwright → Maestro → report
│   │   └── triage-playwright.md # Failure triage from history/{date}.json
│   └── .agents/                 # AI role definitions
│
├── data/
│   ├── qa-matrix-staging.json   # Staging client config (source for clients.ts sync)
│   ├── qa-matrix.json           # Production client config (gitignored)
│   └── mongo-extractor.py       # Extracts client config from MongoDB
│
└── checklists/                  # Manual QA checklists
    └── INDICE.md                # Coverage map index
```

---

## Key File Roles in the Reporting Pipeline

### Inputs (data sources)

| File | Role | Generated by |
|------|------|-------------|
| `tests/e2e/playwright-report/results.json` | Playwright run output | `npx playwright test` |
| `QA/{CLIENT}/{DATE}/cowork-session.md` | Cowork HANDOFF blocks | Tester manually |
| `QA/{Cliente}/{date}/maestro.log` | Maestro flow results | `run-maestro.sh` |
| `data/qa-matrix-staging.json` | Client metadata (names, URLs) | `mongo-extractor.py` |

### Pipeline scripts

| File | What it does |
|------|-------------|
| `tools/publish-results.py` | Reads `results.json` → writes `history/{date}.json` + copies HTML report |
| `tools/live-reporter.js` | Playwright Reporter → atomic-writes `public/live.json` during run |
| `tests/e2e/global-teardown.ts` | Auto-calls `publish-results.py` + git push after every `npx playwright test` |
| `tools/run-live.sh` | Wraps Playwright + calls `publish-results.py` + git push manually |
| `tools/run-maestro.sh` | Runs flows + generates `app-reports/{client}-{date}.html` + updates `manifest.json` |
| `ai-specs/.commands/report-qa.md` | Instructs Claude to generate `qa-reports/{client}-{date}.html` + update `manifest.json` |

### Outputs (published to GitHub Pages)

| File | Written by | Read by dashboard |
|------|-----------|------------------|
| `public/live.json` | `live-reporter.js` via GitHub API | `index.html` (polled every 3s) |
| `public/history/index.json` | `publish-results.py` | `index.html` (date selector) |
| `public/history/{date}.json` | `publish-results.py` | `index.html` (B2B tab) |
| `public/reports/{slug}/` | `publish-results.py` | Linked from dashboard |
| `public/manifest.json` | `run-maestro.sh` + `/report-qa` | `index.html` (APP tab + Cowork section) |
| `public/app-reports/{client}-{date}.html` | `run-maestro.sh` | Linked from manifest |
| `public/qa-reports/{client}-{date}.html` | `/report-qa` (Claude Code) | Linked from manifest |
| `public/data/*.png` | `publish-results.py` | Linked from Playwright report |

---

## public/ — What's Committed vs Gitignored

**Committed (published to GitHub Pages):**
- `public/index.html` — dashboard
- `public/manifest.json` — report listing
- `public/grouped-report.html`, `public/accionables.html`, `public/staging-full-report.html`
- `public/history/` — all run history JSON
- `public/reports/{slug}/` — Playwright HTML reports (excluding webm/zip/trace)
- `public/qa-reports/` — Cowork HTML reports
- `public/app-reports/` — Maestro HTML reports
- `public/data/*.png` — failure screenshots

**Gitignored (local or API-pushed only):**
- `public/live.json` and `public/live.json.tmp` — pushed via GitHub Contents API during run
- `public/reports/data/*.webm` — Playwright video recordings
- `public/reports/data/*.zip` — Playwright trace archives
- `public/reports/trace/` — Playwright trace viewer data

---

## QA/{CLIENT}/{DATE}/ — Files Per Session

Every client-date directory is created by tools and populated incrementally:

```
QA/Bastien/2026-04-15/
├── cowork-session.md          # Appended each time tester saves a HANDOFF mode
├── qa-report-2026-04-15.md   # Written by /report-qa at end of session
├── maestro.log               # Written by run-maestro.sh (if APP client)
└── checklist.md              # Written by run-qa.sh or checklist-generator.py
```

The `cowork-session.md` is the accumulation point — all mode HANDOFFs (A, B, C, D) are appended to the same file. `/report-qa` reads the entire file and consolidates.

---

## Where to Add New Files

**New Playwright spec:**
- Place in `tests/e2e/b2b/` with name `{feature}.spec.ts`
- For per-client config tests: place in `tests/e2e/b2b/config-validation/cv-{area}.spec.ts`
- Use `{client_slug}: {TEST_ID} test description` as test title for automatic client grouping

**New Maestro flow:**
- Single session: `tests/app/flows/{client}-session.yaml`
- Individual flow: `tests/app/flows/{client}-NN-{feature}.yaml` (NN = two-digit number)
- Shared helpers: `tests/app/flows/helpers/`
- Client config: `tests/app/config/config.{client}.yaml` (gitignored — add to `.gitignore` manually)

**New Cowork report:**
- Session file: `QA/{CLIENT}/{DATE}/cowork-session.md` (create if not exists, append if exists)
- HTML report: `public/qa-reports/{client}-{date}.html` (generated by `/report-qa`)

**New pipeline tool:**
- Place in `tools/` with a descriptive name
- If it updates `public/`, ensure it also updates `public/manifest.json` for dashboard visibility

**New dashboard view:**
- Add standalone HTML to `public/` and link from `public/index.html`
- If it needs to appear in the APP tab, add an entry to `public/manifest.json`

---

## Naming Conventions

**Playwright spec files:** `{feature}.spec.ts` — e.g., `cart.spec.ts`, `checkout.spec.ts`

**Config-validation specs:** `cv-{area}.spec.ts` — e.g., `cv-cart.spec.ts`, `cv-payments.spec.ts`

**Test titles (multi-client):** `{client_slug}: {TEST_ID} description` — e.g., `bastien: C2-08 cart adds product`
This prefix is parsed by `publish-results.py` to group results per client.

**Maestro session flow:** `{client}-session.yaml` — runs as single unit, 1 retry max

**Maestro numbered flows:** `{client}-NN-{feature}.yaml` — e.g., `prinorte-04-filtros.yaml`, 3 retries

**Cowork session file:** `cowork-session.md` — one per client-date, all modes in one file

**Cowork HTML report:** `{client}-{date}.html` in `public/qa-reports/`

**Maestro HTML report:** `{client}-{date}.html` in `public/app-reports/`

**History run file:** `YYYY-MM-DD.json` in `public/history/`

**Issue IDs:** `{CLIENT}-QA-{NNN}` — sequential per client, e.g., `Bastien-QA-001`

---

*Structure analysis: 2026-04-19*
