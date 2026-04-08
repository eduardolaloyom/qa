# Sesión Cowork — new-soprole — 2026-04-08

---

## Modo A

```
HANDOFF — new-soprole — Modo A — 2026-04-08
Completado: [C1 ✓] [C2 ✓ con issues] [C3 N/A] [C7 N/A] [A1 N/A]
Issues encontrados:
  SOPROLE-QA-002 | P1 | C2-12 | Doble submit crea pedidos duplicados — botón no se deshabilita, sin idempotencia en API
  SOPROLE-QA-001 | P2 | C2-06 | Click en "−" con qty mínima elimina item directamente sin confirmación
  SOPROLE-QA-003 | P3 | C2-11 | "Número de pedido: #No disponible" en página /confirmation (en /orders sí aparece)
SIGUIENTE MODO A EJECUTAR: B
Contexto: Login con eduardo+newsoproleadmin@yom.ai / laloyom123. Código de cliente debe ingresarse manualmente antes de navegar a /products (sin él el catálogo no carga). 3 pedidos de prueba en staging (#18, #19, #20 — limpiar). Carrito vacío al terminar. enableCoupons visible en /cart. Precio con descuento 4% Dcto visible en catálogo.
```

---

## Modo B

```
HANDOFF — new-soprole — Modo B — 2026-04-08
Completado: [C1 ✓] [C2 ✗] [C3 ✓] [C7 N/A] [A1 N/A]
Issues encontrados:
  SOPROLE-QA-002 | P1 | C2-12 | Doble submit crea pedidos duplicados
  SOPROLE-QA-001 | P2 | C2-06 | Click "−" en mínimo elimina sin confirmación (reconfirmado en Modo B)
  SOPROLE-QA-003 | P3 | C2-11 | "#No disponible" en /confirmation
  SOPROLE-QA-004 | P3 | FLAGS | Badge pendingDocuments sin badge en campana (pendiente verificar flag en MongoDB)
SIGUIENTE MODO A EJECUTAR: C
Contexto: Login con eduardo+newsoproleadmin@yom.ai / laloyom123. Código cliente ingresado manualmente antes de /products. Carrito vacío ✓. enablePaymentDocumentsB2B=true confirmado, hay 1 doc pendiente ($169.364, ID 6041832100). Pedidos de prueba #18, #19, #20 aún pendientes de limpiar.
```

---

## Modo C

```
HANDOFF — new-soprole — Modo C — 2026-04-08
Completado: [C1 ✓] [C2 ✗] [C3 ✓] [C7 ✓*] [A1 N/A]
Issues encontrados:
  SOPROLE-QA-001 | P2 | C2-06 | Click "−" en mínimo elimina sin confirmación
  SOPROLE-QA-002 | P1 | C2-12 | Doble submit crea pedidos duplicados
  SOPROLE-QA-003 | P3 | C2-11 | "#No disponible" en /confirmation
  SOPROLE-QA-004 | P3 | FLAGS | Badge pendingDocuments no visible (MuiBadge-invisible)
SIGUIENTE MODO A EJECUTAR: D
Contexto: URL staging new-soprole.solopide.me. Login eduardo+newsoproleadmin@yom.ai / laloyom123.
  enablePaymentDocumentsB2B=true confirmado, doc $169.364 ID 6041832100 descargable.
  Pedidos de prueba #18, #19, #20 aún pendientes de limpiar.
  *C7-11 parcial: sin opción en menú lateral, sólo footer + tab en /orders.
```

---

## Modo D

```
HANDOFF — new-soprole — Modo D — 2026-04-08
Completado: [C1 ✓] [C2 ✗] [C3 ✓] [C7 ✓*] [C9 ✓] [C10 N/A] [C5 ✓]
Issues encontrados: SOPROLE-QA-005 (P3 — espaciado blanco /orders/{id})
SIGUIENTE MODO A EJECUTAR: completo — emitir veredicto final ✓ (ya emitido)
Contexto: Sesión activa eduardo+newsoproleadmin@yom.ai. Fixture C10 ausente —
  necesita comercio BLOQUEADO para cobertura completa. Pedidos #18-20 pendientes limpiar.
```
