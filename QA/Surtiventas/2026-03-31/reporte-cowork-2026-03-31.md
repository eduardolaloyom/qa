# Reporte QA Cowork — Surtiventas
**Fecha:** 2026-03-31
**Tester:** Claude (Cowork)
**URL:** surtiventas.solopide.me
**Usuario:** max+surtiventasadmin@yom.ai (Max Frings Admin, ID 15698770-0)
**Vendedor asignado:** Maximiliano Cifuentes (ID 201)

---

## Resumen Ejecutivo

| Métrica | Valor |
|---|---|
| Flujos ejecutados | 6/6 |
| Variables config validadas | 7 |
| PASS | 5 |
| FAIL | 1 |
| PARTIAL | 1 |
| Issues nuevos | 4 |
| Issues críticos | 1 |
| **Veredicto** | **CON BLOQUEO CRÍTICO** |

---

## Validación de Config Variables

| Variable | Valor Esperado | Observado en UI | Estado |
|---|---|---|---|
| `purchaseOrderEnabled` | `false` → Sin campo OC | ✓ No existe campo OC en carrito | **PASS** |
| `disableCommerceEdit` | `false` → Campos editables | ✓ Nombre, Teléfono, Email editables en /profile | **PASS** |
| `editAddress` | `true` → Dirección editable en checkout | ❌ Sin selector de dirección. Carrito envía `shippingAddress: null` → HTTP 400 | **FAIL** |
| `hasSingleDistributionCenter` | `true` → Sin botón multicentro | ✓ Sin botón "Ver stock/centros" en catálogo ni detalle | **PASS** |
| `enableOrderApproval` | `false` → Sin botón Aprobar | ✓ Sin columna ni botón de aprobación en /orders | **PASS** |
| `enableSellerDiscount` | `true` → Campo descuento visible | Descuento automático $13 visible en facturación (de promociones). Sin campo manual de descuento % para vendedor/comprador | **PARTIAL** |
| `enableCoupons` | `true` → Campo cupón visible | ✓ Campo "Ingresar cupón" + botón "Aplicar" visible en carrito | **PASS** |

---

## Resultados por Flujo

### FLUJO 1: Compra Simple ⚠️ (bloqueado por bug)

| Check | Resultado | Detalle |
|---|---|---|
| Login exitoso | ✓ PASS | Max Frings Admin logueado, home carga sin spinner |
| Productos cargan con precio | ✓ PASS | 40 productos, precios visibles, imágenes OK (excepto 1 producto) |
| Campo OC | ✓ PASS | NO existe (correcto — purchaseOrderEnabled=false) |
| Campo cupón en carrito | ✓ PASS | "Ingresar cupón" + botón "Aplicar" visible |
| Dirección editable en checkout | ❌ FAIL | No aparece selector/formulario de dirección. El carrito envía directamente con `shippingAddress: null` → HTTP 400 "Error al generar el pedido" |
| Confirmación de pedido | ❌ BLOQUEADO | No se pudo confirmar por SV-QA-001 |
| Número de orden | ❌ BLOQUEADO | No aplica (pedido no procesado) |

**Nota técnica:** Request body enviado: `{"shippingAddress":null,"observation":null,"coupon":"","receiptType":"none"}`. Backend retorna error `kz40001` — `Path 'shippingAddress' is required`.

---

### FLUJO 2: Descuentos y Stock ✅ (con observaciones)

| Check | Resultado | Detalle |
|---|---|---|
| Stock visible en tarjetas | ❌ NO | Sin indicador de stock/cantidad en tarjetas del catálogo |
| Descuento visible | ✓ PASS (parcial) | Descuento automático $13 en facturación (de promociones). Sin campo de descuento % manual |
| 100 unidades permitidas | ✓ PASS | Sistema acepta 100 unidades sin restricción de stock |
| Step pricing | ❌ NO | Precio $21,711/Caja no cambia al subir a 100 unidades |
| Alerta monto mínimo | ❌ NO | Sin alerta de monto mínimo (Surtiventas no configura monto mínimo o está en $0) |

---

### FLUJO 3: Perfil Comercio ✅

| Check | Resultado | Detalle |
|---|---|---|
| Perfil localizado | ✓ PASS | Ruta: /profile ("Mis datos") |
| Campos editables | ✓ PASS | Nombre, Teléfono, Email son inputs editables (disableCommerceEdit=false ✓) |
| Botón "Guardar cambios" | ✓ PASS | Visible al hacer click en "Editar Datos" |
| Campo dirección | ❌ AUSENTE | Sin campo de dirección de despacho en perfil |
| Documentos pendientes | ✓ PASS | Sin notificación de documentos pendientes |
| Vendedores asignados | ✓ INFO | 201 \| Maximiliano Cifuentes \| maximiliano+vendedorstsv@yom.ai \| 89052977 |

---

### FLUJO 4: Stock y Distribución ✅

| Check | Resultado | Detalle |
|---|---|---|
| Stock visible en catálogo | ❌ NO | Sin indicador "Stock: X" en tarjetas |
| Botón "Ver stock/centros" | ✓ PASS | NO existe (correcto — hasSingleDistributionCenter=true) |
| Detalle producto sin multicentro | ✓ PASS | /products/{id} muestra precio + qty selector, sin sección de centros |

