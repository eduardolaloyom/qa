#!/bin/bash
# QA completo para un cliente YOM
# Uso: ./tools/run-qa.sh Soprole

set -e

CLIENT="$1"
DATE=$(date +%Y-%m-%d)
QA_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ -z "$CLIENT" ]; then
  echo "Uso: ./tools/run-qa.sh <NombreCliente>"
  echo ""
  echo "Clientes disponibles:"
  python3 "$QA_ROOT/data/mongo-extractor.py" --output /dev/null 2>&1 | grep "  " || true
  exit 1
fi

echo "=== QA $CLIENT — $DATE ==="
echo ""

# 1. Extraer config de MongoDB
echo "📦 Extrayendo config de MongoDB..."
python3 "$QA_ROOT/data/mongo-extractor.py" --cliente "$CLIENT"
echo ""

# 1b. Regenerar clients.ts desde qa-matrix.json
echo "🔄 Regenerando clients.ts..."
python3 "$QA_ROOT/tools/sync-clients.py"
echo ""

# 2. Generar checklist
OUTPUT_DIR="$QA_ROOT/QA/$CLIENT/$DATE"
mkdir -p "$OUTPUT_DIR"
echo "📋 Generando checklist..."
python3 "$QA_ROOT/tools/checklist-generator.py" --source mongo --cliente "$CLIENT" --output "$OUTPUT_DIR/checklist.md"
echo ""

# 3. Playwright E2E + config validation
# global-teardown.ts auto-publica + commitea + pushea al terminar
CLIENT_LOWER=$(echo "$CLIENT" | tr '[:upper:]' '[:lower:]')
echo "🎭 Corriendo Playwright tests..."
cd "$QA_ROOT/tests/e2e"
npx playwright test --grep "$CLIENT_LOWER" 2>&1 || true
echo ""

# 4. Resumen
echo "=== RESUMEN ==="
echo "📋 Checklist: $OUTPUT_DIR/checklist.md"
echo "🎭 Playwright: dashboard actualizado en GitHub Pages"
echo "📊 Config MongoDB: data/qa-matrix.json"
echo ""
echo "Siguiente: revisar checklist y reportar issues"
