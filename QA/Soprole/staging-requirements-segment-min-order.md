# Staging requirements — Pedido mínimo por segmento (Soprole)

Documento para el equipo de desarrollo. Define exactamente qué datos de staging
necesita QA para ejecutar los tests en `tests/e2e/b2b/segment-min-order.spec.ts`.

---

## Contexto

- **Estado actual**: `salesterms.order.minTotalPrice = 48000` (un valor plano por cliente)
- **Feature solicitada**: mínimo opcional por segmento; si está definido, aplica ese; si no, usa el global; si el usuario está en varios segmentos, gana el mayor
- **Ambiente de pruebas**: `soprole.solopide.me`

---

## Qué necesitamos en staging

### 1. Feature flag habilitado

Nombre de la variable de sitio que activa este comportamiento: **[dev confirmar nombre]**

Debe estar en `true` en `soprole.solopide.me`.

Para el test de "flag OFF" necesitamos saber si hay una forma de desactivarlo sin afectar el sitio completo (ej: otro alias de staging, o un param en la sesión).

---

### 2. Tres segmentos de prueba en Soprole staging

| Segmento | minOrderValue | Descripción |
|---|---|---|
| `QA-SEG-HIGH` | `80000` | Mínimo mayor al global |
| `QA-SEG-MID` | `60000` | Segundo valor para test "max gana" |
| `QA-SEG-NONE` | *(no definido)* | Debe hacer fallback al global 48000 |

Pueden ser segmentos nuevos o usar los existentes (Soprole ya tiene 717 segmentos SAP). Si se reutilizan existentes, pasarnos el nombre/ID para actualizar el fixture.

---

### 3. Tres usuarios de prueba en Soprole staging

| Usuario | Segmentos asignados | Env var esperado |
|---|---|---|
| Usuario A | `QA-SEG-HIGH` (solo) | `SOPROLE_SEGMENT_HIGH_EMAIL` / `_PASSWORD` |
| Usuario B | `QA-SEG-HIGH` + `QA-SEG-MID` | `SOPROLE_SEGMENT_MULTI_EMAIL` / `_PASSWORD` |
| Usuario C | `QA-SEG-NONE` (o sin segmento) | `SOPROLE_SEGMENT_NONE_EMAIL` / `_PASSWORD` (o usar `SOPROLE_EMAIL` existente) |

Los usuarios ya deben tener acceso al catálogo para que Playwright pueda agregar productos al carro.

---

### 4. Comportamiento esperado de la API

QA necesita saber qué endpoint devuelve el `minTotalPrice` resuelto para el usuario logueado. Opciones probables:

- `GET /salesterms` → campo `order.minTotalPrice`
- `GET /cart/config` → campo `minTotalPrice`
- `GET /site/config` → campo `minTotalPrice`

Una vez confirmado, actualizar `interceptSalesterms()` en el spec con el path exacto.

---

### 5. Mensaje de error en UI (B2B)

Cuando el carrito no llega al mínimo del segmento, ¿qué texto muestra la UI?

Opciones:
- Mismo mensaje actual con el monto dinámico: *"Monto mínimo de pedido: $80.000"*
- Texto distinto

QA necesita el texto exacto para agregar un selector a `selectors.ts`.

---

## Checklist para dev antes de avisar a QA

- [ ] Feature flag creado y habilitado en `soprole.solopide.me`
- [ ] Tres segmentos de prueba creados con los valores indicados
- [ ] Tres usuarios de prueba creados y asignados a sus segmentos
- [ ] API endpoint confirmado (qué ruta devuelve el min resuelto)
- [ ] Texto del mensaje de error en UI confirmado
- [ ] Credenciales de los usuarios de prueba enviadas a QA (por canal seguro)

---

## Lo que QA hace cuando dev completa el checklist

1. Agregar credenciales al `.env` local
2. Quitar los `test.skip(true, ...)` del spec
3. Correr `npx playwright test segment-min-order --project=b2b`
4. Si pasan los 5 tests → feature lista para producción
5. Si alguno falla → bug report a dev con screenshot y trace

---

*Fecha creación: 2026-04-22*
*Spec relacionado: `tests/e2e/b2b/segment-min-order.spec.ts`*
