# Checklist QA — Fintech: Pagos Khipu

> Fuente: [Fintech — Notion](https://www.notion.so/2dad8139ba4e801c9005f2f5f1bebcbd)
> Servicio: NestJS backend multi-tenant para pagos vía Khipu
> Fecha creación: 2026-03-27

---

## Contexto

El Fintech Service gestiona pagos a través de Khipu (pasarela de pagos chilena). Es multi-tenant: cada cliente tiene su propia API key de Khipu y credenciales independientes. Usa MongoDB, JWT, Docker, S3, y tareas programadas para actualizar estados.

### Clientes activos con Khipu
- Marley Coffee
- Expressdent
- (nuevos clientes se agregan siguiendo el checklist de Notion)

### Configuración por cliente
- `{CLIENTE}_KHIPU_API_KEY` — API key de Khipu
- `CLIENT_{CLIENTE}_ID` — Client ID para auth
- `CLIENT_{CLIENTE}_SECRET` — Client secret para auth
- `site.payment.externalPayment = "khipu"` en BD `yom-stores.sites`

---

## 1. Flujo de pago Khipu

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| KHP-01 | Iniciar pago desde B2B (cliente con Khipu activo) | Redirect a Khipu con monto correcto | PENDIENTE |
| KHP-02 | Pago exitoso en Khipu → callback | Estado del documento se actualiza a pagado | PENDIENTE |
| KHP-03 | Pago cancelado en Khipu | Documento sigue pendiente, usuario puede reintentar | PENDIENTE |
| KHP-04 | Pago expirado en Khipu | Tarea programada detecta y actualiza estado | PENDIENTE |
| KHP-05 | Monto del pago coincide con documentos seleccionados | No hay diferencia entre lo cobrado y lo adeudado | PENDIENTE |

---

## 2. Multi-tenant: credenciales por cliente

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| KHP-10 | Pago de Marley Coffee usa API key de Marley Coffee | Request a Khipu con key correcta del cliente | PENDIENTE |
| KHP-11 | Pago de Expressdent usa API key de Expressdent | No se cruzan credenciales entre clientes | PENDIENTE |
| KHP-12 | Cliente sin Khipu configurado intenta pagar | No aparece opción de pago externo o muestra error claro | PENDIENTE |
| KHP-13 | API key inválida para un cliente | Error controlado, no expone keys de otros clientes | PENDIENTE |
| KHP-14 | `getSecretKey()` resuelve dominio correctamente | Matching case-insensitive con `includes()` | PENDIENTE |

---

## 3. Documentos de pago (bulk operations)

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| KHP-20 | Crear documento de pago individual | Documento creado con monto y referencia | PENDIENTE |
| KHP-21 | Crear documentos de pago en bulk | Todos los documentos creados correctamente | PENDIENTE |
| KHP-22 | Documento pendiente se auto-finaliza (tarea programada) | Estado cambia automáticamente según respuesta de Khipu | PENDIENTE |
| KHP-23 | Notificación por email post-pago | Email enviado al comercio con confirmación | PENDIENTE |

---

## 4. Seguridad

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| KHP-30 | Request sin JWT válido | Rechazado 401 | PENDIENTE |
| KHP-31 | JWT de un cliente no accede a datos de otro | Aislamiento multi-tenant | PENDIENTE |
| KHP-32 | Secrets de GitHub configurados correctamente | Deploy no falla por variables faltantes | PENDIENTE |

---

## 5. Onboarding nuevo cliente (regresión del checklist)

> Cuando se agrega un nuevo cliente a Khipu, verificar:

| # | Verificación | Estado |
|---|-------------|--------|
| KHP-40 | `getSecretKey()` actualizado con nuevo dominio | PENDIENTE |
| KHP-41 | `getClientCredentials()` actualizado con nuevo switch case | PENDIENTE |
| KHP-42 | `khipuCustomers` array incluye nuevo nombre | PENDIENTE |
| KHP-43 | Dockerfile tiene las 3 variables ARG/ENV | PENDIENTE |
| KHP-44 | GitHub Actions workflow tiene build-args | PENDIENTE |
| KHP-45 | Secrets configurados en GitHub | PENDIENTE |
| KHP-46 | `site.payment.externalPayment = "khipu"` en BD | PENDIENTE |
| KHP-47 | Funciona en staging antes de producción | PENDIENTE |
