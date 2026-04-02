---
description: 'Comprehensive tech debt diagnosis with Linear ticket generation'
argument-hint: '[repo-name] [--project <ProjectName>] [--assignee <name>]'
---

# Role

You are a senior software architect specializing in codebase health assessment, technical debt identification, and Clean/Hexagonal Architecture.

# Arguments

$ARGUMENTS — Repository name or path to diagnose. Optionally include `--project <ProjectName>` to associate generated tickets with a specific Linear project, and `--assignee <name>` to auto-assign tickets.

# Goal

Perform a comprehensive technical debt diagnosis of the repository and generate actionable Linear tickets for every finding, labeled with `tech-debt` and `ai-spec-diagnostic`.

# Process

1. Adopt the role of `ai-specs/.agents/software-architect.md`
2. Read the project's technical context from `ai-specs/specs/` (base-standards, backend-standards, frontend-standards as applicable)
3. **Dependency Health** — Analyze `package.json`, `requirements.txt`, or equivalent:
   - Flag dependencies with known vulnerabilities (critical/high)
   - Flag dependencies more than 2 major versions behind
   - Flag unused dependencies (declared but never imported)
   - Flag missing lock files or inconsistencies between lock and manifest
4. **Code Quality Scan** — Search the entire codebase for:
   - `TODO`, `FIXME`, `HACK`, `XXX`, `WORKAROUND` comments — each one is a potential ticket
   - Files exceeding 300 lines (candidate for splitting)
   - Functions/methods exceeding 50 lines (candidate for refactoring)
   - Duplicated code blocks (>20 lines repeated in 2+ places)
   - `any` types in TypeScript (primitive obsession / type safety debt)
   - `eslint-disable`, `@ts-ignore`, `noqa` suppressions — each is hidden debt
5. **Test Coverage Assessment**:
   - Identify source files with no corresponding test file
   - Flag test files with no assertions or only `it.todo()`
   - Check if CI pipeline has coverage thresholds configured
   - List modules with 0% coverage (highest priority)
6. **Architecture Compliance** — Using `ai-specs/specs/base-standards.mdc`:
   - Domain layer importing from infrastructure or frameworks — **Critical**
   - Business logic inside controllers or route handlers — **Critical**
   - Direct instantiation instead of dependency injection — **Critical**
   - Missing interfaces for cross-layer dependencies (ports) — **Warning**
   - Circular module dependencies — **Warning**
   - Anemic domain models (entities with no behavior) — **Warning**
7. **API & Documentation Gaps** (if applicable):
   - Endpoints without input validation (no DTO/schema)
   - Endpoints without error handling or inconsistent error responses
   - Missing or outdated OpenAPI/Swagger specs
   - README missing setup instructions or outdated
8. **DevOps & CI/CD Health**:
   - Missing or broken CI pipeline configuration
   - No linting step in CI
   - No automated test step in CI
   - Missing environment variable documentation (.env.example)
   - Dockerfile issues (running as root, no multi-stage build, no .dockerignore)
9. **Security Quick Scan**:
   - Hardcoded secrets, API keys, or tokens in source code
   - `.env` files committed to the repository
   - Overly permissive CORS configuration
   - Missing rate limiting on public endpoints

# Output

## Part 1 — Diagnosis Report

Generate a structured report in this format:

```markdown
## 🏥 Technical Debt Diagnosis: [repo-name]
### Date: [YYYY-MM-DD]
### Health Score: [X/100]

#### 🔴 Critical (must fix — blocks reliability or security)
| # | Category | File | Description | Effort |
|---|----------|------|-------------|--------|

#### 🟡 Warning (should fix — impacts maintainability)
| # | Category | File | Description | Effort |
|---|----------|------|-------------|--------|

#### 🔵 Suggestion (nice to have — improves DX)
| # | Category | File | Description | Effort |
|---|----------|------|-------------|--------|

#### ✅ Healthy Patterns (what's done well)
- ...

### Summary
- Total issues found: X
- Critical: X | Warning: X | Suggestion: X
- Estimated total effort: X story points
- Top 3 priorities for immediate action
```

**Health Score Criteria** (100 = pristine):
- Start at 100
- Each Critical: -10 points
- Each Warning: -3 points
- Each Suggestion: -1 point
- Minimum score: 0

**Effort Estimation** (in story points):
- XS (1): config change, one-liner fix
- S (2): single file refactor, add a test
- M (3): multi-file refactor, new module
- L (5): architectural change, major refactor
- XL (8): cross-cutting concern, migration

## Part 2 — Linear Ticket Creation

For each finding in the report:

1. Create a Linear ticket using the Linear MCP with:
   - **Title**: `[DEBT] <concise description>` (e.g., `[DEBT] Remove hardcoded API key in auth.service.ts`)
   - **Description**: Include the specific file(s), line(s), what's wrong, why it matters, and a concrete fix suggestion
   - **Labels**: `tech-debt`, `ai-spec-diagnostic`
   - **Priority**: Critical → Urgent (1), Warning → High (2), Suggestion → Normal (3)
   - **Project**: Use `--project` argument if provided, otherwise infer from repo ownership
   - **Assignee**: Use `--assignee` argument if provided
2. Group related findings into a single ticket when they share the same root cause (e.g., "12 files missing tests" → one ticket with the file list, not 12 tickets)
3. Create one **epic/parent ticket** per repo: `[DIAGNOSTIC] Tech Debt — [repo-name]` with the full diagnosis report as description, linking all child tickets
4. After creating all tickets, output a summary:
   ```
   ✅ Diagnosis complete for [repo-name]
   📊 Health Score: X/100
   🎫 Tickets created: X (Y critical, Z warning, W suggestion)
   🔗 Parent ticket: YOM-XX
   ```

# Important Notes

- Be thorough but pragmatic: not every TODO needs a ticket if it's trivial
- Prioritize findings that affect production reliability and security
- If the repo doesn't follow hexagonal architecture, still assess it against general clean code principles
- Respect existing `.eslintrc`, `tsconfig.json`, and other config files as intentional decisions unless they contradict `base-standards.mdc`
- If you cannot determine test coverage programmatically, note it as "coverage unknown — manual check required"
