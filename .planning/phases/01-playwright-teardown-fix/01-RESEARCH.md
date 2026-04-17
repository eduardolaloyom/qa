# Phase 1: Playwright Teardown Fix - Research

**Researched:** 2026-04-17
**Domain:** Playwright global setup/teardown, Node.js process management, HTTP server lifecycle
**Confidence:** HIGH

## Summary

The current implementation uses `global-setup.ts` to spawn a `python3 -m http.server` process with `detached: true` and immediately calls `server.unref()`, writing its PID to `.http-server.pid`. The teardown reads that PID and calls `process.kill(pid)`. This approach has two verified failure modes: (1) Playwright does NOT guarantee `globalTeardown` runs when the test process is killed via SIGINT/Ctrl+C or crashes — it is a well-documented limitation confirmed by multiple open GitHub issues. (2) The 600ms `setTimeout` in setup is a blind wait with no actual readiness check — if the server takes longer than 600ms, tests start before the server is listening.

**A better approach exists and is built into Playwright:** the `webServer` config option manages the full lifecycle of the server — startup with readiness check, and SIGKILL-guaranteed shutdown even on Ctrl+C — with no PID file required. This replaces the entire `global-setup.ts` / `global-teardown.ts` pattern for the HTTP server concern.

**Primary recommendation:** Replace the PID-file pattern in `global-setup.ts` with Playwright's native `webServer` config option. Keep `global-teardown.ts` for its non-server responsibilities (publish results, git push, triage hint) but remove all server-kill code from it.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| REQ-01 | HTTP server spawned by global-setup.ts must always be cleaned up — even when tests crash or are killed. Port 8080 must not remain occupied. | `webServer` config SIGKILLs the server unconditionally. Port cleanup moves from fragile PID file to Playwright internals. |
| REQ-02 | After any test run (pass, fail, or interrupt), no `http-server` process should remain running. | `webServer` option is documented to kill the process group even on Ctrl+C; confirmed by Playwright source and webserver docs. |
</phase_requirements>

## Current Implementation Audit

### global-setup.ts — What It Does

```typescript
const server = spawn('python3', ['-m', 'http.server', '8080', '--directory', publicDir], {
  detached: true,
  stdio: 'ignore',
});
server.unref();
if (server.pid) writeFileSync(PID_FILE, String(server.pid));
await new Promise(r => setTimeout(r, 600));   // blind 600ms wait
try { execSync('open http://localhost:8080'); } catch {}
```

- Spawns `python3 -m http.server 8080` as a detached process (survives parent exit)
- Calls `server.unref()` — parent will not wait for child on exit
- Writes PID to `.http-server.pid` for teardown to use
- **Waits 600ms unconditionally** — no actual readiness check against port 8080
- Opens the browser (macOS only, best-effort)
- **Skips entirely when `process.env.CI` is set** — server is not needed in CI since tests hit external staging URLs

### global-teardown.ts — What It Does

Has FOUR responsibilities bundled together:

1. **Kill server:** Read PID from `.http-server.pid`, call `process.kill(pid)`, delete file
2. **Delete live.json:** Remove `public/live.json`
3. **Publish results:** Run `python3 tools/publish-results.py`
4. **Git push:** Commit + push `public/` changes (skipped in CI)

The server-kill section is the failing part. The other three responsibilities work correctly and must be preserved.

### global-teardown.ts — Kill Logic Defects

```typescript
const pid = parseInt(readFileSync(PID_FILE, 'utf8').trim());
process.kill(pid);   // sends SIGTERM to PID only, not process group
```

**Defect 1 — SIGTERM to PID only:** `process.kill(pid)` sends SIGTERM to the process with that exact PID. Since the server was spawned with `detached: true`, it leads its own process group. To kill the whole group, you'd need `process.kill(-pid, 'SIGTERM')`. For `python3 -m http.server`, this is unlikely to matter in practice (single process), but it is not robust.

**Defect 2 — No fallback kill:** If SIGTERM is ignored, the process stays alive. No SIGKILL follow-up.

**Defect 3 — No port-based fallback:** If the PID in the file does not match what is actually listening on 8080 (stale file from a previous crashed run), `process.kill(pid)` may either fail silently (wrong process) or kill the wrong process.

