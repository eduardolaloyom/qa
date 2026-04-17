---
phase: 4
slug: live-reporter-race-condition
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-17
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Node.js built-in (no test runner) |
| **Config file** | none |
| **Quick run command** | `node -e "const r=require('./tools/live-reporter.js'); console.log('module OK:', !!r)"` |
| **Full suite command** | Manual: run playwright, verify `node -e "JSON.parse(require('fs').readFileSync('public/live.json','utf8'))"` |
| **Estimated runtime** | ~5 seconds (smoke), ~3 min (full manual) |

---

## Sampling Rate

- **After every task commit:** Run quick command (module loads without error)
- **After every plan wave:** Run full manual validation (playwright run + JSON check)
- **Before `/gsd:verify-work`:** Two-overlapping-runs test + JSON validity check
- **Max feedback latency:** 5 min

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-T1 | 01 | 1 | REQ-06 | structural | `node -e "const r=require('./tools/live-reporter.js'); console.log('OK')"` | ✅ | ⬜ pending |
| 04-01-T2 | 01 | 1 | REQ-06 | structural | `grep -c "renameSync" tools/live-reporter.js` returns ≥1 | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

- `tools/live-reporter.js` — the file being fixed; no test framework needed
- Manual verification is sufficient given the 2-line change scope

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `live.json` valid during write | REQ-06 | Requires live playwright run to observe concurrent write | `cd tests/e2e && npx playwright test b2b/catalog.spec.ts --project=b2b &; node -e "setInterval(()=>{try{JSON.parse(require('fs').readFileSync('../../public/live.json','utf8'));process.stdout.write('.')}catch(e){console.log('INVALID JSON:',e.message)}},500)" &; wait` |
| Two overlapping runs safe | REQ-06 | Requires two simultaneous playwright processes | `cd tests/e2e && npx playwright test b2b/login.spec.ts --project=b2b & npx playwright test b2b/catalog.spec.ts --project=b2b & wait; node -e "JSON.parse(require('fs').readFileSync('../../public/live.json','utf8')); console.log('valid JSON')"` |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: 2 tasks, both have automated verify
- [x] Wave 0 covers all MISSING references (no MISSING markers)
- [x] No watch-mode flags
- [x] Feedback latency < 5 min
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
