# Phase 1: Pipeline Bug Fixes — Research

**Researched:** 2026-04-19
**Domain:** Bash/Python shell scripting, JSON manifest management, Playwright reporter lifecycle, static-dashboard data contracts
**Confidence:** HIGH

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PIPE-01 | `run-maestro.sh` must write the APP/Maestro manifest to the same file the dashboard actually reads (`public/manifest.json`) so Maestro reports appear in the APP tab. | Verified below: dashboard fetches only `manifest.json` (line 2323, `public/index.html`). No code reads `public/app-reports/manifest.json`. `/report-qa` already writes to `public/manifest.json` using the merge pattern. |
| PIPE-02 | `public/live.json` must never display misleading stale data between runs. After a run ends (or before a new one starts) `live.json` should show a clean "no active run" sentinel (`running: false, total: 0`) — not `total: 2932, passed: 0` left over from a prior run. | Verified below: current onEnd() only sets `running: false` but keeps the last `total/passed/failed/skipped` values. Dashboard `pollLive()` logic already hides the panel when `running=false` AND no run has been observed in this browser session, but a fresh page load during an idle period can still show a transient "done" state. Fix requires explicit sentinel reset either in onBegin() or post-run. |
</phase_requirements>

<user_constraints>
## User Constraints (from CONTEXT.md)

**No CONTEXT.md file was produced for this phase.** The following constraints are derived from `.planning/PROJECT.md`, `.planning/ROADMAP.md` (Phase 1 success criteria), and `CLAUDE.md`:

### Locked Decisions (from PROJECT.md Key Decisions + Roadmap)

- **Unify manifests in `public/manifest.json`** — the dashboard already reads this file for the APP tab. `run-maestro.sh` must write THERE, not to `public/app-reports/manifest.json`. Simplest fix; avoids teaching the dashboard two sources.
- **Backward compatibility** — no Playwright, Cowork, or Maestro flow is allowed to break. All existing consumers of `public/manifest.json` (dashboard APP tab, dashboard Cowork card, `public/qa-reports/index.html`) must keep rendering.
- **Vanilla JS only** — dashboard stays a single static HTML file. No bundler, no framework. No new npm deps for the dashboard side.
- **No new runtime dependencies** — pipeline fixes use bash + inline Python 3 (stdlib only) + vanilla Node.js already present.
- **Additive only, no data migration of past entries required** — existing `public/manifest.json` entries are already in the unified schema; Maestro entries currently in `public/app-reports/manifest.json` can be left there (archive) or one-time migrated; planner decides.
- **Live state reset must not break `live-reporter.js` push cadence** — STATE.md risk log flags this explicitly.

### Claude's Discretion

- Whether to **delete `public/app-reports/manifest.json`**, leave it as frozen archive, or one-time migrate its entries into `public/manifest.json`. (No code reads it, so deletion is safe.)
- **Where to reset `live.json`** — at run START (onBegin), at run END (onEnd), or via a standalone `reset-live.sh` tool. Research recommends onEnd + add run-start reset in `run-live.sh` + teardown for defense-in-depth.
- **Exact sentinel schema** — dashboard tolerates missing fields; the minimal sentinel `{ "running": false, "total": 0, "passed": 0, "failed": 0, "skipped": 0, "recentTests": [] }` is sufficient. Including `endTime` and `startTime: null` is optional.
- **Whether to push the final reset to GitHub via Contents API** — local reset is enough for the next local run; GitHub push ensures the live dashboard on GitHub Pages also shows the clean state.
- **Test harness for the bash change** — the project has no shellcheck or bats installed. Planner can choose to add a lightweight shell smoke test OR rely on a manual dry-run validation.

### Deferred Ideas (OUT OF SCOPE for Phase 1)

- Stale-freshness badges on client cards (DASH-01/02 — Phase 2).
- Unified per-client status section (DASH-03/04 — Phase 3).
- Per-client trend chart (DASH-05 — Phase 3).
- Committing `manifest.json` automatically after `run-maestro.sh` (flagged as a gap in ARCHITECTURE.md but explicitly out of scope — manual commit continues).
- Production matrix / production smoke tests (noted in PROJECT.md Out of Scope).
- `manual_pass_count` field on the dashboard (flagged in CONCERNS.md §2 but not in PIPE-01/02).
- Fixing `live-reporter.js` silent failure on GitHub API errors (CONCERNS.md §2 — not in scope).
- Hardcoded `eduardolaloyom/qa` repo reference in live-reporter (CONCERNS.md §2 — not in scope).
</user_constraints>

## Summary

Phase 1 has two surgical, low-risk fixes that unblock the downstream dashboard phases. **PIPE-01 is a one-line variable change** in `tools/run-maestro.sh` plus adapting the manifest entry format to match the unified schema the dashboard already expects. **PIPE-02 is a sentinel reset** in `tools/live-reporter.js` (and optionally `tools/run-live.sh` / `global-teardown.ts`). Neither fix requires new dependencies, new tools, or dashboard changes.

