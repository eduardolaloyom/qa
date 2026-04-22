# Reporte QA — Caren — 2026-04-22

**Ambiente:** Staging · caren.solopide.me  
**App:** YOM Ventas Debug (me.youorder.yomventas.debug)  
**Ejecutado por:** Maestro / Eduardo  
**Flujos ejecutados:** 01 Comercios disponibles · 02 Pedido completo · 03 Comercios bloqueados · 04 Features ON/OFF · 05 Bug bloqueado Tomador de Pedido · 06 Lista completa comercios  
**Comercio de prueba (disponible):** MARIA TERESA (0010001575, Potrerillo S/N, Puchuncaví)  
**Health Score: 45/100** _(P1 confirmado — bloqueo crediticio sin enforcement real)_

---

## Resumen ejecutivo

QA de sesión vendedor completa en staging. Se ejecutaron **6 flujos Maestro** (6/6 PASS en automatización). El flujo end-to-end de pedido funciona y los feature flags OFF se respetan. Sin embargo se detectaron **2 hallazgos críticos de producto**:

- **P1 CONFIRMADO (CAREN-QA-002)**: El bloqueo crediticio de un comercio NO impide que el vendedor acceda al Tomador de Pedido, agregue productos al carrito y vea el botón "Finalizar pedido". Un vendedor puede enviar pedidos a comercios bloqueados. El popup de bloqueo es puramente informativo.
- **P2 (CAREN-QA-001)**: El catálogo del único comercio disponible (MARIA TERESA) muestra solo ~3 productos en Sugerencias. El catálogo completo no carga correctamente.

---

## Hallazgos por severidad

### 🔴 P1 — Crítico (1)

| ID | Área | Descripción |
|----|------|-------------|
| **CAREN-QA-002** | Bloqueo crediticio / Tomador de Pedido | Un comercio bloqueado por estado crediticio permite al vendedor ingresar al Tomador de Pedido, agregar productos al carrito y llegar al botón "Finalizar pedido". Flow 05 confirmó: `assertNotVisible "Finalizar pedido"` → WARNING (la assertion falló = el botón SÍ está visible). El popup "Este comercio se encuentra bloqueado" es solo informativo — no hay enforcement en el flujo de pedido. Impacto: pedidos enviados a comercios sin crédito disponible. |

### 🟠 P2 — Alto (1)

| ID | Área | Descripción |
|----|------|-------------|
| **CAREN-QA-001** | Catálogo / Tomador de Pedido | Catálogo del comercio disponible (MARIA TERESA) muestra solo ~3 productos en el tab Sugerencias (100418, 100419, 100449). Flow 06 confirmó scroll completo del catálogo sin más productos. El staging tiene 1 único comercio disponible — no se puede comparar con otros disponibles. Comparar contra producción para determinar si es bug de datos o de rendering. |

### ℹ️ Info (1)

| ID | Área | Descripción |
|----|------|-------------|
| **CAREN-QA-003** | Catálogo / Imágenes | Los 3 productos del catálogo disponible (100418, 100419, 100449) muestran placeholder de imagen — sin fotos de producto. Esperado en staging (datos de prueba). |

---

## Resultados por flujo

### Flujo 01 — Comercios disponibles

| Check | Resultado |
|-------|-----------|
| 1 comercio disponible visible (MARIA TERESA 0010001575) | ✅ PASS |
| Tag "Disponible" verde en lista | ✅ PASS |
| 4 comercios bloqueados visibles en lista sin filtro | ✅ PASS |
| Acceso al Tomador de Pedido del disponible | ✅ PASS |
| Catálogo carga productos | ✅ PASS (solo ~3 productos — ver CAREN-QA-001) |

### Flujo 02 — Pedido completo (staging — se envía)

| Check | Resultado |
|-------|-----------|
| Agregar productos al carro | ✅ PASS — 100418 + 100419 |
| Sin "Descuento Vendedor" (enableSellerDiscount: false) | ✅ PASS |
| Precios sin IVA incluido (includeTaxRateInPrices: false) | ✅ PASS — Impuesto $0 |
| Neto $21.160 (100418 $7.975 + 100419 $13.185) | ✅ PASS |
| Botón "Finalizar pedido" visible tras scroll | ✅ PASS |
| Diálogo confirmación "ACEPTAR" | ✅ PASS |
| Pantalla éxito "Su pedido ha sido realizado" | ✅ PASS |

