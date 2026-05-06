#!/bin/bash
# Corre flows Caren por tanda (batch)
# Uso: ./tests/app/scripts/run-caren-batch.sh <1|2|3>
#
# Batch 1 — Core      (01-07)  : login, pedido, features, lista, historial  ~15 min
# Batch 2 — Alcance   (08-15)  : búsqueda, catálogo, CD, fecha, cobranza    ~20 min
# Batch 3 — Pendientes(16-30)  : features no implementadas aún               ~20 min

set -euo pipefail

BATCH="${1:-}"
if [[ -z "$BATCH" || ! "$BATCH" =~ ^[123]$ ]]; then
    echo "Uso: $0 <1|2|3>"
    echo ""
    echo "  1 — Core      (01-07)  login, pedido, features, lista, historial"
    echo "  2 — Alcance   (08-15)  búsqueda, catálogo, CD, fecha, cobranza"
    echo "  3 — Pendientes(16-30)  features no implementadas aún"
    exit 1
fi

# ── Setup ─────────────────────────────────────────────────────
JAVA_HOME_BREW=$(brew --prefix openjdk@17 2>/dev/null || true)
[ -n "$JAVA_HOME_BREW" ] && export JAVA_HOME="$JAVA_HOME_BREW"
[ -d "/Applications/Android Studio.app/Contents/jbr/Contents/Home" ] && \
    export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
export PATH="$HOME/Library/Android/sdk/platform-tools:$PATH"

QA_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
CONFIG="$QA_ROOT/tests/app/config/config.caren.yaml"
FLOWS="$QA_ROOT/tests/app/flows/caren"

if [ ! -f "$CONFIG" ]; then
    echo "❌ Config no encontrado: $CONFIG"
    exit 1
fi

# Leer env vars del config yaml
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
done < "$CONFIG"

# ── Definición de batches ──────────────────────────────────────
case "$BATCH" in
1)
    BATCH_NAME="Core"
    FLOWS_LIST=(
        "01-comercios-disponibles.yaml"
        "02-pedido.yaml"
        "04-features.yaml"
        "06-lista-todos-comercios.yaml"
        "07-historial-pedidos.yaml"
    )
    ;;
2)
    BATCH_NAME="Alcance"
    FLOWS_LIST=(
        "03-comercios-bloqueados.yaml"
        "05-bloqueado-tomador-pedido.yaml"
        "05b-bloqueado-carrito-limpio.yaml"
        "08-busqueda-comercios.yaml"
        "09-datos-comercio.yaml"
        "10-catalogo-detallado.yaml"
        "11-selector-cd.yaml"
        "12-fecha-despacho.yaml"
        "13-descuento-vendedor.yaml"
        "14-cobranza.yaml"
        "15-tareas.yaml"
    )
    ;;
3)
    BATCH_NAME="Pendientes"
    FLOWS_LIST=(
        "16-costo-despacho.yaml"
        "17-compartir-pedido.yaml"
        "18-promociones-catalogo.yaml"
        "19-descuentos-volumen.yaml"
        "20-packs-productos.yaml"
        "21-medios-pago.yaml"
        "22-recomendaciones.yaml"
        "23-estado-crediticio.yaml"
        "24-leads.yaml"
        "25-labels-productos.yaml"
        "26-listas-precio.yaml"
        "27-indicadores-venta.yaml"
        "28-geolocalizacion.yaml"
        "29-cambio-contrasena.yaml"
        "30-active-directory.yaml"
    )
    ;;
esac

# ── Verificar device ──────────────────────────────────────────
if ! adb devices 2>/dev/null | grep -q "device$"; then
    echo "❌ No hay device Android conectado (USB debugging activado?)"
    exit 1
fi

echo ""
echo "▶  Caren — Batch $BATCH: $BATCH_NAME"
echo "   ${#FLOWS_LIST[@]} flows · $(date '+%H:%M')"
echo ""

PASSED=0
FAILED=0
FAILED_NAMES=()

for flow_file in "${FLOWS_LIST[@]}"; do
    flow_path="$FLOWS/$flow_file"
    flow_num="${flow_file%%-*}"

    if [ ! -f "$flow_path" ]; then
        echo "  ⚠  No encontrado: $flow_file — saltando"
        continue
    fi

    # Nombre legible desde el YAML
    flow_name=$(python3 -c "
import yaml, sys
with open('$flow_path') as f:
    d = yaml.safe_load(f)
print(d.get('name', '$flow_file') if isinstance(d, dict) else '$flow_file')
" 2>/dev/null || echo "$flow_file")

    printf "  %-55s" "$flow_name"

    if maestro test "${ENV_ARGS[@]}" "$flow_path" > /tmp/maestro_out.txt 2>&1; then
        echo "✅ PASS"
        PASSED=$((PASSED+1))
    else
        echo "❌ FAIL"
        FAILED=$((FAILED+1))
        FAILED_NAMES+=("$flow_name")
        # Mostrar última línea del error
        tail -3 /tmp/maestro_out.txt | sed 's/^/       /'
    fi
done

echo ""
echo "──────────────────────────────────────────────────────"
echo "  Batch $BATCH ($BATCH_NAME): $PASSED PASS · $FAILED FAIL"
if [ ${#FAILED_NAMES[@]} -gt 0 ]; then
    echo ""
    echo "  Flows fallidos:"
    for n in "${FAILED_NAMES[@]}"; do
        echo "    ✗ $n"
    done
fi
echo ""

[ "$FAILED" -eq 0 ] && exit 0 || exit 1
