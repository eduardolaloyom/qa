# QA Plan Client

Plan comprehensive QA for a client: coverage mapping, test scenarios, validation checklist, and Playwright specs.

## Usage

`/qa-plan-client Codelpa` — Generate QA plan for Codelpa

## Steps

1. **Adopt QA Coordinator role** (see `ai-specs/.agents/qa-coordinator.md`)

2. **Gather client context**
   - Fetch Linear tickets for client (deuda técnica, features, post-mortems)
   - Check Notion for client-specific features and configurations
   - Review `checklists/INDICE.md` for existing coverage

3. **Extract MongoDB config** (via `mongo-extractor.py`)
   - Payment methods, promotions, domain rules, banners
   - Multi-store setup, custom workflows

4. **Map test coverage**
   - Identify Tier 1 (critical): auth, payment, order creation
   - Tier 2 (high): config validation, promotions, edge cases
   - Tier 3 (low): UX refinements, formatting

5. **Design test suite**
   - Playwright specs: multi-client config validation, feature testing
   - Maestro flows: user journeys (order, payment, profile)
   - Checklists: backend services, payment gateway integration
   - Cowork validation: visual inspection, real user scenarios

6. **Generate plan document** → `ai-specs/changes/QA-{CLIENT}-{DATE}.md`
   - Coverage map (feature → test type → status)
   - Identified gaps and priority order
   - Success criteria (% pass rate, zero P0 issues)

7. **Output Playwright fixture update** (if new client)
   - Ensure `sync-clients.py` is run
   - Verify `clients.ts` contains client credentials

## Plan Structure

```markdown
# QA Plan: {CLIENT}

## Context
- Features (Linear, Notion)
- Known issues (post-mortems, open bugs)
- Configuration snapshot (MongoDB exports)

## Coverage Map
| Feature | Playwright | Maestro | Checklist | Tier |
|---------|-----------|---------|-----------|------|
| Authentication | ✓ | ✓ | ✓ | 1 |
| Payment Processing | ✓ | ✓ | ✓ | 1 |
| Order Creation | ✓ | ✓ | ✓ | 1 |

## Test Scenarios
- [x] Scenario 1 (critical path)
- [ ] Scenario 2 (edge case)
- [ ] Scenario 3 (regression)

## Gaps & Blockers
- Gap 1: Staging credentials (action: request from team)
- Gap 2: Maestro selector updates (action: re-record)

## Success Criteria
- 100% Tier 1 pass
- <5% Tier 2 failures
- Zero blocking issues found
```

## Key Documents

- `qa-master-prompt.md` — Canonical test cases (Tier 1-3)
- `checklists/INDICE.md` — Existing coverage map
- `plan-qa-b2b.md` — B2B strategy reference
- `GUIA-OPERACIONAL-QA.md` — When to use each tool
