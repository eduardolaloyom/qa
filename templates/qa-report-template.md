# Reporte QA — {CLIENTE}

**Fecha:** {FECHA} · **Ejecutado por:** {NOMBRE} · **Fase PeM:** 8

---

## Resumen

| | |
|---|---|
| **Health Score** | **{SCORE}/100** |
| **Veredicto** | {LISTO / CON CONDICIONES / NO APTO} |
| Issues | {N} total: {N} Critical · {N} High · {N} Medium · {N} Low |
| Features testeadas | {N} de {N} activas |

---

## Health Score

| Categoría | Peso | Score | Ponderado |
|---|---|---|---|
| Flujos core | 25% | /100 | |
| Datos y catálogo | 20% | /100 | |
| Integraciones | 20% | /100 | |
| Features | 15% | /100 | |
| UX y visual | 10% | /100 | |
| Performance | 5% | /100 | |
| Consola/Errores | 3% | /100 | |
| Accesibilidad | 2% | /100 | |
| **TOTAL** | **100%** | | **{TOTAL}** |

---

## Issues

| ID | Severidad | Herramienta | Feature | Descripción | Escalado a | Estado |
|---|---|---|---|---|---|---|
| | | | | | | |

### Detalle de issues Critical/High

#### {CLIENTE}-QA-001: {Título}
- **Severidad / Categoría:** Critical · Bug
- **Herramienta / Feature:** B2B · Crear pedido
- **Descripción:** {qué pasa vs qué debería pasar}
- **Pasos:** 1. ... 2. ... 3. ...
- **Evidencia:**

| Antes | Después (si aplica) |
|---|---|
| ![antes](./screenshots/001-antes.png) | ![después](./screenshots/001-despues.png) |

- **Consola:** {Errores en DevTools asociados al issue, si los hay}
- **Escalado a:** {Nombre — Equipo}
- **Estado:** Abierto

---

## Cobertura Ejecutada

| Caso | Tier | Modo | Estado | Observación |
|------|------|------|--------|-------------|
| C1 Login | 1 | A | ✓ Completo / ✗ Falla / ⚠️ Parcial | |
| C2 Compra | 1 | A | ✓ Completo / ✗ Falla / ⚠️ Parcial | |
| C3 Precios | 1 | B | ✓ Completo / ✗ Falla / ⚠️ Parcial | |
| C7 Documentos | 1 | C | ✓ Completo / N/A (flag=false) | enablePaymentDocumentsB2B={valor} |
| C5 Recomendados | 2 | D | ✓ Completo / N/A | |
| C9 Seguimiento | 2 | D | ✓ Completo / N/A | |
| C10 Bloqueado | 2 | D | ✓ Completo / N/A | |
| A2 Gestión comercios | 2 | D | ✓ Completo / N/A | |
| A3 Config tienda | 2 | D | ✓ Completo / N/A | |

**Tier 1 ejecutados:** {X}/5 · **Tier 2 ejecutados:** {X}/4

---

## Staging Blockers

Casos que no pudieron ejecutarse por falta de datos en el ambiente staging. Requieren configuración antes del próximo ciclo QA.

| Caso | Bloqueador | Qué se necesita para desbloquearlo |
|------|-----------|-------------------------------------|
| | | |

> Si no hubo blockers → escribir "Ninguno".

---

## Gate de Rollout

| Criterio | Cumple |
|---|---|
| Zero Critical abiertos | ☐ |
| Zero High sin plan | ☐ |
| Compra B2B funcional | ☐ |
| Compra APP funcional | ☐ |
| Inyección ERP OK | ☐ |
| Catálogo completo | ☐ |
| Health Score >= 80% | ☐ |

**Veredicto:** {LISTO / CON CONDICIONES / NO APTO}

---

## Ship Readiness (resumen para escalar)

> Copiar este bloque al canal de Slack correspondiente.

| Métrica | Valor |
|---|---|
| Health Score | {SCORE}/100 |
| Issues encontrados | {N} total ({N} Critical, {N} High, {N} Medium, {N} Low) |
| Issues resueltos durante QA | {N} |
| Issues abiertos pendientes | {N} |
| Veredicto | {LISTO / CON CONDICIONES / NO APTO} |
| Bloqueantes | {Lista o "Ninguno"} |

---

## Próximos pasos

| Acción | Responsable | Plazo |
|---|---|---|
| | | |

---

*{FECHA} · {CLIENTE} · {NOMBRE}*
