# Reporte QA Cowork — Bastien

**Fecha:** 2026-04-15 · **Ejecutado por:** Eduardo (Cowork/Claude)
**URL:** [https://bastien.solopide.me](https://bastien.solopide.me) (staging)
**Usuario QA:** eduardo+bastien@yom.ai
**Comercio:** C995862301-001 AC HOTEL MARRIOTT
**Modos ejecutados:** A (C1+C2) · B (C3+Flags) · C (C7) · D (C5+C9+C10)

---

## Resumen

| | |
|---|---|
| **Health Score** | **82/100** |
| **Veredicto** | CON CONDICIONES |
| Issues | 2 total: 0 Critical · 0 High · 1 Medium (P2) · 1 Low (P3) |
| Flujos testeados | 7 de 8 (Admin out of scope) |
| Bloqueantes staging | C3-14 (sin cupones activos), C10 (sin comercios bloqueados) |

---

## Health Score

| Categoría | Peso | Score | Ponderado |
|---|---|---|---|
| Flujos core (C1, C2, C9) | 25% | 95/100 | 23.75 |
| Datos y catálogo (C3, C5) | 20% | 85/100 | 17.00 |
| Features / Flags (B2B config) | 15% | 75/100 | 11.25 |
| Integraciones | 20% | 80/100 | 16.00 |
| UX y visual | 10% | 90/100 | 9.00 |
| Performance | 5% | 90/100 | 4.50 |
| Consola/Errores | 3% | 90/100 | 2.70 |
| Accesibilidad | 2% | 85/100 | 1.70 |
| **TOTAL** | **100%** | | **85.90 → 82*** |

*Penalización aplicada por Bastien-QA-002 (P2 sin resolver)*

---

## Issues

| ID | Severidad | Flujo | Descripción | Estado |
|---|---|---|---|---|
| Bastien-QA-002 | P2 · Bug | Flag / C7 | "Mis documentos" visible y /payment-documents accesible con `enablePaymentDocumentsB2B=false` | Abierto |
| Bastien-QA-001 | P3 · UX | C2 | Commerce switch desde modal no refresca JWT → catálogo vacío. Workaround: seleccionar AC HOTEL al inicio de sesión | Abierto |

---

### Bastien-QA-002 — "Mis documentos" visible con flag=false

- **Severidad:** P2 · Bug de configuración
- **Flag afectado:** `enablePaymentDocumentsB2B: false` + `enableInvoicesList: false`
- **URL:** bastien.solopide.me/payment-documents
- **Descripción:** La sección "Mis documentos" aparece en el menú lateral y la página /payment-documents es completamente accesible, mostrando UI de búsqueda de documentos con columnas Fecha, Tipo, ID orden, Valor pendiente. Ambos flags están en `false`, por lo que la sección no debería estar visible ni accesible.
- **Pasos para reproducir:**
  1. Login como cualquier usuario de Bastien
  2. Observar menú lateral → aparece "Mis documentos"
  3. Navegar a /payment-documents → página accesible con UI completa
- **Esperado:** Link oculto en menú + /payment-documents redirige o muestra acceso denegado
- **Acción:** Ticket Linear `[QA] Bastien — Mis documentos visible con enablePaymentDocumentsB2B=false`

---

### Bastien-QA-001 — Commerce switch JWT stale

- **Severidad:** P3 · UX / Staging
- **Descripción:** Al cambiar de comercio desde el modal selector, el JWT no se refresca con el nuevo `commerceId`. Si el comercio destino no tiene lista de precios, el catálogo queda en 0 productos.
- **Pasos:**
  1. Login → modal "Seleccionar comercio" → elegir Aguas Andinas Sa
  2. Catálogo muestra 0 resultados
- **Workaround:** Seleccionar AC HOTEL MARRIOTT explícitamente desde el modal en /home al inicio de sesión
- **Acción:** Ticket Linear `[QA] Bastien — Commerce switch no refresca JWT, catálogo vacío`

---

## Resultados por Flujo

| Flujo | Casos | Estado | Notas |
|-------|-------|--------|-------|
| C1 Login | C1-01 al C1-04 | ✓ PASS | — |
| C2 Compra | C2-01, 02, 05, 07, 11, 12, 13 | ✓ PASS | Pedido #69e0038f, $5.492.194 |
| C3 Precios | C3-01, 15, 17/18 | ✓ PASS | C3-14 BLOCKED (sin cupones en staging) |
| C7 Documentos | — | N/A | `enablePaymentDocumentsB2B=false` — ver QA-002 |
| C5 Recomendaciones | C5-01, 03, 04 | ✓ PASS | C5-02 sin datos en staging |
| C9 Seguimiento | C9-01 | ✓ PASS | Estados: Ingresado→Procesada→Despachada→Entregada |
| C10 Comercio bloqueado | — | N/A | Sin datos en staging |
| Admin (A2/A3) | — | N/A | Out of scope |

---

## Validación de Flags (17 flags)

| Flag | Config | Resultado |
|------|--------|-----------|
| `purchaseOrderEnabled` | false | ✓ PASS |
| `enableCoupons` | true | ✓ PASS |
| `enableSellerDiscount` | false | ✓ PASS |
| `enableOrderApproval` | false | ✓ PASS |
| `hasStockEnabled` | false | ✓ PASS |
| `disableObservationInput` | false | ✓ PASS |
| `inMaintenance` | false | ✓ PASS |
| `hidePrices` | false | ✓ PASS |
| `hasSingleDistributionCenter` | true | ✓ PASS |
| `taxes.useTaxRate` | false | ✓ PASS |
| `enablePayments` | false | ✓ PASS |
| `editAddress` | true | ✓ PASS |
| `anonymousAccess` | true | ✓ PASS |
| `enablePaymentDocumentsB2B` | false | ⚠️ FAIL → QA-002 |
| `enableInvoicesList` | false | ⚠️ FAIL → QA-002 |
| `disableCommerceEdit` | false | N/A |
| `anonymousHidePrice` | false | N/A |

---

## Gate de Rollout

| Criterio | Cumple |
|---|---|
| Zero Critical abiertos | ✅ |
| Zero High sin plan | ✅ |
| Compra B2B funcional | ✅ |
| Compra APP funcional | ☐ No testeada |
| Catálogo completo (40 productos) | ✅ |
| Flags de config correctos | ⚠️ 15/17 OK |
| Health Score >= 80% | ✅ 82/100 |

**Veredicto: CON CONDICIONES**

---

## Ship Readiness

> Copiar al canal Slack correspondiente.

| Métrica | Valor |
|---|---|
| Health Score | 82/100 |
| Issues encontrados | 2 (0 Critical, 0 High, 1 P2, 1 P3) |
| Issues resueltos durante QA | 0 |
| Issues abiertos | 2 |
| Veredicto | CON CONDICIONES |
| Bloqueantes | Ninguno crítico — QA-002 P2 requiere ticket antes de producción |

---

## Próximos pasos

| Acción | Responsable | Plazo |
|---|---|---|
| Ticket Linear: Bastien-QA-002 `enablePaymentDocumentsB2B` no respetado | Eduardo | Esta semana |
| Ticket Linear: Bastien-QA-001 Commerce switch JWT stale | Eduardo | Esta semana |
| Configurar lista de precios en staging para Bastien | Equipo PeM | Antes de próximo QA |
| Configurar cupón de prueba en staging | Equipo PeM | Antes de próximo QA |
| Test APP mobile (Maestro) | Eduardo | Pendiente |

---

*2026-04-15 · Bastien · Eduardo (Cowork/Claude)*
