---
plan: 06-02
phase: 06-actionable-reports-agent-precision
status: complete
requirements_closed:
  - AGENT-01
  - AGENT-02
---

# Plan 06-02 Summary — AGENT-01 + AGENT-02

## What was done

Added two sections to `ai-specs/.agents/playwright-specialist.md`:

1. `## Error Classification` — Explicit signal-based criteria for classifying failures as `flaky`, `ambiente`, or `bug`. Includes the timeout duration rubric (<5s/5-30s/>30s) as a subsection under `### Ambiente`. No historical run reading required — visual estimation only (D-06).

2. `## Retry vs Escalate` — If/Then rules for when to retry vs escalate. Escalation triggers on 2+ consecutive same-assertion failures or any P0. Includes 3-step retry protocol and explicit P0 rule (no silent retry) (D-07).

## Commit

542130a feat(06-02): add Error Classification and Retry vs Escalate to playwright-specialist
