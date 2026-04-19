# QA Plan Client

Plan QA concreto para un cliente: lee sus flags desde `qa-matrix.json`, aplica las Flag→Test rules y genera un plan ejecutable en `ai-specs/changes/`.

## Uso

`/qa-plan-client Codelpa` — Genera plan QA para Codelpa

## Pasos

1. **Adoptar rol QA Coordinator** (ver `ai-specs/.agents/qa-coordinator.md`)

2. **Leer contexto del cliente**
   - Linear: tickets abiertos del cliente (deuda técnica, features, bugs)
   - `checklists/INDICE.md`: cobertura existente

3. **Generar checklist pre-producción del cliente** → `QA/{CLIENT}/{DATE}/checklist-preproduccion.md`
   - Copiar el template de `checklists/integraciones/checklist-preproduccion-cliente.md`
   - Con los flags del cliente, auto-marcar como `N/A` los items que no aplican:
     - INT-07 Perfiles aprobadores → N/A si `enableOrderApproval: false`
     - INT-08 Formulario comercios → N/A si `enableCreateCommerce: false`
     - Sección [4] Integraciones externas completa → N/A si todos los hooks son `false`
     - Sección [5] Documentos tributarios completa → N/A si `enablePaymentDocumentsB2B=false` AND `enableInvoicesList=false` AND `enableCreditNotes=false`
   - Guardar en `QA/{CLIENT}/{DATE}/checklist-preproduccion.md`
   - Indicar: _"Checklist generado en QA/{CLIENT}/{DATE}/checklist-preproduccion.md — Tech/Analytics deben completarlo y escribir veredicto LISTO antes de ejecutar `/qa-client-validation`"_

5. **Leer flags del cliente desde `data/qa-matrix-staging.json`**
   - Buscar la entrada del cliente por `slug` o `name`
   - Extraer todos los flags booleanos y de configuración
   - Ejemplos de flags críticos a revisar:
     ```
     enableCoupons, enableKhipu, enablePaymentDocumentsB2B,
     enableInvoicesList, pendingDocuments, enableOrderApproval,
     purchaseOrderEnabled, editAddress, hasStockEnabled,
     hasAllDistributionCenters, enableSellerDiscount,
     disableCommerceEdit, anonymousAccess, enableCreditNotes,
     enableOrderValidation, enablePriceOracle,
     pricing.stepPricing, promotions, ERP hooks
     ```

4. **Aplicar Flag→Test rules** (definidas en `ai-specs/specs/qa-standards.mdc`)

   **4a. Tests obligatorios** (siempre, todo cliente):
   | Test | Tool |
   |------|------|
   | `config-validation/` (cv-*.spec.ts — 6 archivos) | Playwright |
   | `cart.spec.ts` | Playwright |
   | `checkout.spec.ts` | Playwright |
   | `checklist-regresion-postmortems.md` (PM1-PM7) | Checklist |
   | COWORK: C1 (Login) + C2 (Flujo de compra) | Cowork |
   | Maestro: `helpers/login.yaml` + flujo de pedido del cliente | Maestro |

   **4b. Tests condicionales** (por flag activo del cliente):
   - `enableCoupons: true` → `coupons.spec.ts` · COWORK: C3-14, C3-15
   - `enableKhipu: true` → `checklist-fintech-khipu.md` · COWORK: verificar opción Khipu en checkout
   - `enablePaymentDocumentsB2B: true` → `payments.spec.ts` · COWORK: C7-10, C7-11, C7-12
   - `enableInvoicesList: true` → COWORK: C7-11 (menú facturas)
   - `pendingDocuments: true` → COWORK: C7-12 (badge documentos)
   - `enableOrderApproval: true` → COWORK: Flujo 5 (botón aprobar en /orders)
   - `purchaseOrderEnabled: true` → COWORK: C2-11 (campo OC en checkout)
   - `editAddress: false` → COWORK: validar dirección locked en checkout
   - `hasStockEnabled: true` → COWORK: C2-01 (stock en tarjetas)
   - `hasAllDistributionCenters: true` → COWORK: botón "Ver stock" multicentro
   - `enableSellerDiscount: true` → COWORK: campo descuento en carrito
   - `disableCommerceEdit: true` → COWORK: Flujo 3 (perfil locked)
   - `anonymousAccess: true` → COWORK: catálogo sin login
   - `enableCreditNotes: true` → `checklist-deuda-tecnica-pagos.md`
   - `enableOrderValidation: true` → COWORK: C2-12 (doble submit + validación)
   - `pricing.stepPricing` exists → `step-pricing.spec.ts` · `prices.spec.ts`
   - `promotions` exist → `promotions.spec.ts` · COWORK: C3-02
   - `enablePriceOracle: true` → COWORK: precio cambia con fecha de entrega
   - ERP hooks configurados → `checklist-integraciones-erp.md` · `checklist-webhooks.md` · COWORK: C4-09

   **4c. Tests omitidos** (flag ausente o false — documentar motivo):
   - `enableKhipu: false` → skip `checklist-fintech-khipu.md`
   - `enablePaymentDocumentsB2B: false` → skip C7-10, C7-11, C7-12
   - `enableCoupons: false` → skip `coupons.spec.ts`, C3-14, C3-15
   - Sin ERP hooks → skip `checklist-integraciones-erp.md`, `checklist-webhooks.md`
   - APP no desplegada para el cliente → skip todos los flows Maestro

