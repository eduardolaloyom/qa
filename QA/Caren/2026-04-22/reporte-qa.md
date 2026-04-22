# Reporte QA — Caren — 2026-04-22

**Ambiente:** Staging · caren.solopide.me  
**App:** YOM Ventas Debug (me.youorder.yomventas.debug)  
**Ejecutado por:** Maestro / Eduardo  
**Flujos ejecutados:** 01–10 (10 flows, primer QA completo Caren)  
**Comercio de prueba (disponible):** MARIA TERESA (0010001575, Potrerillo S/N, Puchuncaví)  
**Health Score producto: 55/100** _(3 bugs confirmados: 2 P2, 1 P3 · 1 en revisión: CAREN-QA-002)_  
**Automatización: 10/10 PASS** _(flows corren sin crashear — bugs detectados por inspección)_

---

## Resumen ejecutivo

Primer QA completo de Caren staging. Se ejecutaron **10 flujos Maestro** cubriendo todos los comercios, catálogos, búsqueda, historial y datos. El flujo end-to-end de pedido funciona y los feature flags OFF se respetan. Se detectaron **3 bugs confirmados** y 1 en revisión:

- **🔵 En revisión — CAREN-QA-002**: Bloqueo crediticio sin enforcement — pendiente verificación con carrito limpio (QA 2026-04-23). Puede ser falso positivo por residuo de carrito del flow 02.
- **P2 — CAREN-QA-001**: Inversión de catálogo — disponible muestra 3 productos, bloqueados muestran catálogo completo
- **P2 — CAREN-QA-004**: Sin fotos en ningún producto de ningún comercio (disponible y bloqueados)
- **P3 — CAREN-QA-003**: Historial de pedidos sin número de pedido visible / sección no encontrada

---

## Hallazgos por severidad

### 🔵 En revisión (1)

| ID | Área | Descripción |
|----|------|-------------|
| **CAREN-QA-002** | Bloqueo crediticio / Tomador de Pedido | Flow 05 detectó "Finalizar pedido" visible en comercio bloqueado. **Pendiente verificación 2026-04-23 con carrito limpio.** Hipótesis: el carrito es por vendedor (no por comercio), por lo que el carrito de MARIA TERESA (flow 02) pudo haberse arrastrado al entrar al bloqueado. Si se confirma con carrito vacío → P1. |

### 🟠 P2 — Alto (2)

| ID | Área | Descripción |
|----|------|-------------|
| **CAREN-QA-001** | Catálogo / Inversión de restricción | El catálogo debería ser el mismo para todos los comercios (catálogo del vendedor). MARIA TERESA (disponible) muestra solo 3 productos (100418, 100419, 100449). Los 4 comercios bloqueados muestran catálogo completo vía "Hacer pedido". Inversión directa: el comercio que PUEDE hacer pedidos tiene catálogo restringido; los que NO deberían, tienen acceso total. Confirmado por flow 06 (scroll completo MARIA TERESA) y flow 10 (todos los bloqueados). |
| **CAREN-QA-004** | Fotos de producto | Ningún producto en ningún comercio muestra foto — todos muestran placeholder de imagen. Aplica al comercio disponible y a todos los bloqueados. Impacto en la experiencia del vendedor: no puede identificar productos visualmente al tomar pedidos. Verificar si es problema de datos en staging o bug de carga de imágenes. |

### 🟡 P3 — Medio (1)

| ID | Área | Descripción |
|----|------|-------------|
| **CAREN-QA-003** | Historial de pedidos | Flow 07 no encontró sección de historial de pedidos accesible desde la navegación principal (menú hamburger, bottom nav). El flujo pasó porque todos los taps fueron opcionales, pero ninguno encontró historial, número de pedido ni detalle de pedidos enviados. Se enviaron pedidos en flow 02 — el historial debería mostrarlos. Requiere verificación manual de la ruta de navegación al historial. |

---

## Resultados por flujo

### Flujo 01 — Comercios disponibles
| Check | Resultado |
|-------|-----------|
| 1 comercio disponible visible (MARIA TERESA 0010001575) | ✅ PASS |
| Tag "Disponible" verde en lista | ✅ PASS |
| 4 comercios bloqueados visibles en lista sin filtro | ✅ PASS |
| Acceso al Tomador de Pedido del disponible | ✅ PASS |
| Catálogo carga productos | ⚠️ Solo ~3 productos — ver CAREN-QA-001 |

### Flujo 02 — Pedido completo (staging — se envía)
| Check | Resultado |
|-------|-----------|
| Agregar productos al carro (100418 + 100419) | ✅ PASS |
| Sin "Descuento Vendedor" (enableSellerDiscount: false) | ✅ PASS |
| Precios sin IVA (includeTaxRateInPrices: false) — Impuesto $0 | ✅ PASS |
| Neto $21.160 (100418 $7.975 + 100419 $13.185) | ✅ PASS |
| Botón "Finalizar pedido" visible tras scroll | ✅ PASS |
| Diálogo confirmación "ACEPTAR" | ✅ PASS |
| Pantalla éxito "Su pedido ha sido realizado" | ✅ PASS |