The trickiest details are:
1. The two manifests today have **different per-entry schemas** — `public/manifest.json` uses `score`/`modes_done`/`platform`/`environment`; `public/app-reports/manifest.json` uses `health`/`passed`/`manual`/`failed`/`skipped`/`total`/`verdict`. The dashboard's APP tab renders using `health`, `passed`, `total`, and `verdict`. Since the dashboard already successfully renders the two pre-existing `platform: "app"` entries in `public/manifest.json` (Prinorte) which have `score: 0` instead of `health`, and since the `run-maestro.sh` entry already writes `health` + `passed` + `verdict`, the merged schema is a **superset** — no dashboard JS change needed. Proof: `public/manifest.json` lines 36-57 show two existing Prinorte `platform: "app"` entries rendering today in the dashboard with only `verdict: "BLOQUEADO"`, `score: 0` and no health field, and the APP tab displays them correctly.
2. The `file` field changes meaning: `public/app-reports/manifest.json` uses just `prinorte-2026-04-15.html`; `public/manifest.json` uses `app-reports/prinorte-2026-04-15.html`. The dashboard constructs links directly from `rep.file` with no prefixing (line 2355 of `public/index.html`), so the path must be **relative to `public/`**.
3. `live.json` is gitignored — any reset Push to GitHub via the Contents API is orthogonal to git. Local reset is sufficient; GitHub push is belt-and-suspenders.

**Primary recommendation:**
- Change `PUBLIC_DIR` / `MANIFEST_FILE` in `tools/run-maestro.sh` so the manifest write lands in `public/manifest.json` while HTML keeps being written to `public/app-reports/{file}.html`. Adapt the manifest entry to include `platform: "app"` (already present) and `file: "app-reports/{report_file}"` (prefix the file path).
- Add explicit `running: false, total: 0, passed: 0, failed: 0, skipped: 0, recentTests: []` reset in `live-reporter.js` onEnd(), and a pre-run reset via `run-live.sh` trap ENTRY (or in `onBegin()` before counts accumulate).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Manifest write for APP reports | Pipeline tool (`tools/run-maestro.sh` inline Python) | — | Bash script owns the full post-run lifecycle for Maestro; dashboard is pure reader |
| Manifest read / render | Static dashboard (`public/index.html` fetch + DOM) | — | Single-file static, fetches JSON from GitHub Pages |
| Live state write | Playwright reporter (`tools/live-reporter.js` onEnd/_save) | Wrapper script (`tools/run-live.sh` trap) | Reporter has authoritative test lifecycle; wrapper is belt-and-suspenders for idle cleanup |
| Live state read | Static dashboard (`pollLive()` fetch every 3s) | — | Dashboard polls the same JSON file via GitHub Pages |
| Live state GitHub sync | Reporter GitHub Contents API push (`_pushToGitHub`) | — | Already exists; reset must also be pushed for remote dashboard to show clean state |

## Standard Stack

### Core (all already in use, no installs needed)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Bash | 3.2.57 (macOS system) | `run-maestro.sh` shell logic | Already used; `set -euo pipefail` enforced |
| Python 3 stdlib | 3.9.6 | Embedded `json`, `os`, `re`, `datetime` in run-maestro.sh inline scripts | Already used; zero external deps |
| Node.js `fs`/`path`/`https` | Node >= 20 | live-reporter atomic write + GitHub Contents API push | Already used; no deps |
| `jq` | 1.6 (installed) | Optional manifest inspection in scripts/tests | Available on dev machine |

