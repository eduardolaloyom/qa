# Sesión Cowork — Bastien — 2026-04-15

---

## MODO A — C1 Login + C2 Flujo de Compra

### [C1] Login y Acceso

```
[C1] LOGIN — Bastien
C1-01 Carga homepage: PASS — bastien.solopide.me carga correctamente
C1-02 Login con creds: PASS — eduardo+bastien@yom.ai / laloyom123
C1-03 Redirect post-login: PASS — redirige a /products
C1-04 Sesión persistente: PASS — JWT en localStorage, comercio activo
```

### [C2] Flujo de Compra

**Comercio usado:** C995862301-001 Ac Hotel Marriott (seleccionado desde modal al inicio)
**Nota:** Al seleccionar AC HOTEL desde el modal, precios reales disponibles ($6.434–$35.530). Comercio por defecto del QA user (69dfe43b) mostraba $0 — hay que seleccionar AC HOTEL explícitamente.

```
[C2] FLUJO DE COMPRA — Bastien (comercio: AC HOTEL MARRIOTT)
C2-01 Catálogo carga: PASS — 40 productos, precios reales visibles ($6.434, $23.424, $35.530...)
C2-02 Búsqueda: PASS — ?name=Brocha retorna resultados correctos
C2-05 Agregar al carrito: PASS — 30 productos agregados, total $5.492.194
C2-06 Cantidad mínima: N/A — showMinOne=false, sin restricción visible
C2-07 Incrementar/decrementar cantidad: PASS — controles +/- funcionales en carrito
C2-11 Crear pedido: PASS — pedido #69e0038f confirmado, total $5.492.194, redirect a /confirmation/
C2-12 Carrito limpio post-pedido: PASS — badge muestra 0 después de confirmar
C2-13 En historial: PASS — pedido visible en /orders, estado "Ingresado", valor $5.492.194
```

**Issues Modo A:**
- `Bastien-QA-001` | P3 | C2 | Commerce selection con JWT stale → catálogo queda en 0 productos al cambiar de comercio desde el selector modal si el comercio destino no tiene lista de precios.
  - Pasos: Login → modal "Seleccionar comercio" → elegir Aguas Andinas Sa → catálogo muestra 0 resultados
  - Workaround: seleccionar AC HOTEL MARRIOTT explícitamente en el modal desde /home al inicio de sesión

---

## MODO B — C3 Precios & Flags

### [C3] Precios y Descuentos

```
[C3] PRECIOS Y DESCUENTOS — Bastien (comercio: AC HOTEL MARRIOTT)
C3-01 Precio base visible: PASS — precios con formato correcto ($6.434, $23.424, $35.530). hidePrices=false confirmado.
C3-02 Precio con descuento: N/A — sin productos con badge de promoción ni precio tachado para este comercio
C3-14 Cupón válido: BLOCKED — coupons=[] en staging, no hay cupones activos para probar
C3-15 Cupón inválido: PASS — mensaje "Cupón inválido" mostrado correctamente, total sin cambio
C3-17/18 Precios por segmento: PASS — precios coherentes con el comercio AC HOTEL (lista de precios activa)
```

### Validación de Flags

| Flag | Valor config | UI observada | Resultado |
|------|-------------|--------------|-----------|
| `purchaseOrderEnabled` | false | Sin campo OC en carrito | ✓ PASS |
| `enableCoupons` | true | "Ingresar cupón" visible en carrito | ✓ PASS |
| `enableSellerDiscount` | false | Sin campo descuento vendedor | ✓ PASS |
| `enableOrderApproval` | false | Sin botón "Aprobar" en /orders | ✓ PASS |
| `hasStockEnabled` | false | Sin indicador de stock en tarjetas | ✓ PASS |
| `disableObservationInput` | false | Campo "ingresar observaciones" presente en carrito | ✓ PASS |
| `inMaintenance` | false | Sitio accesible, sin página de mantenimiento | ✓ PASS |
| `hidePrices` | false | Precios visibles con valores reales | ✓ PASS |
| `hasSingleDistributionCenter` | true | Sin botón "Ver stock / Centros" en tarjetas | ✓ PASS |
| `taxes.useTaxRate` | false | Sin IVA desglosado, impuestos $0 en facturación | ✓ PASS |
| `enablePayments` | false | Sin opción de pago activa en checkout | ✓ PASS |
| `editAddress` | true | Dirección visible en checkout (Andres Bello 2447 P.7, Providencia) | ✓ PASS |
| `enablePaymentDocumentsB2B` | **false** | "Mis documentos" visible en menú + /payment-documents accesible | ⚠️ FAIL |
| `enableInvoicesList` | **false** | Mismo — nav muestra sección documentos | ⚠️ FAIL |
| `anonymousAccess` | true | Catálogo visible sin sesión (confirmado — /products accesible sin token) | ✓ PASS |
| `disableCommerceEdit` | false | No verificado | N/A |

