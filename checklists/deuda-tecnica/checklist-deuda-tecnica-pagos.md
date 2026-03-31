# Checklist QA — Deuda Técnica: Pagos (App + API)

> Fuente: [Deuda Técnica — Notion](https://www.notion.so/protocolodesoporte/Deuda-T-cnica-19ad8139ba4e8061bb86cfd8db6f46fe)
> Item: "Refactor pagos" (plataforma App)
> Fecha creación: 2026-03-27

---

## Contexto del problema

El sistema de pagos tiene dos problemas documentados como deuda técnica:

1. **Inconsistencia de nombres**: El campo se llama `paymentDocuments` en BD pero se envía como `paymentItems` a la API, donde se renombra de vuelta. Esto causa bugs cuando se confunde el contexto (app vs API).

2. **Pagos negativos por notas de crédito**: Cuando una factura tiene notas de crédito asociadas, se generan dos `paymentDocuments` — uno positivo (factura) y uno negativo (nota de crédito). Esto genera edge cases difíciles de manejar.

---

## 1. Consistencia de campos paymentDocuments / paymentItems

| # | Caso | Cómo validar | Estado |
|---|------|-------------|--------|
| PAG-01 | Pago creado desde APP llega correctamente a la API | Crear pago en app → verificar en API que `paymentDocuments` tiene los items correctos | PENDIENTE |
| PAG-02 | Pago creado desde API directa tiene campo correcto | POST `/api/payment` con `paymentItems` → verificar que se almacena como `paymentDocuments` | PENDIENTE |
| PAG-03 | Consulta de pago desde APP muestra datos correctos | GET pago → verificar que la app interpreta correctamente los campos | PENDIENTE |
| PAG-04 | Consulta de pago desde B2B muestra datos correctos | Historial de pagos en B2B → montos coinciden con BD | PENDIENTE |
| PAG-05 | Consulta de pago desde Admin muestra datos correctos | Admin → detalle de pago → campos mapeados correctamente | PENDIENTE |

---

## 2. Pagos con notas de crédito (montos negativos)

| # | Caso | Cómo validar | Estado |
|---|------|-------------|--------|
| PAG-10 | Pago simple sin notas de crédito | Pagar factura sin NC → solo 1 paymentDocument positivo | PENDIENTE |
| PAG-11 | Pago de factura con nota de crédito asociada | Pagar factura con NC → 2 paymentDocuments (positivo + negativo) | PENDIENTE |
| PAG-12 | Monto total del pago es correcto con NC | Factura $100.000 + NC -$20.000 → total pago = $80.000 | PENDIENTE |
| PAG-13 | Múltiples facturas con NC en un solo pago | 3 facturas, 2 con NC → total correcto sumando positivos y negativos | PENDIENTE |
| PAG-14 | NC con monto mayor que factura | NC $150.000 sobre factura $100.000 → verificar comportamiento (¿se permite? ¿error?) | PENDIENTE |
| PAG-15 | Pago parcial de factura con NC | Pagar $50.000 de factura $100.000 que tiene NC -$20.000 → saldo correcto | PENDIENTE |
| PAG-16 | Listado de pagos no muestra montos negativos confusos | En historial de pagos, el usuario ve monto neto, no items negativos sueltos | PENDIENTE |
| PAG-17 | Reporte de pagos suma correctamente con negativos | Reporte/dashboard → totales cuadran incluyendo NC | PENDIENTE |
| PAG-18 | Exportación de pagos incluye desglose NC | Export CSV/Excel → columnas separadas para factura y NC | PENDIENTE |

---

## 3. Edge cases de pagos (derivados de la deuda)

| # | Caso | Cómo validar | Estado |
|---|------|-------------|--------|
| PAG-20 | Pago con monto $0 (factura = NC) | Factura $50.000 + NC -$50.000 → ¿se permite pago de $0? | PENDIENTE |
| PAG-21 | Pago duplicado (mismo monto, misma factura) | Intentar pagar factura ya pagada → debe rechazar o advertir | PENDIENTE |
| PAG-22 | Pago con documentos tributarios inexistentes | Enviar paymentDocuments con IDs inválidos → error claro | PENDIENTE |
| PAG-23 | Concurrencia: dos pagos simultáneos sobre misma factura | Desde app y B2B al mismo tiempo → solo uno debe procesarse | PENDIENTE |
| PAG-24 | Pago offline en app + sync posterior | Crear pago sin conexión → al sincronizar, se procesa correctamente | PENDIENTE |

---

## Notas

- Los tests PAG-01 a PAG-05 son validables hoy sin necesidad de refactor — solo verifican que el mapeo actual funciona.
- Los tests PAG-10 a PAG-18 cubren el comportamiento actual con notas de crédito y son los más propensos a fallar.
- Cuando el equipo ejecute el refactor de pagos, esta checklist sirve como **suite de regresión** para validar que el cambio no rompió nada.