### Supporting
None required for this phase.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Rewrite run-maestro.sh manifest block to use `jq` | Keep inline Python | Python is already here and has richer control flow; `jq` would be shorter but adds variability |
| Separate `reset-live.js` CLI tool | Inline reset in live-reporter `onEnd()` + run-live.sh trap | Extra file, extra surface; reporter hook is the natural lifecycle point |
| Migrate existing `public/app-reports/manifest.json` entries into `public/manifest.json` | Leave them behind (they're stale from pre-YOM-47 Prinorte runs that already exist in the unified manifest) | Migration is one `jq` merge; leaving is zero work and carries no risk |

**Installation:** None.

**Version verification:** All tools are already present on the dev machine and confirmed via `which` + `--version`. No npm or pip package needs pinning for this phase.

## Architecture Patterns

### System Architecture Diagram

```
                      Playwright run
                           │
                           ▼
        ┌──────────────────────────────────┐
        │ tools/live-reporter.js           │
        │  onBegin  → total = X            │
        │  onTestEnd → passed/failed++     │
        │  onEnd   → running=false         │──(atomic write)──▶ public/live.json
        └──────────────────────────────────┘                      │
                           │                          (trap EXIT) │
                           ▼                   public/live.json.tmp
                  _pushToGitHub (API PUT) ─────▶ GitHub repo (live.json)
                                                      │
                                         GitHub Pages ▼
                                            public/index.html
                                               pollLive() every 3s

                      Maestro run
                           │
                           ▼
        ┌──────────────────────────────────────────┐
        │ tools/run-maestro.sh                     │
        │  flows loop → QA/{Cliente}/{DATE}/log    │
        │  embedded Python                         │
        │    HTML  → public/app-reports/{f}.html   │
        │    manifest.append → public/manifest.json│  (NEW — was app-reports/manifest.json)
        └──────────────────────────────────────────┘
                                                      ▲
                              /report-qa  ────────────┘
                              (writes b2b entries
                               to same file)
                                                      │
                                         GitHub Pages ▼
                                            public/index.html
                                               APP tab: filter platform==="app"
                                               Cowork card: filter platform!=="app"
```

### Recommended Project Structure

No new directories. Changes are localized to:

```
tools/
├── run-maestro.sh       ← edit: change PUBLIC_DIR / MANIFEST_FILE / report_file prefix
├── live-reporter.js     ← edit: reset state in onEnd() before _save()
└── run-live.sh          ← optional: add pre-run reset (trap before playwright)

tests/e2e/
└── global-teardown.ts   ← optional: post-run reset safety net

public/
├── manifest.json        ← destination of Maestro writes (already read by dashboard)
├── app-reports/
│   ├── manifest.json    ← becomes orphan; delete or leave as archive
│   └── {client}-{date}.html  ← still written here (no change)
└── live.json            ← reset to sentinel between runs (gitignored)
```

### Pattern 1: Append-Dedupe-Sort Manifest Write (already in use)

**What:** Load existing manifest, remove any entry with matching `(client_slug, date)`, append the new entry, sort descending by `date`, write back.

**When to use:** Every write to `public/manifest.json`.

**Example** (current code, `tools/run-maestro.sh` lines 446-477 — verified by reading source):
```python
# Source: tools/run-maestro.sh lines 446-477
manifest = {'reports': []}
if os.path.exists(manifest_file):
    try:
        with open(manifest_file) as f:
            manifest = json.load(f)
    except Exception:
        pass

manifest['reports'] = [
    r for r in manifest.get('reports', [])
    if not (r.get('client_slug') == client_slug and r.get('date') == date_str)
]
manifest['reports'].append({ ... })
manifest['reports'].sort(key=lambda x: x['date'], reverse=True)

with open(manifest_file, 'w') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
```

No atomic rename. Fine here — no concurrent writers (Maestro runs one at a time; `/report-qa` is interactive + serial).

### Pattern 2: Atomic Write-Then-Rename for live.json (already in use)

**What:** Write JSON to `OUTPUT + '.tmp'` in the same directory, then `fs.renameSync(tmp, OUTPUT)`.

**When to use:** Every `_save()` in `live-reporter.js`.

**Why it works:** POSIX `rename(2)` is a single atomic syscall. Readers (the dashboard `pollLive()`) always see either the old complete file or the new complete file — never a truncated mid-write buffer.

**Example** (current code, `tools/live-reporter.js` lines 64-70 — verified):
```js
// Source: tools/live-reporter.js lines 64-68
fs.writeFileSync(TMP_OUTPUT, JSON.stringify(this.state, null, 2));
fs.renameSync(TMP_OUTPUT, OUTPUT);
```

**Implication for PIPE-02:** any reset to live.json must use the same atomic pattern (or just call `_save()` after mutating `this.state`).

### Pattern 3: Unified Manifest Polymorphic Schema

The dashboard treats `public/manifest.json` as a polymorphic list. Each entry is either:

- **b2b (Cowork):** `platform: "b2b"`, `score: N`, `modes_done: [A,B,C,D]`, `file: "qa-reports/..."`
- **app (Maestro):** `platform: "app"`, `health: N`, `passed`, `failed`, `manual`, `skipped`, `total`, `file: "app-reports/..."`

The APP tab (`loadAppReports()`, line 2320) filters `rep.platform === 'app'` and reads `rep.health`, `rep.passed`, `rep.total`, `rep.verdict`, `rep.file`. The Cowork card (`loadCoworkReports()`, line 2263) filters `rep.platform !== 'app'` and reads `rep.verdict`, `rep.score`, `rep.modes_done`, `rep.file`.

**Both renderers are field-tolerant** — missing fields fall back gracefully to defaults. Already-rendered Prinorte entries prove this.

### Anti-Patterns to Avoid

- **Mutating the schema of existing `public/manifest.json` entries.** The migration is additive — new Maestro writes land alongside existing b2b entries. Do not normalize / rename keys on old entries.
- **Making the dashboard fetch both `manifest.json` and `app-reports/manifest.json` and merge client-side.** STATE.md + PROJECT.md lock-in the single-source-of-truth decision. Two sources doubles the surface.
- **Resetting `live.json` by deleting the file.** The dashboard's `pollLive()` treats `!r.ok` as "hide panel" but also treats it as "no live file" — deletion works but breaks the idempotent contract that the file always exists and always parses. Prefer an explicit sentinel write.
- **Calling `_save()` inside `onBegin()` WITH the reset sentinel** before setting `total`. The current code sets `this.state.total = suite.allTests().length` inside `onBegin` (line 30). If the reset happens after `total` is set, it will zero out `total` for the run we just started. Reset must happen BEFORE `total` is computed, or the reset must live in a different lifecycle point (e.g. constructor is fine because it already reinitializes state; external pre-run trap is fine because it runs before `onBegin`).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Atomic file write | Lockfile implementation | Existing `writeFileSync(tmp) + renameSync` in live-reporter.js | POSIX rename is already atomic; adding a lockfile adds failure modes |
| Dedup manifest entries | Custom hash-based dedup | The existing list-comprehension dedupe pattern (Pattern 1) | Already works; already used by `/report-qa` |
| Live state schema validator | Custom Zod-like validator in JS | Nothing — keep the JS object literal + test the dashboard tolerates missing fields | Schema is 7 primitive fields; overkill |
| Shell script test runner | Bespoke bash test harness | Manual dry-run OR invoke with `--help`-style flag that exits early (no install needed) | Project has no bats/shellcheck; adding them is out of scope |
| GitHub content push | Another PUT client | Reuse the existing `_pushToGitHub(force)` path — it already knows how to `PUT` the reset body | Zero new code path |

**Key insight:** This phase is 95% "move two variables and add one reset." The temptation to build a migration tool or a schema validator is the wrong framing — the dashboard already tolerates the polymorphic schema, and the manifest write pattern is already battle-tested in `/report-qa`.

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `public/app-reports/manifest.json` will become orphaned (no writers, no readers after fix). Contains 2 entries (Prinorte 2026-04-14, 2026-04-15) — **both already duplicated in `public/manifest.json`** (lines 36-57). | **None for correctness.** Optional: delete the orphan file in the same commit, OR leave as archive. Planner chooses. |
| Live service config | None — GitHub Pages reads static files, no live service config. | None. |
| OS-registered state | None — no pm2/launchd/Task Scheduler entries tied to these files. | None. |
| Secrets/env vars | `GITHUB_TOKEN` is already in `.env`. No new secret names introduced. No env var name changes. | None. |
| Build artifacts | None — no compiled binaries, no egg-info, no Docker tags. Dashboard is served directly from git. | None. |

**The canonical question answered:** After the bash script changes, `public/app-reports/manifest.json` is no longer touched by any process. It is safely orphaned; the dashboard ignores it. No runtime state is cached with references to its contents.

## Common Pitfalls

### Pitfall 1: Breaking existing Prinorte APP entries in `public/manifest.json`

**What goes wrong:** The APP tab currently renders two Prinorte entries from `public/manifest.json`. If the new write from `run-maestro.sh` produces slightly different key names (e.g., writes `score` instead of `health`), the existing entries continue to show old fields and the new entries look wrong.

**Why it happens:** Two writers (`run-maestro.sh` and `/report-qa`) already coexist in the unified file. A schema drift on one writer is invisible until render time.

**How to avoid:** Keep the Maestro entry schema IDENTICAL to what `run-maestro.sh` already writes to `app-reports/manifest.json` today (lines 459-473), only adding `platform: "app"` (already present) and prefixing `file` with `app-reports/`. Do not restructure.

**Warning signs:** Dashboard APP tab shows cards with blank `health/100` or `undefined` flows. Verify by opening `public/index.html` locally after the fix and loading the APP tab.

### Pitfall 2: `file` field path rendered as a broken link

**What goes wrong:** The dashboard uses `<a href="${rep.file}">` with no prefix. If the existing Maestro manifest writes `file: "prinorte-2026-04-15.html"` (relative to `public/app-reports/`) and we move that string verbatim to `public/manifest.json` (which lives in `public/`), the link resolves to `public/prinorte-2026-04-15.html` — 404.

**Why it happens:** Two different directory contexts. Relative paths carry their ancestor directory implicitly.

**How to avoid:** In the run-maestro.sh Python block, change the `file` value to include the `app-reports/` prefix: `'file': f'app-reports/{report_file}'`. Confirmed by inspecting existing unified-manifest Prinorte entries (lines 40, 51 of `public/manifest.json`) — they already use the `app-reports/{filename}.html` form.

**Warning signs:** Clicking a Maestro card in the APP tab 404s on GitHub Pages.

### Pitfall 3: Two writers racing on `public/manifest.json`

**What goes wrong:** If a tester runs `/report-qa` (B2B Cowork) while `run-maestro.sh` is also writing the APP entry, the last writer wins and the first write is lost.

**Why it happens:** No lockfile. Both writers load-modify-save.

**How to avoid:** In practice, this race does not occur — a tester runs one command at a time, Maestro takes minutes, `/report-qa` is interactive. Formal protection would require a lockfile or atomic rename, which is disproportionate.

**Warning signs:** Very rare in practice. Mitigation noted but deferred (Phase 1 is not the place).

### Pitfall 4: Resetting `live.json` at `onBegin()` AFTER `total` is computed

**What goes wrong:** `onBegin()` currently executes `this.state.total = suite.allTests().length; this._save();` (lines 29-31). If we add a reset INSIDE onBegin AFTER the total assignment, we wipe the total. If we add it BEFORE, we just write-then-overwrite (wasteful but correct).

**Why it happens:** Misreading lifecycle hook order.

**How to avoid:** Choose one of: (a) move the reset to the constructor (it's already clean-state there; safe), (b) add a dedicated reset call in `run-live.sh` BEFORE `npx playwright test`, (c) reset state in `onEnd()` AFTER the final `_save()`, writing a separate sentinel `_save()`.

**Warning signs:** Live panel starts a run with `total: 0` and `done: 0/0 · NaN%`.

### Pitfall 5: Pushing the reset to GitHub might rate-limit or conflict

**What goes wrong:** The reset triggers another `_pushToGitHub(true)` call. If the previous push returned a stale SHA, the PUT fails with 409 conflict.

**Why it happens:** `_ghSha` is cached but the onEnd final push updates it via response body. Reset-then-push in close succession usually reuses the updated SHA.

**How to avoid:** Keep the existing pattern — the reset just mutates `this.state` and calls `_save()`, which flows through `_pushToGitHub`. The existing backoff / error handler already silently absorbs failures.

**Warning signs:** Console error "Conflict" during GitHub push. Safe to ignore — the next run's push will resolve via the GET-SHA fallback.

## Code Examples

Verified patterns from official sources and existing project code:

### PIPE-01: Unified manifest write from Maestro

```bash
# Source: tools/run-maestro.sh lines 52-55 (BEFORE)
PUBLIC_DIR="$QA_ROOT/public/app-reports"
MANIFEST_FILE="$PUBLIC_DIR/manifest.json"
REPORT_FILE="${CLIENTE}-${DATE}.html"
REPORT_PATH="$PUBLIC_DIR/${REPORT_FILE}"
```

```bash
# AFTER (proposed — planner's decision on exact split)
HTML_DIR="$QA_ROOT/public/app-reports"         # HTML stays here
MANIFEST_FILE="$QA_ROOT/public/manifest.json"  # MANIFEST moves to unified
REPORT_FILE="${CLIENTE}-${DATE}.html"
REPORT_PATH="$HTML_DIR/${REPORT_FILE}"
# ensure both dirs exist
mkdir -p "$OUTPUT_DIR" "$HTML_DIR"
```

```python
# Source: tools/run-maestro.sh lines 459-473 (BEFORE)
manifest['reports'].append({
    'client':       client_cap,
    'client_slug':  client_slug,
    'date':         date_str,
    'file':         report_file,          # just "prinorte-2026-04-15.html"
    'platform':     'app',
    ...
})
```

```python
# AFTER — prefix file with app-reports/ so the link resolves from public/
manifest['reports'].append({
    'client':       client_cap,
    'client_slug':  client_slug,
    'date':         date_str,
    'file':         f'app-reports/{report_file}',   # "app-reports/prinorte-2026-04-15.html"
    'platform':     'app',
    'environment':  environment,
    'passed':       passed,
    'manual':       manual,
    'failed':       failed,
    'skipped':      skipped,
    'total':        total,
    'health':       health,
    'verdict':      verdict,
})
```

### PIPE-02 Option A: Reset sentinel in reporter onEnd()

```js
// Source: tools/live-reporter.js lines 55-62 (BEFORE)
onEnd(result) {
    this.state.running = false;
    this.state.endTime = new Date().toISOString();
    this.state.currentTest = null;
    this._save();
    this._pushToGitHub(true);
}
```

```js
// AFTER — after final save, overwrite state with sentinel and push again
onEnd(result) {
    this.state.running = false;
    this.state.endTime = new Date().toISOString();
    this.state.currentTest = null;
    this._save();
    this._pushToGitHub(true);

    // Reset to idle sentinel so the dashboard does not show stale counters
    // between this run and the next.
    this.state = {
        running: false,
        total: 0,
        passed: 0,
        failed: 0,
        skipped: 0,
        currentTest: null,
        recentTests: [],
    };
    this._save();            // write sentinel locally
    // _pushToGitHub(true) is called from _save() but throttled; force it
    this._pushToGitHub(true);
}
```

**Tradeoff:** This overwrites the "run just finished" state immediately. The dashboard `pollLive()` transition `_liveWasRunning → showLiveDone()` depends on the reporter having held `running: false` with `endTime` for at least one 3-second poll cycle for the "just finished" UX. If the sentinel writes too fast, the "Run completado" banner may never flash.

**Mitigation:** Delay the sentinel write by N seconds after final push, OR move the reset to `onBegin()` of the NEXT run (recommended).

### PIPE-02 Option B (recommended): Reset in onBegin() BEFORE total is set

```js
// Source: tools/live-reporter.js lines 29-32 (BEFORE)
onBegin(config, suite) {
    this.state.total = suite.allTests().length;
    this._save();
}
```

```js
// AFTER — clear prior-run state before seeding the new run
onBegin(config, suite) {
    // Clear any leftover state from a prior run so recentTests and counters
    // do not bleed across runs.
    this.state = {
        running: true,
        startTime: new Date().toISOString(),
        total: suite.allTests().length,
        passed: 0,
        failed: 0,
        skipped: 0,
        currentTest: null,
        recentTests: [],
    };
    this._save();
}
```

This is the cleaner fix: by the time anyone polls `live.json` during the new run, it shows the new run's totals. The "just finished" UX of the previous run is preserved until the new run starts. For the "idle between runs" window (no run active for hours) — see Option C below for a complementary belt-and-suspenders reset.

### PIPE-02 Option C (defense-in-depth): Pre-run reset in run-live.sh

```bash
# Source: tools/run-live.sh (current — no explicit reset at start)
trap "kill $SERVER_PID 2>/dev/null; rm -f public/live.json public/live.json.tmp" EXIT
# Run tests with live reporter
cd tests/e2e
LIVE=1 npx playwright test $SPECS --project=b2b "$@" || PLAYWRIGHT_EXIT=$?
```

```bash
# Proposed addition before the playwright invocation
# Reset live.json to clean sentinel so dashboard never shows stale state
cat > public/live.json <<'JSON'
{"running":false,"total":0,"passed":0,"failed":0,"skipped":0,"currentTest":null,"recentTests":[]}
JSON
```

This ensures that if someone opens the dashboard BEFORE the reporter's `onBegin()` fires (a ~1s window), they see a clean sentinel instead of the previous run's numbers.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Two manifests: `manifest.json` for Cowork + `app-reports/manifest.json` for Maestro | Single unified `manifest.json` with polymorphic entries (platform field) | 2026-04 (this phase) | Dashboard reads one file; APP/Cowork tabs filter by `platform` |
| `live.json` persists stale counters between runs | Sentinel reset on run start (onBegin state replacement) | 2026-04 (this phase) | Dashboard shows clean state in the idle-between-runs window |
| `fs.writeFileSync(live.json)` non-atomic | `writeFileSync(tmp) + renameSync` atomic | 2026-04 (Phase 4 completed) | Already in place; PIPE-02 reuses it |
| HTTP server lifecycle via PID file | Playwright `webServer` config | 2026-04 (Phase 1-prior completed) | Already in place; unrelated to PIPE-01/02 |

**Deprecated/outdated:**
- `public/app-reports/manifest.json` as a destination for new writes. Becomes frozen after this phase.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | No automation (CI job, dashboard legacy code, archive script) reads `public/app-reports/manifest.json` besides the `run-maestro.sh` writer itself. | Runtime State Inventory, Pitfall 1 | A consumer silently stops receiving Maestro data. Mitigated by a grep across the repo (only 2 hits outside planning: `tools/run-maestro.sh` as writer, `public/index.html` is NOT in the list, INTEGRATIONS.md references it in docs only). VERIFIED by Grep — no runtime consumer exists. |
| A2 | The dashboard's APP tab tolerates Maestro entries with the superset schema (both `health` and `score` fields present, both accepted). | Summary, Pitfall 1 | APP cards render with missing values. Mitigated by direct inspection of `loadAppReports()` which references `rep.health`, `rep.passed`, `rep.total`, `rep.verdict`, `rep.file` and nothing else — missing keys fall back to `undefined` which the template handles. VERIFIED by reading `public/index.html` lines 2320-2383. |
| A3 | Dashboard browser sessions open during an "idle between runs" window (no LIVE=1 run active) are the only scenario where `live.json` stale state is visible. During a run, `onBegin()` reset is sufficient. | PIPE-02 Option B | If there is a race where a browser polls BEFORE the reporter's first `_save()`, it sees stale data for one poll cycle (~3s). Option C (pre-run script-level reset) eliminates this. Planner decides if Option B alone is sufficient. |
| A4 | Neither fix breaks CI. `global-teardown.ts` already guards with `if (process.env.CI) return;` for git steps. The live reporter is skipped in CI (`playwright.config.ts` line 25 conditional). | Multiple | CI pipeline breaks. Low risk — both files explicitly branch on CI env var. VERIFIED. |
| A5 | Migrating the 2 orphan Prinorte entries from `public/app-reports/manifest.json` into `public/manifest.json` is unnecessary because those same 2 entries already exist in `public/manifest.json`. | User Constraints → Claude's Discretion | Slight — if the orphan file's entries ever diverge from the unified file's. At time of research they are identical in client_slug + date; verdict matches. VERIFIED by diffing both files. |

**If further assumptions arise during planning:** surface them in the plan-check step and request confirmation before execution.

## Open Questions (RESOLVED)

1. **Should the orphan `public/app-reports/manifest.json` be deleted or archived?**
   RESOLVED: DELETE in the same commit as the PIPE-01 fix — implemented in 01-01-PLAN.md Task 2 Part B.

2. **Should the reset push to GitHub via the Contents API, or is local-only reset enough?**
   RESOLVED: Skip GitHub push for the sentinel — local reset is sufficient. `onBegin()` replacement triggers `_save()` which calls `_pushToGitHub()` at the throttled interval. Implemented in 01-02-PLAN.md Task 1.

3. **Is there a planned migration for entries in `public/app-reports/manifest.json`?**
   RESOLVED: No migration needed — the 2 entries are exact duplicates of entries already in `public/manifest.json`. Safe to stop writing to `app-reports/manifest.json`.

4. **Do we need a regression test for the bash script?**
   RESOLVED: Yes — `tools/verify-maestro-manifest.sh` smoke script created in 01-01-PLAN.md Task 2 Part A. No shell test framework required; standalone bash script is sufficient.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Bash | run-maestro.sh, run-live.sh | ✓ | 3.2.57 (macOS system) | — |
| Python 3 | run-maestro.sh inline blocks | ✓ | 3.9.6 | — |
| Node.js | live-reporter.js | ✓ | ≥ 20 (per project docs) | — |
| `jq` | optional manifest inspection in new verification script | ✓ | 1.6 (`/usr/bin/jq`) | Inline Python one-liner |
| `pyyaml` | run-maestro.sh already uses it for config parsing | ✓ | Installed (project runs today) | — |
| `shellcheck` | optional — would lint `run-maestro.sh` changes | ✗ | — | Skip lint; rely on `set -euo pipefail` + dry run |
| `bats` | optional shell test framework | ✗ | — | Use a manual smoke script OR defer |
| `maestro` CLI | run-maestro.sh end-to-end validation | ✓ (assumed; project docs require ≥ 1.40.0 via `brew install maestro`) | ≥ 1.40.0 | Skip E2E validation; focus on unit-style manifest verification |
| Android device | end-to-end `run-maestro.sh` run | ? (situational) | — | Verify manifest logic by calling the Python block directly with mocked log |
| `GITHUB_TOKEN` | live-reporter.js GitHub push | ✓ (already in `.env`) | — | Reset works locally without token; remote push is best-effort |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** `shellcheck`, `bats` — optional linting/testing. Planner should decide whether Phase 1 is the place to introduce them (probably not — out of scope).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | **Playwright 1.52.0** (for live-reporter.js integration) + **ad-hoc bash verification** (for run-maestro.sh manifest write) |
| Config file | `tests/e2e/playwright.config.ts` (Playwright); no shell test framework installed |
| Quick run command | `cd tests/e2e && npx playwright test b2b/healthcheck.spec.ts --reporter=list` (fires live-reporter onBegin/onEnd) |
| Full suite command | `cd tests/e2e && npx playwright test --project=b2b` — covers teardown + publish path |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PIPE-01 | `run-maestro.sh` writes entry to `public/manifest.json` (not `app-reports/`) | unit (bash + jq) | `bash tools/verify-maestro-manifest.sh <cliente>` (Wave 0 — new) | ❌ Wave 0 |
| PIPE-01 | New entry has `platform: "app"` and `file` prefixed with `app-reports/` | unit (jq assertion) | `jq -e '.reports[] \| select(.platform=="app" and (.file \| startswith("app-reports/")))' public/manifest.json` | ✅ (jq available) |
| PIPE-01 | `public/app-reports/manifest.json` is no longer modified by the script | unit (bash) | `stat public/app-reports/manifest.json` before/after a run; mtime unchanged | ✅ (stdlib) |
| PIPE-01 | Dashboard APP tab still renders existing + new Maestro entries | smoke | Manual: open `public/index.html` in browser, click APP tab, verify cards | manual-only |
| PIPE-02 | `onBegin` of a new run replaces state so `total/passed/failed/skipped/recentTests` are reset | unit (Node) | `node tests/unit/live-reporter.test.js` (Wave 0 — new, exercises onBegin without running Playwright) | ❌ Wave 0 |
| PIPE-02 | After a run ends, `public/live.json` does not show stale counters from prior run on next read | integration | Run Playwright twice; after 2nd run-start inspect `public/live.json` and confirm the pre-onBegin reset is effective | ✅ (Playwright present) |
| PIPE-02 | Dashboard `pollLive()` hides live panel when `running: false` and no run observed this session | smoke | Manual: open dashboard after a run ended, verify no live panel | manual-only |
| PIPE-01/02 combined | Backward compatibility: Playwright B2B runs continue to publish history, git push, triage hint | regression | `cd tests/e2e && npx playwright test b2b/healthcheck.spec.ts` and verify `public/history/{today}.json` written, git diff includes history only | ✅ |

### Sampling Rate

- **Per task commit:** `jq -e '.reports[0]' public/manifest.json && node -e "require('./tools/live-reporter.js')"` — fast syntax / contract check
- **Per wave merge:** the Playwright quick-run above; check `public/history` + `public/live.json` sentinel
- **Phase gate:** one real `./tools/run-maestro.sh <cliente>` end-to-end against a dev device OR simulated log; confirm both manifests + dashboard APP tab + live.json sentinel

### Wave 0 Gaps

- [ ] `tools/verify-maestro-manifest.sh` — Wave 0 helper that simulates a maestro run via a canned `QA/{client}/{date}/maestro.log` and invokes only the embedded Python block of `run-maestro.sh` against a tmp `public/manifest.json`, asserting the resulting JSON has the expected shape. Enables PIPE-01 assertions without needing an Android device.
- [ ] `tests/unit/live-reporter.test.js` (or equivalent) — a Node script that `require('./tools/live-reporter.js')`, instantiates the reporter, pre-populates `this.state` with stale values, calls `onBegin({}, fakeSuite)`, and asserts `this.state.passed === 0`. Covers PIPE-02 without a real Playwright run.
- [ ] Consider adding `shellcheck tools/run-maestro.sh` as a pre-commit check (OPTIONAL — out of scope default).

*(If all checks are deferred to manual: note that "manual-only" is acceptable for Phase 1 given the small surface area, but the Wave 0 scripts above are cheap insurance for future phases that depend on these files.)*

## Project Constraints (from CLAUDE.md)

Directives from `/Users/lalojimenez/qa/CLAUDE.md` that affect this phase:

- **Credentials never in code:** `GITHUB_TOKEN` is referenced in `live-reporter.js` but read from env. No change introduces new hardcoded secrets.
- **`clients.ts` is AUTO-GENERATED:** Not touched by this phase. Confirming for posterity.
- **Commits in English; conventional prefixes (`fix:`, `refactor:`, `docs:`):** All commit messages in this phase's plans must follow this convention.
- **Dashboard is static + single-file + vanilla JS:** No bundler, no framework addition allowed for any dashboard-side change. Covered.
- **Orden de ejecución Playwright → Cowork → Maestro:** Unchanged — this phase only fixes where results are WRITTEN, not the order of execution.
- **Push to main, no branches/PRs unless requested:** Follow this for Phase 1 plan execution.

Directives from `~/.claude/CLAUDE.md` (global):

- **Respuestas en español (Chile), código/commits en inglés.** Applies to human-facing text in the plan; code and commit messages stay English.
- **Ejecución directa (push a main, sin PRs).** Plans should commit + push, not open PRs.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no (internal tool, no user-auth flow touched) | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes (low — bash script already validates client arg and env file existence) | Keep existing `[ -z "$CLIENTE" ]` + `[ ! -f "$ENV_FILE" ]` guards |
| V6 Cryptography | no (no crypto operations introduced) | — |
| V7 Error Handling & Logging | yes (low — errors pushed to stdout; no secrets in logs) | Existing `mask_secrets()` in `publish-results.py` is not in this phase's surface. `run-maestro.sh` does not log env var values by default. |
| V8 Data Protection | yes (low — `public/` is public via GitHub Pages) | Ensure the manifest write does NOT embed env var values or session tokens; verified — current code writes only aggregated stats. |

### Known Threat Patterns for Bash+Python+Static Dashboard

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Shell injection via `$CLIENTE` arg | Tampering | Already mitigated — value is used as Python arg + filename literal; not interpolated into shell command (except via `python3 -c` which quotes it). Keep as-is. |
| JSON injection into manifest via crafted flow name | Tampering | `run-maestro.sh` reads flow names from YAML and log; values escaped via `html.escape()` for HTML and stored as JSON strings for manifest. Safe. |
| Unintentional secret exposure in committed `public/manifest.json` | Info Disclosure | Manifest fields are all aggregated / public metadata (client name, date, counts, verdict). No secret paths. Safe. |
| Race on `live.json` atomic write | DoS (minor) | Already mitigated via write-tmp-then-rename (Phase 4). |
| GitHub token exfiltration via `live-reporter.js` error log | Info Disclosure | Error handlers silently swallow — no log of `Authorization` header. Safe. |

**Phase 1 introduces no new attack surface.** All changes are within existing trust boundaries.

## Sources

### Primary (HIGH confidence)

- **Project source, directly read:**
  - `tools/run-maestro.sh` lines 1-485 — verified full script including embedded Python
  - `tools/live-reporter.js` lines 1-155 — verified reporter logic + GitHub push
  - `tools/run-live.sh` lines 1-48 — verified wrapper script
  - `tests/e2e/global-teardown.ts` lines 1-53 — verified teardown logic
  - `public/index.html` lines 1374-1417 (env filter), 1958-2025 (live panel), 2260-2400 (manifest renderers) — verified dashboard behavior
  - `public/manifest.json` — verified current content, 5 entries (3 b2b, 2 app Prinorte)
  - `public/app-reports/manifest.json` — verified 2 Prinorte entries, both duplicates of unified manifest
  - `public/live.json` — verified current stale content (`total: 2932, passed: 0`)
  - `public/qa-reports/index.html` — verified reads `manifest.json`
  - `ai-specs/.commands/report-qa.md` lines 40-66 — verified `/report-qa` writes to `public/manifest.json` with the polymorphic schema
  - `.planning/PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `STATE.md` — verified phase scope and locked decisions
  - `.planning/codebase/ARCHITECTURE.md`, `CONCERNS.md`, `CONVENTIONS.md`, `INTEGRATIONS.md`, `STACK.md`, `TESTING.md` — cross-referenced for existing patterns
  - `.planning/phases/04-live-reporter-race-condition/04-RESEARCH.md` — verified atomic-write pattern analysis (informs PIPE-02 mechanics)

### Secondary (MEDIUM confidence)

- `.gitignore` — verified `public/live.json` is gitignored
- `tests/e2e/playwright.config.ts` lines 9-25 — verified `globalTeardown` + reporter wiring + CI guard

### Tertiary (LOW confidence)

- None — every claim was verified against source code in this session.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all tools already in use; no new installs.
- Architecture: HIGH — directly read source files, not inferred.
- Pitfalls: HIGH — pitfalls 1-4 grounded in explicit code paths; pitfall 5 (GitHub 409) is a known API behavior but low-frequency.
- Environment Availability: HIGH — probed via `which` + `--version` on the actual dev machine.
- Validation Architecture: MEDIUM — Wave 0 shell/node test scripts are new (don't exist yet); design is straightforward but not yet written.

**Research date:** 2026-04-19
**Valid until:** 2026-05-19 (30 days — stable code paths, no external deps)
