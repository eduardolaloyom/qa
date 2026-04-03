# QA Master Guide — Plataforma YOM

Fuente única de verdad para el proceso de QA. Consolida filosofía, responsabilidades, casos canónicos y procedimientos.

---

## 1. Filosofía QA

**Cowork (Claude) es la herramienta primaria.** Simula interacción humana real, valida que la configuración del cliente se vea correctamente (banners, fechas, datos, flujos completos). Los tests automatizados son regresión y cobertura complementaria.

**Prioridad de herramientas:**
```
Cowork (validación visual + config) 
  > Playwright (regresión E2E) 
  > Maestro (APP mobile) 
  > Checklists manuales (servicios backend)
```

**Tests unitarios no son foco de QA.** Los devs cubren eso. QA cubre integración, configuración de clientes y flujos end-to-end.

---

## 2. Contexto del Producto

**YOM (You Order Me)** — Plataforma SaaS B2B para digitalización del canal tradicional.

| Plataforma | URL | Stack |
|-----------|-----|-------|
| **B2B** (tienda) | `{slug}.youorder.me` | Next.js / React + MUI v5 |
| **Admin** | `admin.youorder.me` | Next.js / React |
| **APP** (vendedores) | App móvil | React Native + Expo SDK 53 |
| **API** | `api.youorder.me/api/v2/` | Node.js / Express |
| **DB** | MongoDB | yom-stores, yom-production, yom-promotions, b2b-marketing |

### Roles en el sistema

| Rol | Descripción |
|-----|-------------|
| COMMERCE | Negocio B2B que compra a través de la tienda |
| SELLER | Vendedor que gestiona comercios vía APP |
| SUPERVISOR | Gestiona y supervisa vendedores |
| ADMIN | Administrador de la plataforma por cliente |
| CLIENT_ADMIN | Empresa que vende (configura su tienda) |

### Multi-tenant
Cada cliente YOM tiene su propia tienda (`{slug}.youorder.me`) con config en MongoDB. Los tests deben validar configuración por cliente, no solo funcionalidad genérica.

---

## 3. Quién Hace Qué

### QA (Lalo)

| Actividad | Herramienta | Frecuencia |
|-----------|-------------|-----------|
| Validar B2B de clientes nuevos | Playwright E2E + checklists funcionales | Cada onboarding |
| Validar APP en puesta en marcha | Maestro flows + checklist app | Cada onboarding |
| Revisar post-deploy a producción | Checklists de regresión (según área afectada) | Cada release |
| Documentar issues encontrados | Templates de escalamiento | Continuo |
| Mantener checklists actualizadas | Agregar casos cuando aparezcan bugs nuevos | Continuo |

### Devs (Diego, Rodrigo)

| Actividad | Herramienta | Frecuencia |
|-----------|-------------|-----------|
| Correr E2E antes de merge a main | `npx playwright test --project=b2b` | Cada PR |
| Agregar tests cuando fixen un bug | Nuevo `.spec.ts` o caso en spec existente | Cada fix |
| Validar integraciones ERP post-cambio | Checklist integraciones + logs erpIntegrations | Cada cambio en hooks |
| Revisar pricing post-cambio | `prices.spec.ts` + `step-pricing.spec.ts` | Cada cambio en pricing |
| No dejar `describe.only` / `test.only` | Code review | Siempre (lección PM1) |

---

## 4. Cuándo Usar Cada Herramienta

### En cada deploy a producción

```
Siempre:
  ✓ Correr E2E B2B completo (Playwright)
  ✓ Revisar checklist regresión post-mortems (los 7 incidentes)

Si toca pricing/promociones:
  ✓ checklist-pricing-engine.md
  ✓ step-pricing.spec.ts + promotions.spec.ts

Si toca cupones:
  ✓ coupons.spec.ts
  ✓ Sección PM1/PM2 de regresión post-mortems

Si toca pagos/cobranza:
  ✓ checklist-deuda-tecnica-pagos.md
  ✓ payments.spec.ts + flow 08-pagos.yaml

Si toca carrito:
  ✓ checklist-carrito-b2b.md
  ✓ cart.spec.ts + checkout.spec.ts

Si toca integraciones/hooks:
  ✓ checklist-integraciones-erp.md
  ✓ checklist-webhooks.md
```

### En onboarding de cliente nuevo