**Critical defect — globalTeardown does not run on SIGINT:** This is the root cause of REQ-01/REQ-02. Confirmed by Playwright GitHub issues #22008, #22793, #33193. When the user presses Ctrl+C, Playwright sends SIGINT to its own process. `globalTeardown` is NOT called. The server process — being detached and unref'd — continues running. `.http-server.pid` is left on disk. Port 8080 stays occupied. Next `npm test` fails.

### run-live.sh — Comparison

`run-live.sh` handles cleanup correctly because it uses bash's `trap`:

```bash
python3 -m http.server $PORT --directory public &
SERVER_PID=$!
trap "kill $SERVER_PID 2>/dev/null; rm -f public/live.json" EXIT
```

The `trap ... EXIT` fires on any exit (SIGINT, SIGTERM, normal exit, error with `set -e`). This is why `run-live.sh` does not leak orphan processes — bash `EXIT` trap is the shell equivalent of a `finally` block. The Playwright `globalTeardown` has no equivalent guarantee.

### Verified Stale State as of Research Date

At research time (2026-04-17), `.http-server.pid` contained PID 5698 and port 8080 was occupied by that same Python process. This proves the bug is actively present: a previous test run ended without cleanup.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| @playwright/test | 1.58.2 (installed), 1.59.1 (latest) | Test runner with built-in webServer lifecycle | Already used; webServer is native Playwright — no extra deps |
| python3 built-in http.server | (system) | Serve static `public/` dashboard | Already working; no change needed |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| lsof (macOS/Linux) | system | Port-based fallback kill | In a defensive teardown to kill whatever holds port 8080 |
| fuser (Linux only) | system | Alternative port-based kill | Not on macOS — skip |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Playwright `webServer` config | `start-server-and-test` npm package | `webServer` is native, zero extra deps, integrated with Playwright lifecycle; `start-server-and-test` wraps the full test run from outside |
| Playwright `webServer` config | `wait-on` + keep PID pattern | More complex, same SIGINT problem remains |
| PID file pattern | Port-based kill (`lsof -ti:8080`) | Port-based kill works when PID is stale but is a blunt instrument |

**Installation:** No new packages needed. Solution uses existing Playwright `webServer` config option.

## Architecture Patterns

### Recommended Fix: Playwright webServer Config

Move the HTTP server management out of `global-setup.ts` into `playwright.config.ts`:

```typescript
// playwright.config.ts
export default defineConfig({
  // Remove: globalSetup (or keep for non-server setup logic)
  globalTeardown: './global-teardown.ts',  // keep for publish/git logic

  webServer: {
    command: 'python3 -m http.server 8080 --directory ../../public',
    url: 'http://localhost:8080',
    reuseExistingServer: !process.env.CI,
    stdout: 'ignore',
    stderr: 'pipe',
  },
  // ...
});
```

**Why this works:**
- Playwright waits for `http://localhost:8080` to return 2xx/3xx before running tests (real readiness check, replaces blind 600ms wait)
- When tests finish OR are interrupted (Ctrl+C), Playwright SIGKILLs the process group
- `reuseExistingServer: !process.env.CI` allows local reuse (developer runs server manually), while CI always starts fresh
- CI already skips the server start (`process.env.CI` check) — `webServer` preserves this by reusing existing or not starting if no CI server

**Note on CI behavior:** The existing code does `if (process.env.CI) return;` in setup. With `webServer`, in CI Playwright will try to connect to `http://localhost:8080`. If nothing is there, it fails. Set `reuseExistingServer: !process.env.CI` AND add a condition, OR keep the CI skip via the config. The simplest path: since CI hits external staging URLs and does NOT need the local dashboard server, skip `webServer` in CI entirely:

```typescript
webServer: process.env.CI ? undefined : {
  command: 'python3 -m http.server 8080 --directory ../../public',
  url: 'http://localhost:8080',
  reuseExistingServer: true,
  stdout: 'ignore',
  stderr: 'pipe',
},
```

### What Happens to global-setup.ts

After migrating server management to `webServer` config:
- The `open http://localhost:8080` call stays in `global-setup.ts` (or is dropped — the browser open is cosmetic)
- The server spawn, PID write, and 600ms wait are all removed
- If the only remaining logic is `execSync('open http://localhost:8080')`, the file can be simplified to just that or removed entirely

### What Happens to global-teardown.ts

Keep the file. Remove only the server-kill block (lines 8-14). The other three responsibilities remain:

