# Phase 5: QA LISTO Weekly Status - Research

**Researched:** 2026-04-20
**Domain:** Python script (PROC-03) + vanilla JS dashboard extension (PROC-04)
**Confidence:** HIGH — all findings verified directly against live files in this repo

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** `PLAYWRIGHT_MIN_PASS_PCT = 80`
- **D-02:** `MAESTRO_MIN_HEALTH = 60`
- **D-03:** Thresholds documented in 3 places: script constants, `weekly-status.json.thresholds`, `ai-specs/specs/qa-listo-criteria.mdc`
- **D-04:** Classification order — BLOQUEADO first, LISTO last, PENDIENTE default
- **D-05:** `CON_CONDICIONES` → PENDIENTE (not BLOQUEADO)
- **D-06:** Cowork sin reporte → PENDIENTE, reason = "Cowork: sin reporte"
- **D-07:** Playwright sin datos → PENDIENTE, reason = "Playwright: sin datos recientes"
- **D-08:** Maestro N/A = no `platform:app` entries in manifest — determined dynamically, no hardcoded list
- **D-09:** Most recent data per client: Playwright = most recent history JSON where client has `passed > 0` OR `failed > 0`; Cowork/Maestro = most recent manifest entry sorted by `date` DESC
- **D-10:** No date argument — always evaluates most recent data, idempotent
- **D-11:** `reference_date` = ISO date the script ran; `generated_at` = full ISO timestamp
- **D-12:** `tools/evaluate-qa-listo.py`, Python 3, no new external deps, `python3 tools/evaluate-qa-listo.py`
- **D-13:** Reads `public/manifest.json` + `public/history/*.json` via `glob("public/history/*.json")`, NOT via `history/index.json`
- **D-14:** Output `public/weekly-status.json`; ends with `git add + git commit + git push` (pull --rebase on rejection)
- **D-15:** Console summary table: BLOQUEADO first, PENDIENTE second, LISTO last
- **D-16:** Dashboard contract in `05-UI-SPEC.md`: `loadWeeklyStatus()` + `weeklyStatusCache` + `renderEstadoBadge()` + extend `updateUnifiedQaTable()` + extend filter pills + colspan 4→5 + adjust column widths
- **D-17:** `reason` field passed through `escapeHtml()` before use as `title` attribute
- **D-18:** `weeklyStatusCache` NOT invalidated on `#runSelector` change

### Claude's Discretion

- Names of internal helper functions in the script (e.g., `load_manifest`, `load_playwright_data`, `classify_client`, `build_reason`)
- Whether the script accepts `--dry-run` for preview without writing
- Logging to stderr vs stdout in the script
- Exact structure of `ai-specs/specs/qa-listo-criteria.mdc`

### Deferred Ideas (OUT OF SCOPE)

- Slack notifications when a client becomes BLOQUEADO
- Linear ticket auto-creation from BLOQUEADO
- Sorting the table by status (BLOQUEADOs first) — would break memorized order
- Filter pills "Listos" and "Pendientes" — seeing only LISTOs is not actionable
- `--date YYYY-MM-DD` argument for retrospective evaluation
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PROC-03 | Script that evaluates QA LISTO criteria per client (Playwright ≥ 80% + Cowork verdict + Maestro health ≥ 60% or N/A) and writes `public/weekly-status.json` | Data structures verified, classification logic simulated successfully with real data, pattern from `publish-results.py` confirmed applicable |
| PROC-04 | Dashboard renders "Estado Semanal" per client reading `public/weekly-status.json`, showing LISTO / PENDIENTE / BLOQUEADO | Exact insertion points confirmed in `public/index.html` — lines 651-652 (widths), 696 (CSS anchor), 1497 (pills), 1503-1507 (thead), 1510 (colspan), 1699-1757 (JS functions) |
</phase_requirements>

---

## Summary

Phase 5 is a two-artifact deliverable: a Python script (`tools/evaluate-qa-listo.py`) that reads existing data files and writes `public/weekly-status.json`, and a set of additive changes to `public/index.html` that render a 5th column in the unified QA table.

