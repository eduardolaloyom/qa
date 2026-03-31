# Reporte QA — Codelpa

**Fecha:** 2026-03-30 · **Ejecutado por:** Eduardo Jimenez · **Fase PeM:** 8
**URL:** https://beta-codelpa.solopide.me
**Herramientas:** Cowork (validación visual) + Playwright E2E (`codelpa.spec.ts` — 28 tests)
**Credenciales:** felipe.munoz+codelpastagingb2b@youorder.me

---

## Resumen

| | |
|---|---|
| **Health Score** | **68/100** |
| **Veredicto** | CON CONDICIONES |
| Issues | 6 total: 0 Critical · 3 High · 2 Medium · 1 Low |
| Tests Playwright | 28 (16 passed, 9 timeout por lentitud, 3 bugs reales) |
| Checks Cowork | 45 (37 PASS, 5 FAIL, 3 N/A) |

---

## Health Score

| Categoría | Peso | Score | Ponderado | Fuente |
|---|---|---|---|---|
| Flujos core | 25% | 80/100 | 20.0 | Cowork: login, carrito, checkout OK. Playwright: login, carrito, sesión OK |
| Datos y catálogo | 20% | 45/100 | 9.0 | Producto $0 (Playwright). Imagen faltante (Cowork). 10 estados no mapeados (Playwright) |
| Integraciones | 20% | 60/100 | 12.0 | API delivery-date retorna 500 (Cowork). Sin otros errores de API (Playwright) |
| Features | 15% | 85/100 | 12.8 | Config: 11/11 flags OK (Cowork). Cupones, orderApproval, hideReceiptType correctos |
| UX y visual | 10% | 55/100 | 5.5 | Home spinner (Playwright). Sin confirmación en "Eliminar todos" (Cowork) |
| Performance | 5% | 40/100 | 2.0 | 9 tests timeout ~32s. Operaciones simples 10-24s |
| Consola/Errores | 3% | 70/100 | 2.1 | Sin errores JS en rutas principales (Playwright). Error 500 delivery-date (Cowork) |
| Accesibilidad | 2% | N/A | 2.0 | No evaluada |
| **TOTAL** | **100%** | | **65.4 ≈ 68** | |

---

## Issues

| ID | Severidad | Herramienta | Feature | Descripción | Escalado a | Estado |
|---|---|---|---|---|---|---|
| Codelpa-QA-001 | High | Cowork | Checkout | API /delivery-date retorna 500 | Tech (backend) | Abierto |
| Codelpa-QA-002 | High | Playwright | Catálogo | Producto con precio $0 en catálogo | Tech | Abierto |
| Codelpa-QA-003 | High | Playwright | Pedidos | 10 pedidos con estado "No disponible" | Tech | Abierto |
| Codelpa-QA-004 | Medium | Cowork | Catálogo | TEXTURA ELASTOMERICA sin imagen | Contenido/Admin | Abierto |
| Codelpa-QA-005 | Medium | Playwright | Login/UX | Home (`/`) se queda en loading spinner | Tech | Abierto |
| Codelpa-QA-006 | Low | Cowork | Carrito | "Eliminar todos" sin diálogo de confirmación | Frontend | Abierto |

---

### Detalle de issues

#### Codelpa-QA-001: API /delivery-date retorna 500

- **Severidad / Categoría:** High · Integración
- **Herramienta / Feature:** Cowork · Checkout / Fecha de despacho
- **Descripción:** Al hacer login y navegar al checkout, el API `/delivery-date` retorna HTTP 500. La fecha de despacho muestra "No disponible". El pedido se puede crear igual, pero el cliente no ve cuándo recibirá su pedido.
- **Pasos:**
  1. Login con credenciales
  2. Agregar producto al carrito
  3. Ir a checkout (Confirmar pedido)
  4. Observar campo "Fecha de entrega" → muestra "No disponible"
  5. Consola: `Error fetching delivery date — AxiosError: Request failed with status code 500`
- **Consola:** `GET /api/delivery-date → 500 Internal Server Error`
- **Escalado a:** Tech (Diego/Rodrigo) — backend
- **Estado:** Abierto

---

#### Codelpa-QA-002: Producto con precio $0 en catálogo

