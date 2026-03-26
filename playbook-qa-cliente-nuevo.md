# Playbook QA — Cliente Nuevo

> Proceso paso a paso para validar que un cliente nuevo está listo para producción.
> Tiempo estimado: 1-2 días dependiendo de complejidad del cliente.

---

## Prerequisitos

Antes de empezar QA, confirmar que el equipo entregó:

| Item | Quién lo entrega | Cómo verificar |
|---|---|---|
| Subdominio B2B activo | Tech (Diego/Rodrigo) | Abrir `https://{cliente}.youorder.me` |
| Usuario vendedor APP | Tech | Login en APP con las credenciales |
| Usuario comercio B2B | Tech | Login en B2B con las credenciales |
| Features configuradas en MongoDB | Tech + Analytics | `checklist-generator.py` las extrae |
| Catálogo cargado | Analytics (Diego F/Nicole) | Productos visibles post-login |
| Integraciones activas (ERP, etc.) | Tech | Según config del cliente |

---

## Fase 1 — Preparación (30 min)

### 1.1 Generar checklist del cliente

```bash
cd ~/Desktop/YOM/qa
python3 tools/checklist-generator.py --cliente {NOMBRE} -o QA/{NOMBRE}/{FECHA}/checklist.md
```

Esto genera un checklist personalizado con los casos que aplican según las features activas del cliente.

### 1.2 Preparar credenciales

Crear archivo de credenciales para los tests automatizados:

```bash
# Para Playwright (B2B)
cat > tests/e2e/.env << EOF
BASE_URL=https://{cliente}.youorder.me
COMMERCE_EMAIL={email-comercio}
COMMERCE_PASSWORD={password}
EOF
```

### 1.3 Confirmar acceso

- [ ] Abrir `https://{cliente}.youorder.me` — carga sin error
- [ ] Si `anonymousAccess=true`: catálogo visible sin login
- [ ] Si `anonymousAccess=false`: redirect a login
- [ ] Abrir APP Yom Ventas → login con credenciales del vendedor

---

## Fase 2 — QA Automatizado B2B (15 min)

### 2.1 Correr Playwright

```bash
cd ~/Desktop/YOM/qa/tests/e2e
npx playwright test
```

Los 19 tests corren contra el subdominio del cliente. Cubren:
- Login / acceso anónimo
- Catálogo y búsqueda
- Carrito (agregar, modificar, eliminar)
- Checkout (crear pedido)
- Precios (consistencia, descuentos, cupones)

### 2.2 Interpretar resultados

| Resultado | Acción |
|---|---|
| Todo verde | Pasar a Fase 3 |
| Login falla | Verificar credenciales o site token expirado → escalar a Tech |
| Precios inconsistentes | Documentar y escalar a Analytics |
| Checkout falla | Verificar monto mínimo, dirección, config → escalar a Tech |

### 2.3 Guardar reporte

```bash
npx playwright show-report
# Screenshot o copiar resumen a QA/{NOMBRE}/{FECHA}/
```

---

## Fase 3 — QA Manual B2B con Cowork (30 min)

Usar el skill de Cowork para exploración visual:

1. Abrir `https://{cliente}.youorder.me`
2. Validar visualmente los 5 flujos:
   - Catálogo: productos con imagen, nombre, precio correcto
   - Carrito: agregar, cantidad, totales
   - Precios: comparar 5 productos catálogo vs carrito
   - Features: cupones, descuentos, según config del cliente
   - UX: búsqueda, filtros, navegación
3. Documentar issues con screenshot

Guardar reporte en `QA/{NOMBRE}/{FECHA}/reporte-cowork.md`

---

## Fase 4 — QA APP Móvil (1-2 horas)

### 4.1 Ambiente

- **Dispositivo:** Celular físico Android (preferido) o emulador
- **APK:** Yom Ventas desde Play Store (producción) o APK staging desde GitHub Actions
- **Credenciales:** Vendedor del cliente nuevo

### 4.2 Ejecutar checklist APP

Seguir el checklist de `checklist-puesta-en-marcha-app.md` adaptado al cliente:

