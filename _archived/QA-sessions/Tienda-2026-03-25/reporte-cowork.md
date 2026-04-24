# QA Report — tienda.youorder.me
**Fecha:** 2026-03-25
**Sitio:** Tienda (staging interno YOM)
**URL:** https://tienda.youorder.me
**Tester:** QA Agent (Claude)
**Credenciales usadas:** eduardo+tienda+comercio@yom.ai

---

## Estado por flujo

| Flujo | Estado | Issues |
|---|---|---|
| 1. Login / Acceso anónimo | ⚠️ PARCIAL | Acceso anónimo OK, login bloqueado por siteTokenExpired |
| 2. Catálogo y búsqueda | ✅ OK | Búsqueda sensible a tildes (comportamiento menor) |
| 3. Carrito | ✅ OK | Sin mensaje "vacío" explícito (UX menor) |
| 4. Checkout | ❌ BLOQUEADO | No se pudo testear — login requerido, token expirado |
| 5. Precios | ⚠️ PARCIAL | Discrepancia precio NESCAFE: catálogo ≠ carrito, sin descuento registrado |

---

## Issues encontrados

### ISSUE-01 — Site Token Expirado (Login completamente bloqueado)
- **Severidad:** 🔴 Critical
- **Flujo:** Flujo 1
- **Descripción:** El token del sitio B2B ha expirado. Cualquier intento de login devuelve HTTP 401 con `errorCode: kz40107` y mensaje `"Site token has expired"`.
- **Endpoint afectado:** `POST https://api.youorder.me/api/v2/auth/local`
- **Error exacto:**
  ```json
  {
    "name": "siteTokenExpired",
    "message": "Site token has expired",
    "errorCode": "kz40107",
    "errors": { "name": "TokenExpiredError", "expiredAt": "2026-03-25T20:30:42.000Z" }
  }
  ```
- **Impacto:** Login bloqueado para todos los usuarios. Flujo 4 (Checkout) no pudo ser testeado.
- **Pasos para reproducir:** Ingresar email + password en `/auth/jwt/login` y hacer submit.

---

### ISSUE-02 — Discrepancia de precio NESCAFE: catálogo vs carrito
- **Severidad:** 🟠 High
- **Flujo:** Flujo 5
- **Descripción:** NESCAFE TRADICION (SKU 82332) muestra $3.873/UN en el catálogo pero $2.900/UN en el carrito (diferencia de $973, -25.1%). El campo "Descuento" en la facturación del carrito muestra $0, lo que hace invisible el origen de la diferencia.
- **Datos:**
  - Precio catálogo: $3.873
  - Precio carrito: $2.900
  - Descuento mostrado en facturación: $0
- **Hipótesis:** `enableSellerDiscount: true` aplica un descuento de seller al precio del carrito pero no lo refleja en la línea "Descuento" del resumen de facturación.
- **Pasos para reproducir:** Ver NESCAFE en catálogo → anotar precio → agregarlo al carrito → comparar precio unitario en carrito con el precio del catálogo.

---

### ISSUE-03 — Búsqueda sensible a tildes (resultados inconsistentes)
- **Severidad:** 🟡 Medium
- **Flujo:** Flujo 2
- **Descripción:** Buscar "cafe" devuelve 2 resultados; buscar "café" devuelve solo 1. La búsqueda no es accent-insensitive de forma consistente. Además, buscar "cafe" incluye "GALLETA COCOSETTE WAFER" como resultado, cuyo nombre no contiene "cafe" — posible false positive por match en campo oculto (descripción, tags, SKU).
- **Pasos para reproducir:** Buscar "cafe" → 2 resultados (NESCAFE + GALLETA COCOSETTE). Buscar "café" → 1 resultado (solo NESCAFE).

---

### ISSUE-04 — Sin mensaje de carrito vacío
- **Severidad:** 🟢 Low
- **Flujo:** Flujo 3
- **Descripción:** Al vaciar el carrito (individual o con "Eliminar todos"), el sistema muestra "0 Producto" y totales en $0, pero no hay un mensaje claro tipo "Tu carrito está vacío" que guíe al usuario hacia el catálogo.
- **Pasos para reproducir:** Agregar un producto → ir al carrito → eliminar → verificar que no hay mensaje de carrito vacío.

