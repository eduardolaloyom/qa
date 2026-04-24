# Reporte QA Cowork — Codelpa

**Fecha:** 2026-03-31 · **Ejecutado por:** Eduardo Jimenez (Cowork/Claude)
**URL:** [https://beta-codelpa.solopide.me](https://beta-codelpa.solopide.me)
**Usuario:** [felipe.munoz+codelpastagingb2b@youorder.me](mailto:felipe.munoz+codelpastagingb2b@youorder.me)
**Comercio:** 77008931 COMERCIAL RDV SPA
**Herramienta:** Cowork (validación visual end-to-end, 6 flujos)
**Referencia:** COWORK-VALIDACION-QA.md

---

## Resumen Ejecutivo


|                                    |                             |
| ---------------------------------- | --------------------------- |
| **Flujos ejecutados**              | 6/6                         |
| **Issues nuevos**                  | 3 (1 High, 1 Medium, 1 Low) |
| **Issues anteriores resueltos**    | 2 (QA-003, QA-005)          |
| **Issues anteriores persistentes** | 2 (QA-001, QA-004)          |
| **Veredicto**                      | CON CONDICIONES             |


---

## Estado de Issues Previos (QA 2026-03-30)


| ID             | Descripción                           | Estado hoy                                      |
| -------------- | ------------------------------------- | ----------------------------------------------- |
| Codelpa-QA-001 | API /delivery-date retorna 500        | ❌ **Persiste**                                  |
| Codelpa-QA-002 | Producto con precio $0                | ⬜ No verificable (user ve solo 2 productos)     |
| Codelpa-QA-003 | 10 pedidos con estado "No disponible" | ✅ **Resuelto** — estados mapeados correctamente |
| Codelpa-QA-004 | TEXTURA ELASTOMERICA sin imagen       | ❌ **Persiste**                                  |
| Codelpa-QA-005 | Home spinner infinito                 | ✅ **Resuelto** — home carga correctamente       |
| Codelpa-QA-006 | "Eliminar todos" sin confirmación     | ❌ **Persiste** (sin cambio)                     |


---

## Issues Nuevos Encontrados Hoy


| ID             | Severidad | Feature                 | Descripción                                                                                                             |
| -------------- | --------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Codelpa-QA-007 | High      | Pedidos                 | Número de pedido "#No disponible" en pantalla de confirmación y detalle                                                 |
| Codelpa-QA-008 | Medium    | Cupones                 | Cupón inválido no muestra mensaje de error al usuario                                                                   |
| Codelpa-QA-009 | Low       | COWORK-VALIDACION-QA.md | Config documentada incorrectamente: purchaseOrderEnabled y editAddress/disableCommerceEdit no coinciden con config real |


---

## Detalle de Issues Nuevos

### Codelpa-QA-007: Número de pedido "#No disponible"

- **Severidad:** High · Bug de visualización
- **Feature:** Confirmación de pedido + Detalle de pedido
- **Descripción:** Tras confirmar un pedido, la pantalla de confirmación (`/confirmation/{id}`) muestra "Número de pedido: #No disponible". Lo mismo en el detalle del pedido (`/orders/{id}`). El ID numérico SÍ existe (pedido #14564 visible en el listado `/orders`), pero no se muestra en confirmación ni en detalle.
- **Impacto:** El cliente no puede ver su número de pedido al comprar. Frena el seguimiento y el soporte post-venta.
- **Pasos para reproducir:**
  1. Login → agregar productos → confirmar pedido
  2. Ver pantalla de confirmación: "Número de pedido: #No disponible"
  3. Navegar a `/orders/{id}`: mismo texto
  4. Ir a `/orders`: el ID (14564) sí aparece en el listado
- **Escalado a:** Tech (Diego/Rodrigo)

---

### Codelpa-QA-008: Cupón inválido sin mensaje de error

- **Severidad:** Medium · UX
- **Feature:** Carrito — campo cupón
- **Descripción:** Al ingresar un código de cupón inválido ("TEST123") y presionar "Aplicar", no aparece ningún mensaje de error, toast, ni indicación visual. El descuento sigue en $0. El usuario queda sin feedback de si el cupón no existe, expiró, o hubo un error de servidor.
- **Pasos:**
  1. Ir a `/cart` con productos en el carrito
  2. Ingresar código "TEST123" en campo cupón
  3. Click "Aplicar"
  4. Resultado: sin respuesta visible al usuario
- **Escalado a:** Frontend

---

### Codelpa-QA-009: Discrepancia en COWORK-VALIDACION-QA.md

- **Severidad:** Low · Documentación
- **Descripción:** El archivo de referencia COWORK-VALIDACION-QA.md describe variables incorrectas para Codelpa. La config real observada en el sitio difiere:


| Variable               | Doc dice                       | Observado hoy                           | Coincide |
| ---------------------- | ------------------------------ | --------------------------------------- | -------- |
| `purchaseOrderEnabled` | `true` (campo OC debe existir) | `false` (no hay campo OC)               | ❌        |
| `editAddress`          | `false` (dirección locked)     | `true` (dropdown editable)              | ❌        |
| `disableCommerceEdit`  | `true` (perfil locked)         | `false` (perfil completamente editable) | ❌        |
| `enableOrderApproval`  | `true`                         | `true` (badge "Pendiente aprobación")   | ✅        |
| `enableSellerDiscount` | `true`                         | `true` (Descuento: $0 visible)          | ✅        |


- **Acción:** Actualizar COWORK-VALIDACION-QA.md con la config real de Codelpa.

---

## Resultados por Flujo

### FLUJO 1: Compra Simple ✅

- Login exitoso ✓ (home carga sin spinner — QA-005 resuelto)
- Catálogo carga: 2 productos con precio ✓
- Campo OC: ❌ NO existe → `purchaseOrderEnabled: false` (discrepancia con doc)
- Campo cupón: ✓ Existe en carrito ("Ingresar cupón")
- Dirección en checkout: Dropdown selector editable ✓ → `editAddress: true`
- Sin selector boleta/factura ✓ → `hideReceiptType: true`
- Monto mínimo: $100.000 — alerta visible cuando no se alcanza ✓
- Pedido creado: #14564 (31/03/2026) ✓
- Estado al crear: "Pendiente aprobación" ✓ → `enableOrderApproval: true`
- Número en confirmación: **"#No disponible"** ⚠️ (Codelpa-QA-007)
- Fecha estimada de entrega: "No disponible" ⚠️ (Codelpa-QA-001 persiste)
- IVA 19% correcto: Neto $151.020 + IVA $28.694 = Total $179.714 ✓

---

### FLUJO 2: Descuentos y Stock ✅

- Stock visible en tarjetas: ❌ Sin indicador (sin texto "Stock: X" en ninguna tarjeta) (¿¿Está la variable stock??)
- Cantidad grande (100 unidades): ✓ Sistema permite, sin restricción
- Step pricing: ❌ No existe — precio unitario constante $54.480 independiente de cantidad (¿¿Está la variable dcto??)
- Campo descuento: ✓ Línea "Descuento: $0" visible en billing summary → `disableShowDiscount: false`
- Monto mínimo $100.000: ✓ Alerta visible "Te faltan $X para cumplir con el monto mínimo"

---

### FLUJO 3: Perfil Comercio ✅

- Perfil ubicado en: `/profile` ✓
- Campos nombre/email/teléfono: **Editables** ✓ → `disableCommerceEdit: false` (discrepancia con doc)
- Link "Editar Datos" visible → formulario abre con campos editables
- Documentos pendientes: ❌ Sin notificación visible
- Crédito disponible: $8.000.000 total / $5.340.305 restante ✓
- Vendedor asignado: Maurico Ercoreca Negron ✓

---

### FLUJO 4: Stock y Distribución ✅ (parcial)

- Stock visible en tarjetas: ❌ Sin indicador
- Botón "Ver stock" / "Centros" en tarjetas: ❌ No existe
- Botón en detalle de producto: ❌ No existe
- Observación: `hasAllDistributionCenters: true` es config backend sin UI visible para el comprador
- "Recomendamos 7 unidades" visible en detalle de producto (sugerencia de cantidad)

---

### FLUJO 5: Órdenes y Aprobación ✅

- Órdenes cargadas: ✓ (28 pedidos totales, paginados de 10 en 10)
- Estados encontrados en historial: Pendiente aprobación, Procesada, Entregada, Ingresado, Despachada
- Estados "No disponible": ❌ Ninguno encontrado → **QA-003 resuelto** ✓
- enableOrderApproval: ✓ Validado por badge "Pendiente aprobación" en órdenes
- Botón "Aprobar" en buyer portal: ❌ No existe (es feature seller-side, no buyer)
- Detalles de orden: ✓ Items, precio, fecha visible
- Número de pedido en detalle: "#No disponible" ⚠️ (Codelpa-QA-007)
- Fecha de entrega: "No disponible" en todos ⚠️ (Codelpa-QA-001 persiste)

---

### FLUJO 6: Promociones y Cupones ✅

- Badges "Promoción/Oferta/%" en tarjetas: ❌ Sin badges (correcto para Codelpa)
- Filtro "Ofertas" en catálogo: ✓ Funciona (muestra productos filtrados)
- Campo cupón en carrito: ✓ Existe (enableCoupons=true confirmado)
- Cupón inválido (TEST123): Sin mensaje de error ⚠️ (Codelpa-QA-008)
- Cupones activos conocidos: Ninguno disponible para esta sesión de staging

---

## Validación de Config (observado vs. documentado)


| Feature                   | Config Real Observada              | Match doc COWORK-VALIDACION-QA.md |
| ------------------------- | ---------------------------------- | --------------------------------- |
| purchaseOrderEnabled      | false (sin campo OC)               | ❌ Doc dice true                   |
| editAddress               | true (dropdown editable)           | ❌ Doc dice false                  |
| disableCommerceEdit       | false (perfil editable)            | ❌ Doc dice true                   |
| enableOrderApproval       | true (badge Pendiente aprobación)  | ✅                                 |
| enableCoupons             | true (campo cupón visible)         | ✅                                 |
| hideReceiptType           | true (sin selector boleta/factura) | ✅                                 |
| disableShowDiscount       | false (Descuento: $0 visible)      | ✅                                 |
| hasStockEnabled           | No UI visible al comprador         | —                                 |
| hasAllDistributionCenters | No UI visible al comprador         | —                                 |
| loginButtons Google+FB    | ✅ Ambos presentes en login         | ✅                                 |


---

## Fixes Confirmados vs. QA Anterior


| Issue                              | Reporte anterior | Hoy                           |
| ---------------------------------- | ---------------- | ----------------------------- |
| QA-003: 10 estados "No disponible" | ❌ Abierto        | ✅ Resuelto — estados mapeados |
| QA-005: Spinner infinito en home   | ❌ Abierto        | ✅ Resuelto — home carga OK    |


---

## Próximos Pasos


| Acción                                                           | Responsable             | Prioridad |
| ---------------------------------------------------------------- | ----------------------- | --------- |
| Fix: Número de pedido "#No disponible" en confirmación y detalle | Tech (Diego/Rodrigo)    | Alta      |
| Fix: API /delivery-date 500 persiste                             | Tech (Diego/Rodrigo)    | Alta      |
| Fix: Cupón inválido sin mensaje de error                         | Frontend                | Media     |
| Subir imagen de TEXTURA ELASTOMERICA                             | Contenido/Admin Codelpa | Media     |
| Actualizar COWORK-VALIDACION-QA.md con config real de Codelpa    | QA (Lalo)               | Baja      |
| Confirmar si QA-002 ($0 precio) fue corregido                    | Tech                    | Baja      |
| Re-run post-fix                                                  | QA (Lalo)               | Post-fix  |


---

*2026-03-31 · Codelpa · Cowork QA (Eduardo Jimenez)*
*Herramienta: Cowork validación visual — 6 flujos completados*