6. **Generar plan** → `ai-specs/changes/QA-{CLIENT}-{DATE}.md`

## Estructura del plan generado

```markdown
# QA Plan: {CLIENT} — {DATE}

## Config Snapshot
Flags extraídos de `data/qa-matrix.json` para {CLIENT}:
| Flag | Valor |
|------|-------|
| enableCoupons | true/false |
| enableKhipu | true/false |
| ... | ... |

## Tests Obligatorios
Todo cliente, toda sesión QA:

| Test | Tool | Tier |
|------|------|------|
| login.spec.ts | Playwright | 1 |
| config-validation.spec.ts | Playwright | 1 |
| cart.spec.ts | Playwright | 1 |
| checkout.spec.ts | Playwright | 1 |
| checklist-regresion-postmortems.md (PM1-PM7) | Checklist | 1 |
| COWORK: C1 (Login) | Cowork | 1 |
| COWORK: C2 (Flujo de compra) | Cowork | 1 |
| Maestro: 01-login.yaml | Maestro | 1 |
| Maestro: 05-pedido.yaml | Maestro | 1 |

## Tests Condicionales
Habilitados por flags activos del cliente:

| Flag | Test | Tool |
|------|------|------|
| enableCoupons: true | coupons.spec.ts · C3-14, C3-15 | Playwright + Cowork |
| ... | ... | ... |

## Tests Omitidos
Skipped por flags ausentes o false:

| Flag | Test omitido | Razón |
|------|-------------|-------|
| enableKhipu: false | checklist-fintech-khipu.md | Flag desactivado |
| ... | ... | ... |

## Plan de Ejecución
Orden recomendado:

**1. Cowork** (validación visual + flujos)
- [ ] C1: Login (C1-01 a C1-06)
- [ ] C2: Flujo de compra (C2-01 a C2-11)
- [ ] [condicionales según flags]

**2. Playwright** (regresión E2E)
- [ ] `npx playwright test --project=b2b` (corre todos los specs del cliente)
- [ ] Specs obligatorios: config-validation/, cart.spec.ts, checkout.spec.ts
- [ ] [specs condicionales según flags]

**3. Maestro** (APP mobile) — solo si APP desplegada para el cliente
- [ ] `./tools/run-maestro.sh {cliente}` (usa {cliente}-session.yaml)

**4. Checklists** (manual)
- [ ] `checklists/regresion/checklist-regresion-postmortems.md`
- [ ] [checklists condicionales según flags]

## Criterios de Éxito
- [ ] 100% Tier 1 tests pasan
- [ ] Zero issues P0 encontrados
- [ ] Cowork emite veredicto LISTO o CON CONDICIONES (documentado)
- [ ] Playwright: sin regresiones en specs obligatorias
- [ ] Issues encontrados registrados con ID {CLIENT}-QA-{NNN}
```

## Documentos clave

- `ai-specs/specs/qa-standards.mdc` — Flag→Test rules (fuente de verdad)
- `qa-master-guide.md` — IDs canónicos de casos (C1-C7, A1, V1)
- `COWORK.md` — Pasos UI concretos para Cowork
- `B2B_REFERENCE.md` — Selectores UI, rutas, stack
- `checklists/INDICE.md` — Mapa de cobertura existente
- `data/qa-matrix-staging.json` — Flags MongoDB por cliente (staging)