**Issues Modo B:**
- `Bastien-QA-002` | P2 | Flag | "Mis documentos" en nav y /payment-documents accesible cuando `enablePaymentDocumentsB2B=false` y `enableInvoicesList=false`
  - URL: bastien.solopide.me/payment-documents
  - Esperado: link oculto en menú + /payment-documents redirige o muestra acceso denegado
  - Actual: link visible, página accesible con UI completa de búsqueda de documentos

---

## MODO C — C7 Documentos Tributarios

```
[C7] DOCUMENTOS TRIBUTARIOS — Bastien
enablePaymentDocumentsB2B: false → C7 N/A en su totalidad

NOTA: Aunque el flag es false, se detectó que /payment-documents es accesible
y "Mis documentos" aparece en el menú lateral → Bastien-QA-002 (P2) registrado en Modo B.
```

---

## MODO D — Tier 2 (B2B only, sin Admin)

### [C5] Canasta base / Recomendaciones

```
[C5] RECOMENDACIONES — Bastien
C5-01 Sección "Recomendados" en nav: PASS — link existe y es navegable
C5-02 Productos sugeridos: N/A — ?suggestions=true devuelve 0 resultados (sin datos en staging)
C5-03 Sección "Ofertas": PASS — ?promotions=true retorna 40 productos con sección visible
C5-04 Sección "Destacados": PASS — link y estructura UI correctos
```

### [C9] Seguimiento de Pedido

```
[C9] SEGUIMIENTO DE PEDIDO — Bastien
C9-01: PASS — pedido #69e0038f accesible en /orders/69e0038f49e61a9c00a08364
Estados visibles: Ingresado → Procesada → Despachada → Entregada
Detalles del comercio: visibles en página de detalle
```

### [C10] Comercio con Crédito Bloqueado

```
[C10] COMERCIO BLOQUEADO — Bastien
C10-01: N/A — Sin comercios con crédito bloqueado configurados en staging
```

---

## VEREDICTO FINAL — Bastien — 2026-04-15

| Flujo | Estado | Issues |
|-------|--------|--------|
| C1 Login | ✓ PASS | — |
| C2 Compra | ✓ PASS | Bastien-QA-001 (P3) — commerce switch JWT stale |
| C3 Precios | ✓ PASS | C3-14 BLOCKED/staging (sin cupones) |
| C7 Documentos | N/A | Bastien-QA-002 (P2) — visible cuando debería estar oculto |
| C5 Recomendaciones | ✓ PASS | — |
| C9 Seguimiento | ✓ PASS | Pedido #69e0038f, estados correctos |
| C10 Comercio bloqueado | N/A | Sin datos en staging |
| Admin (A2/A3) | N/A | Out of scope |

**VEREDICTO FINAL: CON CONDICIONES**

Justificación: Plataforma funcional en todos los flujos ejecutables con comercio AC HOTEL MARRIOTT. Un issue P2 real (documentos visibles con flag=false). El P3 es UX del selector de comercio en staging.

Issues a resolver:
- **Bastien-QA-002 P2** → Ticket Linear: `[QA] Bastien — Mis documentos visible con enablePaymentDocumentsB2B=false`
- **Bastien-QA-001 P3** → Ticket Linear: `[QA] Bastien — Commerce switch no refresca JWT, catálogo vacío`
