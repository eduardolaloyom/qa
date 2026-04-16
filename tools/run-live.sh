#!/bin/bash
# run-live.sh — Run Playwright tests with live dashboard mode
# Usage: ./tools/run-live.sh [--grep "bastien"] [spec files...]
# Opens local server at http://localhost:8080 for live viewing

set -e
cd "$(dirname "$0")/.."

# Default: all b2b specs
SPECS="${*:-tests/e2e/b2b/}"
PORT=8080

echo "LIVE mode — dashboard at http://localhost:${PORT}"
echo ""

# Start local HTTP server for dashboard
python3 -m http.server $PORT --directory public &
SERVER_PID=$!
trap "kill $SERVER_PID 2>/dev/null; rm -f public/live.json" EXIT

# Open browser (macOS)
sleep 0.5 && open "http://localhost:${PORT}" &

# Run tests with live reporter
cd tests/e2e
LIVE=1 npx playwright test $SPECS --project=b2b "$@"
