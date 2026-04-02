# Report QA

Generate comprehensive QA report for a client: test results summary, issue grouping, escalation recommendations.

## Usage

```bash
/report-qa Codelpa 2026-04-02
/report-qa "Seis Sur" 2026-03-30
```

## Steps

1. **Adopt QA Coordinator role** (see `ai-specs/.agents/qa-coordinator.md`)

2. **Gather test results**
   - Locate `QA/{CLIENT}/{DATE}/` folder
   - Parse Playwright reports: `test-results/`, `grouped-report.html`
   - Review Maestro flow logs (if ran)
   - Collect manual checklist results

3. **Extract findings**
   - Count pass/fail by test type (Playwright, Maestro, Checklist)
   - Categorize failures by area: auth, payment, config, UI, data
   - Identify P0/P1 blockers vs. P2/P3 improvements

4. **Cross-reference with sources**
   - Link failures to Linear tickets (deuda técnica, known bugs)
   - Check Notion for client-specific context
   - Note if failure is regression (compare against previous test run)

5. **Generate report** → `QA/{CLIENT}/{DATE}/qa-report-{DATE}.md`
   - Use `templates/qa-report-template.md` as base
   - Include:
     - Test execution summary (dates, environment, duration)
     - Results breakdown (tests/specs run, pass rate, failures)
     - Critical findings (blockers, regressions, data inconsistencies)
     - Recommendations (fix priority, owner assignment)
     - Appendix (detailed logs, issue links)

6. **Escalation (if needed)**
   - Use `templates/escalation-templates.md` for format
   - Identify P0 issues: timeline, impact, owner
   - Propose workarounds or rollback strategy

## Report Structure

```markdown
# QA Report: {CLIENT} — {DATE}

## Summary
- Tests run: X, Passed: Y (Z%)
- Environment: staging/production
- Duration: Xh Ym

## Results by Category
### Playwright E2E (17 clients)
- ✓ config-validation: 17/17 passed
- ✗ payment: 15/17 passed (Codelpa, Surtiventas failed)

### Maestro Flows
- ✓ 05-pedido: PASS
- ✗ 09-concurrencia: FAIL (selector timeout)

### Checklists
- ✓ Regresion: 28/30 (post-mortems checked)
- ⚠ Servicios: 12/15 (payment gateway pending)

## Critical Findings
1. **P0**: Payment gateway auth failing for Codelpa (YOM-182)
2. **P1**: Maestro flow 09 timeout on concurrent orders
3. **P2**: Config banner not rendering in admin (UI change?)

## Recommendations
| Issue | Priority | Owner | Action |
|-------|----------|-------|--------|
| Payment auth | P0 | Backend | Check credential rotation |
| Maestro sync | P1 | Mobile | Re-record selectors |
| Banner render | P2 | Frontend | CSS regression? |

## Appendix
- [Test logs](test-results/)
- [Linked tickets](https://linear.app/...)
- [Failed assertions](...)
```

## Key Documents

- `templates/qa-report-template.md` — Report format and sections
- `templates/escalation-templates.md` — Escalation messaging
- `references/severity-matrix.md` — Issue severity definitions