```
1. playbook-qa-cliente-nuevo.md (proceso completo)
2. checklist-puesta-en-marcha-app.md (si usa APP)
3. Playwright multi-cliente:
   BASE_URL=https://{nuevo-cliente}.youorder.me npx playwright test --project=b2b
4. Si usa Khipu → checklist-fintech-khipu.md (sección onboarding)
5. Si tiene hooks ERP → checklist-webhooks.md + checklist-integraciones-erp.md
```

### Post-incidente

```
1. Identificar qué post-mortem es más similar al incidente
2. Ejecutar sección correspondiente de checklist-regresion-postmortems.md
3. Si no hay test automatizado → crear uno
4. Agregar el caso al checklist para futuros deploys
```

### En migraciones de infraestructura

```
Migración MongoDB:
  ✓ checklist-deuda-tecnica-general.md → sección MG-01 a MG-06
  ✓ E2E completo pre y post migración

Upgrade Node.js:
  ✓ checklist-deuda-tecnica-general.md → sección ND-01 a ND-05

Migración a SSR:
  ✓ checklist-deuda-tecnica-general.md → sección SSR-01 a SSR-07
  ✓ E2E completo post-migración
```

---

## 5. Origen de Checklists

Cada checklist proviene de fuentes reales de Notion. No son casos inventados — son problemas que ya ocurrieron o riesgos documentados.

