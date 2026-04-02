---
description: 'Full workflow - analyze, document, commit, and create PR'
argument-hint: '[optional context about changes]'
---

# /ship-it — Full Ship Workflow

You are executing the `/ship-it` workflow. This is a fully autonomous pipeline: analyze → document → commit → push → PR. Do NOT pause to ask the user for confirmation at any step. Only stop if there's an actual error or conflict.

**User context (if provided):** $ARGUMENTS

## Phase 1: Analyze

1. Run `git status` to see all modified, staged, and untracked files.
2. Run `git diff` (unstaged) and `git diff --cached` (staged) to understand all changes.
3. Run `git log --oneline -10` and `git branch --show-current` to understand current state.
4. Run `git log main..HEAD --oneline` to see commits already on this branch (if not on main).

## Phase 2: Branch

If the current branch is `main`:

- Create a new branch automatically based on the nature of changes:
  - New features → `feat/<short-description>`
  - Bug fixes → `fix/<short-description>`
  - Refactoring → `refactor/<short-description>`
  - Docs only → `docs/<short-description>`
  - Config/maintenance → `chore/<short-description>`
- Use kebab-case, keep it short (2-4 words max).
- Run `git checkout -b <branch-name>`.

If already on a feature branch, stay on it.

## Phase 3: Documentation

Analyze the diff against main. If there are significant changes (new endpoints, new DB tables, new features, changed architecture), update documentation:

- **ai-specs/specs/base-standards.mdc**: Update Implementation Status, Key API Endpoints, Database Schema sections as needed.
- **README.md**: Update feature lists, environment variables, or setup instructions as needed.

Skip this phase if changes are minor (bug fixes, small refactors, config tweaks).

## Phase 4: Commit

Group all changes into atomic commits by concern. Stage and commit each group separately.

**Grouping strategy:**

- `apps/frontend/` → frontend commit(s)
- `apps/backend/src/auth/` → auth commit
- `apps/backend/src/quotes/` → quotes commit
- `apps/backend/src/boostr/` → boostr commit
- `apps/backend/src/products/` → products commit
- `apps/backend/prisma/` → db commit
- `packages/shared-types/` → shared-types commit
- `ai-specs/` → specs commit
- `*.md` files, docs → docs commit
- Config files (root `*.config.*`, `.eslintrc`, `turbo.json`, etc.) → config commit
- Test files → commit with their related feature, or separate test commit

**All commit messages, branch names, and PR content MUST be in English** (per base-standards.mdc).

**Commit message format:** `<gitmoji> <type>(<scope>): description`

Gitmoji reference:

- ✨ feat — New feature
- 🐛 fix — Bug fix
- 📝 docs — Documentation
- ♻️ refactor — Refactoring
- 🚀 perf — Performance
- ✅ test — Tests
- 🔧 chore — Configuration/maintenance
- 🗃️ db — Database changes
- 💄 ui — UI/style changes
- 🏷️ types — Type annotations
- 🔥 remove — Remove code/files
- ⬆️ deps — Upgrade dependencies

**CRITICAL: NEVER include "Co-Authored-By: Claude" or "Generated with Claude Code" in commit messages.**

Use HEREDOC format for commit messages:

```bash
git commit -m "$(cat <<'EOF'
<gitmoji> <type>(<scope>): description
EOF
)"
```

If there's only one logical group, make a single commit. Don't over-split.

## Phase 5: Push & PR

1. Push the branch: `git push -u origin <branch-name>`
2. Create the PR using `gh pr create`:

```bash
gh pr create --title "<concise title>" --body "$(cat <<'EOF'
## Summary
<bullet points summarizing all changes>

## Changes
<list of commits with their messages>

## Test plan
<checklist of what to test>
EOF
)"
```

- PR title: Short (under 70 chars), describes the overall change.
- PR body: Summary bullets, list of commits, and test plan.
- Target branch: `main`

3. Output the PR URL to the user.

## Output

When done, print a summary:

```
✅ Ship complete!
🌿 Branch: <branch-name>
📝 Commits: <number of commits created>
🔗 PR: <pr-url>
```
