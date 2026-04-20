# Report QA

Generate comprehensive QA report for a client: test results summary, issue grouping, escalation recommendations.

## Usage

```bash
/report-qa Codelpa 2026-04-02
/report-qa "Seis Sur" 2026-03-30
```

## Steps

1. **Adopt QA Coordinator role** (see `ai-specs/.agents/qa-coordinator.md`)

2. **Gather Cowork results (sesiones A/B/C/D)**
   - Read `QA/{CLIENT}/{DATE}/cowork-session.md` (archivo único con todos los HANDOFFs del día)
   - Extract: flujos completados por modo, issues encontrados, contexto acumulado
   - Si no existe → indicar al usuario que ejecute los modos Cowork y agregue cada HANDOFF al archivo de sesión

3. **Gather Playwright results**
   - Locate `QA/{CLIENT}/{DATE}/` folder or read `public/grouped-report.html`
   - Parse pass/fail counts by spec (cart, prices, coupons, promotions, etc.)
   - Si no hay resultados Playwright → anotar "no ejecutado" en el reporte

4. **Extract and consolidate findings**
   - Unificar issues de todos los HANDOFFs (Cowork) + fallos Playwright
   - Categorizar: auth, payment, config, UI, data
   - Identificar P0/P1 bloqueantes vs. P2/P3 mejoras
   - Detectar duplicados (mismo bug reportado por Cowork y Playwright)
   - **Extraer Staging Blockers**: del campo `Staging blockers:` de cada HANDOFF, listar qué casos no pudieron ejecutarse y por qué
   - **Calcular cobertura**: del campo `Coverage:` de cada HANDOFF, sumar Tier 1 y Tier 2 ejecutados sobre total esperado
   - **Extraer mejoras al proceso**: del campo `Process improvements:` de cada HANDOFF, consolidar lista de mejoras sugeridas (tests faltantes, pasos no documentados, flags nuevos)

5. **Cross-reference with sources**
   - Link failures to Linear tickets (deuda técnica, known bugs)
   - Note if failure is regression (compare against previous test run)

6. **Generate report** → dos archivos simultáneamente:

   **a) `QA/{CLIENT}/{DATE}/qa-report-{DATE}.md`** (lectura local / GitHub)
   - Use `templates/qa-report-template.md` as base
   - Include:
     - **Resumen ejecutivo** (primeras 3 líneas bajo el título, ANTES de cualquier sección):
       `{VEREDICTO} | Score {N}/100 | {X} issues críticos (P0: {N}, P1: {M})`
       Ejemplo: `CON_CONDICIONES | Score 72/100 | 1 issue crítico (P0: 0, P1: 1)`
       Valores posibles de veredicto: LISTO, CON_CONDICIONES, NO_APTO, BLOQUEADO
       Seguido de `---` (línea horizontal separadora)
     - Cowork results: tabla por modo (A/B/C/D) con ✓/✗ por flujo
     - Playwright results: pass rate por spec
     - **Cobertura Ejecutada**: tabla con C1/C2/C3/C7/C5/C9/C10/A2/A3 — estado y Tier 1/2 ejecutados de N
     - **Staging Blockers**: tabla con casos no ejecutables, motivo, qué se necesita para desbloquearlos
     - **Mejoras sugeridas al proceso**: tabla con mejoras del campo `Process improvements:` — tipo (test/playbook/flag), descripción, acción (`/qa-improve {CLIENTE} {FECHA}`)
     - Issues detallados: ID, severidad, descripción, pasos, evidencia
     - **Accionables** (auto-generado por Claude, solo P0 y P1):
       Tabla 4 columnas: `Issue | Severidad | Dueño | Plazo`
       - Dueño: uno de `Tech`, `QA`, `PM` — asignar según tipo de issue:
         - Bug de app/API → Tech
         - Selector roto / flaky / cobertura de test → QA
         - Config de cliente, precio, dato incorrecto visible → PM
       - Plazo relativo a la fecha del run:
         - P0 → "0-1 días (urgente)"
         - P1 → "2-5 días (esta semana)"
       - P2 y P3 NO van en Accionables — continúan en sección "Issues detallados"
       Ejemplo:
       | Issue | Severidad | Dueño | Plazo |
       |-------|-----------|-------|-------|
       | Checkout falla para mobile | P1 | Tech | 2-5 días |
     - Gate de Rollout con veredicto final
     - Ship Readiness block para Slack

   **b) `public/qa-reports/{CLIENT}-{DATE}.html`** (dashboard GitHub Pages)
   - HTML autónomo, mismo contenido que el .md pero formateado
   - Resumen ejecutivo en las primeras 3 líneas visibles del body: `{VEREDICTO} | Score {N}/100 | {X} issues críticos (P0: {N}, P1: {M})` — mismo contenido que el .md, en un `<div class="executive-summary">` antes del primer `<section>`
   - Estructura: header con cliente/fecha/veredicto, secciones colapsables por modo, tabla de issues con colores por severidad
   - Incluir enlace "← Dashboard" a `../`

   **c) Actualizar `public/manifest.json`** (manifest unificado B2B + APP)
   - Agregar entrada con estructura estándar:
     ```json
     { "client": "{CLIENT}", "date": "{DATE}", "file": "qa-reports/{CLIENT}-{DATE}.html", "verdict": "{LISTO/CON_CONDICIONES/NO_APTO/BLOQUEADO}", "score": {N}, "modes_done": ["A","B","C","D"], "platform": "b2b", "environment": "{staging|production}" }
     (usar el ambiente confirmado al inicio de la sesión Cowork — staging = solopide.me, production = youorder.me)
     ```
   - No eliminar entradas anteriores, solo agregar la nueva al array `reports`
   - Si el archivo no existe, crearlo con estructura `{ "reports": [] }`

7. **Escalation (if needed)**
   - Use `templates/escalation-templates.md` for format
   - Identify P0 issues: timeline, impact, owner
   - Propose workarounds or rollback strategy

## Report Structure

```markdown
# QA Report: {CLIENT} — {DATE}

{VEREDICTO} | Score {N}/100 | {X} issues críticos (P0: {N}, P1: {M})

---

## Summary
- Tests run: X, Passed: Y (Z%)
- Environment: staging/production
- Duration: Xh Ym

## Results by Category
### Playwright E2E (17 clients)
- ✓ config-validation: 17/17 passed
- ✗ payment: 15/17 passed (Codelpa, Surtiventas failed)

### Maestro Flows
- ✓ 05-pedido: PASS
- ✗ 09-concurrencia: FAIL (selector timeout)

### Checklists
- ✓ Regresion: 28/30 (post-mortems checked)
- ⚠ Servicios: 12/15 (payment gateway pending)

## Critical Findings
1. **P0**: Payment gateway auth failing for Codelpa (YOM-182)
2. **P1**: Maestro flow 09 timeout on concurrent orders
3. **P2**: Config banner not rendering in admin (UI change?)

## Accionables

> Solo P0 y P1. P2/P3 continúan en Issues detallados.

| Issue | Severidad | Dueño | Plazo |
|-------|-----------|-------|-------|
| {descripción corta del issue} | P0/P1 | Tech/QA/PM | 0-1 días / 2-5 días |

## Appendix
- [Test logs](test-results/)
- [Linked tickets](https://linear.app/...)
- [Failed assertions](...)
```

## Key Documents

- `templates/qa-report-template.md` — Report format and sections
- `templates/escalation-templates.md` — Escalation messaging
- `references/severity-matrix.md` — Issue severity definitions