---

### ISSUE-05 — taxRate: 0 en config pero se cobran impuestos
- **Severidad:** 🟡 Medium
- **Flujo:** Flujo 5
- **Descripción:** La configuración del sitio indica `taxes.useTaxRate: true` con `taxRate: 0`. Sin embargo, la facturación del carrito muestra impuestos cobrados (~20.4% sobre el neto). Ejemplo: Neto $37.719 + Impuestos $7.687 = $45.406. Puede ser que taxRate: 0 signifique "IVA estándar por defecto" y no "sin impuesto", pero esto debería verificarse contra la lógica del sistema.
- **Pasos para reproducir:** Agregar productos al carrito → revisar desglose de facturación → comparar % de impuestos con el taxRate configurado.

---

## Datos del sitio

### Catálogo
- **Total productos:** 34
- **Categorías visibles:** 1 (Abarrotes)

### 5 productos con nombre + precio (referencia cruzada catálogo vs carrito)

| Producto | SKU | Precio Catálogo | Precio Carrito | Match |
|---|---|---|---|---|
| NESCAFE TRADICIONX25GR CJ48 | 82332 | $3.873/UN | $2.900/UN | ❌ Difiere |
| BASE MAGGI PASTA BOLOGNESA CJ24 | 80492 | $4.466/UN | $4.466/UN | ✅ Igual |
| CALDO COST.MAGGI DESMENZ. CJ1 | 82539 | $28.268/UN | $28.268/UN | ✅ Igual |
| CALDO GLLN.MAGGI DSMZ. CJ24 | 81349 | $5.813/UN | $5.813/UN | ✅ Igual |
| CALDO GLLN.MAGGIX88GR CJ36 | 80877 | $3.958/UN | $3.958/UN | ✅ Igual |

### Features confirmadas visualmente

| Feature (config) | Estado |
|---|---|
| anonymousAccess: true | ✅ Confirmado — catálogo y precios visibles sin login |
| anonymousHidePrice: false | ✅ Confirmado — precios visibles anónimo |
| anonymousHideCart: false | ✅ Confirmado — carrito accesible anónimo |
| loginButtons: google + facebook | ✅ Confirmado — ambos botones visibles en /auth/jwt/login |
| enableCoupons: true | ✅ Confirmado — campo "Ingresar cupón" visible en carrito |
| enableSellerDiscount: true | ✅ Confirmado — GALLETA COCOSETTE muestra "5% Dcto" ($45.089 → $42.835) |
| disableShowDiscount: false | ✅ Confirmado — descuento visible en catálogo |
| editAddress: true | ❌ No verificado — checkout bloqueado |
| purchaseOrderEnabled: true | ❌ No verificado — checkout bloqueado |
| enableOrderApproval: true | ❌ No verificado — checkout bloqueado |
| currency: CLP | ✅ Confirmado — todos los precios en CLP ($) |
| Monto mínimo de pedido | ✅ Visible — $40.000 (advertencia en carrito) |
| payment.enableNewPaymentModule: true | ❌ No verificado — checkout bloqueado |

---

## Resumen ejecutivo

El sitio `tienda.youorder.me` funciona correctamente para acceso anónimo, navegación de catálogo, búsqueda y gestión de carrito. El **bloqueador crítico es el site token expirado**, que impide el login de cualquier usuario y bloquea completamente el flujo de checkout. Adicionalmente, hay una **discrepancia de precio en NESCAFE** que no se refleja en la facturación del carrito (potencial bug en la integración del seller discount con el resumen de pagos).

**Acciones inmediatas requeridas:**
1. Renovar el site token (ISSUE-01) — bloquea login y checkout
2. Investigar discrepancia de precio NESCAFE catálogo vs carrito (ISSUE-02)
3. Retestear Flujo 4 (Checkout) una vez resuelto ISSUE-01