| Sección | Qué validar | Tiempo |
|---|---|---|
| Autenticación | Login, logout, recuperar password | 10 min |
| Sincronización | Datos se cargan, sync manual funciona | 10 min |
| Comercios | Listado, búsqueda, filtros, estados | 10 min |
| Detalle comercio | Info, tareas, datos, cobranza | 10 min |
| Flujo pedido | Catálogo → carrito → checkout completo | 20 min |
| Precios | Consistencia catálogo vs carrito vs MongoDB | 15 min |
| Pedidos | Historial, detalle, estados | 10 min |
| Cobranza | Registrar pagos, facturas | 10 min |
| Offline | Navegar sin internet, crear pedido offline, sync al reconectar | 15 min |

### 4.3 Puntos críticos por features del cliente

Verificar según la config en MongoDB:

| Feature | Si está activa, verificar que... |
|---|---|
| `enableCoupons` | Campo de cupón visible en checkout |
| `enableSellerDiscount` | Vendedor puede aplicar descuento % |
| `enableAskDeliveryDate` | Selector de fecha aparece antes de confirmar |
| `enableOrderApproval` | Pedido pasa a estado "Pendiente aprobación" |
| `enablePaymentsCollection` | Sección de cobranza funcional |
| `enableCreditNotes` | Notas de crédito visibles |
| `enableTask` | Pestaña tareas en comercio |
| `hasStockEnabled` | Stock visible en catálogo |
| `enableChooseSaleUnit` | Dropdown de unidad de venta |
| `includeTaxRateInPrices` | Precios incluyen/excluyen IVA según config |

---

## Fase 5 — Documentar y escalar (30 min)

### 5.1 Clasificar issues

| Severidad | Criterio | Ejemplo |
|---|---|---|
| Critical | Bloquea uso de la plataforma | Login no funciona, sync falla |
| Alta | Funcionalidad core rota | Pedido no se crea, precio incorrecto |
| Media | Funcionalidad secundaria con problema | Búsqueda sensible a tildes, filtro no funciona |
| Baja | UX o cosmético | Sin mensaje "carrito vacío", texto cortado |

### 5.2 Escalar por canal

| Tipo de issue | A quién | Canal |
|---|---|---|
| Bug de código | Rodrigo / Diego C | Slack #tech |
| Datos incorrectos | Diego F / Nicole | Slack #analytics |
| Config mal puesta | Tech | Slack #tech |
| Contenido del cliente | Max → Cliente | Slack #cs |
| Integración ERP | Analytics + Tech | Slack #tech + #analytics |

Usar templates de `templates/escalation-templates.md`.

### 5.3 Guardar evidencia

```
QA/{NOMBRE}/{FECHA}/
├── checklist.md          ← Checklist generado con resultados
├── reporte-cowork.md     ← Reporte visual B2B
├── reporte-app.md        ← Resultados APP
├── playwright-report/    ← Reporte HTML de Playwright
└── screenshots/          ← Evidencia de issues
```

---

## Fase 6 — Veredicto

### Gate de Rollout

| Criterio | Peso | Umbral |
|---|---|---|
| Flujos core (login, pedido, sync) | 30% | 100% PASS |
| Datos y catálogo correctos | 20% | 100% PASS |
| Integraciones (ERP, pagos) | 20% | 100% PASS |
| Features del cliente | 15% | 90%+ PASS |
| UX y transversales | 10% | 80%+ PASS |
| Performance | 5% | Sin bloqueos |

### Veredicto final

| Estado | Condición | Acción |
|---|---|---|
| **LISTO** | Todo PASS, 0 bugs critical/high | Avanzar a capacitaciones → Rollout |
| **CON CONDICIONES** | Bugs medium que no bloquean uso | Rollout con plan de resolución documentado |
| **NO APTO** | Bugs critical o high sin resolver | Volver a fase de desarrollo/config, re-testear |

---

## Resumen rápido

```
1. Generar checklist          →  python3 checklist-generator.py --cliente X
2. Correr Playwright (B2B)    →  npx playwright test (15 min)
3. Explorar B2B con Cowork    →  validación visual (30 min)
4. Testear APP en celular     →  checklist manual (1-2 hrs)
5. Documentar y escalar       →  issues + evidencia (30 min)
6. Veredicto                  →  LISTO / CON CONDICIONES / NO APTO
```