```typescript
// REMOVE this block:
if (existsSync(PID_FILE)) {
  try {
    const pid = parseInt(readFileSync(PID_FILE, 'utf8').trim());
    process.kill(pid);
  } catch {}
  try { unlinkSync(PID_FILE); } catch {}
}
```

Keep: live.json cleanup, publish-results.py, git push, triage hint.

### Defensive Fallback in global-teardown.ts (Optional but Recommended)

Even with `webServer`, add a port-based cleanup as belt-and-suspenders in `global-teardown.ts`:

```typescript
// Belt-and-suspenders: kill anything holding port 8080
// (handles edge case where webServer didn't manage to clean up)
try {
  execSync('lsof -ti:8080 | xargs kill -9 2>/dev/null || true', { shell: '/bin/bash' });
} catch {}
// Also remove stale PID file if somehow it exists
try { unlinkSync(PID_FILE); } catch {}
```

This pattern is macOS/Linux only (which matches the project's macOS development environment). In CI, this runs harmlessly if nothing is on port 8080.

### Anti-Patterns to Avoid

- **Keeping the PID file pattern:** Does not solve the SIGINT problem. Even with better kill logic, globalTeardown still doesn't run on Ctrl+C.
- **Adding `process.on('SIGINT')` in global-setup:** Playwright overrides signal handlers; relying on this from inside globalSetup is fragile and undocumented.
- **Using `kill -9` on PID directly in teardown only:** Does not help when teardown never runs.
- **Increasing the 600ms wait:** Masks the symptom. A real readiness check is always better.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Server readiness check | `setTimeout(600)` polling | `webServer.url` readiness probe | Playwright retries the URL until it responds; blind sleep is unreliable |
| Server lifecycle on Ctrl+C | `process.on('SIGINT')` in setup | `webServer` config | Playwright owns the signal handling at the runner level |
| Port cleanup script | Custom bash cleanup script | `webServer` + `lsof -ti:8080` one-liner | Built-in is more reliable; lsof one-liner handles the rare edge case |

**Key insight:** The PID file pattern is the wrong abstraction. Playwright already solved this problem with `webServer`. Using it removes ~25 lines of fragile cleanup code and replaces it with 6 lines of config.

## Common Pitfalls

### Pitfall 1: globalTeardown SIGINT Gap
**What goes wrong:** User presses Ctrl+C mid-test. Port 8080 stays occupied. Next `npm test` call fails immediately with "address already in use."
**Why it happens:** Playwright sends SIGINT to its own process. The `globalTeardown` hook is not called on SIGINT. The detached server process is orphaned.
**How to avoid:** Use `webServer` config — Playwright's internal runner kills the webServer process group regardless of how it exits.
**Warning signs:** `.http-server.pid` exists at the start of a new test run; `lsof -i:8080` shows a Python process.

### Pitfall 2: Stale PID File from Previous Crash
**What goes wrong:** `.http-server.pid` contains a PID from a previous run. The old process is gone, but a new one starts on port 8080 with a different PID. Teardown kills the wrong (already-dead) process; new process lives on.
**Why it happens:** `global-setup.ts` writes a new PID but teardown from the previous crash never deleted the file, so no collision occurs — but the file is always re-written. The real risk is if the old PID is recycled by the OS for another process.
**How to avoid:** Switch to `webServer` config; eliminate the PID file entirely.

### Pitfall 3: webServer in CI
**What goes wrong:** `webServer` config attempts to start the local dashboard server in CI, where `public/` may not be populated or the port may not be needed.
**Why it happens:** `webServer` runs unless explicitly skipped.
**How to avoid:** Use `process.env.CI ? undefined : { ... }` for the webServer config, preserving the existing CI skip behavior.

### Pitfall 4: reuseExistingServer Masking Leaks
**What goes wrong:** Developer runs tests, server leaks. Next run succeeds because `reuseExistingServer: true` reuses the leaked process. Looks like it's working, but orphan processes accumulate.
**Why it happens:** `reuseExistingServer: true` was designed for developer convenience, not cleanup.
**How to avoid:** Add the `lsof -ti:8080` fallback kill at the top of `global-teardown.ts` even when using `webServer`. This kills any leftover before teardown completes.

### Pitfall 5: 600ms Blind Wait
**What goes wrong:** On a slow machine or cold start, `python3 -m http.server` takes longer than 600ms to bind to port 8080. Tests start while server is still initializing.
**Why it happens:** `await new Promise(r => setTimeout(r, 600))` is not a readiness check.
**How to avoid:** `webServer.url: 'http://localhost:8080'` — Playwright polls until it gets a response.

## Code Examples

### Recommended playwright.config.ts Change

```typescript
// Source: https://playwright.dev/docs/test-webserver
export default defineConfig({
  // globalSetup can be removed if open-browser is the only remaining logic
  // globalSetup: './global-setup.ts',
  globalTeardown: './global-teardown.ts',

  webServer: process.env.CI ? undefined : {
    command: 'python3 -m http.server 8080 --directory ../../public',
    url: 'http://localhost:8080',
    reuseExistingServer: true,
    stdout: 'ignore',
    stderr: 'pipe',
  },

  // rest of config unchanged...
});
```

### Recommended global-teardown.ts (server block removed)

```typescript
// Source: current global-teardown.ts with server kill block removed
import { execSync } from 'child_process';
import { readFileSync, unlinkSync, existsSync } from 'fs';
import { join } from 'path';

const PID_FILE = join(__dirname, '../../.http-server.pid');

export default async function globalTeardown() {
  // Belt-and-suspenders: kill anything on port 8080
  // (webServer config handles this normally; this is the fallback)
  try {
    execSync('lsof -ti:8080 | xargs kill -9 2>/dev/null || true', { shell: '/bin/bash' });
  } catch {}
  // Clean up stale PID file if it somehow exists
  try { unlinkSync(PID_FILE); } catch {}

  // Limpiar live.json (unchanged)
  try { unlinkSync(join(__dirname, '../../public/live.json')); } catch {}

  // Publicar resultados al dashboard (unchanged)
  const root = join(__dirname, '../..');
  try {
    execSync('python3 tools/publish-results.py', { cwd: root, stdio: 'inherit' });
  } catch (e) {
    console.error('publish-results.py failed:', e);
  }

  // Git commit + push (unchanged, skip en CI)
  if (process.env.CI) return;
  try {
    const date = new Date().toISOString().split('T')[0];
    execSync(
      `git diff --quiet public/ && git diff --cached --quiet public/ || ` +
      `(git add public/ && git commit -m "chore: publish playwright results ${date}" && ` +
      `(git push || (git pull --rebase && git push)))`,
      { cwd: root, shell: '/bin/bash', stdio: 'inherit' }
    );
  } catch (e) {
    console.error('git push failed:', e);
  }

  // Triage hint (unchanged)
  try {
    const historyFile = join(root, 'public', 'history', `${new Date().toISOString().split('T')[0]}.json`);
    if (existsSync(historyFile)) {
      const run = JSON.parse(readFileSync(historyFile, 'utf8'));
      const failed = run.failed || 0;
      const flaky = (run.failure_groups || []).filter((g: any) => g.category === 'flaky').reduce((acc: number, g: any) => acc + g.count, 0);
      if (failed > 0) {
        console.log(`\n${'─'.repeat(60)}`);
        console.log(`${failed} test(s) failed — run /triage-playwright to analyze`);
        if (flaky > 0) console.log(`   + ${flaky} flaky (passed on retry)`);
        console.log(`${'─'.repeat(60)}\n`);
      }
    }
  } catch {}
}
```

### Simplified global-setup.ts (optional — open browser only)

```typescript
// If kept at all, global-setup.ts becomes just the browser open:
import { execSync } from 'child_process';

export default async function globalSetup() {
  if (process.env.CI) return;
  // webServer config handles the server lifecycle.
  // Just open the browser (best-effort, macOS only).
  try { execSync('open http://localhost:8080'); } catch {}
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual PID file management | Playwright `webServer` config | Playwright v1.10+ | Built-in lifecycle — no PID files, no blind waits, guaranteed cleanup |
| `setTimeout(N)` for readiness | `webServer.url` readiness poll | Playwright v1.10+ | Real readiness check eliminates race conditions |
| Custom SIGINT handlers in setup | `webServer` manages shutdown | Playwright v1.x | Playwright-level signal handling is more reliable than user-space handlers |

**Deprecated/outdated:**
- The PID file pattern: predates Playwright's `webServer` config. Appropriate for tools without lifecycle management; obsolete here.

## Open Questions

1. **`global-setup.ts` browser-open behavior after removing server spawn**
   - What we know: `open http://localhost:8080` is macOS-only, best-effort (wrapped in try/catch)
   - What's unclear: Whether the browser-open timing matters relative to when `webServer` finishes its readiness check. With `webServer`, the server is ready before `globalSetup` runs, so opening immediately is safe.
   - Recommendation: Keep `open` call in `global-setup.ts`, or drop it entirely (cosmetic feature). Either is correct.

2. **Does `reuseExistingServer: true` work correctly in this project's local dev flow?**
   - What we know: `reuseExistingServer` reuses whatever is on port 8080 if present. If `run-live.sh` is running, it already has a server there.
   - What's unclear: Whether there is a scenario where `run-live.sh` and `npx playwright test` are run simultaneously.
   - Recommendation: `reuseExistingServer: true` locally is correct — it prevents double-server conflicts.

3. **`public/` directory population before tests**
   - What we know: `public/live.json` is deleted in teardown; the server serves `public/` as static files
   - What's unclear: Whether `public/` is always populated enough to serve before tests start, or if setup must create files first
   - Recommendation: Low risk — `public/` contains static dashboard HTML that pre-exists; `live.json` is written by the live reporter during tests. No blocking issue.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Playwright 1.58.2 |
| Config file | `tests/e2e/playwright.config.ts` |
| Quick run command | `cd tests/e2e && npx playwright test --project=b2b b2b/login.spec.ts` |
| Full suite command | `cd tests/e2e && npx playwright test` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-01 | Port 8080 not occupied after normal test run | smoke | `cd tests/e2e && npx playwright test && lsof -i:8080 \| grep -v grep && echo FAIL \|\| echo PASS` | ❌ Wave 0 manual verification |
| REQ-01 | .http-server.pid cleaned up after run | smoke | `ls .http-server.pid 2>/dev/null && echo FAIL \|\| echo PASS` | ❌ Wave 0 manual verification |
| REQ-02 | Port 8080 not occupied after Ctrl+C | smoke | Manual: run tests, Ctrl+C, then `lsof -i:8080` | ❌ Manual only — cannot automate SIGINT injection reliably |

**Note:** REQ-01 and REQ-02 are infrastructure reliability requirements, not feature test cases. Verification is primarily observational: run tests (or interrupt them), then check port/process state. No new test files needed — the fix is in config and setup files, verified by running the existing test suite twice in a row without failure.

### Sampling Rate
- **Per task commit:** `cd tests/e2e && npx playwright test b2b/login.spec.ts --project=b2b` (quick smoke to confirm tests still run)
- **Per wave merge:** `cd tests/e2e && npx playwright test` (full suite)
- **Phase gate:** Run full suite, then run it again immediately — second run must not fail with "address already in use"

### Wave 0 Gaps
- None — no new test files needed. Existing test suite + manual port check verifies the fix.

## Sources

### Primary (HIGH confidence)
- https://playwright.dev/docs/test-webserver — webServer config, reuseExistingServer, gracefulShutdown, SIGKILL behavior
- https://playwright.dev/docs/test-global-setup-teardown — limitations of globalSetup/globalTeardown vs project dependencies
- https://playwright.dev/docs/api/class-testconfig — full API reference for webServer options
- Direct code audit: `tests/e2e/global-setup.ts`, `tests/e2e/global-teardown.ts`, `tests/e2e/playwright.config.ts`, `tools/run-live.sh`

### Secondary (MEDIUM confidence)
- https://github.com/microsoft/playwright/issues/22008 — Feature request: globalTeardown on Ctrl+C/UI Mode exit (confirmed limitation)
- https://github.com/microsoft/playwright/issues/22793 — globalTeardown not running bug report
- https://github.com/microsoft/playwright/issues/33193 — globalTeardown not running in VS Code extension (v1.48)

### Tertiary (LOW confidence — for context only)
- Various WebSearch results on lsof/fuser port cleanup patterns — standard Unix tooling, well-established

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — existing tools, no new dependencies
- Architecture: HIGH — webServer config is official Playwright, directly verified against docs
- Pitfalls: HIGH — SIGINT behavior confirmed by multiple official GitHub issues; stale PID scenario reproduced live in the project repo

**Research date:** 2026-04-17
**Valid until:** 2026-07-17 (Playwright `webServer` API is stable; unlikely to change)
