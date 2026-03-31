# Checklist QA — Regresión basada en Post-mortems

> Fuente: [Post-mortems — Notion](https://www.notion.so/915bf7626ea141879a941f45b2e2ec57)
> Cada caso existe porque ya falló en producción. Son los tests de regresión más valiosos.
> Fecha creación: 2026-03-27

---

## PM-1: Cupones — Creación de orden con cupón (yom-api)

> **Incidente:** Import mal hecho rompió creación de órdenes con cupones. 39 llamadas fallaron en ~3 horas. Los tests existían pero estaban desactivados por un `describe.only`.

| # | Caso | Resultado esperado | Plataforma | Estado |
|---|------|-------------------|-----------|--------|
| PM1-01 | Crear orden con cupón de producto | Orden creada, descuento aplicado | B2B / API | PENDIENTE |
| PM1-02 | Crear orden con cupón de orden (% descuento total) | Orden creada, descuento en total | B2B / API | PENDIENTE |
| PM1-03 | Crear orden sin cupón (no debe romperse por cambios en cupones) | Orden creada normalmente | B2B / API | PENDIENTE |
| PM1-04 | Cupón inválido o expirado | Error claro, orden no se crea con descuento | B2B / API | PENDIENTE |
| PM1-05 | Cupón ya usado (límite de uso) | Rechazado con mensaje claro | B2B / API | PENDIENTE |

---

## PM-2: Cupones B2B — Tipo de cupón no soportado (yom-web)

> **Incidente:** B2B no soportaba cupones de orden (solo de producto). Pasó en pleno Cyber con Soprole — banner de 10% descuento y nadie podía usarlo.

| # | Caso | Resultado esperado | Plataforma | Estado |
|---|------|-------------------|-----------|--------|
| PM2-01 | Aplicar cupón de producto en checkout B2B | Descuento aplicado al producto | B2B | PENDIENTE |
| PM2-02 | Aplicar cupón de orden en checkout B2B | Descuento aplicado al total | B2B | PENDIENTE |
| PM2-03 | Cupón de orden + productos con descuento propio | Ambos descuentos se calculan correctamente | B2B | PENDIENTE |
| PM2-04 | Modal de cupón no queda en loading infinito | Botón de carga se desactiva post-respuesta | B2B | PENDIENTE |

---

## PM-3: Descuentos App Móvil — Crash al agregar descuento (yom-sales)

> **Incidente:** Un fix que seteaba un campo a `null` causó crash en la sección "Mi Pedido" al agregar descuento. Faltaba validación `instanceof` antes del casteo.

| # | Caso | Resultado esperado | Plataforma | Estado |
|---|------|-------------------|-----------|--------|
| PM3-01 | Agregar descuento a producto en pedido | Descuento aplicado, sin crash | App | PENDIENTE |
| PM3-02 | Agregar descuento a producto sin precio base | No crash, muestra error o ignora | App | PENDIENTE |
| PM3-03 | Editar descuento existente | Monto se actualiza correctamente | App | PENDIENTE |
| PM3-04 | Remover descuento de producto | Precio vuelve al original | App | PENDIENTE |

---

## PM-4: Step Pricing — Precios escalonados Soprole (yom-api)

> **Incidente:** Código sobreescribía los steps de precio. Soprole estuvo sin precios escalonados por días. No se detectó porque los tests estaban rotos y el ambiente local no tenía casos complejos.

| # | Caso | Resultado esperado | Plataforma | Estado |
|---|------|-------------------|-----------|--------|
| PM4-01 | Producto con step pricing muestra escalones correctos | Precios por tramo visibles (ej: 1-10 → $100, 11-50 → $90) | B2B / App | PENDIENTE |
| PM4-02 | Agregar producto con cantidad en tramo superior | Precio unitario corresponde al tramo | B2B / App | PENDIENTE |
| PM4-03 | Cambiar cantidad cruza tramo → precio se actualiza | Precio recalculado al nuevo tramo | B2B / App | PENDIENTE |
| PM4-04 | Step pricing + override de precio por segmento | Override tiene prioridad sobre step base | API | PENDIENTE |
| PM4-05 | Step pricing + promoción activa | Ambos se calculan correctamente sin conflicto | API | PENDIENTE |

---

## PM-5: Servicio de Promotions colapsado (yom-promotions)

> **Incidente:** Promotions tenía pocos pods y se llamaba desde catálogo + carrito (alta frecuencia). Al caer, fallaron catálogo, carrito y todo lo que mostraba precios.

| # | Caso | Resultado esperado | Plataforma | Estado |
|---|------|-------------------|-----------|--------|
| PM5-01 | Catálogo carga con promociones activas | Productos muestran precios con descuento | B2B / App | PENDIENTE |
| PM5-02 | Carrito calcula total con promociones | Descuentos reflejados en subtotal y total | B2B / App | PENDIENTE |
| PM5-03 | Servicio promotions lento → catálogo maneja timeout | No queda en loading infinito, muestra precios base o error | B2B | PENDIENTE |
| PM5-04 | Promoción expirada no se aplica | Precio vuelve al base | B2B / App | PENDIENTE |

---

## PM-6: Carga excesiva API — Índices faltantes en MongoDB (yom-api)

> **Incidente:** Query a colección de orders sin índices adecuados causó lentitud generalizada en toda la API. Afectó B2B, App y todas las integraciones.

| # | Caso | Resultado esperado | Plataforma | Estado |
|---|------|-------------------|-----------|--------|
| PM6-01 | Listado de órdenes responde en <3s | No hay full scan, query usa índices | API | PENDIENTE |
| PM6-02 | Filtrar órdenes por fecha responde rápido | Índice compuesto funciona | API | PENDIENTE |
| PM6-03 | Múltiples requests simultáneos a /orders | API no se degrada significativamente | API | PENDIENTE |

---

## PM-7: Caída yom-api — Dependencia cheerio sin pinear (yom-api)

> **Incidente:** `cheerio ^1.0.0-rc.3` se auto-actualizó a 1.0.0 que no soporta Node 12. API caída ~1.5 horas. Fix: pinear versión exacta.

| # | Caso | Resultado esperado | Plataforma | Estado |
|---|------|-------------------|-----------|--------|
| PM7-01 | API health-check responde correctamente | GET /api/health-check → 200 | API | PENDIENTE |
| PM7-02 | Hooks que usan cheerio (ej: elmuneco/runa) funcionan | Endpoint de hook responde sin MODULE_NOT_FOUND | API | PENDIENTE |

---

## Lecciones transversales (aplicar en todo QA)

| # | Lección del post-mortem | Cómo aplicar en QA |
|---|------------------------|-------------------|
| L1 | Tests desactivados por `describe.only` no se detectaron | Verificar en CI que no haya `.only` en tests |
| L2 | Dependencias sin pinear rompen producción | Auditar package.json por versiones con `^` en deps críticas |
| L3 | Ambiente local no refleja complejidad de producción | Tests deben cubrir al menos Soprole (cliente más complejo) |
| L4 | Un fix rompe otra funcionalidad que usa el mismo código | Tests de regresión deben cubrir múltiples flujos por componente |
| L5 | Falta Sentry/alertas de errores 500 | Validar que los endpoints no devuelven 500 silenciosamente |
| L6 | Índices faltantes en queries nuevas | Todo nuevo query a MongoDB debe verificarse con `.explain()` |