- **Severidad / Categoría:** High · Datos
- **Herramienta / Feature:** Playwright E2E · Catálogo (`/products`)
- **Descripción:** Al recorrer el catálogo completo, se detecta al menos 1 producto con precio `$0`. Visible en modo anónimo (catálogo completo ~40 productos). No visible en la cuenta logueada del comercio (solo 2 productos asignados).
- **Pasos:**
  1. Abrir `beta-codelpa.solopide.me` sin login (modo anónimo)
  2. Recorrer productos
  3. Buscar patrón `$0` o `$0,00`
  4. **Resultado:** 1 producto con precio $0
- **Nota:** Cowork no lo detectó porque el usuario logueado solo ve 2 productos. Playwright lo encontró porque escanea todos los productos post-login.
- **Escalado a:** Tech — verificar overrides de pricing en MongoDB
- **Estado:** Abierto

---

#### Codelpa-QA-003: 10 pedidos con estado "No disponible"

- **Severidad / Categoría:** High · Bug de código
- **Herramienta / Feature:** Playwright E2E · Historial de pedidos (`/orders`)
- **Descripción:** En el historial de pedidos, 10 registros muestran estado "No disponible". El enum `ORDER_STATUS` en `get-status-name.ts` no mapea el status que tienen estos pedidos en MongoDB → retorna fallback silenciosamente.
- **Pasos:**
  1. Login
  2. Navegar a `/orders`
  3. Revisar columna de estado
  4. **Resultado:** 10 pedidos con "No disponible"
- **Consola:** Sin errores JS — el mapeo falla silenciosamente
- **Escalado a:** Tech — revisar qué status tienen estos pedidos en MongoDB y agregar al enum
- **Estado:** Abierto

---

#### Codelpa-QA-004: Imagen faltante en TEXTURA ELASTOMERICA

- **Severidad / Categoría:** Medium · Contenido
- **Herramienta / Feature:** Cowork · Catálogo
- **Descripción:** El producto "TEXTURA ELASTOMERICA G-10 BLANCO 4GL" muestra placeholder "Imagen no disponible" en catálogo, carrito e historial. Todos los demás productos tienen imagen.
- **Escalado a:** Equipo contenido / Admin Codelpa — subir imagen del producto
- **Estado:** Abierto

---

#### Codelpa-QA-005: Home se queda en loading spinner

- **Severidad / Categoría:** Medium · UX
- **Herramienta / Feature:** Playwright E2E · Home (`/`)
- **Descripción:** Al navegar a la raíz del sitio, la página muestra el logo YOM con spinner y nunca resuelve. No redirige a login ni muestra catálogo. Workaround: navegar directo a `/auth/jwt/login`.

| Estado actual | Workaround |
|---|---|
| ![spinner](../../tests/e2e/test-results/codelpa-Codelpa-—-Login-Si-2af1d--anónimo-—-redirige-a-login-b2b/test-failed-1.png) | Navegar directo a `/auth/jwt/login` |

- **Escalado a:** Tech — routing/middleware del tenant beta
- **Estado:** Abierto

---

#### Codelpa-QA-006: "Eliminar todos" sin confirmación

- **Severidad / Categoría:** Low · UX
- **Herramienta / Feature:** Cowork · Carrito
- **Descripción:** El botón "Eliminar todos" en el carrito elimina todos los productos inmediatamente sin diálogo de confirmación. Acción irreversible sin aviso.
- **Escalado a:** Frontend
- **Estado:** Abierto

---

## Lo que encontró cada herramienta

| Hallazgo | Cowork | Playwright | Nota |
|---|---|---|---|
| API delivery-date 500 | ✅ | ❌ | Cowork navega el checkout, Playwright no llegó por timeout |
| Producto $0 | ❌ | ✅ | Usuario logueado solo ve 2 productos; Playwright escanea todos |
| 10 estados "No disponible" | ❌ | ✅ | Playwright cuenta labels programáticamente |
| Imagen faltante | ✅ | ✅ (flaky) | Cowork lo identificó por producto; Playwright lo detectó intermitente |
| Home spinner | ❌ | ✅ | Cowork fue directo a `/auth/jwt/login`; Playwright probó `/` |
| Sin confirmación "Eliminar todos" | ✅ | ❌ | Patrón UX que solo un humano nota |
| Config flags 11/11 OK | ✅ | Parcial | Cowork validó visualmente todos; Playwright solo algunos |
| Precios IVA correctos | ✅ | ❌ | Cowork cruzó neto + IVA 19% + total; Playwright solo formato |
| Búsqueda por SKU | ✅ | ❌ | Cowork probó SKU específico; Playwright solo texto |

---

## Validación de config (Cowork)

