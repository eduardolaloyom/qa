# Checklist Pre-Go-Live — Clientes Nuevos YOM

> **Propósito:** Obligatorio correr ANTES de salir a producción con cualquier cliente nuevo.
> Si algún ítem falla → **bloquear salida hasta resolver**.
> Origen: post-mortems PM-8 a PM-12 (incidentes Cedisur, 2026-03-31) + lecciones transversales PM-1 a PM-7.
> Fecha creación: 2026-03-31

---

## 🔴 Bloquers — No salir sin estos

### 1. Datos maestros completos

| # | Verificación | Cómo validar | Estado |
|---|------|-----------|--------|
| DM-01 | Catálogo de productos cargado | Contar SKUs en app vs fuente. Delta = 0 o explicado. | PENDIENTE |
| DM-02 | Sin productos duplicados | Buscar SKUs que aparezcan más de una vez | PENDIENTE |
| DM-03 | Todos los productos tienen imagen | Ningún placeholder ni imagen vacía visible | PENDIENTE |
| DM-04 | Catálogo de bancos propios cargado (medios de pago Transferencia) | Seleccionar Transferencia → aparecen cuentas de abono | PENDIENTE |
| DM-05 | Catálogo de bancos emisores cargado (Cheque) | Seleccionar Cheque → aparece listado de bancos | PENDIENTE |
| DM-06 | Catálogo de segmentos / listas de precio configurados | Al menos 1 segmento con lista de precio asignada | PENDIENTE |

---

### 2. Flujos críticos de cobranza (App)

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| COB-01 | Seleccionar factura → aparecen medios de pago | Lista visible sin acción adicional | PENDIENTE |
| COB-02 | Flujo completo con Efectivo | Cobro registrado en SAP | PENDIENTE |
| COB-03 | Flujo completo con Transferencia | Cobro registrado + cuenta de abono correcta | PENDIENTE |
| COB-04 | Flujo completo con Cheque | Cobro registrado + banco emisor correcto | PENDIENTE |
| COB-05 | Cobro con 2 medios de pago → SAP recibe 1 línea por comprobante | No desglosa por medio de pago | PENDIENTE |
| COB-06 | Facturas pendientes en app = facturas pendientes en API | Cruzar conteo UI vs `tax_document` | PENDIENTE |

---

### 3. Flujos críticos de pedidos (App / B2B)

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| PED-01 | Crear pedido con producto simple | Pedido en SAP con precio correcto | PENDIENTE |
| PED-02 | Crear pedido con productos de múltiples categorías | Orden completa sin errores | PENDIENTE |
| PED-03 | Precios mostrados coinciden con lista de precio del cliente | Sin diferencias entre catálogo y checkout | PENDIENTE |
| PED-04 | Stock reflejado correctamente (si aplica) | Sin pedidos sobre stock | PENDIENTE |

---

### 4. Integración SAP

| # | Verificación | Cómo validar | Estado |
|---|------|-----------|--------|
| SAP-01 | Webhook de actualización de estado de órdenes configurado | Al cambiar estado en SAP → se refleja en app | PENDIENTE |
| SAP-02 | Usuario STG de SAP disponible para pruebas | Credenciales recibidas y funcionando | PENDIENTE |
| SAP-03 | S2S (server-to-server) configurado y testeado | Transacción de prueba end-to-end sin errores | PENDIENTE |

---

## 🟡 Importantes — Resolver antes del piloto

### 5. Configuración del cliente en Admin

| # | Verificación | Cómo validar | Estado |
|---|------|-----------|--------|
| CFG-01 | Usuarios vendedores creados en Admin | Al menos los del piloto pueden loguear | PENDIENTE |
| CFG-02 | Campos obligatorios configurados son coherentes con el proceso del cliente | Ningún campo obliga a datos que el proceso no contempla | PENDIENTE |
| CFG-03 | Límite de crédito / descuento configurado correctamente | Documentación SD revisada y matcheada | PENDIENTE |

### 6. App funcionando

| # | Verificación | Cómo validar | Estado |
|---|------|-----------|--------|
| APP-01 | APK STG distribuida a usuarios del piloto | Todos tienen la última versión instalada | PENDIENTE |
| APP-02 | App sincroniza correctamente (no queda en loading) | Abrir → sincronizar → catálogo visible | PENDIENTE |
| APP-03 | VPN / conectividad resuelta si aplica | Acceso a endpoints sin errores de red | PENDIENTE |

---

## ✅ Proceso de sign-off

Antes de confirmar go-live, los siguientes roles deben haber corrido sus secciones:

| Sección | Responsable |
|---------|------------|
| Datos maestros (DM) | QA YOM + cliente (Rodrigo/Matias) |
| Flujos cobranza (COB) | QA YOM con usuario real del cliente |
| Flujos pedidos (PED) | QA YOM con usuario real del cliente |
| Integración SAP (SAP) | Dev YOM (Daniel) + IT cliente (Pablo) |
| Configuración Admin (CFG) | Dev YOM (Daniel / Alejandro) |
| App (APP) | QA YOM + al menos 1 vendedor del piloto |

**Go-live se confirma cuando:** todos los 🔴 Bloquers están en ✅ y los responsables firman off.

---

## Historial de uso

| Cliente | Fecha | QA | Resultado |
|---------|-------|----|-----------|
| Cedisur | 2026-03-31 | — | DM-02, DM-03, DM-04, DM-05, COB-01, COB-05, COB-06 fallaron en piloto. Salida a prod lunes en riesgo. |