---

### FLUJO 5: Órdenes ✅

| Check | Resultado | Detalle |
|---|---|---|
| Página /orders carga | ✓ PASS | Sin spinner, sin error |
| Órdenes presentes | ℹ️ INFO | 0 pedidos (por bug de checkout — nunca se completó un pedido) |
| Botón "Aprobar" | ✓ PASS | NO existe en tabla ni en detalle (enableOrderApproval=false ✓) |
| Columnas de tabla | ✓ PASS | Fecha pedido, Fecha de entrega, ID del pedido, Dirección, Valor, Estado |
| Tabs disponibles | ℹ️ INFO | "Mis pedidos" y "Mis documentos" |

---

### FLUJO 6: Promociones y Cupones ⚠️

| Check | Resultado | Detalle |
|---|---|---|
| Badges promoción en catálogo | ✓ PASS | "5% Dcto" en Esp. Cartulina, "65% Dcto" en Abrelatas Reforzado |
| Filtro "Ofertas" en sidebar | ✓ PASS | Checkbox activa filtro "Promociones" en el catálogo |
| Precio "Antes de" en cards | ✓ PASS | "Antes: $251" visible en productos con descuento |
| Campo cupón visible | ✓ PASS | "Ingresar cupón" + botón "Aplicar" |
| Cupón inválido → mensaje error | ❌ FAIL | Al ingresar "TESTCUPON" y hacer click en "Aplicar", el campo se vacía silenciosamente sin mensaje de error al usuario |

---

## Issues Encontrados

| ID | Severidad | Descripción | Flujo | Estado |
|---|---|---|---|---|
| SV-QA-001 | 🔴 CRÍTICO | **shippingAddress null en checkout**: No hay selector de dirección en el carrito. El pedido se envía con `shippingAddress: null` → HTTP 400. Usuarios no pueden realizar pedidos. | F1 | 🆕 Nuevo |
| SV-QA-002 | 🟡 MEDIO | **Imagen no disponible**: "Aderezo Cesar 250 Gr Gourmet" muestra placeholder "Imagen no disponible" en carrito y catálogo. Posiblemente issue plataforma-wide (mismo que Codelpa QA-004) | F1 | 🆕 Nuevo |
| SV-QA-003 | 🟡 MEDIO | **Cupón inválido sin mensaje de error**: Al aplicar cupón inválido, el campo se vacía sin feedback al usuario. Mismo issue que Codelpa QA-008 | F6 | 🆕 Nuevo |
| SV-QA-004 | 🔵 BAJO | **Sin indicador de stock en tarjetas**: `hasStockEnabled` podría estar activo pero no se muestra indicador de stock en tarjetas del catálogo | F2/F4 | 🆕 Nuevo |

---

## Detalle SV-QA-001 (Crítico)

**Descripción:** El checkout de Surtiventas no muestra formulario ni selector de dirección de despacho. Al hacer click en "Confirmar pedido", se envía directamente una solicitud POST a `/api/v2/orders` con `shippingAddress: null`. El backend retorna HTTP 400 con error de validación requerida.

**Request enviado:**
```json
{
  "shippingAddress": null,
  "observation": null,
  "coupon": "",
  "receiptType": "none"
}
```

**Error recibido:**
```json
{
  "name": "validationFailure",
  "errorCode": "kz40001",
  "errors": {
    "shippingAddress": {
      "message": "Path `shippingAddress` is required.",
      "type": "required"
    }
  }
}
```

**Posibles causas:**
1. El test commerce no tiene ninguna dirección de despacho configurada en el sistema
2. El componente de selección/edición de dirección (`editAddress: true`) no se está renderizando antes de la confirmación

**Impacto:** Bloqueo total del flujo de compra para todos los usuarios de Surtiventas.

---

## Observaciones Generales

- **Banner/carrusel home vacío:** La página de inicio muestra el carrusel principal en blanco (sin imágenes). Posible issue de configuración de banners.
- **Nombres de productos con asteriscos:** Múltiples productos tienen nombres como `**Carpeta Vinil...` o `**Lamina Termol...` — parece ser metadata o prefijo de staging.
- **Sin monto mínimo de pedido:** A diferencia de Codelpa ($100,000), Surtiventas no parece tener restricción de monto mínimo (no apareció alerta al intentar confirmar).
- **Bug cupón (SV-QA-003) igual a Codelpa QA-008:** Sugiere que es un bug de la plataforma compartida, no específico de cliente.

---

## Próximos Pasos

| Prioridad | Acción | Responsable |
|---|---|---|
| 🔴 P0 | Investigar SV-QA-001: ¿el commerce test tiene dirección configurada? Si sí → bug de UI. Si no → agregar dirección y re-testear | Tech (Diego/Rodrigo) |
| 🟡 P1 | Confirmar si SV-QA-002 (imagen) y SV-QA-003 (cupón) son plataforma-wide (ya reportados como Codelpa QA-004 y QA-008) | QA |
| 🔵 P2 | Revisar si `enableSellerDiscount=true` debería mostrar campo buyer-side o es solo seller-app | PM |
| 🔵 P2 | Banner home vacío: configurar imágenes de carrusel para staging | Tech |