All inputs are already present and have known, stable schemas. The manifest has 5 entries (3 Cowork b2b, 2 Maestro app); the history directory has 9 dated JSON files. Only 4 clients have real Playwright data (bastien, sonrie, codelpa, surtiventas). The remaining ~35 clients appear in history files with `tests: 0, passed: 0, failed: 0` — they are seeded entries from `load_previous_clients()` and must be treated as "sin datos" by the evaluation script. This is the single most important edge case the planner must address.

The dashboard changes are surgical: 3 CSS additions, 3 HTML edits (1 new `<th>`, 1 colspan change, 1 new pill button), and ~30 lines of new/extended JS. The existing `escapeHtml()`, `loadManifestCached()` cache pattern, and filter pills pattern are all reusable with minor extension. No new dependencies, no build step.

**Primary recommendation:** Write the script and dashboard changes as two separate plans (one per requirement), in dependency order: PROC-03 first (produces `weekly-status.json`), PROC-04 second (consumes it).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Evaluate deploy-readiness per client | Script (Python) | — | Logic belongs at data layer — reads 3 pipeline outputs, applies thresholds, writes verdict JSON. UI must NOT compute status. |
| Persist weekly-status.json | Script (Python) | git | Mirrors existing pattern: publish-results.py writes history/*.json, run-maestro.sh writes manifest.json. Same tool, same git push. |
| Document thresholds | Script constants + ai-specs mdc | weekly-status.json (metadata) | Thresholds change rarely — belong in code and prose doc, not UI. JSON carries them for traceability. |
| Render Estado badge | Frontend (static HTML/JS) | — | UI reads JSON verdict, applies CSS class. Zero computation of status in browser. |
| Filter by BLOQUEADO | Frontend CSS + JS | — | Same pattern as existing filter-problemas and filter-stale (Phase 3). `tbody.classList` toggle drives CSS display:none. |

---

## Standard Stack

### Core (PROC-03 script)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib: `json` | built-in | Parse/write JSON files | No external dep needed |
| Python stdlib: `glob` | built-in | Enumerate `public/history/*.json` | D-13: explicit glob, not index.json |
| Python stdlib: `pathlib.Path` | built-in | All file paths — consistent with `publish-results.py` | Project convention |
| Python stdlib: `datetime` | built-in | Generate `generated_at` ISO timestamp and `reference_date` | No dep needed |
| Python stdlib: `sys` | built-in | `sys.exit()`, stderr output | Standard pattern |

**No new pip dependencies.** `publish-results.py` uses `yaml` (PyPI) but the new script has no YAML to parse. All inputs are JSON.

### Core (PROC-04 dashboard)

| Asset | Location | Role | Pattern Source |
|-------|----------|------|----------------|
| `weeklyStatusCache` | global var | Cache weekly-status.json fetch | Mirrors `cachedManifest` / `loadManifestCached()` (line 1581) |
| `loadWeeklyStatus()` | new async fn | Fetch + cache weekly-status.json | Same pattern: `fetch('file.json?v=' + Date.now())`, silent 404 |
| `renderEstadoBadge(slug, weeklyStatus)` | new pure fn | Returns `<span>` HTML for Estado column | Mirrors `renderPlaywrightBadge`, `renderCoworkBadge`, `renderMaestroBadge` |
| `escapeHtml()` | line 2439 | XSS-safe `reason` in `title` attribute | Already defined — just call it |

### Supporting

| Item | Version | Purpose |
|------|---------|---------|
| `ai-specs/specs/qa-listo-criteria.mdc` | new file | Prose documentation of thresholds for the team (D-03) |
| `public/weekly-status.json` | new output | JSON bridge between script and dashboard |

---

## Architecture Patterns

### System Architecture Diagram

```
[tools/evaluate-qa-listo.py]
         |
         ├── reads public/manifest.json
         |     └── most recent b2b entry per client_slug → Cowork verdict
         |     └── most recent app entry per client_slug → Maestro score (or N/A if absent)
         |
         ├── reads public/history/20*.json (glob, sorted DESC)
         |     └── first file where client has passed+failed > 0 → Playwright pct
         |
         ├── applies classification logic (BLOQUEADO > LISTO > PENDIENTE)
         |
         └── writes public/weekly-status.json
                   └── git add + git commit + git push

[public/index.html — initDashboard()]
         |
         ├── loadWeeklyStatus() ← fetch('weekly-status.json?v=ts')
         |       └── stores in weeklyStatusCache
         |
         └── updateUnifiedQaTable(run)
                   └── for each client slug:
                         ├── renderPlaywrightBadge()  [unchanged]
                         ├── renderCoworkBadge()      [unchanged]
                         ├── renderMaestroBadge()     [unchanged]
                         └── renderEstadoBadge(slug, weeklyStatusCache)
                               └── reads weeklyStatusCache?.clients?.[slug]
                               └── returns <span class="u-badge estado-{listo|pendiente|bloqueado|sin-dato}">
```

### Recommended Project Structure (no changes to existing structure)

```
tools/
├── evaluate-qa-listo.py   # NEW — PROC-03
├── publish-results.py     # existing (pattern reference)
└── ...

public/
├── weekly-status.json     # NEW output of evaluate-qa-listo.py
├── manifest.json          # existing input
├── history/20*.json       # existing input
└── index.html             # modified for PROC-04

ai-specs/specs/
└── qa-listo-criteria.mdc  # NEW — threshold documentation (D-03)
```

### Pattern 1: History file glob — find most recent Playwright data per client

**What:** Walk `public/history/20*.json` sorted DESC. For each file, check `clients[slug]`. First file where `passed + failed > 0` = most recent real run for that client.

**Critical edge case:** Many clients have `tests: 0, passed: 0, failed: 0` in history files — these are `load_previous_clients()` seeded entries. A client with only `tests: 0` records across all history files = "sin datos" → PENDIENTE.

```python
# Source: [VERIFIED: direct inspection of public/history/2026-04-17.json]
import glob
from pathlib import Path

def load_playwright_data(project_root: Path) -> dict:
    """Return most recent real Playwright result per client_slug.
    Returns {} for clients with no real run (tests=0 in all files).
    """
    files = sorted(
        (f for f in glob.glob(str(project_root / "public/history/20*.json"))
         if not f.endswith("index.json")),
        reverse=True
    )
    result = {}
    for f in files:
        with open(f) as fp:
            data = json.load(fp)
        for slug, c in data.get("clients", {}).items():
            if slug in result:
                continue
            passed = c.get("passed", 0)
            failed = c.get("failed", 0)
            tests = c.get("tests", 0)
            if passed + failed > 0:  # real run, not seeded
                result[slug] = {
                    "tests": tests,
                    "passed": passed,
                    "failed": failed,
                    "date": Path(f).stem,
                }
    return result
```

**Verified behavior with real data:** 4 clients have real data (bastien 100%, sonrie 100%, codelpa 81.2%, surtiventas 80%). ~35 other slugs exist in history with `tests: 0` — correctly skipped.

### Pattern 2: Manifest — most recent Cowork and Maestro per client

**What:** Iterate `manifest.json.reports`, filter by `platform`, group by `client_slug`, keep entry with max `date`.

```python
# Source: [VERIFIED: direct inspection of public/manifest.json]
def load_manifest_data(project_root: Path) -> tuple:
    """Returns (cowork_by_slug, maestro_by_slug).
    cowork_by_slug: {slug: {verdict, score, date}}
    maestro_by_slug: {slug: {score, date}}  — only for app clients
    """
    with open(project_root / "public/manifest.json") as f:
        manifest = json.load(f)
    
    cowork = {}
    maestro = {}
    for r in manifest.get("reports", []):
        slug = r.get("client_slug")
        date = r.get("date", "")
        if not slug or not date:
            continue
        platform = r.get("platform")
        if platform == "b2b":
            if slug not in cowork or date > cowork[slug]["date"]:
                cowork[slug] = {"verdict": r.get("verdict"), "score": r.get("score"), "date": date}
        elif platform == "app":
            if slug not in maestro or date > maestro[slug]["date"]:
                maestro[slug] = {"score": r.get("score", 0), "date": date}
    return cowork, maestro
```

**Verified manifest structure:**
- All reports have: `client`, `client_slug`, `date`, `environment`, `file`, `modes_done`, `platform`, `score`, `verdict`
- `platform` values observed: `"b2b"` and `"app"` only
- Only `prinorte` has `platform: app` entries — Maestro N/A is the default for everyone else
- The `score` field in APP entries is the Maestro health score (0-100)

### Pattern 3: Classification logic

```python
# Source: [VERIFIED: logic derived from D-04/D-05/D-06/D-07/D-08 in CONTEXT.md + simulated with real data]
def classify_client(slug, pw_data, cowork_data, maestro_data,
                    pw_min=80, mt_min=60) -> dict:
    """Returns {"status": "BLOQUEADO|LISTO|PENDIENTE", "reason": "..."}"""
    blocked = False
    all_green = True
    reasons = []

    # Playwright
    pw = pw_data.get(slug)
    if pw:
        pct = round(pw["passed"] / pw["tests"] * 100, 1) if pw["tests"] > 0 else 0
        if pct < pw_min:
            blocked = True
            reasons.append(f"Playwright {pct}% < {pw_min}%")
        # else: OK, green
    else:
        all_green = False
        reasons.append("Playwright: sin datos recientes")

    # Cowork
    cw = cowork_data.get(slug)
    if cw:
        verdict = cw.get("verdict", "")
        if verdict == "BLOQUEADO":
            blocked = True
            reasons.append("Cowork: BLOQUEADO")
        elif verdict != "LISTO":
            all_green = False
            reasons.append(f"Cowork: {verdict}")
        # "LISTO" → green, no reason needed
    else:
        all_green = False
        reasons.append("Cowork: sin reporte")

    # Maestro (only if client has APP entries)
    mt = maestro_data.get(slug)
    if mt is not None:
        score = mt.get("score", 0)
        if score < mt_min:
            blocked = True
            reasons.append(f"Maestro score {score} < {mt_min}")
        # else: OK, green — N/A is not required for LISTO
    # If mt is None: N/A — does not affect classification

    if blocked:
        return {"status": "BLOQUEADO", "reason": "; ".join(reasons)}
    if all_green:
        return {"status": "LISTO"}  # no reason for LISTO is correct
    return {"status": "PENDIENTE", "reason": reasons[0] if reasons else ""}
```

**Simulated results with real live data (2026-04-20):**
```
bastien   → PENDIENTE | Cowork: CON_CONDICIONES
codelpa   → PENDIENTE | Cowork: sin reporte
new-soprole → PENDIENTE | Playwright: sin datos recientes
prinorte  → BLOQUEADO | Maestro score 0 < 60  (note: also no PW data, but BLOQUEADO wins)
sonrie    → PENDIENTE | Cowork: CON_CONDICIONES
surtiventas → PENDIENTE | Cowork: sin reporte
```

### Pattern 4: Dashboard — loadWeeklyStatus() cache

**What:** Mirror of `loadManifestCached()` at line 1583. Silent 404 fail → `{ clients: {} }`.

```javascript
// Source: [VERIFIED: mirrored from public/index.html line 1583]
let weeklyStatusCache = null;

async function loadWeeklyStatus() {
    if (weeklyStatusCache) return weeklyStatusCache;
    try {
        const r = await fetch('weekly-status.json?v=' + Date.now());
        if (!r.ok) throw new Error('no weekly-status');
        weeklyStatusCache = await r.json();
        console.info('weekly-status.json loaded:', weeklyStatusCache.reference_date);
        return weeklyStatusCache;
    } catch {
        console.info('weekly-status.json not found — showing "Sin evaluar"');
        weeklyStatusCache = { clients: {} };
        return weeklyStatusCache;
    }
}
```

### Pattern 5: renderEstadoBadge() — pure helper

```javascript
// Source: [VERIFIED: contract from 05-UI-SPEC.md + escapeHtml at line 2439]
function renderEstadoBadge(slug, weeklyStatus) {
    const entry = weeklyStatus?.clients?.[slug];
    const status = entry?.status;
    const reason = entry?.reason;

    if (status === 'LISTO') {
        const title = reason ? ` title="${escapeHtml(reason)}"` : '';
        return `<span class="u-badge estado-listo"${title}>&#10003; LISTO</span>`;
    }
    if (status === 'PENDIENTE') {
        const title = reason ? ` title="${escapeHtml(reason)}"` : '';
        return `<span class="u-badge estado-pendiente"${title}>&#9680; PENDIENTE</span>`;
    }
    if (status === 'BLOQUEADO') {
        const title = reason ? ` title="${escapeHtml(reason)}"` : '';
        return `<span class="u-badge estado-bloqueado"${title}>&#10007; BLOQUEADO</span>`;
    }
    if (status !== undefined && status !== null) {
        console.warn(`weekly-status: unknown status "${status}" for client "${slug}"`);
    }
    return '<span class="u-badge estado-sin-dato">Sin evaluar</span>';
}
```

**Note on Unicode icons:** UI-SPEC specifies `✓` (U+2713), `◐` (U+25D0), `✗` (U+2717). Use HTML entities `&#10003;`, `&#9680;`, `&#10007;` or literal Unicode in the template literal — both work in UTF-8 HTML.

### Anti-Patterns to Avoid

- **Reading `history/index.json` for client data:** The index only has totals (`total`, `passed`, `failed`, `duration`), NOT per-client breakdown. D-13 mandates glob of individual dated files.
- **Using `tests > 0` instead of `passed + failed > 0` to detect real runs:** Some clients have `tests: 32` but `passed: 0, failed: 0` if all were skipped. The safe check is `passed + failed > 0`.
- **Hardcoding app client list:** Memory.md names `prinorte`, `surtiventas`, `coexito` as app clients — but D-08 says determine dynamically from manifest. The `appClients` array in index.html (line 1580) is for a different purpose (Maestro badge logic) and must not be used by the script.
- **Computing status in the browser:** The UI must ONLY read `weekly-status.json`. Classification logic belongs exclusively in the script.
- **Polling weekly-status.json:** Loaded once at init, not polled. Only `live.json` is polled (every 3s).
- **Blocking render on weekly-status.json fetch:** The fetch is fire-and-forget-before-updateUnifiedQaTable. If it fails, the table still renders with "Sin evaluar" badges.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Git commit+push | Custom subprocess shell | Follow exact pattern from publish-results.py: `subprocess.run(["git", ...])` or `os.system()` | Already tested and working in the repo |
| XSS-safe HTML attribute | Custom escaping | `escapeHtml()` at line 2439 — already defined | Covers `&`, `<`, `>`, `"` — all chars needed for `title` attribute |
| Cache-busted fetch | Custom URL builder | `fetch('file.json?v=' + Date.now())` — exact pattern from line 1586 | Already in use for manifest, history files |
| Client-side filter | CSS class toggle | `tbody.classList.add('filter-bloqueado')` + CSS `display: none` — Phase 3 pattern | Zero JS per-row filtering, pure CSS |

---

## Common Pitfalls

### Pitfall 1: Seeded clients classified as PENDIENTE "Playwright: sin datos" when they might have real data in older files

**What goes wrong:** The script globs history files DESC and skips clients where `passed + failed == 0`. But if a client ran tests last week (file exists, data is real), it correctly picks it up. The issue is clients that truly NEVER ran — they'll be PENDIENTE forever until someone runs Playwright for them.

**Why it happens:** `load_previous_clients()` in `publish-results.py` seeds all 35+ clients into every new history file with `tests: 0`. The glob visits the most recent file first (2026-04-17) where these clients all have zeros, correctly continues to older files, and finds nothing — correct behavior.

**How to avoid:** The fix is in the loop: `continue` to older files (don't `break`) when a client has `passed + failed == 0`. The `if slug not in result` guard combined with `if passed + failed > 0` achieves this correctly.

**Warning signs:** If `weekly-status.json` shows ALL clients as PENDIENTE "sin datos", the loop broke early.

### Pitfall 2: `LISTO` assigned when Cowork says `LISTO` but Playwright has no data

**What goes wrong:** If the `all_green` variable is only checked after Playwright AND Cowork AND Maestro, but a client has `cw.verdict == 'LISTO'` and `mt == None` (N/A), the `all_green` might remain `True` even if Playwright has no data.

**Why it happens:** Forgetting to set `all_green = False` in the Playwright "no data" branch.

**How to avoid:** The Playwright "else" branch (no data) MUST set `all_green = False`. Verified in the pattern above.

**Warning signs:** A client like `new-soprole` (Cowork=CON_CONDICIONES, no PW data) incorrectly showing LISTO.

### Pitfall 3: `reason` field for LISTO entries

**What goes wrong:** Including a `reason` key with empty string for LISTO clients bloats the JSON and causes the dashboard to render an empty `title=""` attribute (ugly tooltip on hover that shows nothing).

**How to avoid:** Only include `reason` in the output JSON when it's non-empty. The `renderEstadoBadge()` helper checks `if (reason)` before adding `title`. In the script, use `{"status": "LISTO"}` without `reason` key (as shown in CONTEXT.md example).

### Pitfall 4: colspan not updated breaks empty state row

**What goes wrong:** After adding the 5th column to `<thead>`, the empty state `<tr><td colspan="4">` still spans only 4 columns — it won't stretch across the full table.

**How to avoid:** Two places to update:
1. Line 1510: `<tr><td colspan="4" class="loading">` → `colspan="5"`
2. Line 1703 (JS): `tbody.innerHTML = '<tr><td colspan="4"` → `colspan="5"` (there are two occurrences in `updateUnifiedQaTable`)

**Warning signs:** Empty state row appears narrower than the table header.

### Pitfall 5: Column widths don't sum to ~100%

**What goes wrong:** Adding a 14% `u-col-estado` without reducing `u-col-client` and `u-col-badge` causes horizontal scroll or layout overflow.

**Current widths (Phase 3):** `.u-col-client: 30%`, `.u-col-badge: 23.33%` × 3 = 70% + 30% = 100%.

**New widths (Phase 5):** `.u-col-client: 24%`, `.u-col-badge: 18%` × 3 = 54%, `.u-col-estado: 14%` = 92% (remainder: `auto` by table layout = fine).

**How to avoid:** Update BOTH `.u-col-client` (30% → 24%) and `.u-col-badge` (23.33% → 18%) when adding the new column.

### Pitfall 6: `loadWeeklyStatus()` called after `updateUnifiedQaTable()`

**What goes wrong:** If `updateUnifiedQaTable()` renders before `weeklyStatusCache` is populated, all Estado badges show "Sin evaluar" even when the JSON exists.

**How to avoid:** In `initDashboard()`, `await loadWeeklyStatus()` BEFORE calling `updateUnifiedQaTable(latestRun)`. Or make `updateUnifiedQaTable` itself call `loadWeeklyStatus()` (already async) and await it — the manifest fetch already follows this pattern (`const manifest = await loadManifestCached()` at line 1707).

**Recommended approach:** Follow the manifest pattern — call `await loadWeeklyStatus()` inside `updateUnifiedQaTable` before the `.map()`, similar to how `loadManifestCached()` is called at line 1707.

---

## Code Examples

### weekly-status.json output schema

```json
{
  "generated_at": "2026-04-21T10:00:00.000000+00:00",
  "reference_date": "2026-04-21",
  "thresholds": {
    "playwright_min_pass_pct": 80,
    "maestro_min_health": 60
  },
  "clients": {
    "bastien":     { "status": "PENDIENTE", "reason": "Cowork: CON_CONDICIONES" },
    "codelpa":     { "status": "PENDIENTE", "reason": "Cowork: sin reporte" },
    "prinorte":    { "status": "BLOQUEADO", "reason": "Maestro score 0 < 60" },
    "sonrie":      { "status": "PENDIENTE", "reason": "Cowork: CON_CONDICIONES" },
    "surtiventas": { "status": "PENDIENTE", "reason": "Cowork: sin reporte" }
  }
}
```

Note: LISTO entries omit `reason` key entirely. PENDIENTE and BLOQUEADO include non-empty `reason`.

### CSS additions (add after line 696, after `.u-badge.u-na`)

```css
/* Phase 5: Estado column + badges */
.u-col-client { width: 24%; }   /* was 30% — override to shrink */
.u-col-badge  { width: 18%; }   /* was 23.33% — override to shrink */
.u-col-estado { width: 14%; }   /* new */
.u-badge.estado-listo    { background: #d1fae5; color: #065f46; }
.u-badge.estado-pendiente{ background: #fef3c7; color: #92400e; }
.u-badge.estado-bloqueado{ background: #fee2e2; color: #991b1b; }
.u-badge.estado-sin-dato { background: #f3f4f6; color: #9ca3af; border: 1px solid #e5e7eb; }
#unifiedQaBody.filter-bloqueado tr:not([data-estado="bloqueado"]) { display: none; }
```

### HTML additions

```html
<!-- Pill (add after "Stale" pill, line 1497) -->
<button class="unified-filter-pill" data-filter="bloqueado" type="button">Bloqueados</button>

<!-- thead (add after Maestro th, line 1506) -->
<th class="u-col-estado">Estado</th>

<!-- empty state colspan (line 1510) -->
<tr><td colspan="5" class="loading">Cargando estado unificado…</td></tr>
```

### Script git push pattern (from publish-results.py)

```python
# Source: [VERIFIED: CLAUDE.md "commit + push en un solo flujo" + project pattern]
import subprocess

def git_commit_push(project_root: Path, date: str) -> None:
    subprocess.run(["git", "add", "public/weekly-status.json"], cwd=project_root, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"chore(weekly-status): update QA LISTO status {date}"],
        cwd=project_root, check=True
    )
    result = subprocess.run(["git", "push", "origin", "main"], cwd=project_root)
    if result.returncode != 0:
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=project_root, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=project_root, check=True)
```

### Console summary format

```
Estado QA LISTO — 2026-04-21
─────────────────────────────────────────────────────
BLOQUEADO  prinorte       Maestro score 0 < 60
PENDIENTE  bastien        Cowork: CON_CONDICIONES
PENDIENTE  codelpa        Cowork: sin reporte
PENDIENTE  new-soprole    Playwright: sin datos recientes
PENDIENTE  sonrie         Cowork: CON_CONDICIONES
PENDIENTE  surtiventas    Cowork: sin reporte
LISTO      (ninguno aún)
─────────────────────────────────────────────────────
1 BLOQUEADO · 5 PENDIENTES · 0 LISTOS
→ public/weekly-status.json actualizado
```

---

## Data Sources — Verified Schemas

### public/manifest.json

```json
{
  "reports": [
    {
      "client": "Sonrie",
      "client_slug": "sonrie",
      "date": "2026-04-16",
      "file": "qa-reports/sonrie-2026-04-16.html",
      "verdict": "CON_CONDICIONES",
      "score": 87,
      "modes_done": ["FULL"],
      "platform": "b2b",
      "environment": "staging"
    }
  ]
}
```

**Fields always present (verified across all 5 entries):** `client`, `client_slug`, `date`, `environment`, `file`, `modes_done`, `platform`, `score`, `verdict`.

**Verdict values observed:** `CON_CONDICIONES`, `BLOQUEADO`. `LISTO` not yet observed but documented in COWORK.md.

**Platform values:** `"b2b"` (Cowork reports) and `"app"` (Maestro reports). No other values observed.

**App clients in manifest:** Only `prinorte` (2 entries, both BLOQUEADO, score=0).

### public/history/YYYY-MM-DD.json (per client entry)

```json
{
  "clients": {
    "bastien": {
      "name": "Bastien (staging)",
      "url": "https://bastien.solopide.me",
      "environment": "staging",
      "tests": 100,
      "passed": 100,
      "failed": 0,
      "reportUrl": "reports/bastien/index.html",
      "last_tested": "2026-04-16"
    }
  }
}
```

**Fields relevant to script:** `tests`, `passed`, `failed`. The `last_tested` field is informational only — the script uses the filename date for tracking, not `last_tested`.

**Edge case — seeded entries (tests=0):** 35+ clients appear in 2026-04-17.json with `tests: 0, passed: 0, failed: 0`. These are seeded by `load_previous_clients()` in `publish-results.py` and MUST NOT be treated as "has Playwright data".

**Clients with real data (verified 2026-04-20):**
- `bastien`: 100% (100/100) on 2026-04-16 (seeded into 2026-04-17)
- `sonrie`: 100% (95/95) on 2026-04-17
- `codelpa`: 81.2% (26/32) on 2026-04-07 (seeded into later files)
- `surtiventas`: 80% (20/25) on 2026-04-07 (seeded into later files)

### Exact insertion points in public/index.html

| What | Line | Current content | Change |
|------|------|-----------------|--------|
| `.u-col-client` width | 651 | `width: 30%` | → `24%` |
| `.u-col-badge` width | 652 | `width: 23.33%` | → `18%` |
| CSS anchor for new block | 696 | `.u-badge.u-na { ... }` | Add new block AFTER this line |
| Filter pill "Stale" | 1497 | last pill in group | Add "Bloqueados" pill AFTER |
| `<thead>` last `<th>` | 1506 | `<th class="u-col-badge">Maestro</th>` | Add `<th class="u-col-estado">Estado</th>` AFTER |
| Empty state colspan | 1510 | `colspan="4"` | → `colspan="5"` |
| `updateUnifiedQaTable` start | 1699 | `async function updateUnifiedQaTable` | Extend — add `await loadWeeklyStatus()` + 5th column |
| Empty state in JS (line 1703) | 1703 | `colspan="4"` in JS string | → `colspan="5"` |
| Empty state in JS (line 1727) | 1727 | `colspan="4"` in JS fallback | → `colspan="5"` |
| `setupUnifiedFilterPills` | 1731 | `function setupUnifiedFilterPills()` | Add `filter-bloqueado` to classList.remove + new branch |
| `resetUnifiedFilterPills` | 1749 | `function resetUnifiedFilterPills()` | Add `filter-bloqueado` to classList.remove |
| `initDashboard()` | 1817 | `async function initDashboard()` | Add `loadWeeklyStatus()` call before `updateUnifiedQaTable` |

---

## Environment Availability

Step 2.6: SKIPPED. Phase 5 is pure file I/O + git operations. No external services, databases, or CLI tools beyond Python 3 and git (both confirmed available in the repo — publish-results.py already runs successfully).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `LISTO` verdict is a valid Cowork verdict (not observed yet in manifest, but defined in COWORK.md) | Classification logic | If "LISTO" is never written (e.g., script uses different casing), no client ever reaches LISTO status — verify against COWORK.md |
| A2 | The `score` field in manifest `platform: app` entries is the Maestro health score (0-100) that D-02 references | Standard Stack | If `score` maps to something else, MAESTRO_MIN_HEALTH comparison is wrong — verified against manifest where prinorte score=0 matches known BLOQUEADO state |

**All other claims are VERIFIED** against live files in this session.

---

## Open Questions (RESOLVED)

1. **Does `all_slugs` for the script come from all three data sources or only from history clients?**
   - What we know: History has ~36 slugs (including seeded); manifest has 5 unique slugs; their union has ~36 entries
   - What's unclear: Should the script output status for clients that appear ONLY in history (not in manifest) and ONLY in manifest (not in history)?
   - Recommendation: Union of all three sources. A client with Cowork/Maestro data but no Playwright history is still evaluated (PENDIENTE). A client in history-only with tests=0 everywhere is PENDIENTE "Playwright: sin datos" + "Cowork: sin reporte".

2. **`new-soprole` slug — does it have Playwright tests in fixture?**
   - What we know: `new-soprole` appears in manifest (Cowork CON_CONDICIONES) but has `tests: 0` in all history files
   - What's unclear: Whether there's a `new-soprole.spec.ts` or config-validation fixture for it
   - Recommendation: Treat as PENDIENTE "Playwright: sin datos" for now — correct per D-07. If tests are added later, script auto-updates.

---

## Sources

### Primary (HIGH confidence — VERIFIED against live files)

- `public/manifest.json` — complete field inventory verified, all 5 entries inspected
- `public/history/2026-04-17.json` — full per-client structure verified, seeded vs real data pattern confirmed
- `public/history/*.json` (9 files) — Python simulation of classification logic executed successfully
- `public/index.html` — lines 620-724 (CSS), 1480-1514 (HTML), 1583-1593 (loadManifestCached), 1699-1757 (JS functions), 2439-2442 (escapeHtml) all inspected directly
- `tools/publish-results.py` — full file read, git push pattern and glob pattern confirmed

### Secondary (HIGH confidence — from locked CONTEXT.md decisions)

- `05-CONTEXT.md` — all D-XX decisions verified as locked and non-contradicting with observed data
- `05-UI-SPEC.md` — complete visual contract verified consistent with current index.html CSS

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Python stdlib only, no new deps, all patterns from existing code
- Architecture: HIGH — data flows verified by running classification simulation against real data
- Pitfalls: HIGH — each pitfall discovered by inspecting actual data (seeded clients, colspan, widths)
- Insertion points: HIGH — exact line numbers verified against current file

**Research date:** 2026-04-20
**Valid until:** 2026-05-20 (stable data formats; invalid if manifest schema changes or history format changes)
