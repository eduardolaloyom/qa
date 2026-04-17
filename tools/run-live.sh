#!/bin/bash
# run-live.sh — Run Playwright tests with live dashboard mode + auto-publish
# Usage: ./tools/run-live.sh [--grep "bastien"] [spec files...]
# Opens local server at http://localhost:8080 for live viewing
# After tests finish: publishes to dashboard and pushes to GitHub Pages

set -e
cd "$(dirname "$0")/.."

# Default: all b2b specs (relative to tests/e2e/ where playwright runs)
SPECS="${*:-b2b/}"
PORT=8080

echo "LIVE mode — dashboard at http://localhost:${PORT}"
echo ""

# Start local HTTP server for dashboard
python3 -m http.server $PORT --directory public &
SERVER_PID=$!
trap "kill $SERVER_PID 2>/dev/null; rm -f public/live.json public/live.json.tmp" EXIT

# Open browser (macOS)
sleep 0.5 && open "http://localhost:${PORT}" &

# Run tests with live reporter (capture exit code — don't fail on test failures)
cd tests/e2e
LIVE=1 npx playwright test $SPECS --project=b2b "$@" || PLAYWRIGHT_EXIT=$?
cd ../..

# ── Publish results to dashboard ──────────────────────────────────────────────
echo ""
echo "📤 Publicando resultados al dashboard..."
python3 tools/publish-results.py

# ── Git commit + push ─────────────────────────────────────────────────────────
DATE=$(date +%Y-%m-%d)
if git diff --quiet public/ 2>/dev/null && git diff --cached --quiet public/ 2>/dev/null; then
    echo "ℹ️  Sin cambios nuevos en public/ — skip push"
else
    git add public/
    git commit -m "chore: publish playwright results ${DATE}"
    git push || (git pull --rebase && git push)
    echo "✅ Dashboard actualizado en GitHub Pages"
fi

# Exit with playwright's exit code (0 = all passed, 1 = failures)
exit ${PLAYWRIGHT_EXIT:-0}