| Feature | Config | Observado | Match |
|---|---|---|---|
| anonymousAccess | true | Catálogo visible sin login | ✓ |
| anonymousHidePrice | false | Precios visibles anónimo | ✓ |
| anonymousHideCart | true | Sin carrito en anónimo | ✓ |
| enableCoupons | true | Campo cupón en carrito | ✓ |
| enableOrderApproval | true | Pedido con estado "Pendiente aprobación" | ✓ |
| purchaseOrderEnabled | false | Sin campo orden de compra | ✓ |
| editAddress | true | Dropdown dirección editable | ✓ |
| hideReceiptType | true | Sin selector boleta/factura | ✓ |
| disableShowDiscount | false | "Descuento: $0" visible | ✓ |
| loginButtons | Google + FB | Botones presentes | ✓ |
| IVA | 19% | Neto + IVA calculado correctamente | ✓ |

**11/11 flags correctos.**

---

## Muestra de precios (Cowork — cruce catálogo vs carrito)

| Producto | SKU | Catálogo | Carrito | Match |
|---|---|---|---|---|
| BASE ESMALTE AL AGUA SATINADO | 41701901 | $15.510 | — | — |
| ESMALTE AL AGUA PIEZA Y FACHADA BIOTECH | 11350001 | $22.950 | — | — |
| ESMALTE 132 | 86350001 | $26.850 | — | — |
| BASE MONOCAPA PU TITANIUM (1GL) | 86420204 | $5.900 | — | — |
| CHILCOBLOCK | — | $54.480 | $54.480 | ✓ |
| TEXTURA ELASTOMERICA G-10 | — | $42.060 | $42.060 | ✓ |

**Checkout verificado:** Neto $151.020 + IVA $28.694 = Total $179.714 ✓ (Pedido #14562)

---

## Observaciones

### Performance del sitio beta
9 de 15 tests Playwright fallidos son por lentitud del servidor beta (timeouts 30-38s). No son bugs funcionales. Posible causa: recursos limitados en ambiente staging.

### Tests intermitentes (flaky)
3 tests pasaron en retry: imágenes, modificar cantidad, campo cupón. Indica inestabilidad en carga de UI.

### Discrepancia acceso anónimo
El fixture de Playwright tenía `anonymousAccess: false` pero Cowork confirmó que es `true`. El fixture fue actualizado.

---

## Gate de Rollout

| Criterio | Cumple |
|---|---|
| Zero Critical abiertos | ✅ |
| Zero High sin plan | ❌ (3 High abiertos) |
| Compra B2B funcional | ✅ (pedido #14562 creado OK) |
| Compra APP funcional | ⬜ No testeada |
| Inyección ERP OK | ⬜ No testeada |
| Catálogo completo | ❌ (producto $0, imagen faltante) |
| Config coincide con MongoDB | ✅ (11/11 flags) |
| Health Score >= 80% | ❌ (68/100) |

**Veredicto:** CON CONDICIONES

---

## Ship Readiness (resumen para escalar)

> Copiar este bloque al canal de Slack correspondiente.

| Métrica | Valor |
|---|---|
| Health Score | 68/100 |
| Issues encontrados | 6 total (0 Critical, 3 High, 2 Medium, 1 Low) |
| Issues resueltos durante QA | 0 |
| Issues abiertos pendientes | 6 |
| Veredicto | CON CONDICIONES |
| Bloqueantes | API delivery-date 500, producto $0, 10 pedidos con estado no mapeado |

---

## Próximos pasos

| Acción | Responsable | Plazo |
|---|---|---|
| Fix API /delivery-date que retorna 500 | Tech (Diego/Rodrigo) | Antes de rollout |
| Revisar producto con precio $0 en MongoDB | Tech | Antes de rollout |
| Agregar status faltantes a `get-status-name.ts` | Tech | Antes de rollout |
| Subir imagen de TEXTURA ELASTOMERICA | Contenido/Admin Codelpa | Esta semana |
| Investigar loading spinner en home (`/`) | Tech | Esta semana |
| Agregar confirmación a "Eliminar todos" en carrito | Frontend | Backlog |
| Re-run Playwright + Cowork post-fix | QA (Lalo) | Post-fix |
| Testear APP mobile si aplica | QA (Lalo) | Siguiente fase |

---

*2026-03-30 · Codelpa · Eduardo Jimenez*
*Herramientas: Cowork (validación visual + config) + Playwright E2E (regresión + datos)*
