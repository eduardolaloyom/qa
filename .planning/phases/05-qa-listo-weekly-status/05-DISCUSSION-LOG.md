# Phase 5: QA LISTO Weekly Status - Discussion Log

> **Audit trail only.** Decisions are captured in CONTEXT.md.

**Date:** 2026-04-21
**Phase:** 05-qa-listo-weekly-status
**Mode:** auto (todas las decisiones seleccionadas automáticamente con defaults recomendados)
**Areas discussed:** Thresholds, Cowork mapping, Script invocation, Reference data, Maestro N/A, BLOQUEADO boundary

---

## Thresholds del script

| Option | Description | Selected |
|--------|-------------|----------|
| Playwright ≥ 70% | Umbral bajo, muchos LISTOS | |
| Playwright ≥ 80% | Umbral riguroso, alcanzable | ✓ |
| Playwright ≥ 85% | Umbral alto, pocos LISTOS al inicio | |
| Maestro ≥ 50% | Permisivo | |
| Maestro ≥ 60% | Coherente con ejemplo UI-SPEC | ✓ |
| Maestro ≥ 70% | Exigente | |

**Auto-selected:** Playwright 80% / Maestro 60%
**Rationale:** 80% es alto pero los clientes estables muestran 95-100%; 60% para Maestro es conservador dado que el coverage de flows es menor.

---

## Cowork veredicto mapping

| Veredicto | Comportamiento | Selected |
|-----------|----------------|----------|
| LISTO | Permite LISTO si el resto pasa | ✓ |
| CON_CONDICIONES | PENDIENTE (no bloquea) | ✓ |
| CON_CONDICIONES | BLOQUEADO | |
| BLOQUEADO | Fuerza BLOQUEADO siempre | ✓ |
| Sin reporte | PENDIENTE | ✓ |
| Sin reporte | BLOQUEADO | |

**Auto-selected:** CON_CONDICIONES → PENDIENTE (no bloqueante)
**Rationale:** CON_CONDICIONES significa QA aprobó con observaciones — deployable con conciencia. Solo BLOQUEADO es incompatible con deploy.

---

## Script invocation (PROC-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Python script `tools/evaluate-qa-listo.py` | Mirrors publish-results.py pattern | ✓ |
| Shell script `tools/evaluate-qa-listo.sh` | Más simple pero menos legible | |
| Slash command `/qa-listo` | Requiere ai-specs/.commands/ adicional | |

**Auto-selected:** Python script `tools/evaluate-qa-listo.py`
**Rationale:** Consistente con el patrón establecido del repo (publish-results.py). Python permite lógica condicional legible. Sin slash command para PROC-03 — el script se invoca directo.

---

## Referencia temporal — datos a evaluar

| Option | Description | Selected |
|--------|-------------|----------|
| Dato más reciente por cliente | Independiente de la fecha de hoy | ✓ |
| Fecha del día (argumento `--date`) | Requiere argumento explícito | |
| Últimos N días (ventana temporal) | Complejo, ambiguo | |

**Auto-selected:** Dato más reciente por cliente
**Rationale:** Consistente con `last_tested` del dashboard. El script evalúa el mejor dato disponible por pipeline por cliente, sin requerir que todos hayan corrido el mismo día.

---

## Maestro N/A — determinación dinámica

| Option | Description | Selected |
|--------|-------------|----------|
| Lista hardcodeada de app-clients | Requiere mantenimiento manual | |
| Dinámica desde manifest.json | Self-correcting, cero mantenimiento | ✓ |

**Auto-selected:** Dinámica desde manifest — si no hay entradas `platform:app` para el cliente, es N/A.
**Rationale:** Evita sincronizar una lista paralela. Si un cliente gana flows Maestro, automáticamente deja de ser N/A.

---

## BLOQUEADO vs PENDIENTE boundary

| Option | Description | Selected |
|--------|-------------|----------|
| BLOQUEADO con cualquier dato faltante | Muy agresivo, muchos falsos positivos | |
| BLOQUEADO solo con bloqueo explícito | PENDIENTE es el default seguro | ✓ |

**Auto-selected:** BLOQUEADO solo explícito. PENDIENTE es el estado por defecto cuando hay datos insuficientes o condicionados.
**Rationale:** Un cliente sin Cowork aún no debería estar BLOQUEADO — está pendiente de evaluación. BLOQUEADO tiene connotación de "no deployar" que no aplica a datos faltantes.

---

## Claude's Discretion

- Nombres internos de funciones del script
- Argumento opcional `--dry-run`
- Logging a stderr vs stdout
- Estructura exacta de `ai-specs/specs/qa-listo-criteria.mdc`

## Deferred Ideas

- Notificaciones Slack cuando cliente queda BLOQUEADO → NOTIF-V2-01
- Integración Linear auto-crear tickets → LINEAR-V2-01
- Sort por estado en la tabla → mejora futura
- `--date` argumento para evaluación retrospectiva → mejora futura del script
