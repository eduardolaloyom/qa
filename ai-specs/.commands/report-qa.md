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

5. **Cross-reference with sources**
   - Link failures to Linear tickets (deuda técnica, known bugs)
   - Note if failure is regression (compare against previous test run)

6. **Generate report** → dos archivos simultáneamente:

   **a) `QA/{CLIENT}/{DATE}/qa-report-{DATE}.md`** (lectura local / GitHub)
   - Use `templates/qa-report-template.md` as base
   - Include:
     - Resumen ejecutivo: modos completados, issues por severidad, veredicto
     - Cowork results: tabla por modo (A/B/C/D) con ✓/✗ por flujo
     - Playwright results: pass rate por spec
     - **Cobertura Ejecutada**: tabla con C1/C2/C3/C7/C5/C9/C10/A2/A3 — estado y Tier 1/2 ejecutados de N
     - **Staging Blockers**: tabla con casos no ejecutables, motivo, qué se necesita para desbloquearlos
     - Issues detallados: ID, severidad, descripción, pasos, evidencia
     - Gate de Rollout con veredicto final
     - Ship Readiness block para Slack

   **b) `public/qa-reports/{CLIENT}-{DATE}.html`** (dashboard GitHub Pages)
   - HTML autónomo, mismo contenido que el .md pero formateado
   - Estructura: header con cliente/fecha/veredicto, secciones colapsables por modo, tabla de issues con colores por severidad
   - Incluir enlace "← Dashboard" a `../`

   **c) Actualizar `public/manifest.json`** (manifest unificado B2B + APP)
   - Agregar entrada con estructura estándar:
     ```json
     { "client": "{CLIENT}", "date": "{DATE}", "file": "qa-reports/{CLIENT}-{DATE}.html", "verdict": "{LISTO/CON_CONDICIONES/NO_APTO/BLOQUEADO}", "score": {N}, "modes_done": ["A","B","C","D"], "platform": "b2b" }
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

## Recommendations
| Issue | Priority | Owner | Action |
|-------|----------|-------|--------|
| Payment auth | P0 | Backend | Check credential rotation |
| Maestro sync | P1 | Mobile | Re-record selectors |
| Banner render | P2 | Frontend | CSS regression? |

## Appendix
- [Test logs](test-results/)
- [Linked tickets](https://linear.app/...)
- [Failed assertions](...)
```

## Key Documents

- `templates/qa-report-template.md` — Report format and sections
- `templates/escalation-templates.md` — Escalation messaging
- `references/severity-matrix.md` — Issue severity definitions
