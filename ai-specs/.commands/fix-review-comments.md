---
description: 'Review and fix GitHub PR review comments on the current branch'
argument-hint: '[optional PR number or URL]'
---

# /fix-review-comments — Fix PR Review Comments

You are executing the `/fix-review-comments` workflow. Your job is to fetch all unresolved review comments from the current PR and fix them one by one.

**User context (if provided):** $ARGUMENTS

## Phase 1: Identify the PR

1. Run `git branch --show-current` to get the current branch.
2. If $ARGUMENTS contains a PR number or URL, use that. Otherwise, detect the PR automatically:
   ```bash
   gh pr view --json number,title,url,headRefName
   ```
3. If no PR is found for the current branch, stop and inform the user.

## Phase 2: Fetch Review Comments

1. Fetch all **unresolved** review threads using GraphQL (this gives you the thread IDs needed to resolve them later):
   ```bash
   gh api graphql -f query='
     query($owner: String!, $repo: String!, $number: Int!) {
       repository(owner: $owner, name: $repo) {
         pullRequest(number: $number) {
           reviewThreads(first: 100) {
             nodes {
               id
               isResolved
               comments(first: 10) {
                 nodes {
                   id
                   path
                   line
                   body
                   author { login }
                   diffHunk
                 }
               }
             }
           }
         }
       }
     }
   ' -f owner='{owner}' -f repo='{repo}' -F number={number}
   ```
   Filter to only threads where `isResolved` is `false`.
2. Also fetch top-level PR review comments (review summaries):
   ```bash
   gh pr view {number} --json reviews --jq '.reviews[] | select(.state == "CHANGES_REQUESTED" or .state == "COMMENTED") | {author: .author.login, state: .state, body: .body}'
   ```
3. Group comments by file path. Ignore comments that are just approvals or simple acknowledgments (e.g., "LGTM", "looks good").
4. **Save the thread IDs** of each comment group so you can resolve them after fixing.
5. Present a summary to the user:
   ```
   Found X review comments on PR #N:
   - file/path.ts (Y comments)
   - other/file.ts (Z comments)
   ```

## Phase 3: Fix Each Comment

For each file with comments, in order:

1. Read the file.
2. Read each comment and understand what change is being requested.
3. Categorize the comment:
   - **Code change requested**: Fix the code as requested.
   - **Question/clarification**: If you can address it with a code comment or improvement, do so. If it requires human input, skip it and note it at the end.
   - **Nitpick/style**: Apply the suggested style change.
   - **Disagreement/discussion**: Skip — do NOT change code for comments that are discussions. Note them at the end.
4. Apply the fix, ensuring:
   - The fix addresses exactly what the reviewer asked for.
   - No unrelated changes are introduced.
   - All project standards are followed (reference `ai-specs/specs/` as needed).
   - Tests still pass after the change.

## Phase 4: Verify

**All checks below MUST pass before proceeding to commit. Do NOT skip any.**

1. Run linting and fix any errors:
   ```bash
   npm run lint
   ```
   If lint fails, fix all reported issues before continuing. Re-run until clean.
2. Run type checking (if the project uses TypeScript):
   ```bash
   npm run typecheck  # or npx tsc --noEmit
   ```
   Fix any type errors before continuing.
3. Run the project's test suite to make sure nothing is broken.
4. If any check fails, fix the issue and re-run all checks from step 1.

## Phase 5: Resolve Review Threads

After fixing each comment, resolve its review thread using the GraphQL API. Use the thread `id` saved from Phase 2:

```bash
gh api graphql -f query='
  mutation($threadId: ID!) {
    resolveReviewThread(input: { threadId: $threadId }) {
      thread { isResolved }
    }
  }
' -f threadId='{thread_id}'
```

- Only resolve threads where you actually addressed the comment (code change, style fix, or clarification added).
- Do NOT resolve threads you skipped (discussions, needs human input).

## Phase 6: Commit & Push

1. Stage all changed files.
2. Create a single commit with the format:
   ```bash
   git commit -m "$(cat <<'EOF'
   ♻️ refactor: address PR review comments

   Fixes review feedback on PR #<number>:
   - <brief description of each fix>
   EOF
   )"
   ```
   If changes span multiple concerns, split into multiple commits grouped logically.
3. Push to the current branch:
   ```bash
   git push
   ```

**CRITICAL: NEVER include "Co-Authored-By: Claude" or "Generated with Claude Code" in commit messages.**

## Phase 7: Report

Print a summary:

```
Done! Fixed review comments on PR #<number>

Addressed:
- <file>: <what was fixed>
- <file>: <what was fixed>

Skipped (needs human input):
- <file>: <comment summary and why it was skipped>

Verify: <PR URL>
```

If all comments were addressed, suggest the user can re-request review.
