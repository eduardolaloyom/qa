# AI Specs — YOM QA Framework

This is a **specs-driven QA framework** adapted from the base ai-specs architecture. It provides standardized roles, commands, and workflows for comprehensive testing across Cowork, Playwright E2E, Maestro mobile, and manual checklists.

## What This Framework Provides

✅ **Standardized QA roles** (QA Coordinator, Playwright Specialist, Maestro Specialist)  
✅ **Automated workflows** for client planning, test execution, reporting  
✅ **Reusable specs and standards** for test organization and naming  
✅ **Multi-client management** — same code, different client configs  
✅ **AI-assisted testing** — Claude as primary QA driver + automation as verification  

## Quick Start

### 1. Plan QA for a Client
```bash
/qa-plan-client Codelpa
```
Generates coverage map, identifies gaps, creates test plan.

### 2. Run Playwright Tests
```bash
/run-playwright b2b      # B2B tienda tests (17 clients)
/run-playwright admin    # Admin portal tests
/run-playwright staging  # Staging tests (*.solopide.me)
```

### 3. Generate QA Report
```bash
/report-qa Codelpa 2026-04-02
```
Summarizes test results, prioritizes issues, recommends actions.

## Directory Structure

```
ai-specs/
├── .agents/              # Role definitions
│   ├── qa-coordinator.md          # Orchestrates plans, maps coverage
│   ├── playwright-specialist.md    # E2E test expertise
│   └── maestro-specialist.md       # APP mobile flows
├── .commands/            # Workflows
│   ├── qa-plan-client.md          # Plan QA for client
│   ├── run-playwright.md          # Execute E2E tests
│   └── report-qa.md               # Generate QA report
├── specs/                # Standards & documentation
│   ├── qa-standards.mdc           # Testing conventions, patterns
│   ├── backend-standards.mdc      # API/backend standards
│   └── ...
└── changes/              # Generated plans per client/phase
    ├── QA-Codelpa-2026-04-02.md
    └── ...
```

## Key Roles

### QA Coordinator
**Responsibility:** Plan and orchestrate QA across all tools and clients.

- Map test coverage (which feature tested where?)
- Identify gaps (what's not tested?)
- Generate plans and reports
- Coordinate findings across Linear, Notion, Slack, test results

**Reference:** `ai-specs/.agents/qa-coordinator.md`

### Playwright Specialist
**Responsibility:** Write and maintain E2E specs for B2B/Admin platforms.

- Multi-client configuration validation
- Regression detection via config-driven tests
- Fixture management (clients.ts, loginHelper)
- Debugging test failures

**Reference:** `ai-specs/.agents/playwright-specialist.md`

### Maestro Specialist
**Responsibility:** Create and maintain APP mobile flows.

- Critical user journeys (order, payment, profile)
- Element selector stability
- Flow composition and reusability
- Debugging flow failures

**Reference:** `ai-specs/.agents/maestro-specialist.md`

## Key Workflows

### `/qa-plan-client {CLIENT}`
1. Gather context (Linear, Notion, MongoDB config)
2. Map coverage (Cowork, Playwright, Maestro, Checklists)
3. Identify gaps and blockers
4. Generate plan document → `ai-specs/changes/QA-{CLIENT}-{DATE}.md`

**Output:** Comprehensive plan linking coverage to tests.

### `/run-playwright {PROJECT}`
1. Verify prerequisites (credentials, clients.ts sync)
2. Execute Playwright tests
3. Parse results and generate report
4. Output: HTML summary + test results

**Output:** Pass/fail metrics, failure categorization.

### `/report-qa {CLIENT} {DATE}`
1. Collect test results (Playwright, Maestro, Checklists)
2. Categorize failures (auth, payment, config, UI, data)
3. Cross-reference with Linear/Notion
4. Generate actionable report

**Output:** Client-specific QA report with escalation recommendations.

## Standards & Conventions

### Test Organization
```
Tier 1 (Critical)    → 100% pass required (auth, payment, order creation)
Tier 2 (High)        → Regression detection (known features)
Tier 3 (Low)         → Edge cases, UX refinements
```

### File Naming
```
Playwright specs:    {feature}.spec.ts          (e.g., cart.spec.ts)
Maestro flows:       {NN}-{feature}.yaml        (e.g., 05-pedido.yaml)
Checklists:          checklist-{category}-{area}.md
Test cases:          {PREFIX}-{NN}              (e.g., PM1, CART-01, ERP-01)
Issues:              {CLIENT}-QA-{NNN}          (e.g., Codelpa-QA-001)
```

### Multi-Client Architecture
```
MongoDB (live config)
  ↓ mongo-extractor.py
data/qa-matrix.json
  ↓ sync-clients.py
tests/e2e/fixtures/clients.ts (AUTO-GENERATED — never edit!)
  ↓ loginHelper + parameterized tests
Playwright E2E
```

**Critical rule:** `clients.ts` is auto-generated. Always regenerate via `sync-clients.py` after config changes.

## Important Files

| File | Purpose |
|------|---------|
| `ai-specs/specs/qa-standards.mdc` | Testing conventions, patterns, coverage model |
| `ai-specs/.agents/qa-coordinator.md` | QA Coordinator role definition |
| `ai-specs/.agents/playwright-specialist.md` | Playwright Specialist role |
| `ai-specs/.agents/maestro-specialist.md` | Maestro Specialist role |
| `CLAUDE.md` | Project instructions for Claude Code |
| `qa-master-prompt.md` | Canonical test cases (Tier 1-3) |
| `checklists/INDICE.md` | Coverage map |

## Extending the Framework

### Add a New QA Workflow
1. Create file in `ai-specs/.commands/{workflow-name}.md`
2. Follow the pattern: Steps, Prerequisites, Expected Output
3. Update `.manifest.json` to include new command in "adapted" section
4. Reference the workflow in `CLAUDE.md`

### Add a New Role
1. Create file in `ai-specs/.agents/{role-name}.md`
2. Define responsibilities, key documents, communication style
3. Update `CLAUDE.md` to list the new role

### Update Standards
1. Edit `ai-specs/specs/qa-standards.mdc`
2. Document changes in commit message
3. All agents/commands automatically pick up new standards

## Updating from Upstream

The framework supports merging upstream improvements while preserving local customizations:

```bash
/update-ai-specs
```

This workflow intelligently merges:
- **safe_to_overwrite**: Framework files (replaced directly)
- **adapted**: Project-specific files (flagged for review)
- **symlinks**: Recreation (never overwritten)

See `.manifest.json` for classification.

## Key Documents

- **`ai-specs/specs/qa-standards.mdc`** — Full testing philosophy, coverage model, naming conventions
- **`CLAUDE.md`** — Project instructions for Claude Code
- **`qa-master-prompt.md`** — Canonical test cases (reference for planning)
- **`checklists/INDICE.md`** — Coverage map (reference to avoid duplication)
- **`plan-qa-b2b.md`** — B2B testing strategy
- **`qa-app-strategy.md`** — APP mobile strategy

## Questions?

Refer to:
- `ai-specs/specs/qa-standards.mdc` for standards and conventions
- `CLAUDE.md` for available commands and roles
- Individual role files (`.agents/*.md`) for detailed responsibilities
