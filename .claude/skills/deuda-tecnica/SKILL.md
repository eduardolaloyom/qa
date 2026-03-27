---
name: deuda-tecnica
description: Consulta Linear y Notion para generar un reporte priorizado de deuda técnica pendiente con impacto QA y tests afectados. Usar cuando se necesite revisar estado de deuda técnica.
allowed-tools: Bash, Read, Grep, Glob, mcp__claude_ai_Linear__list_issues, mcp__claude_ai_Linear__get_issue, mcp__claude_ai_Linear__list_teams, mcp__claude_ai_Notion__notion-fetch, mcp__claude_ai_Notion__notion-search
---

# Reporte de Deuda Técnica QA

Genera un reporte priorizado de deuda técnica desde múltiples fuentes.

## Pasos

### 1. Consultar Linear
- Busca issues abiertos del equipo YOM con labels que contengan "tech-debt", "deuda", "bug", o "QA"
- Extrae: título, estado, asignado, prioridad, labels
- Filtra solo issues relevantes a QA (tests, validaciones, integraciones, datos)

### 2. Consultar Notion
- Busca la página de deuda técnica en el workspace de Engineering
- Extrae items pendientes con su estado y prioridad
- Referencia: la URL está en la memoria del proyecto (reference_deuda_tecnica.md)

### 3. Revisar checklists locales
- Lee `checklists/deuda-tecnica/checklist-deuda-tecnica-general.md`
- Lee `checklists/deuda-tecnica/checklist-deuda-tecnica-pagos.md`
- Identifica items marcados como PENDIENTE

### 4. Cruzar con tests existentes
- Para cada item de deuda, busca en `tests/e2e/` y `tests/app/flows/` si existe un test que lo cubra
- Usa `checklists/INDICE.md` como mapa de cobertura

### 5. Generar reporte
Formato de salida:

```markdown
# Reporte Deuda Técnica QA — {FECHA}

## Resumen
- Total items: X
- Con test automatizado: X
- Sin cobertura: X
- Críticos: X

## Detalle

| # | Item | Fuente | Severidad | Test existente | Asignado | Estado |
|---|------|--------|-----------|----------------|----------|--------|
| 1 | ... | Linear/Notion/Checklist | Alta/Media/Baja | spec.ts o N/A | Nombre | Abierto/En progreso |

## Recomendaciones
- Items sin cobertura que deberían tener test automatizado
- Items críticos que necesitan atención inmediata
```

Responder siempre en español.