| Checklist | Fuente en Notion | Qué cubre |
|-----------|-----------------|-----------|
| Regresión post-mortems | [Post-mortems](https://www.notion.so/915bf7626ea141879a941f45b2e2ec57) | 7 incidentes reales |
| Deuda técnica — Pagos | [Deuda Técnica](https://www.notion.so/19ad8139ba4e8061bb86cfd8db6f46fe) | paymentDocuments, notas crédito |
| Deuda técnica — General | [Deuda Técnica](https://www.notion.so/19ad8139ba4e8061bb86cfd8db6f46fe) | Race conditions, migraciones |
| Pricing engine | [Pricing Tech Wiki](https://www.notion.so/27b1bef354734c8aa97414ca9944cee8) | 4 descuentos + impuestos |
| Carrito B2B | [Tareas carrito](https://www.notion.so/294d8139ba4e8067b628f5af1d37e6a9) | Refresh, migración, historial |
| Eventos GA4 | [[B2B] Eventos](https://www.notion.so/2bdd8139ba4e80d0aeddc9f861d92b79) | 62 eventos, funnel conversión |
| Puesta en marcha APP | Proceso interno | Login, sync, pedidos, precios app |
| Integraciones ERP | [Cronjob reintento](https://www.notion.so/24fd8139ba4e80438aa0e71412c0721e) | Hooks, cronjob 30min |
| Webhooks | [Webhooks Tech Wiki](https://www.notion.so/222d8139ba4e805a9d1fd8c35d51d9c4) | 13 hooks, estados |
| Fintech / Khipu | [Fintech](https://www.notion.so/2dad8139ba4e801c9005f2f5f1bebcbd) | Pagos Khipu multi-tenant |
| Integration Validator | [Integration Validator](https://www.notion.so/320d8139ba4e80cc80d9c413e092ab2e) | Lambda CSV/JSON/Excel |

---

## 6. Flujos Críticos — Tier 1 (Prioridad Máxima)

Si alguno de estos falla en producción, el cliente no puede operar.

### [C1] Login de Comercio (B2B)

| ID | Caso | Tipo |
|---|---|---|
| C1-01 | Login exitoso con email y contraseña | E2E |
| C1-02 | Login fallido — contraseña incorrecta | Integration |
| C1-03 | Login fallido — usuario no existe | Integration |
| C1-05 | Login con comercio bloqueado | Integration |
| C1-07 | Sesión persistente (recordarme) | E2E |
| C1-08 | Logout exitoso | E2E |

### [C2] Flujo de Compra Completo (B2B)

| ID | Caso | Tipo |
|---|---|---|
| C2-01 | Ver catálogo con productos | E2E |
| C2-02 | Buscar producto por nombre | E2E |
| C2-05 | Agregar producto al carro | E2E |
| C2-06 | Agregar producto con cantidad < mínimo | Integration |
| C2-11 | Crear pedido exitoso | E2E |
| C2-12 | Doble submit de crear pedido | Integration |
| C2-13 | Pedido aparece en historial | E2E |

### [C3] Cálculo de Precios y Descuentos

| ID | Caso | Tipo |
|---|---|---|
| C3-01 | Precio base sin sobrescritura | Unit |
| C3-02 | Precio con override REPLACE | Unit |
| C3-14 | Cupón de descuento válido | E2E |
| C3-15 | Cupón expirado | Integration |
| C3-17 | Producto sin override → no visible en catálogo | Integration |
| C3-18 | Override base disabled + override segmento enabled | Integration |

### [C4] Inyección de Pedido al ERP

| ID | Caso | Tipo |
|---|---|---|
| C4-01 | Inyección exitosa | Integration |
| C4-02 | Inyección con timeout | Integration |
| C4-08 | Reintentos ante fallo con backoff | Integration |
| C4-09 | `externalIdRequired=true` sin externalId → fallo silencioso | Integration |

### [V1] Vendedor Toma Pedido (APP)

| ID | Caso | Tipo |
|---|---|---|
| V1-01 | Ver comercios asignados | E2E (Maestro) |
| V1-03 | Tomar pedido — agregar productos | E2E (Maestro) |
| V1-04 | Confirmar pedido | E2E (Maestro) |
| V1-05 | Pedido offline | E2E (Maestro) |
| V1-06 | Sync de pedidos offline | E2E (Maestro) |

### [A1] Login de Admin

| ID | Caso | Tipo |
|---|---|---|
| A1-01 | Login admin exitoso | E2E |
| A1-03 | Acceso sin autenticación → redirect | Integration |
| A1-06 | Admin gestiona productos | E2E |
| A1-07 | Admin gestiona promociones | E2E |
| A1-08 | Admin gestiona banners | E2E |

### [C7] Documentos Tributarios

| ID | Caso | Tipo |
|---|---|---|
| C7-01 | Factura generada post-pedido | Integration |
| C7-06 | Nota de crédito vinculada | Integration |
| C7-10 | Factura visible en B2B (flag enablePaymentDocumentsB2B) | E2E |
| C7-12 | Badge documentos pendientes | E2E |

---

## 7. Flujos Tier 2

Implementar después de Tier 1. Regresión de features conocidas.

| ID | Flujo |
|---|---|
| C9 | Seguimiento de pedido en B2B |
| C10 | Estado crediticio bloqueado |
| C5 | Canasta base y recomendaciones (B2B + APP) |
| C6 | Sincronización de datos (Scheduled API) |
| C8 | Validación de integración del cliente (Pre-QA) |
| V2 | Ruta del día vendedor |
| A2 | Gestión de comercios (Admin) |
| A3 | Configuración de tienda (Admin branding) |

---

## 8. Flujos Tier 3 (Backlog)

| ID | Flujo |
|---|---|
| C11 | Compartir pedido |
| V5 | Gestión de tareas (vendedor) |
| A4 | Dashboards Metabase |

---

## 9. Fixtures de Datos de Prueba

### Comercios
```
commerce_active           → activo, crédito OK, segmento estándar
commerce_blocked          → estado crediticio BLOQUEADO
commerce_alert            → estado crediticio ALERTA
commerce_new              → recién creado, sin historial
commerce_b2b_multi_segment → en múltiples segmentos con overrides
```

### Productos
```
product_active            → ACTIVE, stock > 0, imagen, precio base
product_no_stock          → ACTIVE, stock = 0
product_discontinued      → DISCONTINUED (no debe aparecer en catálogo)
product_with_min_unit     → MinUnit = 6 (mínimo de compra)
product_with_step         → paso de incremento (múltiplos)
product_low_price         → precio < $50 (debe bloquearse en carro)
product_multi_format      → pack/unidad/caja
```

### Órdenes
```
order_pending             → PENDIENTE
order_confirmed           → CONFIRMADA por ERP
order_in_process          → EN_PROCESO
order_delivered           → ENTREGADA
order_cancelled           → CANCELADA
order_with_observations   → con notas del comercio
order_offline             → creada offline en APP (pendiente sync)
```

### Cupones y Promociones
```
promo_catalog_active      → descuento de catálogo vigente
promo_catalog_expired     → descuento expirado
promo_volume_stepped      → descuento por volumen con 3 escalas
promo_coupon_valid        → cupón activo
promo_coupon_expired      → cupón vencido
promo_coupon_used         → cupón de uso único ya usado
```

### Overrides (Precios por segmento)
```
override_replace          → operación REPLACE para segmento A
override_add              → ADD (+$500) para segmento B
override_multiply         → MULTIPLY (×0.9) para segmento C
override_base_disabled    → enabled=false, prioridad 10000, precio 99999
override_segment_enabled  → activa producto sobre base disabled
override_conflict_multi   → 2 overrides para mismo producto, segmentos distintos
```

---

## 10. Cómo Correr los Tests

### Pipeline Completo (MongoDB → Playwright)

```bash
# Ejecuta: extrae Mongo → regenera clients.ts → genera checklist → corre Playwright
./tools/run-qa.sh Codelpa

# O paso a paso:
python3 data/mongo-extractor.py          # Extrae 4 DBs → data/qa-matrix.json
python3 tools/sync-clients.py            # qa-matrix.json → clients.ts (AUTO-GENERADO)
npx playwright test --project=b2b        # Tests B2B
npx playwright test --project=admin      # Tests Admin
```

### Playwright

```bash
cd tests/e2e

# Todos los tests B2B
npx playwright test --project=b2b

# Solo un cliente
npx playwright test --project=b2b -g "codelpa"

# Debug modo visual
npx playwright test --project=b2b --headed

# Un spec específico
npx playwright test --project=b2b checkout
```

### Maestro (APP mobile)

```bash
# Todos los flows
maestro test tests/app/flows/

# Un flow específico
maestro test tests/app/flows/05-pedido.yaml

# Con grabación
maestro record tests/app/flows/05-pedido.yaml
```

### Checklists manuales

1. Abrir el `.md` correspondiente
2. Ejecutar cada caso según columna "Cómo validar"
3. Cambiar estado `PENDIENTE` → `PASS` o `FAIL`
4. Si FAIL → escalar usando `templates/escalation-templates.md`

---

## 11. Reglas de Testing

1. **Cada test independiente** — no depende del orden ni estado de otro test
2. **Fixtures para datos** — nunca hardcodear emails o IDs de clientes reales
3. **Nombres descriptivos** — `should_block_cart_when_product_price_below_50`, no `test_cart_3`
4. **Un assert por comportamiento** — no mezclar múltiples comportamientos
5. **Consistencia cross-platform** — B2B y APP deben mostrar lo mismo para el mismo comercio
6. **Ambiente separado** — `.env.test`, nunca tocar datos de clientes reales
7. **Lógica de segmentos** — los precios dependen del segmento del comercio, testear con segmento explícito
8. **Credenciales en `.env`** — nunca en código

---

## 12. Mantenimiento

### Agregar un caso nuevo

1. Identificar a qué checklist pertenece (regresión, deuda técnica, servicios, funcional)
2. Agregar con ID secuencial al final de la tabla correspondiente
3. Si es automatizable → crear o extender el `.spec.ts` o `.yaml`
4. Actualizar `checklists/INDICE.md` si se creó checklist nueva

### Después de un incidente en producción

1. Documentar en `checklists/regresion/checklist-regresion-postmortems.md`
2. Crear test automatizado si el caso es reproducible en E2E
3. Agregar a "siempre correr pre-deploy"

### Fuentes a revisar periódicamente

| Fuente | Qué buscar | Frecuencia |
|--------|-----------|-----------|
| [Post-mortems (Notion)](https://www.notion.so/915bf7626ea141879a941f45b2e2ec57) | Incidentes nuevos → casos de regresión | Semanal |
| [Deuda Técnica (Notion)](https://www.notion.so/19ad8139ba4e8061bb86cfd8db6f46fe) | Items nuevos o resueltos | Quincenal |
| Slack #tech | Bugs reportados, cambios urgentes | Diario |
| GitHub PRs | Áreas siendo modificadas | Diario |

---

## 13. Links a Documentos Relacionados

| Documento | Propósito |
|-----------|-----------|
| `B2B_REFERENCE.md` | Selectores UI, componentes, código Playwright B2B |
| `ai-specs/.agents/qa-coordinator.md` | Rol QA Coordinator |
| `ai-specs/.agents/playwright-specialist.md` | Rol Playwright Specialist |
| `ai-specs/.agents/maestro-specialist.md` | Rol Maestro Specialist |
| `ai-specs/specs/qa-standards.mdc` | Estándares: naming, cobertura, fixtures |
| `checklists/INDICE.md` | Mapa de cobertura: checklist → test → estado |
| `playbook-qa-cliente-nuevo.md` | Onboarding QA completo (6 fases) |
| `qa-app-strategy.md` | Estrategia APP mobile |
| `templates/qa-report-template.md` | Template de reporte QA |
| `templates/escalation-templates.md` | Templates de escalamiento |
| `references/issue-taxonomy.md` | Taxonomía de issues (severidad, categoría) |
