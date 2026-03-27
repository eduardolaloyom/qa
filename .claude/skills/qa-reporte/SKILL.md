---
name: qa-reporte
description: Genera reporte semanal de QA — tests agregados, bugs encontrados, deuda cerrada, cobertura actual. Usar al final de cada semana o cuando se necesite un resumen.
allowed-tools: Bash, Read, Grep, Glob, mcp__claude_ai_Linear__list_issues, mcp__claude_ai_Linear__get_issue, mcp__claude_ai_Slack__slack_search_public_and_private
---

# Reporte Semanal QA

Genera un resumen del trabajo QA de la última semana.

## Pasos

### 1. Cambios en el repo (última semana)
Ejecutar:
```
git log --since="1 week ago" --oneline --stat
```
- Contar specs Playwright nuevos o modificados (`tests/e2e/**/*.spec.ts`)
- Contar flows Maestro nuevos o modificados (`tests/app/flows/*.yaml`)
- Contar checklists nuevos o modificados (`checklists/**/*.md`)
- Identificar otros cambios relevantes (tools, templates, data)

### 2. Issues en Linear
- Buscar issues cerrados esta semana con labels QA, tech-debt, bug
- Buscar issues nuevos creados esta semana
- Contar por estado: cerrados, en progreso, nuevos

### 3. Bugs en Slack
- Buscar en canales #tech, #engineering, #bugs mensajes de la última semana que mencionen "bug", "error", "fix", "broken", "falla"
- Resumir los bugs reportados y su estado

### 4. Cobertura actual
- Contar total de specs en `tests/e2e/` (grep -c "test(" en cada spec)
- Contar total de flows en `tests/app/flows/`
- Contar total de casos en checklists (grep PENDIENTE/PASS/FAIL)

### 5. Generar reporte
Usar como base `templates/qa-report-template.md` y adaptar:

```markdown
# Reporte QA Semanal — Semana del {FECHA_INICIO} al {FECHA_FIN}

## Resumen ejecutivo
{2-3 líneas con lo más importante de la semana}

## Tests agregados/modificados
| Tipo | Nuevos | Modificados | Total actual |
|------|--------|-------------|--------------|
| Playwright specs | X | X | X |
| Maestro flows | X | X | X |
| Checklist cases | X | X | X |

## Issues Linear
| Estado | Cantidad |
|--------|----------|
| Cerrados esta semana | X |
| En progreso | X |
| Nuevos esta semana | X |

## Bugs reportados en Slack
1. {Bug} — {Canal} — {Estado}
2. ...

## Cobertura actual
- E2E Playwright: {X} specs, {Y} test cases
- APP Maestro: {X} flows
- Checklists: {X} casos ({Y}% PASS, {Z}% PENDIENTE, {W}% FAIL)

## Próximos pasos
- {Recomendaciones basadas en los datos}
```

Responder siempre en español.