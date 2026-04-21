#!/bin/bash
# QA Prinorte APP — 2 reintentos automáticos + intervención manual en el 3ro

export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"

ENV_FILE="tests/app/config/config.prinorte.yaml"
SESSION="tests/app/flows/prinorte-session.yaml"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

run_session() {
  local env_args=()
  while IFS= read -r line; do
    # Saltar comentarios y líneas vacías
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// }" ]] && continue
    # Extraer KEY: "VALUE" o KEY: VALUE
    if [[ "$line" =~ ^([A-Z_][A-Z0-9_]*):\ *\"?([^\"#]*)\"?$ ]]; then
      local key="${BASH_REMATCH[1]}"
      local value="${BASH_REMATCH[2]}"
      value="${value%"${value##*[! ]}"}"  # trim trailing spaces
      [[ -n "$value" ]] && env_args+=("-e" "${key}=${value}")
    fi
  done < "$ENV_FILE"
  maestro test --reinstall-driver "${env_args[@]}" "$SESSION"
}

export PATH="$HOME/Library/Android/sdk/platform-tools:$PATH"

# Deshabilitar Google Autofill/Password Manager en el emulador
adb shell settings put secure autofill_service null 2>/dev/null || true

echo -e "${YELLOW}=== QA Prinorte APP — $(date '+%Y-%m-%d %H:%M') ===${NC}"
echo ""

# Intento 1
echo -e "${CYAN}[Intento 1/3] Corriendo sesión...${NC}"
if run_session; then
  echo -e "${GREEN}✓ PASS${NC}"
  exit 0
fi

echo -e "${RED}✗ Falló intento 1 — reintentando automáticamente...${NC}"
echo ""

# Intento 2
echo -e "${CYAN}[Intento 2/3] Reintento automático...${NC}"
if run_session; then
  echo -e "${GREEN}✓ PASS${NC}"
  exit 0
fi

echo -e "${RED}✗ Falló intento 2${NC}"
echo ""

# Intento 3 — intervención manual
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}[Intento 3/3] Intervención manual${NC}"
echo -e "  Revisa el dispositivo, corrige lo que necesites."
echo -e "  Presiona ENTER cuando estés listo..."
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
read -r

echo -e "${CYAN}[Intento 3/3] Corriendo post-intervención...${NC}"
if run_session; then
  echo -e "${GREEN}✓ PASS${NC}"
  exit 0
fi

echo -e "${RED}✗ FAIL — falló después de 3 intentos${NC}"
exit 1