### Flujo 03 — Comercios bloqueados
| Comercio | Popup crediticio | Sin Finalizar Pedido |
|----------|-----------------|----------------------|
| 0000000000 (Nuevo San Juan, 23 B N 19 238) | ✅ PASS | ⚠️ No verificado en este flow |
| 000 / 0010010531 (Los Alerces, Arica) | ✅ PASS | ⚠️ No verificado en este flow |
| 2 A SERVICIOS LOGISTICOS SPA / 0010010445 | ✅ PASS | ⚠️ No verificado en este flow |
| 5TA ZONA CARABINEROS VALPO / 0010005517 | ✅ PASS | ⚠️ No verificado en este flow |

### Flujo 04 — Features ON/OFF
| Feature | Valor config | UI observada | Estado |
|---------|-------------|--------------|--------|
| enableCreateCommerce | false | Sin botón "Crear/Nuevo Comercio" | ✅ PASS |
| hasMultiUnitEnabled | false | Sin selector DIS/Display | ✅ PASS |
| useNewPromotions | false | Sin badge PROMO/% | ✅ PASS |
| enableSellerDiscount | false | Sin "Descuento Vendedor" | ✅ PASS |

### Flujo 05 — Bug bloqueado: acceso a Tomador de Pedido
| Check | Resultado |
|-------|-----------|
| Ingresa al Tomador de Pedido desde comercio bloqueado | ❌ BUG — acceso exitoso (debería bloquearse) |
| Agrega producto al carrito desde comercio bloqueado | ❌ BUG — agrega sin restricción |
| "Finalizar pedido" NO visible en bloqueado | ❌ FAIL — botón SÍ visible → **P1 confirmado** |

### Flujo 06 — Lista completa de comercios
| Check | Resultado |
|-------|-----------|
| Solo 1 comercio disponible (MARIA TERESA) | ✅ PASS |
| Scroll completo catálogo MARIA TERESA: 3 productos únicamente | ⚠️ BUG — ver CAREN-QA-001 |

### Flujo 07 — Historial de pedidos
| Check | Resultado |
|-------|-----------|
| Sección historial accesible desde nav principal | ❌ No encontrada — ver CAREN-QA-003 |
| Número de pedido visible | ❌ No encontrado |
| Detalle de pedidos enviados (flow 02) visible | ❌ No encontrado |

### Flujo 08 — Búsqueda en lista de comercios
| Check | Resultado |
|-------|-----------|
| Búsqueda por nombre "MARIA" retorna resultados | ✅ PASS |
| Búsqueda por RUT "0010001575" retorna resultados | ✅ PASS |

### Flujo 09 — Datos de TODOS los comercios
| Comercio | Ficha accesible | Info visible |
|----------|-----------------|-------------|
| MARIA TERESA (disponible) | ✅ PASS | Datos básicos visibles |
| 0000000000 (bloqueado) | ✅ PASS | Info crédito a confirmar manualmente |
| 000 / 0010010531 (bloqueado) | ✅ PASS | Info crédito a confirmar manualmente |
| 2 A SERVICIOS LOGISTICOS SPA (bloqueado) | ✅ PASS | Info crédito a confirmar manualmente |
| 5TA ZONA CARABINEROS VALPO (bloqueado) | ✅ PASS | Info crédito a confirmar manualmente |

### Flujo 10 — Catálogo de TODOS los comercios
| Comercio | Accede catálogo | Fotos | Productos visibles |
|----------|-----------------|-------|-------------------|
| MARIA TERESA (disponible) | ✅ | ❌ Sin fotos | ~3 productos |
| 0000000000 (bloqueado) | ✅ vía "Hacer pedido" | ❌ Sin fotos | Catálogo completo |
| 000 / 0010010531 (bloqueado) | ✅ vía "Hacer pedido" | ❌ Sin fotos | Catálogo completo |
| 2 A SERVICIOS LOGISTICOS SPA (bloqueado) | ✅ vía "Hacer pedido" | ❌ Sin fotos | Catálogo completo |
| 5TA ZONA CARABINEROS VALPO (bloqueado) | ✅ vía "Hacer pedido" | ❌ Sin fotos | Catálogo completo |

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

1. **🔴 CAREN-QA-002 (P1)**: Implementar enforcement real del bloqueo crediticio — deshabilitar "Hacer pedido" en ficha del bloqueado o bloquear "Finalizar pedido" en el Tomador de Pedido cuando el comercio está bloqueado.
2. **🟠 CAREN-QA-001 (P2)**: Investigar inversión de catálogo — MARIA TERESA muestra 3 productos, bloqueados muestran catálogo completo. El catálogo debería ser idéntico para todos. Revisar si el filtro de disponibilidad está afectando el catálogo.
3. **🟠 CAREN-QA-004 (P2)**: Verificar carga de fotos de producto — ningún comercio muestra imágenes. Confirmar si es problema de datos en staging o bug de rendering.
4. **🟡 CAREN-QA-003 (P3)**: Identificar ruta de navegación al historial de pedidos y verificar que los pedidos enviados aparezcan con número de pedido.

---

*Generado: 2026-04-22 | Tool: Maestro (10 flows) | Automatización: 10/10 PASS | Bugs producto: 4 (1 P1, 2 P2, 1 P3)*
