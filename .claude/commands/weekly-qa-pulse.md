# Weekly QA Pulse

Genera un resumen ejecutivo del estado QA de todos los clientes activos: quién se testeó, qué issues quedaron abiertos, quién necesita QA urgente.

## Usage

```
/weekly-qa-pulse
/weekly-qa-pulse 2026-04-28
```

## Pasos

### 1. Adoptar rol
Adoptar el rol `weekly-qa-pulse` (ver `ai-specs/.agents/weekly-qa-pulse.md`).

### 2. Determinar ventana de tiempo

- Sin argumento → semana actual (lunes a hoy)
- Con fecha → semana que contiene esa fecha

### 3. Cargar fuentes de datos

**Reportes Cowork:**
```python
# Leer public/manifest.json → array reports
# Filtrar por fecha en la ventana
# Agrupar por client_slug → último score y veredicto
```

**Historia Playwright:**
```bash
ls public/history/*.json | sort | tail -7
# Para cada JSON: extraer stats.passed, stats.total, date
```

**Clientes activos:**
```python
# Leer data/qa-matrix-staging.json → clients
# Filtrar hasCustomer=true
```

**Issues Linear (best-effort):**
```bash
# Leer LINEAR_API_KEY de tests/e2e/.env
# Query: issues con label "qa" en estado != Done/Cancelled
# Si falla → marcar como "no disponible" y continuar
```

### 4. Calcular estado por cliente

Para cada cliente activo:
1. Buscar último reporte en `manifest.json` → score, veredicto, fecha
2. Calcular días desde último QA
3. Buscar issues abiertos en Linear
4. Asignar estado según umbrales del agente

### 5. Generar y mostrar el pulse

Mostrar el resumen en el formato definido en `ai-specs/.agents/weekly-qa-pulse.md`.

### 6. Guardar el pulse (opcional)

Si el usuario confirma → guardar en `QA/_pulse/YYYY-WNN.md`:

```bash
mkdir -p QA/_pulse
# Escribir el markdown del pulse
git add QA/_pulse/YYYY-WNN.md
git commit -m "chore(pulse): weekly QA pulse {SEMANA}"
git push
```

### 7. Cerrar

```
📊 Pulse generado — Semana {N}, {AÑO}

{N} clientes OK · {N} en ATENCIÓN · {N} CRÍTICOS · {N} SIN QA

Próximos pasos sugeridos:
1. /qa-plan-client {cliente_prioritario} — sin QA hace {N} días
2. /triage-playwright — {N} issues P1 sin resolver
```

## Reglas

- Linear es best-effort — si la API falla, el pulse igual se genera sin esa info
- Clients sin ningún reporte histórico → estado `⬜ SIN QA` automáticamente
- No lanzar tests ni generar reportes — solo leer y sintetizar
- Si hay P0 abierto en cualquier cliente → mostrarlo con 🚨 al inicio

## Archivos clave

- `public/manifest.json` — historial reportes Cowork
- `public/history/` — historial runs Playwright
- `data/qa-matrix-staging.json` — clientes activos
- `tests/e2e/.env` — LINEAR_API_KEY
- `ai-specs/.agents/weekly-qa-pulse.md` — rol a adoptar