### Flujo 03 — Comercios bloqueados

| Comercio | Popup crediticio | Sin Confirmar Pedido (flow 03) |
|----------|-----------------|-------------------------------|
| 0000000000 (Nuevo San Juan, 23 B N 19 238) | ✅ PASS | ✅ PASS |
| 000 / 0010010531 (Los Alerces, Arica) | ✅ PASS | ✅ PASS |
| 2 A SERVICIOS LOGISTICOS SPA / 0010010445 | ✅ PASS | ✅ PASS |
| 5TA ZONA CARABINEROS VALPO / 0010005517 | ✅ PASS | ✅ PASS |

### Flujo 04 — Features ON/OFF

| Feature | Valor config | UI observada | Estado |
|---------|-------------|--------------|--------|
| enableCreateCommerce | false | Sin botón "Crear/Nuevo Comercio" en lista | ✅ PASS |
| hasMultiUnitEnabled | false | Sin selector DIS/Display en catálogo | ✅ PASS |
| useNewPromotions | false | Sin badge PROMO/% descuento en catálogo | ✅ PASS |
| enableSellerDiscount | false | Sin "Descuento Vendedor" en carrito | ✅ PASS |
| loginButtons.facebook/google | false | Login completado sin botones sociales (implícito) | ✅ PASS |

### Flujo 05 — Bug bloqueado: acceso a Tomador de Pedido

| Check | Resultado |
|-------|-----------|
| Ingresa al Tomador de Pedido desde comercio bloqueado | ✅ PASS (acceso exitoso = bug confirmado) |
| Agrega producto al carrito desde comercio bloqueado | ✅ PASS (agrega = bug confirmado) |
| "Finalizar pedido" NO visible en comercio bloqueado | ❌ FAIL — botón SÍ visible → **P1 confirmado** |

### Flujo 06 — Lista completa de comercios

| Check | Resultado |
|-------|-----------|
| Scroll completo de lista sin filtro | ✅ PASS |
| Solo 1 comercio disponible en staging (MARIA TERESA) | ✅ PASS — índices 1, 2, 3 no encontrados |
| Catálogo del disponible accesible con scroll 3x | ✅ PASS |
| No existe segundo comercio disponible para comparar catálogos | ✅ INFO |

---

## Comercios en staging

| RUT | Nombre | Estado | Dirección |
|-----|--------|--------|-----------|
| 0010001575 | MARIA TERESA | Disponible | Potrerillo S/N, Puchuncaví |
| 0000000000 | 0000000000 | Bloqueado | Nuevo San Juan 23 B N 19 238 |
| 0010010531 | 000 | Bloqueado | Los Alerces, Arica |
| 0010010445 | 2 A SERVICIOS LOGISTICOS SPA | Bloqueado | Copihues 828-B, Nueva Aurora, Viña |
| 0010005517 | 5TA ZONA CARABINEROS VALPO | Bloqueado | Buenos Aires 750, Valparaíso |

---

## Acciones prioritarias

1. **🔴 CAREN-QA-002 (P1)**: Implementar enforcement real del bloqueo crediticio en el flujo de pedido. El popup informativo debe ir acompañado de bloqueo funcional: deshabilitar "Hacer pedido" en la ficha del comercio bloqueado, o bloquear el botón "Finalizar pedido" en el Tomador de Pedido cuando el comercio está bloqueado.
2. **🟠 CAREN-QA-001 (P2)**: Verificar por qué MARIA TERESA muestra solo 3 productos en Sugerencias. Comparar contra producción. Posibles causas: filtro de stock, categoría, fecha de vigencia, o bug de paginación en el tab Sugerencias.

---

*Generado: 2026-04-22 | Tool: Maestro (6 flows, 6/6 PASS automatización) | Próxima QA: post-fix CAREN-QA-002*
