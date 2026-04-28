#!/usr/bin/env bash
# Daily repo cleanup — removes test artifacts and stale screenshots.
# Safe to run any time; does not touch source code, specs, or QA reports.

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== QA repo cleanup — $(date '+%Y-%m-%d %H:%M') ==="

# 1. Remove .DS_Store files anywhere in the repo
DS_COUNT=$(find . -name ".DS_Store" -not -path "./.git/*" | wc -l | tr -d ' ')
if [ "$DS_COUNT" -gt 0 ]; then
  find . -name ".DS_Store" -not -path "./.git/*" -delete
  echo "✓ Removed $DS_COUNT .DS_Store files"
fi

# 2. Clear local test-results (gitignored, regenerated each run)
if [ -d "test-results" ] && [ "$(ls -A test-results 2>/dev/null)" ]; then
  rm -rf test-results/*
  echo "✓ Cleared test-results/"
fi
if [ -d "tests/e2e/test-results" ] && [ "$(ls -A tests/e2e/test-results 2>/dev/null)" ]; then
  rm -rf tests/e2e/test-results/*
  echo "✓ Cleared tests/e2e/test-results/"
fi

# 3. Prune public/data/*.png older than 30 days (failure screenshots accumulate)
PRUNED=$(find public/data -name "*.png" -mtime +30 2>/dev/null | wc -l | tr -d ' ')
if [ "$PRUNED" -gt 0 ]; then
  find public/data -name "*.png" -mtime +30 -delete
  echo "✓ Pruned $PRUNED failure screenshots older than 30 days"
fi

# 4. Remove empty QA subdirectories (no files = no value)
EMPTY_COUNT=0
while IFS= read -r dir; do
  if [ -z "$(ls -A "$dir" 2>/dev/null)" ]; then
    rmdir "$dir"
    EMPTY_COUNT=$((EMPTY_COUNT + 1))
  fi
done < <(find QA -mindepth 1 -type d 2>/dev/null | sort -r)
[ "$EMPTY_COUNT" -gt 0 ] && echo "✓ Removed $EMPTY_COUNT empty QA directories"

# 5. Commit and push if there are tracked changes
if ! git diff --quiet HEAD -- public/data/ 2>/dev/null || git ls-files --deleted | grep -q .; then
  git add -A public/data/ || true
  git add -u
  git commit -m "chore(cleanup): prune stale screenshots and artifacts" || true
  git push || true
  echo "✓ Changes committed and pushed"
else
  echo "✓ No tracked changes to commit"
fi

echo "=== Done ==="
