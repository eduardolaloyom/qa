#!/bin/bash
# Corre flows Maestro de cualquier cliente divididos en 3 batches
# Uso: ./tests/app/scripts/run-batch.sh <cliente> <1|2|3>
#
# Batches se dividen automáticamente en tercios por número de flow:
#   Batch 1 — primer tercio  (flows core)
#   Batch 2 — segundo tercio (features existentes)
#   Batch 3 — último tercio  (features nuevas/pendientes)
#
# Si existe tests/app/flows/<cliente>/batches.yaml, usa esa definición.
#
# Ejemplos:
#   ./tests/app/scripts/run-batch.sh caren 1
#   ./tests/app/scripts/run-batch.sh prinorte 2
#   ./tests/app/scripts/run-batch.sh bastien 3

set -euo pipefail

CLIENTE="${1:-}"
BATCH="${2:-}"

if [[ -z "$CLIENTE" || -z "$BATCH" || ! "$BATCH" =~ ^[123]$ ]]; then
    echo "Uso: $0 <cliente> <1|2|3>"
    echo ""
    echo "  1 — Batch core       (primer tercio de flows)"
    echo "  2 — Batch existentes (segundo tercio)"
    echo "  3 — Batch pendientes (último tercio)"
    echo ""
    echo "  Ejemplo: $0 caren 1"
    exit 1
fi

# ── Setup Java/ADB ────────────────────────────────────────────
JAVA_HOME_BREW=$(brew --prefix openjdk@17 2>/dev/null || true)
[ -n "$JAVA_HOME_BREW" ] && export JAVA_HOME="$JAVA_HOME_BREW"
[ -d "/Applications/Android Studio.app/Contents/jbr/Contents/Home" ] && \
    export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
export PATH="$HOME/Library/Android/sdk/platform-tools:$PATH"

QA_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
FLOWS_DIR="$QA_ROOT/tests/app/flows/$CLIENTE"
CONFIG_FILE="$QA_ROOT/tests/app/config/config.${CLIENTE}.yaml"
BATCHES_FILE="$FLOWS_DIR/batches.yaml"

# ── Validaciones ──────────────────────────────────────────────
if [ ! -d "$FLOWS_DIR" ]; then
    echo "❌ No hay flows para '$CLIENTE' en: $FLOWS_DIR"
    exit 1
fi
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config no encontrado: $CONFIG_FILE"
    exit 1
fi

# ── Cargar env vars del config ────────────────────────────────
ENV_ARGS=()
while IFS= read -r line; do
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// }" ]] && continue
    if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_.]*)[[:space:]]*:[[:space:]]*\"?([^\"]*)\"?[[:space:]]*$ ]]; then
        key="${BASH_REMATCH[1]}"
        val="${BASH_REMATCH[2]}"
        val="${val%"${val##*[! ]}"}"
        [[ -n "$val" && "$key" != "env" ]] && ENV_ARGS+=("--env" "${key}=${val}")
    fi
done < "$CONFIG_FILE"

# ── Determinar flows del batch ────────────────────────────────
ALL_FLOWS=($(ls "$FLOWS_DIR"/[0-9]*.yaml 2>/dev/null | sort))
TOTAL=${#ALL_FLOWS[@]}

if [ "$TOTAL" -eq 0 ]; then
    echo "❌ No hay flows numerados en $FLOWS_DIR"
    exit 1
fi

# Si existe batches.yaml, usarlo; si no, dividir en tercios
if [ -f "$BATCHES_FILE" ]; then
    BATCH_FLOWS=($(python3 - "$BATCHES_FILE" "$BATCH" << 'PY'
import sys, yaml
with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)
batch_key = f"batch{sys.argv[2]}"
flows = data.get(batch_key, data.get(f"batch_{sys.argv[2]}", []))
print('\n'.join(flows))
PY
))
    BATCH_FLOWS=("${BATCH_FLOWS[@]/#/$FLOWS_DIR/}")
    BATCH_NAME=$(python3 -c "
import yaml
with open('$BATCHES_FILE') as f:
    d = yaml.safe_load(f)
print(d.get('names', {}).get('batch$BATCH', 'Batch $BATCH'))
" 2>/dev/null || echo "Batch $BATCH")
else
    # Auto-dividir en tercios
    T1=$(( (TOTAL + 2) / 3 ))         # primer tercio (redondeo arriba)
    T2=$(( T1 + (TOTAL - T1 + 1) / 2 )) # segundo tercio

    case "$BATCH" in
        1) BATCH_FLOWS=("${ALL_FLOWS[@]:0:$T1}")
           BATCH_NAME="Core (flows 1-$T1 de $TOTAL)" ;;
        2) BATCH_FLOWS=("${ALL_FLOWS[@]:$T1:$((T2-T1))}")
           BATCH_NAME="Existentes (flows $((T1+1))-$T2 de $TOTAL)" ;;
        3) BATCH_FLOWS=("${ALL_FLOWS[@]:$T2}")
           BATCH_NAME="Pendientes (flows $((T2+1))-$TOTAL de $TOTAL)" ;;
    esac
fi

if [ ${#BATCH_FLOWS[@]} -eq 0 ]; then
    echo "⚠  No hay flows en el batch $BATCH para '$CLIENTE'"
    exit 0
fi

# ── Verificar device ──────────────────────────────────────────
if ! adb devices 2>/dev/null | grep -q "device$"; then
    echo "❌ No hay device Android conectado (USB debugging activado?)"
    exit 1
fi

# ── Correr batch ──────────────────────────────────────────────
CLIENTE_CAP=$(python3 -c "print('$CLIENTE'.capitalize())")
echo ""
echo "▶  $CLIENTE_CAP — Batch $BATCH: $BATCH_NAME"
echo "   ${#BATCH_FLOWS[@]} flows · $(date '+%H:%M')"
echo ""

PASSED=0
FAILED=0
FAILED_NAMES=()

for flow_path in "${BATCH_FLOWS[@]}"; do
    [ ! -f "$flow_path" ] && continue

    flow_name=$(python3 -c "
import yaml, sys
try:
    with open('$flow_path') as f:
        d = yaml.safe_load(f)
    print(d.get('name', '$flow_path') if isinstance(d, dict) else '$flow_path')
except:
    print('$(basename $flow_path)')
" 2>/dev/null || basename "$flow_path")

    printf "  %-55s" "$flow_name"

    if maestro test "${ENV_ARGS[@]}" "$flow_path" > /tmp/maestro_batch_out.txt 2>&1; then
        echo "✅ PASS"
        PASSED=$((PASSED+1))
    else
        echo "❌ FAIL"
        FAILED=$((FAILED+1))
        FAILED_NAMES+=("$flow_name")
        tail -3 /tmp/maestro_batch_out.txt | sed 's/^/       /'
    fi
done

echo ""
echo "──────────────────────────────────────────────────────"
echo "  Batch $BATCH ($CLIENTE_CAP): $PASSED PASS · $FAILED FAIL de ${#BATCH_FLOWS[@]} flows"
if [ ${#FAILED_NAMES[@]} -gt 0 ]; then
    echo ""
    echo "  Fallidos:"
    for n in "${FAILED_NAMES[@]}"; do
        echo "    ✗ $n"
    done
fi
echo ""

[ "$FAILED" -eq 0 ] && exit 0 || exit 1
