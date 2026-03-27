---
name: test-coverage
description: Analiza cobertura de tests comparando flujos en qa-master-prompt.md contra specs Playwright y flows Maestro existentes. Identifica gaps de automatización.
allowed-tools: Read, Grep, Glob, Bash
---

# Análisis de Cobertura de Tests

Compara los casos de prueba definidos contra la automatización existente para encontrar gaps.

## Pasos

### 1. Extraer casos del master prompt
- Lee `qa-master-prompt.md` completo
- Identifica todos los test cases organizados por Tier (1, 2, 3) y categoría (C1-C8, V1, A1)
- Cuenta el total de casos definidos

### 2. Mapear tests automatizados existentes
- Glob `tests/e2e/**/*.spec.ts` — lista todas las specs Playwright
- Glob `tests/app/flows/*.yaml` — lista todos los flows Maestro
- Para cada archivo, lee las primeras líneas para entender qué flujos cubre
- En Playwright busca `test.describe` y `test(` para contar casos
- En Maestro cuenta los steps con assertions

### 3. Leer mapa de cobertura actual
- Lee `checklists/INDICE.md` para el estado actual documentado
- Identifica qué checklists tienen test automatizado asociado y cuáles no

### 4. Cruzar y detectar gaps
Para cada caso en qa-master-prompt.md, determina:
- Tiene spec Playwright → AUTOMATIZADO
- Tiene flow Maestro → AUTOMATIZADO (APP)
- Solo está en checklist manual → MANUAL
- No tiene nada → GAP

### 5. Generar reporte
Formato de salida:

```markdown
# Cobertura de Tests QA — {FECHA}

## Resumen
- Casos totales en master prompt: X
- Automatizados (Playwright): X ({%})
- Automatizados (Maestro): X ({%})
- Solo manual (checklists): X ({%})
- Sin cobertura (GAP): X ({%})

## Cobertura por categoría

| Categoría | Casos | Playwright | Maestro | Manual | Gap |
|-----------|-------|------------|---------|--------|-----|
| C1 Login | X | X | X | X | X |
| C2 Compra | X | X | X | X | X |
| ... | ... | ... | ... | ... | ... |

## Gaps prioritarios (sin ninguna cobertura)
1. {Caso} — {Categoría} — Sugerencia: {Playwright/Maestro/Checklist}
2. ...

## Recomendación de automatización
Casos manuales que deberían automatizarse, ordenados por impacto:
1. ...
```

Responder siempre en español.