# QA Coverage Analysis

Compare what should be tested (qa-master-guide.md Tier 1-3) vs. what is tested (Playwright specs, Maestro flows, Checklists). Identify gaps by priority.

## Usage

```
/qa-coverage-analysis
/qa-coverage-analysis --tier 1         # Only Tier 1 gaps
/qa-coverage-analysis --area admin     # Only Admin coverage
```

## Steps

1. **Adopt QA Coordinator role** (see `ai-specs/.agents/qa-coordinator.md`)

2. **Extract expected cases from qa-master-guide.md**
   - Read Section 6 (Tier 1), Section 7 (Tier 2), Section 8 (Tier 3)
   - Build list: `{ID} | {description} | {tier} | {platform}`
   - Example: `C1-01 | Login exitoso B2B | 1 | B2B`

3. **Scan Playwright specs for coverage**
   - Read all `tests/e2e/**/*.spec.ts`
   - Match test names and comments to case IDs
   - Build coverage map: `{case_ID} → {spec_file}`

4. **Scan Maestro flows for coverage**
   - Read all `tests/app/flows/*.yaml`
   - Match flow names and comments to case IDs
   - Build coverage map: `{case_ID} → {flow_file}`

5. **Read checklists/INDICE.md**
   - Extract current coverage index
   - Note which features are ⚠ manual (no automation)

6. **Compute gaps**
   - For each case ID in master guide: `covered = exists in Playwright OR Maestro OR Checklist`
   - Classify uncovered cases by tier and area (B2B, Admin, APP)

7. **Generate gap report** → output to console or `ai-specs/changes/coverage-gap-{DATE}.md`

## Output Format

```markdown
# Coverage Analysis — {DATE}

## Summary
- Tier 1: X/Y covered (Z%)
- Tier 2: X/Y covered (Z%)
- Total gaps: N cases

## P0 — Missing Tier 1 Automation

| Case ID | Description | Area | Action |
|---------|-------------|------|--------|
| C1-05 | Login comercio bloqueado | B2B | Create Playwright spec |
| A1-07 | Admin gestiona promociones | Admin | Create admin/promotions.spec.ts |

## P1 — Tier 2 without automation

| Case ID | Description | Area | Current Coverage |
|---------|-------------|------|-----------------|
| C9 | Seguimiento de pedido | B2B | ⚠ manual checklist only |

## Recommendations
1. Priority: {highest-impact gap}
2. Quick win: {easiest gap to close}
3. Long-term: {complex scenarios needing Maestro}
```

## Key Documents

- `qa-master-guide.md` — Source of expected test cases (Sections 6-8)
- `checklists/INDICE.md` — Current coverage index (update after fixing gaps)
- `ai-specs/specs/qa-coverage-mapping.mdc` — Coverage model and conventions
