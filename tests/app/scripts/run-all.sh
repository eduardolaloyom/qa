#!/bin/bash
# Ejecuta todos los smoke tests de la APP
# Uso: ./scripts/run-all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FLOWS_DIR="$SCRIPT_DIR/../flows"
CONFIG_DIR="$SCRIPT_DIR/../config"
ENV_FILE="$CONFIG_DIR/env.yaml"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar que env.yaml existe
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: $ENV_FILE no encontrado${NC}"
    echo "Copia config/env.example.yaml a config/env.yaml y completa los datos"
    exit 1
fi

# Verificar que Maestro está instalado
if ! command -v maestro &> /dev/null; then
    echo -e "${RED}Error: Maestro no instalado${NC}"
    echo "Instalar con: curl -Ls 'https://get.maestro.mobile.dev' | bash"
    exit 1
fi

# Verificar emulador o dispositivo conectado
if ! adb devices | grep -q "device$"; then
    echo -e "${RED}Error: No hay emulador o dispositivo conectado${NC}"
    echo "Iniciar emulador: emulator -avd yom_test"
    exit 1
fi

echo -e "${YELLOW}=== YOM APP Smoke Tests ===${NC}"
echo ""

PASSED=0
FAILED=0
TOTAL=0

# Ejecutar cada flujo (excluyendo helpers)
for flow in "$FLOWS_DIR"/[0-9]*.yaml; do
    TOTAL=$((TOTAL + 1))
    FLOW_NAME=$(basename "$flow" .yaml)

    echo -n "[$FLOW_NAME] "

    if maestro test --env "$ENV_FILE" "$flow" > /tmp/maestro-$FLOW_NAME.log 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Log: /tmp/maestro-$FLOW_NAME.log"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo -e "${YELLOW}=== Resultados ===${NC}"
echo -e "Total: $TOTAL | ${GREEN}Passed: $PASSED${NC} | ${RED}Failed: $FAILED${NC}"

if [ $FAILED -gt 0 ]; then
    exit 1
fi
