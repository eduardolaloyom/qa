---
phase: 3
slug: b2b-parallel-execution
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-17
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Playwright 1.52.x |
| **Config file** | `tests/e2e/playwright.config.ts` |
| **Quick run command** | `cd tests/e2e && npx playwright test b2b/config-validation/cv-cart.spec.ts --project=b2b --workers=4 --reporter=list` |
| **Full suite command** | `cd tests/e2e && npx playwright test b2b/config-validation/ --project=b2b --workers=4` |
| **Estimated runtime** | ~5–15 min (network-dependent) |

---

## Sampling Rate

- **After every task commit:** Run quick command (cv-cart only)
- **After every plan wave:** Run full config-validation suite
- **Before `/gsd:verify-work`:** Full suite green × 2 consecutive runs
- **Max feedback latency:** 15 min (bounded by staging network)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-T1 | 01 | 1 | REQ-05 | structural | `grep -c "clearCartForTest" tests/e2e/b2b/config-validation/cv-cart.spec.ts` | ✅ | ⬜ pending |
| 03-01-T2 | 01 | 1 | REQ-05 | integration | `cd tests/e2e && npx playwright test b2b/config-validation/ --project=b2b --workers=4 --reporter=list 2>&1 \| tail -3` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

- `tests/e2e/b2b/config-validation/cv-*.spec.ts` — the spec files ARE the subject of REQ-05
- `tests/e2e/playwright.config.ts` — `fullyParallel: true`, `workers: 4` already configured
- No new test infrastructure needed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| ≥50% time reduction vs sequential | REQ-05 | Timing varies by network; no automated threshold check | Run `time npx playwright test b2b/config-validation/ --project=b2b --workers=1` then `--workers=4`; compare wall-clock times |
| No flaky cart-state conflicts | REQ-05 | Server-side state depends on staging; runs must be observed | Run cv-cart spec 3× at workers=4; confirm no new failures vs workers=1 run |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: 2 tasks, both have automated verify
- [x] Wave 0 covers all MISSING references (no MISSING markers)
- [x] No watch-mode flags
- [x] Feedback latency < 15 min
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
